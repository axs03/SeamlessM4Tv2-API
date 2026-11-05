"""Runtime settings, read from environment variables."""

import os
from dataclasses import dataclass


def _int(name: str, default: int) -> int:
    value = os.getenv(name, "").strip()
    return int(value) if value else default


@dataclass(frozen=True)
class Settings:
    model_id: str = "facebook/seamless-m4t-v2-large"
    device: str = "auto"  # auto | cpu | cuda | mps
    dtype: str = "auto"  # auto | float32 | float16 | bfloat16
    max_upload_mb: int = 25
    max_audio_seconds: int = 120  # 0 disables the check
    max_text_chars: int = 2000  # 0 disables the check
    api_key: str = ""  # empty disables auth
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            model_id=os.getenv("MODEL_ID", cls.model_id),
            device=os.getenv("DEVICE", cls.device).lower(),
            dtype=os.getenv("DTYPE", cls.dtype).lower(),
            max_upload_mb=_int("MAX_UPLOAD_MB", cls.max_upload_mb),
            max_audio_seconds=_int("MAX_AUDIO_SECONDS", cls.max_audio_seconds),
            max_text_chars=_int("MAX_TEXT_CHARS", cls.max_text_chars),
            api_key=os.getenv("API_KEY", ""),
            log_level=os.getenv("LOG_LEVEL", cls.log_level).upper(),
        )
