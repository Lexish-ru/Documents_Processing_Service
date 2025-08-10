from django.contrib import admin
from django.utils import timezone
from .models import Document
from .tasks import send_user_document_status_email

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "status", "uploaded_at", "reviewed_at")
    list_filter = ("status", "uploaded_at")
    search_fields = ("id", "owner__username", "owner__email")
    actions = ("approve_documents", "reject_documents")

    def approve_documents(self, request, queryset):
        count = 0
        now = timezone.now()
        for doc in queryset:
            if doc.status != Document.Status.APPROVED:
                doc.status = Document.Status.APPROVED
                doc.reviewed_at = now
                doc.reviewed_by = request.user
                doc.save(update_fields=["status", "reviewed_at", "reviewed_by"])
                send_user_document_status_email.delay(doc.pk)
                count += 1
        self.message_user(request, f"Approved: {count}")
    approve_documents.short_description = "Approve selected"

    def reject_documents(self, request, queryset):
        count = 0
        now = timezone.now()
        for doc in queryset:
            if doc.status != Document.Status.REJECTED:
                doc.status = Document.Status.REJECTED
                doc.reviewed_at = now
                doc.reviewed_by = request.user
                doc.save(update_fields=["status", "reviewed_at", "reviewed_by"])
                send_user_document_status_email.delay(doc.pk)
                count += 1
        self.message_user(request, f"Rejected: {count}")
    reject_documents.short_description = "Reject selected"
