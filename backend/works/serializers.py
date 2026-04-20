from pathlib import Path

from rest_framework import serializers

from works.models import Work


class WorkDocumentSerializer(serializers.ModelSerializer):
    has_document = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = Work
        fields = (
            'id',
            'topic',
            'document_original_name',
            'has_document',
            'download_url',
        )

    def get_has_document(self, obj):
        return bool(obj.document)

    def get_download_url(self, obj):
        if not obj.document:
            return None

        request = self.context.get('request')
        if request is None:
            return None

        return request.build_absolute_uri(f'/works/{obj.pk}/document/')


class WorkDocumentUploadSerializer(serializers.Serializer):
    document = serializers.FileField()

    def validate_document(self, value):
        if Path(value.name).suffix.lower() != '.docx':
            raise serializers.ValidationError('Можно загружать только файлы .docx.')
        return value

    def save(self, **kwargs):
        work = self.context['work']
        document = self.validated_data['document']

        if work.document:
            work.document.delete(save=False)

        work.document = document
        work.document_original_name = document.name
        work.save(update_fields=['document', 'document_original_name'])

        return work
