# SeamlessM4Tv2-API

A small HTTP API and Docker image for Meta's
[SeamlessM4T v2](https://huggingface.co/facebook/seamless-m4t-v2-large), one model that
translates speech and text across about 100 languages. All five tasks of the model are exposed:

| Endpoint | Task | Input | Output |
| -------- | ---- | ----- | ------ |
| `POST /t2tt` | Text to text translation | JSON | JSON text |
| `POST /t2st` | Text to speech translation | JSON | WAV (or JSON with text + audio) |
| `POST /s2tt` | Speech to text translation | audio upload | JSON text |
| `POST /s2st` | Speech to speech translation | audio upload | WAV (or JSON with text + audio) |
| `POST /asr` | Speech recognition (same language) | audio upload | JSON text |
| `GET /languages` | Supported languages and what each can do | | JSON |
| `GET /health` | `200 ok`, `503 loading`, or `500 error` | | JSON |

`/t2s` and `/s2s` from earlier versions still work (they are `/t2st` and `/s2st`).

Audio uploads can be any format ffmpeg reads (wav, mp3, m4a, ogg, flac, webm, even video files).
Stereo is mixed to mono and everything is resampled to 16 kHz. Output audio is 16 kHz mono 16-bit WAV.

## Requirements

- Docker (or Python 3.11+ with ffmpeg for running without Docker).
- **Memory:** the large model is 2.3B parameters. On CPU (float32) plan for about 12 GB of free RAM.
  On an NVIDIA GPU (float16) about 6 GB of VRAM.
- **Disk:** about 10 GB for the model weights, downloaded on first start.
- CPU works but is slow; a GPU is strongly recommended for speech output.

## Run with Docker Compose (recommended)

```bash
git clone https://github.com/axs03/SeamlessM4Tv2-API.git
cd SeamlessM4Tv2-API

# CPU
docker compose up -d --build

# NVIDIA GPU (needs the NVIDIA Container Toolkit)
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d --build
```

The first start downloads the model into the `models` volume, so it only happens once.
Watch progress with `docker compose logs -f` and wait until `/health` says `ok`:

```bash
curl http://localhost:8080/health
# {"status":"loading"}  -> still downloading or loading
# {"device":"cpu","model":"facebook/seamless-m4t-v2-large","status":"ok"}
```

## Run with plain Docker

```bash
docker build -t seamless-api .
docker run -d --name seamless-api -p 8080:8080 -v seamless-models:/models seamless-api

# GPU build and run
docker build -t seamless-api:cuda \
  --build-arg TORCH_INDEX_URL=https://download.pytorch.org/whl/cu126 \
  --build-arg TORCH_VERSION=2.14.1 .
docker run -d --gpus all --name seamless-api -p 8080:8080 -v seamless-models:/models seamless-api:cuda
```

Image names must be lowercase. `--privileged` is not needed.

## Run without Docker

```bash
python -m venv .venv && source .venv/bin/activate
pip install --index-url https://download.pytorch.org/whl/cpu torch==2.15.0   # or a CUDA build
pip install -r requirements.txt
gunicorn -c gunicorn.conf.py "app:create_app()"      # serves on http://localhost:8080
```

ffmpeg must be on your `PATH`.

## Usage

Language codes are the model's 3-letter codes (`eng`, `fra`, `hin`, `cmn`, ...). Not every
language works for every task: speech output covers 36 languages, text output 98. See
[Supported_Langs.md](Supported_Langs.md) or `GET /languages`. Unsupported combinations return
a `400` with a clear message.

### Text to text

```bash
curl -X POST http://localhost:8080/t2tt \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, how are you?", "src_lang": "eng", "tgt_lang": "fra"}'
# {"text": "<translated text>"}
```

### Text to speech

```bash
curl -X POST http://localhost:8080/t2st \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, how are you?", "src_lang": "eng", "tgt_lang": "spa"}' \
  --output output.wav
```

The translated text is also sent in the `X-Translated-Text` response header (percent-encoded
UTF-8). Add `"response_format": "json"` to get `{"text", "sample_rate", "audio_base64"}` instead.

### Speech to text

```bash
curl -X POST http://localhost:8080/s2tt -F "file=@speech.mp3" -F "tgt_lang=eng"
```

### Speech to speech

```bash
curl -X POST http://localhost:8080/s2st -F "file=@speech.wav" -F "tgt_lang=fra" --output output.wav
```

Add `-F "response_format=json"` for text + base64 audio.

### Speech recognition

```bash
curl -X POST http://localhost:8080/asr -F "file=@speech.wav" -F "lang=eng"
```

### Windows (PowerShell 7+)

```powershell
Invoke-RestMethod -Uri "http://localhost:8080/t2tt" -Method Post -ContentType "application/json" `
  -Body '{"text": "Hello", "src_lang": "eng", "tgt_lang": "fra"}'

Invoke-WebRequest -Uri "http://localhost:8080/s2st" -Method Post `
  -Form @{ file = Get-Item 'C:\path\to\speech.wav'; tgt_lang = 'fra' } `
  -OutFile "C:\path\to\output.wav"
```

### Parameters

| Name | Used by | Required | Notes |
| ---- | ------- | -------- | ----- |
| `text` | `/t2tt`, `/t2st` | yes | Up to `MAX_TEXT_CHARS` characters |
| `src_lang` | `/t2tt`, `/t2st` | yes | Language of `text` |
| `tgt_lang` | `/t2tt`, `/t2st`, `/s2tt`, `/s2st` | yes | Output language |
| `lang` | `/asr` | yes | Spoken language |
| `file` | `/s2tt`, `/s2st`, `/asr` | yes | Multipart upload, any ffmpeg-readable format |
| `response_format` | `/t2st`, `/s2st` | no | `wav` (default) or `json` |

Errors are JSON: `{"error": "..."}` with status `400` (bad input), `401` (API key),
`413` (too large or too long), `503` (model still loading) or `500`.

## Configuration

Set as environment variables (for example in `docker-compose.yml`):

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `MODEL_ID` | `facebook/seamless-m4t-v2-large` | Hugging Face model id or local path |
| `DEVICE` | `auto` | `auto` (CUDA, then Apple MPS, then CPU), `cpu`, `cuda`, `mps` |
| `DTYPE` | `auto` | `auto` (float16 on CUDA, else float32), `float32`, `float16`, `bfloat16` |
| `API_KEY` | empty | If set, requests need `Authorization: Bearer <key>` (`/ping` and `/health` stay open) |
| `MAX_UPLOAD_MB` | `25` | Upload size limit |
| `MAX_AUDIO_SECONDS` | `120` | Audio length limit, `0` disables. Quality drops on long clips; split long audio |
| `MAX_TEXT_CHARS` | `2000` | Text length limit, `0` disables |
| `PORT` | `8080` | Listen port |
| `REQUEST_TIMEOUT` | `600` | gunicorn worker timeout in seconds |
| `THREADS` | `4` | Request threads. Generation runs one request at a time; the rest wait |
| `LOG_LEVEL` | `INFO` | Log level |
| `HF_HOME` | `/models` (Docker) | Model cache location |

One container holds one copy of the model, and requests are processed one at a time.
To serve more traffic, run more containers behind a load balancer.

## Development

```bash
pip install --index-url https://download.pytorch.org/whl/cpu torch==2.15.0
pip install -r requirements-dev.txt
ruff check .
pytest                   # API tests with a fake model, no download
pytest -m integration    # real transformers code path with a tiny random model (~5 MB download)
```

## License

The code in this repository is MIT licensed (see [LICENSE](LICENSE)).
The model weights are Meta's and licensed under
[CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/): **non-commercial use only**.
