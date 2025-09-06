import tempfile

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


@pytest.fixture(autouse=True)
def _celery_eager(settings):
    """Запуск Celery-задач в синхронном режиме (без брокера)."""
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True


@pytest.fixture(autouse=True)
def _email_locmem(settings):
    """Использование локального почтового backend (outbox)."""
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"


@pytest.fixture(autouse=True)
def _tmp_media(settings):
    """Временный MEDIA_ROOT для загрузки файлов в тестах."""
    tmpdir = tempfile.mkdtemp()
    settings.MEDIA_ROOT = tmpdir
    yield


@pytest.fixture
def user(db):
    """Тестовый пользователь."""
    User = get_user_model()
    return User.objects.create_user(
        username="user",
        email="user@example.com",
        password="pass12345",
    )


@pytest.fixture
def admin_user(db):
    """Тестовый администратор."""
    User = get_user_model()
    return User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="adminpass",
    )


@pytest.fixture
def api_client(user):
    """API-клиент, авторизованный под обычным пользователем."""
    client = APIClient()
    client.login(username="user", password="pass12345")
    return client


@pytest.fixture
def api_client_other(db):
    """API-клиент, авторизованный под другим пользователем."""
    User = get_user_model()
    User.objects.create_user("other", "other@example.com", "pass12345")
    client = APIClient()
    client.login(username="other", password="pass12345")
    return client


@pytest.fixture
def sample_file():
    """Простейший файл для загрузки в тестах."""
    return SimpleUploadedFile("test.txt", b"hello world", content_type="text/plain")
