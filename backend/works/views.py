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
from works.models import Work, WorkRequest, WorkType
from works.serializers import (
    WorkDetailSerializer,
    WorkDocumentSerializer,
    WorkDocumentUploadSerializer,
    WorkRequestCreateSerializer,
    WorkRequestSerializer,
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
    @extend_schema(
        tags=WORKS_TAG,
        operation_id='work_type_list',
        description='Return a list of all work types.',
        responses={200: WorkTypeSerializer(many=True)},
    )
    def get(self, request):
        work_types = WorkType.objects.all()
        return Response(WorkTypeSerializer(work_types, many=True).data)


class WorkRequestCreateView(APIView):
    @extend_schema(
        tags=WORKS_TAG,
        operation_id='work_request_create',
        description='Create a work request. Only students can create requests.',
        request=WorkRequestCreateSerializer,
        responses={
            201: WorkRequestSerializer,
            403: OpenApiResponse(description='Only students can create work requests'),
        },
    )
    def post(self, request):
        if not request.user.is_student:
            raise PermissionDenied('Only students can create work requests.')

        serializer = WorkRequestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        work_request = serializer.save(student=request.user.student_profile)
        return Response(WorkRequestSerializer(work_request).data, status=status.HTTP_201_CREATED)


class WorkRequestRespondBaseView(APIView):
    respond_status = None

    def post(self, request, pk):
        if not request.user.is_teacher:
            raise PermissionDenied('Only teachers can respond to work requests.')

        work_request = get_object_or_404(
            WorkRequest.objects.select_related('teacher__user', 'type'),
            pk=pk,
            teacher__user=request.user,
        )

        if work_request.status != WorkRequest.Status.PENDING:
            return Response(
                {'detail': 'Only pending requests can be accepted or rejected.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        work_request.status = self.respond_status
        work_request.save(update_fields=['status'])
        return Response(WorkRequestSerializer(work_request).data)


class WorkRequestAcceptView(WorkRequestRespondBaseView):
    respond_status = WorkRequest.Status.ACCEPTED

    @extend_schema(
        tags=WORKS_TAG,
        operation_id='work_request_accept',
        description='Accept a work request. Only the teacher the request is addressed to can accept it.',
        request=None,
        responses={
            200: WorkRequestSerializer,
            400: OpenApiResponse(description='Request is not pending'),
            403: OpenApiResponse(description='Permission denied'),
            404: OpenApiResponse(description='Work request not found'),
        },
    )
    def post(self, request, pk):
        return super().post(request, pk)


class WorkRequestRejectView(WorkRequestRespondBaseView):
    respond_status = WorkRequest.Status.REJECTED

    @extend_schema(
        tags=WORKS_TAG,
        operation_id='work_request_reject',
        description='Reject a work request. Only the teacher the request is addressed to can reject it.',
        request=None,
        responses={
            200: WorkRequestSerializer,
            400: OpenApiResponse(description='Request is not pending'),
            403: OpenApiResponse(description='Permission denied'),
            404: OpenApiResponse(description='Work request not found'),
        },
    )
    def post(self, request, pk):
        return super().post(request, pk)


class MyWorkRequestsView(APIView):
    @extend_schema(
        tags=WORKS_TAG,
        operation_id='my_work_requests_list',
        description='Return all work requests of the current user.',
        responses={200: WorkRequestSerializer(many=True)},
    )
    def get(self, request):
        if request.user.is_student:
            requests_qs = WorkRequest.objects.filter(student__user=request.user)
        else:
            requests_qs = WorkRequest.objects.filter(teacher__user=request.user)

        requests_qs = requests_qs.select_related('teacher__user', 'type')
        return Response(WorkRequestSerializer(requests_qs, many=True).data)


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
