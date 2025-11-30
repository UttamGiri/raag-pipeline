FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY src/ /app/src/

RUN useradd -m appuser
USER appuser

CMD ["python", "-m", "src.pipelines.ingestion_pipeline"]

