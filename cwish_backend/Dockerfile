FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_NO_CACHE_DIR=on

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
  && rm -rf /var/lib/apt/lists/*

COPY cwish_backend/requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY cwish_backend /app

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


