import base64
import io
import subprocess
from urllib.parse import unquote

import numpy as np
import pytest
from scipy.io import wavfile

import audio as audio_io
from app import create_app
from config import Settings


class FakeTranslator:
    device = "cpu"

    def __init__(self):
        self.calls = []

    def t2tt(self, text, src, tgt):
        self.calls.append(("t2tt", text, src, tgt))
        return f"[{tgt}] {text}"

    def t2st(self, text, src, tgt):
        self.calls.append(("t2st", text, src, tgt))
        return np.zeros(1600, dtype=np.float32), "héllo wörld"

    def s2tt(self, wave, tgt):
        self.calls.append(("s2tt", wave.shape, tgt))
        return f"[{tgt}] speech"

    def s2st(self, wave, tgt):
        self.calls.append(("s2st", wave.shape, tgt))
        return np.zeros(3200, dtype=np.float32), "bonjour"

    def asr(self, wave, lang):
        self.calls.append(("asr", wave.shape, lang))
        return "hello"


def make_app(**overrides):
    fake = FakeTranslator()
    app = create_app(Settings(**overrides), loader=lambda: fake)
    state = app.extensions["model_state"]
    for _ in range(200):  # loader runs in a thread; the fake returns at once
        if state.translator is not None:
            break
        import time

        time.sleep(0.01)
    return app, fake


@pytest.fixture
def client_and_fake():
    app, fake = make_app()
    return app.test_client(), fake


def wav_bytes(seconds=1.0, channels=1, rate=44100):
    n = int(seconds * rate)
    t = np.linspace(0, seconds, n, endpoint=False)
    tone = (0.3 * np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16)
    data = np.stack([tone] * channels, axis=1) if channels > 1 else tone
    buf = io.BytesIO()
    wavfile.write(buf, rate, data)
    return buf.getvalue()


def mp3_bytes(seconds=1.0):
    proc = subprocess.run(
        ["ffmpeg", "-nostdin", "-loglevel", "error", "-f", "lavfi",
         "-i", f"sine=frequency=440:duration={seconds}", "-ac", "2", "-f", "mp3", "pipe:1"],
        capture_output=True, check=True,
    )
    return proc.stdout


# ---------- health / meta ----------

def test_ping(client_and_fake):
    client, _ = client_and_fake
    assert client.get("/ping").data == b"pong"


def test_health_ok(client_and_fake):
    client, _ = client_and_fake
    r = client.get("/health")
    assert r.status_code == 200 and r.json["status"] == "ok"


def test_health_loading_and_503_while_loading():
    import threading

    gate = threading.Event()
    app = create_app(Settings(), loader=lambda: gate.wait(5) or FakeTranslator())
    client = app.test_client()
    assert client.get("/health").status_code == 503
    r = client.post("/t2tt", json={"text": "hi", "src_lang": "eng", "tgt_lang": "fra"})
    assert r.status_code == 503
    gate.set()


def test_health_error_when_load_fails():
    def boom():
        raise RuntimeError("no weights")

    app = create_app(Settings(), loader=boom)
    state = app.extensions["model_state"]
    import time

    for _ in range(200):
        if state.error:
            break
        time.sleep(0.01)
    r = app.test_client().get("/health")
    assert r.status_code == 500 and "no weights" in r.json["error"]


def test_languages(client_and_fake):
    client, _ = client_and_fake
    langs = {lang["code"]: lang for lang in client.get("/languages").json["languages"]}
    assert langs["fra"]["speech_target"] is True
    assert langs["afr"]["speech_target"] is False


# ---------- text input ----------

def test_t2tt(client_and_fake):
    client, fake = client_and_fake
    r = client.post("/t2tt", json={"text": "Hello", "src_lang": "eng", "tgt_lang": "fra"})
    assert r.status_code == 200 and r.json["text"] == "[fra] Hello"
    assert fake.calls == [("t2tt", "Hello", "eng", "fra")]


@pytest.mark.parametrize("body,needle", [
    (None, "JSON object"),
    ({"src_lang": "eng", "tgt_lang": "fra"}, "text"),
    ({"text": "hi", "tgt_lang": "fra"}, "src_lang"),
    ({"text": "hi", "src_lang": "eng"}, "tgt_lang"),
    ({"text": "hi", "src_lang": "eng", "tgt_lang": "xx"}, "unknown language"),
])
def test_t2tt_validation(client_and_fake, body, needle):
    client, fake = client_and_fake
    r = client.post("/t2tt", json=body) if body is not None else client.post("/t2tt", data="x")
    assert r.status_code == 400 and needle in r.json["error"]
    assert fake.calls == []


def test_text_too_long():
    app, _ = make_app(max_text_chars=5)
    body = {"text": "123456", "src_lang": "eng", "tgt_lang": "fra"}
    r = app.test_client().post("/t2tt", json=body)
    assert r.status_code == 413


