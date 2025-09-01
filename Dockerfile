FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (kept minimal; extend if you add libs later)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
  && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# App
COPY . /app

# Entrypoint
COPY docker/entrypoint.sh /app/docker/entrypoint.sh
RUN chmod +x /app/docker/entrypoint.sh

EXPOSE 8000
CMD ["/app/docker/entrypoint.sh"]
