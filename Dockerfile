FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/app/.cache/huggingface

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir \
        torch==2.15.0 torchvision==0.29.2 \
        --index-url https://download.pytorch.org/whl/cpu \
    && python -m pip install --no-cache-dir -r requirements.txt

COPY config.py .
COPY app.py .
COPY PRODUCT.md .
COPY src ./src
COPY scripts ./scripts
COPY docs ./docs

RUN mkdir -p /app/data/raw /app/data/processed /app/storage/faiss /app/.cache/huggingface

EXPOSE 8501

ENTRYPOINT ["python", "scripts/docker_entrypoint.py"]
