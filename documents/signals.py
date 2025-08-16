from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Document
from .tasks import send_admin_new_document_email, send_user_document_status_email


@receiver(pre_save, sender=Document)
def _track_old_status(sender, instance: Document, **kwargs):
    """
    Перед сохранением подтягиваем прошлый статус из БД,
    чтобы потом в post_save понять — изменился ли он.
    """
    if instance.pk:
        try:
            old = sender.objects.only("status").get(pk=instance.pk).status
        except sender.DoesNotExist:
            old = None
        instance._old_status = old  # временный атрибут в памяти


@receiver(post_save, sender=Document)
def _notify_on_events(sender, instance: Document, created: bool, **kwargs):
    """
    - При создании документа уведомляем администратора.
    - При изменении статуса уведомляем владельца.
    """
    if created:
        # Новая загрузка → письмо админу
        send_admin_new_document_email.delay(instance.pk)
        return

    old = getattr(instance, "_old_status", None)
    if old is not None and old != instance.status:
        # Есть e-mail владельца? — отправляем
        if getattr(instance.owner, "email", None):
            send_user_document_status_email.delay(instance.pk)
