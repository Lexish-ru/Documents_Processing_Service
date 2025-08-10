from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from .models import Document

@shared_task
def send_admin_new_document_email(document_id: int):
    doc = Document.objects.select_related("owner").get(pk=document_id)
    subject = f"[Documents] Новый документ #{doc.pk}"
    body = f"Пользователь {doc.owner} загрузил документ #{doc.pk}.\nСтатус: {doc.status}"
    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [settings.ADMIN_EMAIL])

@shared_task
def send_user_document_status_email(document_id: int):
    doc = Document.objects.select_related("owner").get(pk=document_id)
    if not doc.owner.email:
        return  # нечего слать
    subject = f"[Documents] Ваш документ #{doc.pk}: {doc.status}"
    reason = f"\nПричина: {doc.comment}" if doc.comment else ""
    body = f"Статус вашего документа изменён на: {doc.status}.{reason}"
    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [doc.owner.email])
