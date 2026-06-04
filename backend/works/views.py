from pathlib import Path

from django.http import FileResponse
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User
from works.models import Work
from works.serializers import (
    WorkDetailSerializer,
    WorkDocumentSerializer,
    WorkDocumentUploadSerializer,
    WorkShortSerializer,
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


class UserWorksView(APIView):
    @extend_schema(
        tags=WORKS_TAG,
        operation_id='user_works_list',
        description='Return all works associated with a user by their user id.',
        responses={
            200: WorkShortSerializer(many=True),
            401: OpenApiResponse(description='Authentication required'),
            404: OpenApiResponse(description='User not found'),
        },
    )
    def get(self, request, user_pk):
        user = get_object_or_404(User, pk=user_pk)

        if user.role == User.Role.STUDENT:
            works = Work.objects.filter(student__user_id=user_pk)
        else:
            works = Work.objects.filter(supervisor__user_id=user_pk)

        works = works.select_related('student__user', 'supervisor__user', 'department', 'work_type')
        serializer = WorkShortSerializer(works, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
