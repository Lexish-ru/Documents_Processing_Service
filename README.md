# Documents Processing Service

Сервис на Django + DRF для загрузки документов зарегистрированными пользователями.  
При загрузке администратор получает e‑mail. В админке администратор подтверждает или отклоняет документы; пользователю приходит e‑mail‑уведомление. Отправка писем выполняется через очередь задач Celery.

---

## Возможности

- API для загрузки документов авторизованными пользователями.
- Уведомление администратора по e‑mail при каждой новой загрузке.
- Панель администратора с быстрыми действиями:
  - Approve selected — подтвердить,
  - Reject selected — отклонить.
- Уведомление пользователя по e‑mail после подтверждения/отклонения.
- Очередь задач: Celery + Redis.
- Автогенерируемая документация API (Swagger UI).
- Контейнеризация: Docker + docker‑compose.
- Тесты (pytest) с покрытием ≥75% (фактически ~90%).
- Пример CI (GitHub Actions) с линтингом, тестами и деплоем по SSH.

---

## Технологии

- Django 5, Django REST Framework
- Celery 5, Redis
- PostgreSQL 16
- drf‑spectacular (OpenAPI/Swagger)
- gunicorn
- Nginx (внешний прокси, раздача статики/медиа)
- Docker / docker‑compose
- pytest / pytest‑django / pytest‑cov
- flake8

---

## Быстрый старт (Docker)

1) Подготовить `.env` в корне проекта (пример ниже).  
2) Запустить инфраструктуру и приложение:

```bash
docker compose up -d --build db redis web nginx
```

3) Выполнить миграции и создать суперпользователя:

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

4) Открыть:
- Swagger: `http://localhost/api/docs/`
- Схема OpenAPI: `http://localhost/api/schema/`
- Админка: `http://localhost/admin/`

---

## Переменные окружения (`.env` пример)

```dotenv
# Django
DJANGO_SECRET_KEY=dev-secret
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=*

# БД
POSTGRES_DB=app
POSTGRES_USER=app
POSTGRES_PASSWORD=app
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Очередь
REDIS_URL=redis://redis:6379/0

# Почта
DEFAULT_FROM_EMAIL=noreply@example.com
ADMIN_EMAIL=admin@example.com
```

> По умолчанию для разработки используется console email backend — письма печатаются в логах контейнера `web`. Для SMTP можно переопределить `EMAIL_BACKEND` и переменные подключения в `settings.py`.

---

## Архитектура и компоненты

```
nginx :80
  ├─ раздаёт /static и /media из общих томов
  └─ проксирует / → web:8000 (gunicorn)

web :8000
  ├─ Django + DRF (API, админка)
  ├─ Celery задачи autodiscover в проекте
  └─ collectstatic пишет в /app/static (общий том)

celery
  └─ worker для e‑mail уведомлений

redis
  └─ брокер/результаты Celery

db (postgres)
  └─ хранилище данных
```

Тома:
- `static:/app/static` и `media:/app/media` подключены к `web` и `nginx`.  
Nginx раздаёт их через:

```nginx
location /static/ { alias /app/static/; }
location /media/  { alias /app/media/;  }
```

---

## Настройка проекта

Ключевые части кода:

- **Модель** `documents.models.Document`  
  Поля: `owner`, `file`, `status` (`PENDING/APPROVED/REJECTED`), `uploaded_at`, `reviewed_at`, `reviewed_by`, `comment`.

- **API** (`documents/api/…`)  
  - `DocumentViewSet`: аутентификация обязательна; видны только собственные документы пользователя; загрузка через `multipart/form-data`.  
  - `DocumentSerializer`: на `create()` подставляет текущего пользователя как `owner`.

- **Уведомления**  
  - Сигнал `post_save` на `Document` → Celery‑задача `send_admin_new_document_email` отправляет письмо администратору о новой загрузке.
  - Экшены в админке `Approve/Reject` меняют статус, выставляют `reviewed_*` и запускают `send_user_document_status_email` пользователю.

- **Celery**  
  - `config/celery.py` настраивает приложение, читает переменные из `settings` с префиксом `CELERY_`.
  - В `settings.py`: `CELERY_BROKER_URL` и `CELERY_RESULT_BACKEND` берутся из `REDIS_URL`.

- **Swagger**  
  - `drf-spectacular` подключён, эндпоинты: `/api/schema/` и `/api/docs/`.

---

## Эндпоинты

Базовый префикс: `/api/v1/`

- `POST /documents/` — загрузка файла.  
  Тело: `multipart/form-data`, поле `file` (обязательно).  
  Ответ `201`: объект документа.

- `GET /documents/` — список собственных документов (последние сверху).

- `GET /documents/{id}/` — данные своего документа по ID.  
  Документы других пользователей недоступны.

Авторизация: Session или Basic (стандартные механизмы DRF/Django).

---

## Админка

- `http://localhost/admin/`  
- Модель `Document` с экшенами:
  - **Approve selected** — статус `APPROVED`, выставляет `reviewed_*`, отправляет письмо пользователю.
  - **Reject selected** — статус `REJECTED`, выставляет `reviewed_*`, отправляет письмо пользователю.

---

## Тесты и качество кода

Запуск тестов:

```bash
docker compose run --rm web pytest -q
```

Отчёт о покрытии выводится в консоль, порог задан в `pytest.ini` (`--cov-fail-under=75`).  
Линтинг:

```bash
docker compose run --rm web flake8
```

---

## Продакшен‑заметки

- Установить реальный SMTP‑бэкенд и закрыть `DEBUG=0`.
- Уточнить `DJANGO_ALLOWED_HOSTS` (домен/хосты).
- Для gunicorn в Dockerfile/compose используется:
  ```
  gunicorn config.wsgi:application --bind 0.0.0.0:8000
  ```
- Настроить ротацию логов и ресурсы Celery (количество воркеров).
- Подключить постоянные тома для БД, статики и медиа.

---

## Запуск без Docker (локально, опционально)

Только для разработки:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt

export DJANGO_SECRET_KEY=dev-secret
export DJANGO_DEBUG=1
export POSTGRES_DB=app
export POSTGRES_USER=app
export POSTGRES_PASSWORD=app
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export REDIS_URL=redis://localhost:6379/0
export DEFAULT_FROM_EMAIL=noreply@example.com
export ADMIN_EMAIL=admin@example.com

python manage.py migrate
python manage.py runserver
```

Celery в отдельном терминале:
```bash
celery -A config worker -l info
```

---
