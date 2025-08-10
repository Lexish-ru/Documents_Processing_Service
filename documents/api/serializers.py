from rest_framework import serializers
from documents.models import Document

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ("id", "file", "status", "uploaded_at", "reviewed_at", "comment")
        read_only_fields = ("status", "uploaded_at", "reviewed_at", "comment")

    def create(self, validated_data):
        user = self.context["request"].user
        return Document.objects.create(owner=user, **validated_data)
