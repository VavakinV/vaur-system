from pathlib import Path

from django.http import FileResponse
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from works.models import Work, WorkRequest, WorkType
from works.serializers import (
    WorkDetailSerializer,
    WorkDocumentSerializer,
    WorkDocumentUploadSerializer,
    WorkRequestCreateSerializer,
    WorkRequestDetailSerializer,
    WorkRequestStudentSerializer,
    WorkRequestStudentUpdateSerializer,
    WorkRequestTeacherSerializer,
    WorkRequestUpdateSerializer,
    WorkShortSerializer,
    WorkTypeSerializer,
)


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


def get_accessible_work(pk, user, denied_message):
    try:
        work = Work.objects.select_related(
            'student__user',
            'supervisor__user',
            'department',
            'work_type',
        ).get(pk=pk)
    except Work.DoesNotExist as exc:
        raise NotFound('Work not found.') from exc

    if not can_access_work(user, work):
        raise PermissionDenied(denied_message)

    return work


class WorkBaseView(APIView):
    access_denied_message = 'You have no access to this file.'

    def get_work(self, pk, user):
        return get_accessible_work(pk, user, self.access_denied_message)


class WorkShortView(WorkBaseView):
    @extend_schema(
        tags=WORKS_TAG,
        operation_id='work_short_get',
        description='Return short information about a work by id.',
        responses={
            200: WorkShortSerializer,
            403: OpenApiResponse(description='Permission denied'),
            404: OpenApiResponse(description='Work not found'),
        },
    )
    def get(self, request, pk):
        work = self.get_work(pk, request.user)
        serializer = WorkShortSerializer(work)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WorkDetailView(WorkBaseView):
    @extend_schema(
        tags=WORKS_TAG,
        operation_id='work_detail_get',
        description='Return detailed information about a work by id.',
        responses={
            200: WorkDetailSerializer,
            403: OpenApiResponse(description='Permission denied'),
            404: OpenApiResponse(description='Work not found'),
        },
    )
    def get(self, request, pk):
        work = self.get_work(pk, request.user)
        serializer = WorkDetailSerializer(work, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class WorkDocumentView(WorkBaseView):
    parser_classes = (MultiPartParser, FormParser)
    access_denied_message = 'You have no access to this work.'

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
            raise NotFound('Work not found.')

        filename = work.document_original_name or Path(work.document.name).name
        response = FileResponse(work.document.open('rb'), as_attachment=True, filename=filename)
        response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        return response


class WorkTypeListView(APIView):
    def get(self, request):
        types = WorkType.objects.all()
        return Response(WorkTypeSerializer(types, many=True).data)


class WorkRequestListCreateView(APIView):
    def get(self, request):
        user = request.user
        if user.role == 'student':
            student = user.student_profile
            requests = WorkRequest.objects.filter(student=student).select_related(
                'type', 'teacher__user',
            )
            return Response(WorkRequestStudentSerializer(requests, many=True).data)
        if user.role == 'teacher':
            teacher = user.teacher_profile
            requests = WorkRequest.objects.filter(teacher=teacher).select_related(
                'type', 'student__user', 'student__group_number',
            )
            return Response(WorkRequestTeacherSerializer(requests, many=True).data)
        return Response({'detail': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)

    def post(self, request):
        user = request.user
        if user.role != 'student':
            return Response({'detail': 'Только студенты могут подавать заявки.'}, status=status.HTTP_403_FORBIDDEN)
        student = user.student_profile
        serializer = WorkRequestCreateSerializer(data=request.data, context={'student': student})
        serializer.is_valid(raise_exception=True)
        work_request = serializer.save()
        return Response(
            WorkRequestStudentSerializer(work_request).data,
            status=status.HTTP_201_CREATED,
        )


_REQUEST_DETAIL_SELECT = (
    'type', 'teacher__user', 'teacher__department',
    'student__user', 'student__group_number',
)


class WorkRequestUpdateView(APIView):
    def get(self, request, pk):
        user = request.user
        student = getattr(user, 'student_profile', None)
        teacher = getattr(user, 'teacher_profile', None)
        try:
            if student:
                work_request = WorkRequest.objects.select_related(
                    *_REQUEST_DETAIL_SELECT
                ).get(pk=pk, student=student)
            elif teacher:
                work_request = WorkRequest.objects.select_related(
                    *_REQUEST_DETAIL_SELECT
                ).get(pk=pk, teacher=teacher)
            else:
                return Response({'detail': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)
        except WorkRequest.DoesNotExist:
            return Response({'detail': 'Заявка не найдена.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(WorkRequestDetailSerializer(work_request).data)

    def patch(self, request, pk):
        user = request.user

        if user.role == 'teacher':
            teacher = user.teacher_profile
            try:
                work_request = WorkRequest.objects.select_related(
                    'type', 'student__user', 'student__group_number',
                ).get(pk=pk, teacher=teacher)
            except WorkRequest.DoesNotExist:
                return Response({'detail': 'Заявка не найдена.'}, status=status.HTTP_404_NOT_FOUND)
            serializer = WorkRequestUpdateSerializer(work_request, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            return Response(WorkRequestTeacherSerializer(serializer.save()).data)

        if user.role == 'student':
            student = user.student_profile
            try:
                work_request = WorkRequest.objects.select_related(
                    'type', 'teacher__user',
                ).get(pk=pk, student=student)
            except WorkRequest.DoesNotExist:
                return Response({'detail': 'Заявка не найдена.'}, status=status.HTTP_404_NOT_FOUND)
            serializer = WorkRequestStudentUpdateSerializer(work_request, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            return Response(WorkRequestStudentSerializer(serializer.save()).data)

        return Response({'detail': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)
