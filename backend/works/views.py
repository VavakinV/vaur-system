from pathlib import Path

from django.http import FileResponse
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from works.models import Work
from works.serializers import WorkDocumentSerializer, WorkDocumentUploadSerializer


WORKS_TAG = ['Works']


def can_access_work(user, work):
    if not user.is_authenticated:
        return False

    if user.is_staff or user.is_superuser:
        return True

    student_profile = getattr(user, 'student_profile', None)
    if student_profile and work.student_id == student_profile.id:
        return True

    teacher_profile = getattr(user, 'teacher_profile', None)
    if teacher_profile and (work.supervisor_id == teacher_profile.id or teacher_profile.is_norm_controller):
        return True

    return False


class WorkDocumentView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def get_work(self, pk, user):
        try:
            work = Work.objects.select_related(
                'student__user',
                'supervisor__user',
                'department',
                'work_type',
            ).get(pk=pk)
        except Work.DoesNotExist as exc:
            raise NotFound('Работа не найдена.') from exc

        if not can_access_work(user, work):
            raise PermissionDenied('Недостаточно прав для доступа к файлу работы.')

        return work

    @extend_schema(
        tags=WORKS_TAG,
        operation_id='work_upload_document',
        request=WorkDocumentUploadSerializer,
        responses={
            200: WorkDocumentSerializer,
            403: OpenApiResponse(description='Permission denied'),
            404: OpenApiResponse(description='Work not found'),
        },
    )
    def post(self, request, pk):
        work = self.get_work(pk, request.user)
        serializer = WorkDocumentUploadSerializer(data=request.data, context={'work': work})
        serializer.is_valid(raise_exception=True)
        work = serializer.save()
        response_serializer = WorkDocumentSerializer(work, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=WORKS_TAG,
        operation_id='work_download_document',
        responses={
            200: OpenApiResponse(description='DOCX file'),
            403: OpenApiResponse(description='Permission denied'),
            404: OpenApiResponse(description='Work or file not found'),
        },
    )
    def get(self, request, pk):
        work = self.get_work(pk, request.user)
        if not work.document:
            raise NotFound('Файл работы не загружен.')

        filename = work.document_original_name or Path(work.document.name).name
        response = FileResponse(work.document.open('rb'), as_attachment=True, filename=filename)
        response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        return response
