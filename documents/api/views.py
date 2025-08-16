from rest_framework import viewsets, permissions, parsers

from documents.models import Document
from .serializers import DocumentSerializer


class IsOwnerOnly(permissions.BasePermission):
    """Разрешение: доступ только владельцу объекта."""

    def has_object_permission(self, request, view, obj):
        return obj.owner_id == request.user.id


class DocumentViewSet(viewsets.ModelViewSet):
    """ViewSet для документов текущего пользователя."""

    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOnly]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def get_queryset(self):
        """Вернуть документы текущего пользователя."""
        return (
            Document.objects.filter(owner=self.request.user)
            .order_by("-uploaded_at")
        )
