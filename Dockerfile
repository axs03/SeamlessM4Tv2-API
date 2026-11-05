FROM python:3.12-slim

# CPU build by default. For NVIDIA GPUs use docker-compose.gpu.yml, or:
#   docker build --build-arg TORCH_INDEX_URL=https://download.pytorch.org/whl/cu126 \
#                --build-arg TORCH_VERSION=2.14.1 -t seamless-api:cuda .
ARG TORCH_INDEX_URL=https://download.pytorch.org/whl/cpu
ARG TORCH_VERSION=2.15.0

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    HF_HOME=/models \
    PORT=8080

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --index-url "${TORCH_INDEX_URL}" "torch==${TORCH_VERSION}" \
    && pip install -r requirements.txt

COPY app.py audio.py config.py gunicorn.conf.py languages.py model.py ./

# Run as a non-root user. Model weights (~10 GB) are cached in /models;
# mount a volume there so they download only once.
RUN useradd --create-home --uid 1000 app \
    && mkdir -p /models && chown app:app /models
USER app
VOLUME ["/models"]

EXPOSE 8080

# The first start downloads the model, so allow a long start period.
HEALTHCHECK --interval=30s --timeout=5s --start-period=30m --retries=3 \
    CMD python -c "import os,sys,urllib.request; sys.exit(0 if urllib.request.urlopen(f'http://127.0.0.1:{os.environ[\"PORT\"]}/health', timeout=4).status == 200 else 1)"

CMD ["gunicorn", "-c", "gunicorn.conf.py", "app:create_app()"]
