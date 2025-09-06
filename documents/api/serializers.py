from rest_framework import serializers
from documents.models import Document
from documents.validators import validate_uploaded_file


class DocumentSerializer(serializers.ModelSerializer):
    def validate_file(self, value):
        validate_uploaded_file(value)
        return value

    """Сериализатор модели Document."""

    class Meta:
        model = Document
        fields = ("id", "file", "status", "uploaded_at", "reviewed_at", "comment")
        read_only_fields = ("status", "uploaded_at", "reviewed_at", "comment")

    def create(self, validated_data):
        """Создать документ от имени текущего пользователя."""
        user = self.context["request"].user
        return Document.objects.create(owner=user, **validated_data)
