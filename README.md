# SeamlessM4Tv2-API
Custom API endpoints for generating text-to-speech and speech-to-speech translation audio files, ready for deployment. 
<p> SeamlessM4T-v2 is a collection of models designed to provide high quality translation, allowing people from different linguistic communities to communicate effortlessly through speech and text. </p>

## Cloning and Installation
Begin by cloning the repository onto your local machine using 
``` gitignore
git clone https://github.com/as9219/SeamlessM4Tv2-API.git
```
Open your preferred IDE and make sure to have the latest version of Python installed.
Next, install all the requirments using 
``` bat
pip install -r requirements.txt
```

## Execution and Making Test Calls
Run the application in your IDE or command line using 

``` python
python App.py
```
or
``` python
python3 App.py
``` 

A flask server should start and you will have your local flask URL.

### CURL Paramaters
| **Name**        | **Importance**     | **Description**                    |
|---------------------|----------|------------------------------------|
| text                | <code>required</code> | Any text you would like to convert |
| src_lang            | <code>optional</code> | default: eng                       |
| tgt_lang            | <code>optional</code> | default: fra                       |
| flask_localhost_url | <code>required</code> | Your flask localhost URL           |

### CURL Commands
#### T2S
``` bat
curl -X POST -H "Content-Type: application/json" -d '{"text": "Hello World, I am making a text to speech curl command!", "src_lang": "eng", "tgt_lang": "fra"}' {flask_localhost_url}/t2s
```

#### S2S
``` bat
curl -X POST -H "Content-Type: multipart/form-data" -F "file=path/to/audio_file.wav" -F "tgt_lang=eng" {flask_localhost_url}/s2s
```