def test_t2st_rejects_text_only_target(client_and_fake):
    client, fake = client_and_fake
    r = client.post("/t2st", json={"text": "hi", "src_lang": "eng", "tgt_lang": "afr"})
    assert r.status_code == 400 and "speech target" in r.json["error"]
    assert fake.calls == []


@pytest.mark.parametrize("path", ["/t2st", "/t2s"])
def test_t2st_wav(client_and_fake, path):
    client, _ = client_and_fake
    r = client.post(path, json={"text": "hi", "src_lang": "eng", "tgt_lang": "fra"})
    assert r.status_code == 200 and r.mimetype == "audio/wav"
    rate, data = wavfile.read(io.BytesIO(r.data))
    assert rate == 16000 and data.dtype == np.int16 and len(data) == 1600
    assert unquote(r.headers["X-Translated-Text"]) == "héllo wörld"


def test_t2st_json(client_and_fake):
    client, _ = client_and_fake
    r = client.post("/t2st", json={"text": "hi", "src_lang": "eng", "tgt_lang": "fra",
                                   "response_format": "json"})
    assert r.json["text"] == "héllo wörld" and r.json["sample_rate"] == 16000
    rate, _ = wavfile.read(io.BytesIO(base64.b64decode(r.json["audio_base64"])))
    assert rate == 16000


# ---------- speech input ----------

def test_s2tt_stereo_wav_is_downmixed_and_resampled(client_and_fake):
    client, fake = client_and_fake
    r = client.post("/s2tt", data={"tgt_lang": "eng",
                                   "file": (io.BytesIO(wav_bytes(1.0, channels=2)), "a.wav")})
    assert r.status_code == 200, r.json
    assert fake.calls == [("s2tt", (16000,), "eng")]


@pytest.mark.parametrize("path", ["/s2st", "/s2s"])
def test_s2st_accepts_mp3(client_and_fake, path):
    client, fake = client_and_fake
    r = client.post(path, data={"tgt_lang": "fra", "file": (io.BytesIO(mp3_bytes()), "a.mp3")})
    assert r.status_code == 200 and r.mimetype == "audio/wav"
    assert fake.calls[0][0] == "s2st" and fake.calls[0][2] == "fra"


def test_asr(client_and_fake):
    client, fake = client_and_fake
    r = client.post("/asr", data={"lang": "eng", "file": (io.BytesIO(wav_bytes()), "a.wav")})
    assert r.json == {"text": "hello"} and fake.calls[0][2] == "eng"


def test_asr_rejects_speech_only_language(client_and_fake):
    client, _ = client_and_fake  # 'kam' is a speech source with no text output
    r = client.post("/asr", data={"lang": "kam", "file": (io.BytesIO(wav_bytes()), "a.wav")})
    assert r.status_code == 400


def test_missing_file(client_and_fake):
    client, _ = client_and_fake
    r = client.post("/s2tt", data={"tgt_lang": "eng"})
    assert r.status_code == 400 and "file" in r.json["error"]


def test_garbage_file(client_and_fake):
    client, fake = client_and_fake
    r = client.post("/s2tt", data={"tgt_lang": "eng",
                                   "file": (io.BytesIO(b"not audio at all"), "a.wav")})
    assert r.status_code == 400 and "decode" in r.json["error"]
    assert fake.calls == []


def test_audio_too_long():
    app, fake = make_app(max_audio_seconds=1)
    r = app.test_client().post("/s2tt", data={"tgt_lang": "eng",
                                              "file": (io.BytesIO(wav_bytes(2.0)), "a.wav")})
    assert r.status_code == 413 and fake.calls == []


def test_upload_too_large():
    app, _ = make_app(max_upload_mb=1)
    big = io.BytesIO(b"0" * (2 * 1024 * 1024))
    r = app.test_client().post("/s2tt", data={"tgt_lang": "eng", "file": (big, "a.wav")})
    assert r.status_code == 413 and "MB" in r.json["error"]


# ---------- auth ----------

def test_api_key():
    app, _ = make_app(api_key="secret")
    client = app.test_client()
    body = {"text": "hi", "src_lang": "eng", "tgt_lang": "fra"}
    assert client.get("/health").status_code == 200  # open for healthchecks
    assert client.post("/t2tt", json=body).status_code == 401
    bad = {"Authorization": "Bearer nope"}
    assert client.post("/t2tt", json=body, headers=bad).status_code == 401
    good = {"Authorization": "Bearer secret"}
    assert client.post("/t2tt", json=body, headers=good).status_code == 200


# ---------- audio helpers ----------

def test_encode_wav_clips():
    rate, data = wavfile.read(io.BytesIO(audio_io.encode_wav(np.array([2.0, -2.0, 0.0]))))
    assert rate == 16000 and list(data) == [32767, -32767, 0]
