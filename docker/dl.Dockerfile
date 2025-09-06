FROM nvidia/cuda:12.4.1-runtime-ubuntu22.04
RUN apt-get update && apt-get install -y python3-pip && rm -rf /var/lib/apt/lists/*
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8000 NVIDIA_VISIBLE_DEVICES=all
COPY services/dl-api/requirements.txt /app/requirements.txt
RUN pip install -U pip && pip install -r requirements.txt
# If using PyTorch GPU, uncomment and pick proper CUDA wheels:
# RUN pip install torch --index-url https://download.pytorch.org/whl/cu121
COPY services/dl-api /app
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=8000"]
