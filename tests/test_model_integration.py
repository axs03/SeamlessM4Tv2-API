"""Runs all five tasks through the real transformers code path.

Uses the real processor and generation config of facebook/seamless-m4t-v2-large
(small files only) with a tiny, randomly initialized model, so output text and
audio are noise but every call, argument and return shape is the real one.
Run with: pytest -m integration
"""

import numpy as np
import pytest

torch = pytest.importorskip("torch")
transformers = pytest.importorskip("transformers")

pytestmark = pytest.mark.integration

REPO = "facebook/seamless-m4t-v2-large"
SMALL_FILES = [
    "config.json", "generation_config.json", "preprocessor_config.json",
    "special_tokens_map.json", "tokenizer_config.json", "added_tokens.json",
    "sentencepiece.bpe.model", "tokenizer.model",
]

TINY = dict(
    hidden_size=32, encoder_layers=1, decoder_layers=1, encoder_attention_heads=2,
    decoder_attention_heads=2, encoder_ffn_dim=32, decoder_ffn_dim=32,
    speech_encoder_layers=1, speech_encoder_attention_heads=2,
    speech_encoder_intermediate_size=32, num_adapter_layers=1,
    t2u_encoder_layers=1, t2u_decoder_layers=1, t2u_encoder_attention_heads=2,
    t2u_decoder_attention_heads=2, t2u_encoder_ffn_dim=32, t2u_decoder_ffn_dim=32,
    t2u_variance_predictor_embed_dim=32, t2u_variance_predictor_hidden_dim=16,
    upsample_initial_channel=64, unit_embed_dim=32, lang_embed_dim=8, spkr_embed_dim=8,
    max_new_tokens=6,
)


@pytest.fixture(scope="module")
def translator():
    from huggingface_hub import snapshot_download
    from transformers import (
        AutoProcessor,
        GenerationConfig,
        SeamlessM4Tv2Config,
        SeamlessM4Tv2Model,
    )

    from seamless_api.model import Translator

    try:
        path = snapshot_download(REPO, allow_patterns=SMALL_FILES)
    except Exception as exc:  # offline
        pytest.skip(f"cannot download processor files: {exc}")
    config = SeamlessM4Tv2Config.from_pretrained(path, **TINY)
    torch.manual_seed(0)
    tiny = SeamlessM4Tv2Model(config)
    tiny.generation_config = GenerationConfig.from_pretrained(path)
    tiny.generation_config.max_new_tokens = 6
    processor = AutoProcessor.from_pretrained(path)
    return Translator(REPO, device="cpu", model=tiny, processor=processor)


def tone(seconds=1.0):
    t = np.linspace(0, seconds, int(16000 * seconds), endpoint=False)
    return (0.3 * np.sin(2 * np.pi * 220 * t)).astype(np.float32)


def test_text_tasks(translator):
    assert isinstance(translator.t2tt("Hello world", "eng", "fra"), str)
    assert isinstance(translator.s2tt(tone(), "fra"), str)
    assert isinstance(translator.asr(tone(), "eng"), str)


def test_speech_tasks(translator):
    for wave, text in (translator.t2st("Hello world", "eng", "fra"),
                       translator.s2st(tone(), "spa")):
        assert isinstance(text, str)
        assert wave.dtype == np.float32 and wave.ndim == 1 and wave.size > 0


def test_language_table_matches_model(translator):
    from seamless_api.languages import LANGUAGES

    gen = translator.model.generation_config
    text_codes = set(gen.text_decoder_lang_to_code_id)
    speech_codes = set(gen.vocoder_lang_code_to_id)
    table_text = {c for c, lang in LANGUAGES.items() if lang.text_target}
    table_speech = {c for c, lang in LANGUAGES.items() if lang.speech_target}
    assert table_text == text_codes
    assert table_speech == speech_codes
    vocab = translator.processor.tokenizer.get_vocab()
    missing = [c for c, lang in LANGUAGES.items() if lang.text_source and f"__{c}__" not in vocab]
    assert missing == []
