from pathlib import Path

from rest_framework import serializers

from works.models import Work, WorkRequest, WorkType


class WorkShortSerializer(serializers.ModelSerializer):
    student_full_name = serializers.CharField(source='student.user', read_only=True)
    supervisor_full_name = serializers.CharField(source='supervisor.user', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    work_type_name = serializers.CharField(source='work_type.name', read_only=True)
    has_document = serializers.SerializerMethodField()

    class Meta:
        model = Work
        fields = (
            'id',
            'topic',
            'student_full_name',
            'supervisor_full_name',
            'department_name',
            'work_type_name',
            'norm_control_status',
            'has_document',
        )

    def get_has_document(self, obj):
        return bool(obj.document)


class WorkDetailSerializer(WorkShortSerializer):
    student_id = serializers.IntegerField(read_only=True)
    supervisor_id = serializers.IntegerField(read_only=True)
    department_id = serializers.IntegerField(read_only=True)
    work_type_id = serializers.IntegerField(read_only=True)
    document_original_name = serializers.CharField(read_only=True)
    download_url = serializers.SerializerMethodField()

    class Meta(WorkShortSerializer.Meta):
        fields = WorkShortSerializer.Meta.fields + (
            'student_id',
            'supervisor_id',
            'department_id',
            'work_type_id',
            'document_original_name',
            'download_url',
        )

    def get_download_url(self, obj):
        if not obj.document:
            return None

        request = self.context.get('request')
        if request is None:
            return None

        return request.build_absolute_uri(f'/works/{obj.pk}/document/')


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


class WorkTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkType
        fields = ('id', 'name')


class WorkRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkRequest
        fields = ('teacher', 'type', 'topic')


class WorkRequestSerializer(serializers.ModelSerializer):
    teacher_full_name = serializers.CharField(source='teacher.user', read_only=True)
    work_type_name = serializers.CharField(source='type.name', read_only=True)

    class Meta:
        model = WorkRequest
        fields = (
            'id',
            'teacher_id',
            'teacher_full_name',
            'type_id',
            'work_type_name',
            'topic',
            'status',
            'created_at',
        )


class WorkDocumentUploadSerializer(serializers.Serializer):
    document = serializers.FileField()

    def validate_document(self, value):
        if Path(value.name).suffix.lower() != '.docx':
            raise serializers.ValidationError('Accessable only .docx files.')
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
