FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# системные зависимости: psycopg2 + libmagic (для python-magic) + netcat (опционально)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl libmagic1 netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# без лишних entrypoint-файлов: миграции/статик инлайном и gunicorn
CMD ["sh", "-c", "python manage.py migrate --noinput || true; python manage.py collectstatic --noinput || true; exec gunicorn config.wsgi:application --bind 0.0.0.0:8000"]
