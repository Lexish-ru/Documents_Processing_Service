from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .models import Document
from .tasks import send_admin_new_document_email, send_user_document_status_email


@receiver(pre_save, sender=Document)
def _track_old_status(sender, instance: Document, **kwargs):
    """Запоминаем старый статус, чтобы в post_save понять, менялся ли он."""
    if instance.pk:
        try:
            instance._old_status = sender.objects.only("status").get(pk=instance.pk).status
        except sender.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Document)
def _notify_on_events(sender, instance: Document, created: bool, **kwargs):
    """
    - Новая загрузка: уведомляем администратора.
    - Обновление с изменением статуса: уведомляем владельца.
    """
    if created:
        send_admin_new_document_email.delay(instance.pk)
        return

    old = getattr(instance, "_old_status", None)
    if old is not None and old != instance.status:
        send_user_document_status_email.delay(instance.pk)
