# syntax=docker/dockerfile:1

# Use Python 3.10 for wider binary compatibility (PyTorch/Detectron2/TF)
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    TF_ENABLE_ONEDNN_OPTS=0 \
    PYTHONIOENCODING=UTF-8

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    ffmpeg \
    libsm6 \
    libxext6 \
    libgl1 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for layer caching
COPY services/dl-api/requirements.txt ./

# Install Python deps
RUN python -m pip install --upgrade pip \
 && pip install -r requirements.txt \
 # Try installing detectron2 (CPU)
 && pip install --no-build-isolation "git+https://github.com/facebookresearch/detectron2.git"

# Copy application code
COPY services/dl-api/ ./

# Create furniture DB at build time (optional; ignore failures)
RUN python furniture_data/create_database.py || true

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
