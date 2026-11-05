"""Audio decoding and encoding.

Input of any format ffmpeg can read is converted to the 16 kHz mono float32
waveform the model expects. Output is 16-bit PCM WAV.
"""

import io
import os
import subprocess
import tempfile

import numpy as np
from scipy.io import wavfile

SAMPLE_RATE = 16000
FFMPEG_TIMEOUT_SECONDS = 300


class AudioDecodeError(ValueError):
    pass


def decode(data: bytes) -> np.ndarray:
    """Decode any ffmpeg-readable audio/video bytes to mono 16 kHz float32."""
    if not data:
        raise AudioDecodeError("empty audio file")
    # A real file (not a pipe) so formats that need seeking (mp4/m4a) work.
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "input")
        with open(path, "wb") as f:
            f.write(data)
        try:
            proc = subprocess.run(
                [
                    "ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error",
                    "-i", path,
                    "-vn", "-ac", "1", "-ar", str(SAMPLE_RATE), "-f", "f32le", "pipe:1",
                ],
                capture_output=True,
                timeout=FFMPEG_TIMEOUT_SECONDS,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise AudioDecodeError("audio decoding timed out") from exc
    if proc.returncode != 0:
        detail = proc.stderr.decode(errors="replace").strip().splitlines()
        raise AudioDecodeError(
            "could not decode audio" + (f": {detail[-1]}" if detail else "")
        )
    audio = np.frombuffer(proc.stdout, dtype=np.float32)
    if audio.size == 0:
        raise AudioDecodeError("audio file contains no audio samples")
    return audio


def duration_seconds(audio: np.ndarray) -> float:
    return audio.shape[-1] / SAMPLE_RATE


def encode_wav(audio: np.ndarray) -> bytes:
    """Encode a float waveform in [-1, 1] as 16-bit PCM WAV bytes."""
    pcm = (np.clip(np.asarray(audio, dtype=np.float32), -1.0, 1.0) * 32767).astype(np.int16)
    buf = io.BytesIO()
    wavfile.write(buf, SAMPLE_RATE, pcm)
    return buf.getvalue()
