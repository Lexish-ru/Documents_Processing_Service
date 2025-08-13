from django.core import mail
from django.urls import reverse
from documents.models import Document

def test_upload_creates_document_and_emails_admin(api_client, sample_file, settings):
    settings.ADMIN_EMAIL = "admin@example.com"
    url = reverse("document-list")
    resp = api_client.post(url, data={"file": sample_file}, format="multipart")
    assert resp.status_code == 201
    assert Document.objects.count() == 1
    # сигнал запустил Celery-задачу, письмо админу лежит в outbox
    assert len(mail.outbox) == 1
    assert "Новый документ" in mail.outbox[0].subject

def test_list_shows_only_own_documents(api_client, api_client_other, user, db, sample_file):
    # создаём по одному документу от каждого пользователя
    from django.core.files.base import ContentFile
    d1 = Document.objects.create(owner=user, file=ContentFile(b"a", name="a.txt"))
    other_doc_owner = Document.objects.create(owner=Document._meta.get_field("owner").remote_field.model.objects.get(username="other"),
                                              file=ContentFile(b"b", name="b.txt"))
    url = reverse("document-list")
    # текущий пользователь видит только свой d1
    resp = api_client.get(url)
    assert resp.status_code == 200
    ids = [item["id"] for item in resp.json()]
    assert d1.id in ids
    assert other_doc_owner.id not in ids

def test_cannot_access_foreign_document_detail(api_client, api_client_other, user, sample_file):
    from django.core.files.base import ContentFile
    doc = Document.objects.create(owner=user, file=ContentFile(b"x", name="x.txt"))
    # другой пользователь пытается посмотреть detail — получит 404 (фильтрация по owner)
    from django.urls import reverse
    url = reverse("document-detail", args=[doc.id])
    resp = api_client_other.get(url)
    assert resp.status_code == 404
