from django.contrib import admin, messages
from django.utils import timezone

from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "status", "uploaded_at", "reviewed_at")
    list_filter = ("status", "uploaded_at")
    search_fields = ("id", "owner__username", "owner__email")
    actions = ("approve_documents", "reject_documents")

    @admin.action(description="Approve selected")
    def approve_documents(self, request, queryset):
        now = timezone.now()
        processed = 0
        for doc in queryset:
            if doc.status != Document.Status.APPROVED:
                doc.status = Document.Status.APPROVED
                doc.reviewed_at = now
                doc.reviewed_by = request.user
                doc.save(update_fields=["status", "reviewed_at", "reviewed_by"])
                processed += 1
        self.message_user(request, f"Approved: {processed}", level=messages.SUCCESS)

    @admin.action(description="Reject selected")
    def reject_documents(self, request, queryset):
        now = timezone.now()
        processed = 0
        for doc in queryset:
            if doc.status != Document.Status.REJECTED:
                doc.status = Document.Status.REJECTED
                doc.reviewed_at = now
                doc.reviewed_by = request.user
                doc.save(update_fields=["status", "reviewed_at", "reviewed_by"])
                processed += 1
        self.message_user(request, f"Rejected: {processed}", level=messages.WARNING)
