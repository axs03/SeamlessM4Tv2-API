"""Languages supported by SeamlessM4T v2.

Generated from Supported_Langs.md (the facebook/seamless-m4t-v2-large model card), then
corrected against the model's own generation_config.json and tokenizer, which the
model card table disagrees with in a few places:
- Malay text uses the code zlm (the card lists zsm, which the tokenizer does not have).
- cmn_Hant has no speech output (it is not in the vocoder's language list).
- Santali (sat) is a text language missing from the card.
tests/test_model_integration.py checks this table against the model.
"""

from typing import NamedTuple


class Language(NamedTuple):
    name: str
    script: str
    speech_source: bool
    text_source: bool
    speech_target: bool
    text_target: bool


LANGUAGES: dict[str, Language] = {
    "afr": Language("Afrikaans", "Latn", True, True, False, True),
    "amh": Language("Amharic", "Ethi", True, True, False, True),
    "arb": Language("Modern Standard Arabic", "Arab", True, True, True, True),
    "ary": Language("Moroccan Arabic", "Arab", True, True, False, True),
    "arz": Language("Egyptian Arabic", "Arab", True, True, False, True),
    "asm": Language("Assamese", "Beng", True, True, False, True),
    "ast": Language("Asturian", "Latn", True, False, False, False),
    "azj": Language("North Azerbaijani", "Latn", True, True, False, True),
    "bel": Language("Belarusian", "Cyrl", True, True, False, True),
    "ben": Language("Bengali", "Beng", True, True, True, True),
    "bos": Language("Bosnian", "Latn", True, True, False, True),
    "bul": Language("Bulgarian", "Cyrl", True, True, False, True),
    "cat": Language("Catalan", "Latn", True, True, True, True),
    "ceb": Language("Cebuano", "Latn", True, True, False, True),
    "ces": Language("Czech", "Latn", True, True, True, True),
    "ckb": Language("Central Kurdish", "Arab", True, True, False, True),
    "cmn": Language("Mandarin Chinese", "Hans", True, True, True, True),
    "cmn_Hant": Language("Mandarin Chinese", "Hant", True, True, False, True),
    "cym": Language("Welsh", "Latn", True, True, True, True),
    "dan": Language("Danish", "Latn", True, True, True, True),
    "deu": Language("German", "Latn", True, True, True, True),
    "ell": Language("Greek", "Grek", True, True, False, True),
    "eng": Language("English", "Latn", True, True, True, True),
    "est": Language("Estonian", "Latn", True, True, True, True),
    "eus": Language("Basque", "Latn", True, True, False, True),
    "fin": Language("Finnish", "Latn", True, True, True, True),
    "fra": Language("French", "Latn", True, True, True, True),
    "fuv": Language("Nigerian Fulfulde", "Latn", True, True, False, True),
    "gaz": Language("West Central Oromo", "Latn", True, True, False, True),
    "gle": Language("Irish", "Latn", True, True, False, True),
    "glg": Language("Galician", "Latn", True, True, False, True),
    "guj": Language("Gujarati", "Gujr", True, True, False, True),
    "heb": Language("Hebrew", "Hebr", True, True, False, True),
    "hin": Language("Hindi", "Deva", True, True, True, True),
    "hrv": Language("Croatian", "Latn", True, True, False, True),
    "hun": Language("Hungarian", "Latn", True, True, False, True),
    "hye": Language("Armenian", "Armn", True, True, False, True),
    "ibo": Language("Igbo", "Latn", True, True, False, True),
    "ind": Language("Indonesian", "Latn", True, True, True, True),
    "isl": Language("Icelandic", "Latn", True, True, False, True),
    "ita": Language("Italian", "Latn", True, True, True, True),
    "jav": Language("Javanese", "Latn", True, True, False, True),
    "jpn": Language("Japanese", "Jpan", True, True, True, True),
    "kam": Language("Kamba", "Latn", True, False, False, False),
    "kan": Language("Kannada", "Knda", True, True, False, True),
    "kat": Language("Georgian", "Geor", True, True, False, True),
    "kaz": Language("Kazakh", "Cyrl", True, True, False, True),
    "kea": Language("Kabuverdianu", "Latn", True, False, False, False),
    "khk": Language("Halh Mongolian", "Cyrl", True, True, False, True),
    "khm": Language("Khmer", "Khmr", True, True, False, True),
    "kir": Language("Kyrgyz", "Cyrl", True, True, False, True),
    "kor": Language("Korean", "Kore", True, True, True, True),
    "lao": Language("Lao", "Laoo", True, True, False, True),
    "lit": Language("Lithuanian", "Latn", True, True, False, True),
    "ltz": Language("Luxembourgish", "Latn", True, False, False, False),
    "lug": Language("Ganda", "Latn", True, True, False, True),
    "luo": Language("Luo", "Latn", True, True, False, True),
    "lvs": Language("Standard Latvian", "Latn", True, True, False, True),
    "mai": Language("Maithili", "Deva", True, True, False, True),
    "mal": Language("Malayalam", "Mlym", True, True, False, True),
    "mar": Language("Marathi", "Deva", True, True, False, True),
    "mkd": Language("Macedonian", "Cyrl", True, True, False, True),
    "mlt": Language("Maltese", "Latn", True, True, True, True),
    "mni": Language("Meitei", "Beng", True, True, False, True),
    "mya": Language("Burmese", "Mymr", True, True, False, True),
    "nld": Language("Dutch", "Latn", True, True, True, True),
    "nno": Language("Norwegian Nynorsk", "Latn", True, True, False, True),
    "nob": Language("Norwegian Bokmål", "Latn", True, True, False, True),
    "npi": Language("Nepali", "Deva", True, True, False, True),
    "nya": Language("Nyanja", "Latn", True, True, False, True),
    "oci": Language("Occitan", "Latn", True, False, False, False),
    "ory": Language("Odia", "Orya", True, True, False, True),
    "pan": Language("Punjabi", "Guru", True, True, False, True),
    "pbt": Language("Southern Pashto", "Arab", True, True, False, True),
    "pes": Language("Western Persian", "Arab", True, True, True, True),
    "pol": Language("Polish", "Latn", True, True, True, True),
    "por": Language("Portuguese", "Latn", True, True, True, True),
    "ron": Language("Romanian", "Latn", True, True, True, True),
    "rus": Language("Russian", "Cyrl", True, True, True, True),
    "sat": Language("Santali", "Olck", False, True, False, True),
    "slk": Language("Slovak", "Latn", True, True, True, True),
    "slv": Language("Slovenian", "Latn", True, True, False, True),
    "sna": Language("Shona", "Latn", True, True, False, True),
    "snd": Language("Sindhi", "Arab", True, True, False, True),
    "som": Language("Somali", "Latn", True, True, False, True),
    "spa": Language("Spanish", "Latn", True, True, True, True),
    "srp": Language("Serbian", "Cyrl", True, True, False, True),
    "swe": Language("Swedish", "Latn", True, True, True, True),
    "swh": Language("Swahili", "Latn", True, True, True, True),
    "tam": Language("Tamil", "Taml", True, True, False, True),
    "tel": Language("Telugu", "Telu", True, True, True, True),
    "tgk": Language("Tajik", "Cyrl", True, True, False, True),
    "tgl": Language("Tagalog", "Latn", True, True, True, True),
    "tha": Language("Thai", "Thai", True, True, True, True),
    "tur": Language("Turkish", "Latn", True, True, True, True),
    "ukr": Language("Ukrainian", "Cyrl", True, True, True, True),
    "urd": Language("Urdu", "Arab", True, True, True, True),
    "uzn": Language("Northern Uzbek", "Latn", True, True, True, True),
    "vie": Language("Vietnamese", "Latn", True, True, True, True),
    "xho": Language("Xhosa", "Latn", True, False, False, False),
    "yor": Language("Yoruba", "Latn", True, True, False, True),
    "yue": Language("Cantonese", "Hant", True, True, False, True),
    "zlm": Language("Malay", "Latn", True, True, False, True),
    "zul": Language("Zulu", "Latn", True, True, False, True),
}
