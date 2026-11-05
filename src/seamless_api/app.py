"""HTTP API for SeamlessM4T v2: all five tasks of the model.

Tasks: t2tt (text->text), t2st (text->speech), s2tt (speech->text),
s2st (speech->speech), asr (speech->text in the same language).
"""

import base64
import hmac
import logging
import os
import threading
import time
from urllib.parse import quote

from flask import Flask, Response, jsonify, request
from werkzeug.exceptions import HTTPException

from . import audio as audio_io
from .config import Settings
from .languages import LANGUAGES

log = logging.getLogger("seamless_api")

OPEN_ENDPOINTS = {"ping", "health"}


class ApiError(Exception):
    def __init__(self, message: str, status: int = 400):
        super().__init__(message)
        self.message = message
        self.status = status


class ModelState:
    """Loads the model in a background thread so /health answers during startup."""

    def __init__(self, loader):
        self._loader = loader
        self._lock = threading.Lock()
        self._started = False
        self.translator = None
        self.error = None

    def start(self):
        with self._lock:
            if self._started:
                return
            self._started = True
        threading.Thread(target=self._load, name="model-loader", daemon=True).start()

    def _load(self):
        started = time.monotonic()
        try:
            self.translator = self._loader()
            log.info("model ready in %.1fs", time.monotonic() - started)
        except Exception as exc:  # noqa: BLE001 - surfaced via /health
            log.exception("model failed to load")
            self.error = f"{type(exc).__name__}: {exc}"

    def get(self):
        if self.translator is not None:
            return self.translator
        if self.error:
            raise ApiError(f"model failed to load: {self.error}", 500)
        raise ApiError("model is still loading, retry shortly", 503)


def _default_loader(settings: Settings):
    def load():
        from .model import Translator  # heavy import (torch, transformers)

        return Translator(settings.model_id, device=settings.device, dtype=settings.dtype)

    return load


