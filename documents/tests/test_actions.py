# documents/tests/test_actions.py
from django.core import mail
from django.urls import reverse
from django.core.files.base import ContentFile
from documents.models import Document


def _post_admin_action(client, action, ids):
    url = reverse("admin:documents_document_changelist")
    data = {"action": action, "_selected_action": [str(i) for i in ids]}
    return client.post(url, data, follow=True)


def test_admin_approve_sends_email_to_user(client, admin_user, user, db):
    client.force_login(admin_user)
    doc = Document.objects.create(owner=user, file=ContentFile(b"d", name="d.txt"))
    before = len(mail.outbox)  # письмо админу уже тут

    resp = _post_admin_action(client, "approve_documents", [doc.id])
    doc.refresh_from_db()
    assert resp.status_code == 200
    assert doc.status == Document.Status.APPROVED

    # Проверяем, что добавилось ровно одно новое письмо
    assert len(mail.outbox) == before + 1
    m = mail.outbox[-1]  # последнее письмо — пользователю
    assert user.email in m.to
    assert "APPROVED" in (m.subject + m.body)


def test_admin_reject_sends_email_to_user(client, admin_user, user, db):
    client.force_login(admin_user)
    doc = Document.objects.create(owner=user, file=ContentFile(b"r", name="r.txt"))
    before = len(mail.outbox)  # письмо админу уже тут

    resp = _post_admin_action(client, "reject_documents", [doc.id])
    doc.refresh_from_db()
    assert resp.status_code == 200
    assert doc.status == Document.Status.REJECTED

    # Проверяем, что добавилось ровно одно новое письмо
    assert len(mail.outbox) == before + 1
    m = mail.outbox[-1]
    assert user.email in m.to
    assert "REJECTED" in (m.subject + m.body)
