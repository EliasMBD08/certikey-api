FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/prod.in

COPY certikey/ certikey/
COPY entrypoint.sh entrypoint.sh
RUN chmod +x entrypoint.sh

WORKDIR /app/certikey

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "certikey.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "2"]
