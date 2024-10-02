# python runtime
FROM --platform=linux/amd64 python:3.11-slim

# working dir for container
WORKDIR /app

COPY . /app

# dependencies
RUN apt-get update && apt-get install -y \
    libgomp1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# installing requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# exposing 8080
EXPOSE 8080

# run w/ gunicorn for prod
ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:8080", "App:app"]
