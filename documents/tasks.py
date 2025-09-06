# documents/tasks.py
from __future__ import annotations

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from .models import Document


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_jitter=True, max_retries=3)
def send_admin_new_document_email(self, document_id: int) -> None:
    """
    Уведомляет администратора о новом документе.

    1) Берёт документ по ID.
    2) Рендерит txt и HTML шаблоны.
    3) Отправляет письмо на settings.ADMIN_EMAIL.
    """
    admin_email = getattr(settings, "ADMIN_EMAIL", "") or ""
    if not admin_email:
        return  # Адрес не задан — тихо выходим

    doc = Document.objects.select_related("owner").get(pk=document_id)
    context = {
        "id": doc.pk,
        "owner": str(doc.owner),
        "status": doc.status,
        "uploaded_at": doc.uploaded_at,
    }

    subject = f"[Documents] Новый документ #{doc.pk}"
    text_body = render_to_string("emails/admin_new_document.txt", context)
    html_body = render_to_string("emails/admin_new_document.html", context)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@localhost"),
        to=[admin_email],
    )
    msg.attach_alternative(html_body, "text/html")
    msg.send()


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_jitter=True, max_retries=3)
def send_user_document_status_email(self, document_id: int) -> None:
    """
    Уведомляет владельца документа об изменении статуса.

    1) Берёт документ по ID.
    2) Если у владельца нет email — выходим.
    3) Рендерит txt и HTML шаблоны и отправляет письмо.
    """
    doc = Document.objects.select_related("owner").get(pk=document_id)
    to_email = (doc.owner.email or "").strip()
    if not to_email:
        return

    context = {
        "id": doc.pk,
        "status": doc.status,
        "comment": doc.comment,
        "reviewed_at": doc.reviewed_at,
    }

    subject = f"[Documents] Ваш документ #{doc.pk}: {doc.status}"
    text_body = render_to_string("emails/user_status_update.txt", context)
    html_body = render_to_string("emails/user_status_update.html", context)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@localhost"),
        to=[to_email],
    )
    msg.attach_alternative(html_body, "text/html")
    msg.send()
