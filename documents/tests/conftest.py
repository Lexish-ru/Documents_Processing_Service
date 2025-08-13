import io
import os
import tempfile
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

@pytest.fixture(autouse=True)
def _celery_eager(settings):
    # чтобы Celery- задачи выполнялись синхронно, без Redis
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True

@pytest.fixture(autouse=True)
def _email_locmem(settings):
    # письма складываются в django.core.mail.outbox
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

@pytest.fixture(autouse=True)
def _tmp_media(settings):
    tmpdir = tempfile.mkdtemp()
    settings.MEDIA_ROOT = tmpdir
    yield
    # не удаляем — pytest сам приберёт tmp по окончании раннера

@pytest.fixture
def user(db):
    User = get_user_model()
    return User.objects.create_user(
        username="user",
        email="user@example.com",
        password="pass12345"
    )

@pytest.fixture
def admin_user(db):
    User = get_user_model()
    return User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="adminpass"
    )

@pytest.fixture
def api_client(user):
    client = APIClient()
    client.login(username="user", password="pass12345")
    return client

@pytest.fixture
def api_client_other(db):
    User = get_user_model()
    other = User.objects.create_user("other", "other@example.com", "pass12345")
    client = APIClient()
    client.login(username="other", password="pass12345")
    return client

@pytest.fixture
def sample_file():
    return SimpleUploadedFile("test.txt", b"hello world", content_type="text/plain")
