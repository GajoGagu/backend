FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8000

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY services/crud-api/requirements.txt /app/requirements.txt
RUN pip install -U pip && pip install -r requirements.txt

# Copy application code
COPY services/crud-api /app

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "main:app", "--host=0.0.0.0", "--port=8000"]