### Supported Languages
This was grabbed from <a href='https://huggingface.co/facebook/seamless-m4t-v2-large'>the official documentation</a><br>
| **code** | **language**           | **script** | **Source** | **Target** |
| -------- | ---------------------- | ---------- | ---------- | ---------- |
| afr      | Afrikaans              | Latn       | Sp, Tx     | Tx         |
| amh      | Amharic                | Ethi       | Sp, Tx     | Tx         |
| arb      | Modern Standard Arabic | Arab       | Sp, Tx     | Sp, Tx     |
| ary      | Moroccan Arabic        | Arab       | Sp, Tx     | Tx         |
| arz      | Egyptian Arabic        | Arab       | Sp, Tx     | Tx         |
| asm      | Assamese               | Beng       | Sp, Tx     | Tx         |
| ast      | Asturian               | Latn       | Sp         | \--        |
| azj      | North Azerbaijani      | Latn       | Sp, Tx     | Tx         |
| bel      | Belarusian             | Cyrl       | Sp, Tx     | Tx         |
| ben      | Bengali                | Beng       | Sp, Tx     | Sp, Tx     |
| bos      | Bosnian                | Latn       | Sp, Tx     | Tx         |
| bul      | Bulgarian              | Cyrl       | Sp, Tx     | Tx         |
| cat      | Catalan                | Latn       | Sp, Tx     | Sp, Tx     |
| ceb      | Cebuano                | Latn       | Sp, Tx     | Tx         |
| ces      | Czech                  | Latn       | Sp, Tx     | Sp, Tx     |
| ckb      | Central Kurdish        | Arab       | Sp, Tx     | Tx         |
| cmn      | Mandarin Chinese       | Hans       | Sp, Tx     | Sp, Tx     |
| cmn_Hant | Mandarin Chinese       | Hant       | Sp, Tx     | Sp, Tx     |
| cym      | Welsh                  | Latn       | Sp, Tx     | Sp, Tx     |
| dan      | Danish                 | Latn       | Sp, Tx     | Sp, Tx     |
| deu      | German                 | Latn       | Sp, Tx     | Sp, Tx     |
| ell      | Greek                  | Grek       | Sp, Tx     | Tx         |
| eng      | English                | Latn       | Sp, Tx     | Sp, Tx     |
| est      | Estonian               | Latn       | Sp, Tx     | Sp, Tx     |
| eus      | Basque                 | Latn       | Sp, Tx     | Tx         |
| fin      | Finnish                | Latn       | Sp, Tx     | Sp, Tx     |
| fra      | French                 | Latn       | Sp, Tx     | Sp, Tx     |
| fuv      | Nigerian Fulfulde      | Latn       | Sp, Tx     | Tx         |
| gaz      | West Central Oromo     | Latn       | Sp, Tx     | Tx         |
| gle      | Irish                  | Latn       | Sp, Tx     | Tx         |
| glg      | Galician               | Latn       | Sp, Tx     | Tx         |
| guj      | Gujarati               | Gujr       | Sp, Tx     | Tx         |
| heb      | Hebrew                 | Hebr       | Sp, Tx     | Tx         |
| hin      | Hindi                  | Deva       | Sp, Tx     | Sp, Tx     |
| hrv      | Croatian               | Latn       | Sp, Tx     | Tx         |
| hun      | Hungarian              | Latn       | Sp, Tx     | Tx         |
| hye      | Armenian               | Armn       | Sp, Tx     | Tx         |
| ibo      | Igbo                   | Latn       | Sp, Tx     | Tx         |
| ind      | Indonesian             | Latn       | Sp, Tx     | Sp, Tx     |
| isl      | Icelandic              | Latn       | Sp, Tx     | Tx         |
| ita      | Italian                | Latn       | Sp, Tx     | Sp, Tx     |
| jav      | Javanese               | Latn       | Sp, Tx     | Tx         |
| jpn      | Japanese               | Jpan       | Sp, Tx     | Sp, Tx     |
| kam      | Kamba                  | Latn       | Sp         | \--        |
| kan      | Kannada                | Knda       | Sp, Tx     | Tx         |
| kat      | Georgian               | Geor       | Sp, Tx     | Tx         |
| kaz      | Kazakh                 | Cyrl       | Sp, Tx     | Tx         |
| kea      | Kabuverdianu           | Latn       | Sp         | \--        |
| khk      | Halh Mongolian         | Cyrl       | Sp, Tx     | Tx         |
| khm      | Khmer                  | Khmr       | Sp, Tx     | Tx         |
| kir      | Kyrgyz                 | Cyrl       | Sp, Tx     | Tx         |
| kor      | Korean                 | Kore       | Sp, Tx     | Sp, Tx     |
| lao      | Lao                    | Laoo       | Sp, Tx     | Tx         |
| lit      | Lithuanian             | Latn       | Sp, Tx     | Tx         |
| ltz      | Luxembourgish          | Latn       | Sp         | \--        |
| lug      | Ganda                  | Latn       | Sp, Tx     | Tx         |
| luo      | Luo                    | Latn       | Sp, Tx     | Tx         |
| lvs      | Standard Latvian       | Latn       | Sp, Tx     | Tx         |
| mai      | Maithili               | Deva       | Sp, Tx     | Tx         |
| mal      | Malayalam              | Mlym       | Sp, Tx     | Tx         |
| mar      | Marathi                | Deva       | Sp, Tx     | Tx         |
| mkd      | Macedonian             | Cyrl       | Sp, Tx     | Tx         |
| mlt      | Maltese                | Latn       | Sp, Tx     | Sp, Tx     |
| mni      | Meitei                 | Beng       | Sp, Tx     | Tx         |
| mya      | Burmese                | Mymr       | Sp, Tx     | Tx         |
| nld      | Dutch                  | Latn       | Sp, Tx     | Sp, Tx     |
| nno      | Norwegian Nynorsk      | Latn       | Sp, Tx     | Tx         |
| nob      | Norwegian Bokmål       | Latn       | Sp, Tx     | Tx         |
| npi      | Nepali                 | Deva       | Sp, Tx     | Tx         |
| nya      | Nyanja                 | Latn       | Sp, Tx     | Tx         |
| oci      | Occitan                | Latn       | Sp         | \--        |
| ory      | Odia                   | Orya       | Sp, Tx     | Tx         |
| pan      | Punjabi                | Guru       | Sp, Tx     | Tx         |
| pbt      | Southern Pashto        | Arab       | Sp, Tx     | Tx         |
| pes      | Western Persian        | Arab       | Sp, Tx     | Sp, Tx     |
| pol      | Polish                 | Latn       | Sp, Tx     | Sp, Tx     |
| por      | Portuguese             | Latn       | Sp, Tx     | Sp, Tx     |
| ron      | Romanian               | Latn       | Sp, Tx     | Sp, Tx     |
| rus      | Russian                | Cyrl       | Sp, Tx     | Sp, Tx     |
| slk      | Slovak                 | Latn       | Sp, Tx     | Sp, Tx     |
| slv      | Slovenian              | Latn       | Sp, Tx     | Tx         |
| sna      | Shona                  | Latn       | Sp, Tx     | Tx         |
| snd      | Sindhi                 | Arab       | Sp, Tx     | Tx         |
| som      | Somali                 | Latn       | Sp, Tx     | Tx         |
| spa      | Spanish                | Latn       | Sp, Tx     | Sp, Tx     |
| srp      | Serbian                | Cyrl       | Sp, Tx     | Tx         |
| swe      | Swedish                | Latn       | Sp, Tx     | Sp, Tx     |
| swh      | Swahili                | Latn       | Sp, Tx     | Sp, Tx     |
| tam      | Tamil                  | Taml       | Sp, Tx     | Tx         |
| tel      | Telugu                 | Telu       | Sp, Tx     | Sp, Tx     |
| tgk      | Tajik                  | Cyrl       | Sp, Tx     | Tx         |
| tgl      | Tagalog                | Latn       | Sp, Tx     | Sp, Tx     |
| tha      | Thai                   | Thai       | Sp, Tx     | Sp, Tx     |
| tur      | Turkish                | Latn       | Sp, Tx     | Sp, Tx     |
| ukr      | Ukrainian              | Cyrl       | Sp, Tx     | Sp, Tx     |
| urd      | Urdu                   | Arab       | Sp, Tx     | Sp, Tx     |
| uzn      | Northern Uzbek         | Latn       | Sp, Tx     | Sp, Tx     |
| vie      | Vietnamese             | Latn       | Sp, Tx     | Sp, Tx     |
| xho      | Xhosa                  | Latn       | Sp         | \--        |
| yor      | Yoruba                 | Latn       | Sp, Tx     | Tx         |
| yue      | Cantonese              | Hant       | Sp, Tx     | Tx         |
| zlm      | Colloquial Malay       | Latn       | Sp         | \--        |
| zsm      | Standard Malay         | Latn       | Tx         | Tx         |
| zul      | Zulu                   | Latn       | Sp, Tx     | Tx         |

## Containerizing Using Docker
For containerizing, download the latest version of <a href='https://www.docker.com/products/docker-desktop/'>Docker</a> and install it on your machine. <br>
Make sure Docker is running. You can check by using <code>docker --version</code>.<br>
Navigate to <code>your/project/path</code> for this project. Type <code>docker build -t SeamlessM4Tv2-API</code> in your terminal. Docker will now build the container.
