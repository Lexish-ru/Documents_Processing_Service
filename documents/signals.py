from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Document
from .tasks import send_admin_new_document_email


@receiver(post_save, sender=Document)
def notify_admin_on_create(sender, instance: Document, created, **kwargs):
    if created:
        send_admin_new_document_email.delay(instance.pk)
