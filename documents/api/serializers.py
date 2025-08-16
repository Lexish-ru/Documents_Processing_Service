from rest_framework import serializers
from documents.models import Document


class DocumentSerializer(serializers.ModelSerializer):
    """Сериализатор модели Document."""

    class Meta:
        model = Document
        fields = ("id", "file", "status", "uploaded_at", "reviewed_at", "comment")
        read_only_fields = ("status", "uploaded_at", "reviewed_at", "comment")

    def create(self, validated_data):
        """Создать документ от имени текущего пользователя."""
        user = self.context["request"].user
        return Document.objects.create(owner=user, **validated_data)
