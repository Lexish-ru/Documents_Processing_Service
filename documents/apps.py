from django.apps import AppConfig


class DocumentsConfig(AppConfig):
    """Класс конфигурации приложения."""
    default_auto_field = "django.db.models.BigAutoField"
    name = "documents"

    def ready(self):
        from . import signals  # noqa: F401
