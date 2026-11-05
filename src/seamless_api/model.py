"""SeamlessM4T v2 model wrapper exposing the model's five tasks."""

import logging
import threading

import numpy as np
import torch
from transformers import AutoProcessor, SeamlessM4Tv2Model

from .audio import SAMPLE_RATE

log = logging.getLogger(__name__)

# NNPACK prints "Could not initialize NNPACK" on CPUs it does not support (common
# under amd64 emulation on Apple Silicon). It is not needed for this model.
torch.backends.nnpack.enabled = False

_DTYPES = {"float32": torch.float32, "float16": torch.float16, "bfloat16": torch.bfloat16}


def pick_device(requested: str = "auto") -> str:
    requested = (requested or "auto").lower()
    if requested != "auto":
        return requested
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def pick_dtype(requested: str, device: str) -> torch.dtype:
    requested = (requested or "auto").lower()
    if requested == "auto":
        return torch.float16 if device == "cuda" else torch.float32
    if requested not in _DTYPES:
        raise ValueError(f"unsupported DTYPE {requested!r}, use one of {sorted(_DTYPES)}")
    return _DTYPES[requested]


class Translator:
    """One loaded model. Calls are serialized: one generation at a time."""

    def __init__(self, model_id: str, device: str = "auto", dtype: str = "auto",
                 model=None, processor=None):
        self.device = pick_device(device)
        self.dtype = pick_dtype(dtype, self.device)
        log.info("loading %s on %s (%s)", model_id, self.device, self.dtype)
        self.processor = processor or AutoProcessor.from_pretrained(model_id)
        if model is None:
            model = SeamlessM4Tv2Model.from_pretrained(model_id, dtype=self.dtype)
        self.model = model.to(self.device).eval()
        self._lock = threading.Lock()

    # ----- input preparation -----

    def _to_device(self, inputs):
        inputs = inputs.to(self.device)
        if "input_features" in inputs:
            inputs["input_features"] = inputs["input_features"].to(self.dtype)
        return inputs

    def _text_inputs(self, text: str, src_lang: str):
        return self._to_device(self.processor(text=text, src_lang=src_lang, return_tensors="pt"))

    def _audio_inputs(self, wave: np.ndarray):
        return self._to_device(
            self.processor(audio=wave, sampling_rate=SAMPLE_RATE, return_tensors="pt")
        )

    # ----- generation -----

    def _generate_text(self, inputs, tgt_lang: str) -> str:
        with self._lock, torch.inference_mode():
            out = self.model.generate(**inputs, tgt_lang=tgt_lang, generate_speech=False)
        return self.processor.decode(out[0][0], skip_special_tokens=True).strip()

    def _generate_speech(self, inputs, tgt_lang: str) -> tuple[np.ndarray, str]:
        with self._lock, torch.inference_mode():
            out = self.model.generate(
                **inputs, tgt_lang=tgt_lang, return_intermediate_token_ids=True
            )
        wave = out.waveform[0]
        if out.waveform_lengths is not None:
            # 0-dim for a single input in current transformers, 1-dim in others.
            wave = wave[: int(out.waveform_lengths.reshape(-1)[0])]
        text = self.processor.decode(out.sequences[0], skip_special_tokens=True).strip()
        return wave.float().cpu().numpy(), text

    # ----- the five tasks -----

    def t2tt(self, text: str, src_lang: str, tgt_lang: str) -> str:
        return self._generate_text(self._text_inputs(text, src_lang), tgt_lang)

    def t2st(self, text: str, src_lang: str, tgt_lang: str) -> tuple[np.ndarray, str]:
        return self._generate_speech(self._text_inputs(text, src_lang), tgt_lang)

    def s2tt(self, wave: np.ndarray, tgt_lang: str) -> str:
        return self._generate_text(self._audio_inputs(wave), tgt_lang)

    def s2st(self, wave: np.ndarray, tgt_lang: str) -> tuple[np.ndarray, str]:
        return self._generate_speech(self._audio_inputs(wave), tgt_lang)

    def asr(self, wave: np.ndarray, lang: str) -> str:
        # ASR is speech-to-text with the target set to the spoken language.
        return self._generate_text(self._audio_inputs(wave), lang)
