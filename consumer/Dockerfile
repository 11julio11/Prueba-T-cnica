FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY consumer/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY consumer/consumer.py .

RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

CMD ["python", "consumer.py"]
