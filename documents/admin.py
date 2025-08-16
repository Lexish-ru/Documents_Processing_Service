from django.contrib import admin, messages
from django.utils import timezone

from .models import Document
from .tasks import send_user_document_status_email


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Админ-интерфейс модели Document."""

    list_display = ("id", "owner", "status", "uploaded_at", "reviewed_at")
    list_filter = ("status", "uploaded_at")
    search_fields = ("id", "owner__username", "owner__email")
    actions = ("approve_documents", "reject_documents")

    @admin.action(description="Approve selected")
    def approve_documents(self, request, queryset):
        now = timezone.now()
        processed = 0
        for doc in queryset.select_related("owner"):
            if doc.status == Document.Status.APPROVED:
                continue
            doc.status = Document.Status.APPROVED
            doc.reviewed_at = now
            doc.reviewed_by = request.user
            doc.save(update_fields=["status", "reviewed_at", "reviewed_by"])
            # письмо пользователю — только если есть адрес
            if getattr(doc.owner, "email", None):
                send_user_document_status_email.delay(doc.pk)
            processed += 1
        self.message_user(request, f"Approved: {processed}", level=messages.SUCCESS)

    @admin.action(description="Reject selected")
    def reject_documents(self, request, queryset):
        now = timezone.now()
        processed = 0
        for doc in queryset.select_related("owner"):
            if doc.status == Document.Status.REJECTED:
                continue
            doc.status = Document.Status.REJECTED
            doc.reviewed_at = now
            doc.reviewed_by = request.user
            doc.save(update_fields=["status", "reviewed_at", "reviewed_by"])
            if getattr(doc.owner, "email", None):
                send_user_document_status_email.delay(doc.pk)
            processed += 1
        self.message_user(request, f"Rejected: {processed}", level=messages.WARNING)