def create_app(settings: Settings | None = None, loader=None) -> Flask:
    settings = settings or Settings.from_env()
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = settings.max_upload_mb * 1024 * 1024
    state = ModelState(loader or _default_loader(settings))
    app.extensions["model_state"] = state
    state.start()

    # ---------- helpers ----------

    def check_lang(code, field: str, capability: str, label: str) -> str:
        if not code:
            raise ApiError(f"missing parameter: {field}")
        lang = LANGUAGES.get(code)
        if lang is None:
            raise ApiError(f"unknown language code for {field}: {code!r} (see GET /languages)")
        if not getattr(lang, capability):
            raise ApiError(f"{field}={code!r} ({lang.name}) is not supported as {label}")
        return code

    def json_body() -> dict:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            raise ApiError("request body must be a JSON object")
        return data

    def text_param(data: dict) -> str:
        text = data.get("text")
        if not isinstance(text, str) or not text.strip():
            raise ApiError("missing parameter: text")
        if settings.max_text_chars and len(text) > settings.max_text_chars:
            raise ApiError(f"text is longer than {settings.max_text_chars} characters", 413)
        return text

    def uploaded_audio():
        file = request.files.get("file")
        if file is None or not file.filename:
            raise ApiError("missing file upload (multipart field 'file')")
        try:
            wave = audio_io.decode(file.read())
        except audio_io.AudioDecodeError as exc:
            raise ApiError(str(exc)) from exc
        seconds = audio_io.duration_seconds(wave)
        if settings.max_audio_seconds and seconds > settings.max_audio_seconds:
            raise ApiError(
                f"audio is {seconds:.0f}s long, the limit is {settings.max_audio_seconds}s", 413
            )
        return wave

    def response_format(value) -> str:
        fmt = (value or "wav").lower()
        if fmt not in ("wav", "json"):
            raise ApiError("response_format must be 'wav' or 'json'")
        return fmt

    def speech_response(wave, text: str, fmt: str, download_name: str):
        wav = audio_io.encode_wav(wave)
        if fmt == "json":
            return jsonify(
                text=text,
                sample_rate=audio_io.SAMPLE_RATE,
                audio_base64=base64.b64encode(wav).decode("ascii"),
            )
        resp = Response(wav, mimetype="audio/wav")
        resp.headers["Content-Disposition"] = f'attachment; filename="{download_name}"'
        # Headers must be latin-1, so the translated text is percent-encoded (UTF-8).
        resp.headers["X-Translated-Text"] = quote(text, safe="")
        return resp

    # ---------- auth and errors ----------

    @app.before_request
    def require_api_key():
        if not settings.api_key or request.endpoint in OPEN_ENDPOINTS:
            return None
        header = request.headers.get("Authorization", "")
        token = header[7:] if header.startswith("Bearer ") else ""
        if not hmac.compare_digest(token.encode(), settings.api_key.encode()):
            return jsonify(error="missing or invalid API key"), 401
        return None

    @app.errorhandler(ApiError)
    def api_error(exc: ApiError):
        return jsonify(error=exc.message), exc.status

    @app.errorhandler(HTTPException)
    def http_error(exc: HTTPException):
        if exc.code == 413:
            return jsonify(error=f"upload is larger than {settings.max_upload_mb} MB"), 413
        return jsonify(error=exc.description), exc.code

    @app.errorhandler(Exception)
    def unexpected_error(exc: Exception):
        log.exception("unhandled error on %s", request.path)
        return jsonify(error="internal server error"), 500

    # ---------- routes ----------

    @app.get("/ping")
    def ping():
        return "pong", 200

    @app.get("/health")
    def health():
        if state.translator is not None:
            return jsonify(status="ok", model=settings.model_id, device=state.translator.device)
        if state.error:
            return jsonify(status="error", error=state.error), 500
        return jsonify(status="loading"), 503

    @app.get("/languages")
    def languages():
        return jsonify(
            languages=[
                {
                    "code": code,
                    "name": lang.name,
                    "script": lang.script,
                    "speech_source": lang.speech_source,
                    "text_source": lang.text_source,
                    "speech_target": lang.speech_target,
                    "text_target": lang.text_target,
                }
                for code, lang in LANGUAGES.items()
            ]
        )

    @app.post("/t2tt")
    def t2tt():
        data = json_body()
        text = text_param(data)
        src = check_lang(data.get("src_lang"), "src_lang", "text_source", "a text source")
        tgt = check_lang(data.get("tgt_lang"), "tgt_lang", "text_target", "a text target")
        return jsonify(text=state.get().t2tt(text, src, tgt))

    @app.post("/t2st")
    @app.post("/t2s")  # legacy name
    def t2st():
        data = json_body()
        text = text_param(data)
        src = check_lang(data.get("src_lang"), "src_lang", "text_source", "a text source")
        tgt = check_lang(data.get("tgt_lang"), "tgt_lang", "speech_target", "a speech target")
        fmt = response_format(data.get("response_format"))
        wave, out_text = state.get().t2st(text, src, tgt)
        return speech_response(wave, out_text, fmt, "translated_text_audio.wav")

    @app.post("/s2tt")
    def s2tt():
        tgt = check_lang(request.form.get("tgt_lang"), "tgt_lang", "text_target", "a text target")
        wave = uploaded_audio()
        return jsonify(text=state.get().s2tt(wave, tgt))

    @app.post("/s2st")
    @app.post("/s2s")  # legacy name
    def s2st():
        tgt = check_lang(
            request.form.get("tgt_lang"), "tgt_lang", "speech_target", "a speech target"
        )
        fmt = response_format(request.form.get("response_format"))
        wave = uploaded_audio()
        out_wave, out_text = state.get().s2st(wave, tgt)
        return speech_response(out_wave, out_text, fmt, "translated_speech_audio.wav")

    @app.post("/asr")
    def asr():
        lang = check_lang(request.form.get("lang"), "lang", "speech_source", "a speech source")
        check_lang(lang, "lang", "text_target", "a transcription language")
        wave = uploaded_audio()
        return jsonify(text=state.get().asr(wave, lang))

    return app


# gunicorn runs the factory directly: gunicorn "seamless_api.app:create_app()".
if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
