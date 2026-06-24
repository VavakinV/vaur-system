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
from works.models import Work, WorkCorrection, WorkRequest, WorkType
from works.serializers import (
    WorkCorrectionSerializer,
    WorkCorrectionWriteSerializer,
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
            'student__group_number',
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


class WorkListView(APIView):
    def get(self, request):
        user = request.user
        qs = Work.objects.select_related(
            'student__user', 'student__group_number',
            'supervisor__user', 'department', 'work_type',
        )
        if user.role == 'student':
            works = qs.filter(student=user.student_profile)
        elif user.role == 'teacher':
            works = qs.filter(supervisor=user.teacher_profile)
        else:
            return Response({'detail': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)
        return Response(WorkShortSerializer(works, many=True).data)


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


class WorkRequestMyView(APIView):
    def get(self, request):
        user = request.user
        if user.role == 'student':
            requests = WorkRequest.objects.filter(student=user.student_profile).select_related(
                'type', 'teacher__user',
            )
            return Response(WorkRequestStudentSerializer(requests, many=True).data)
        if user.role == 'teacher':
            requests = WorkRequest.objects.filter(teacher=user.teacher_profile).select_related(
                'type', 'student__user', 'student__group_number',
            )
            return Response(WorkRequestTeacherSerializer(requests, many=True).data)
        return Response({'detail': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)


class WorkRequestAcceptView(APIView):
    def post(self, request, pk):
        user = request.user
        if user.role != 'teacher':
            return Response({'detail': 'Только преподаватели могут подтверждать заявки.'}, status=status.HTTP_403_FORBIDDEN)
        work_request = get_object_or_404(
            WorkRequest.objects.select_related('teacher__department', 'student', 'type'),
            pk=pk, teacher=user.teacher_profile,
        )
        if work_request.status != WorkRequest.Status.PENDING:
            return Response({'detail': 'Можно подтверждать только заявки со статусом "В ожидании".'}, status=status.HTTP_400_BAD_REQUEST)
        work_request.status = WorkRequest.Status.ACCEPTED
        work_request.save(update_fields=['status'])
        created_work = Work.objects.create(
            student=work_request.student,
            supervisor=work_request.teacher,
            department=work_request.teacher.department,
            work_type=work_request.type,
            topic=work_request.topic,
        )
        work_request = WorkRequest.objects.select_related(
            'type', 'student__user', 'student__group_number',
        ).get(pk=pk)
        data = WorkRequestTeacherSerializer(work_request).data
        data['created_work_id'] = created_work.id
        return Response(data)


class WorkRequestRejectView(APIView):
    def post(self, request, pk):
        user = request.user
        if user.role != 'teacher':
            return Response({'detail': 'Только преподаватели могут отклонять заявки.'}, status=status.HTTP_403_FORBIDDEN)
        work_request = get_object_or_404(WorkRequest, pk=pk, teacher=user.teacher_profile)
        if work_request.status != WorkRequest.Status.PENDING:
            return Response({'detail': 'Можно отклонять только заявки со статусом "В ожидании".'}, status=status.HTTP_400_BAD_REQUEST)
        work_request.status = WorkRequest.Status.REJECTED
        work_request.save(update_fields=['status'])
        work_request = WorkRequest.objects.select_related(
            'type', 'student__user', 'student__group_number',
        ).get(pk=pk)
        return Response(WorkRequestTeacherSerializer(work_request).data)


class WorkUserView(APIView):
    def get(self, request, user_id):
        target_user = get_object_or_404(User, pk=user_id)
        qs = Work.objects.select_related(
            'student__user', 'student__group_number',
            'supervisor__user', 'department', 'work_type',
        )
        student_profile = getattr(target_user, 'student_profile', None)
        if student_profile:
            works = qs.filter(student=student_profile)
        else:
            teacher_profile = getattr(target_user, 'teacher_profile', None)
            works = qs.filter(supervisor=teacher_profile) if teacher_profile else qs.none()
        return Response(WorkShortSerializer(works, many=True).data)


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


class WorkCorrectionListCreateView(APIView):
    def get(self, request, pk):
        work = get_accessible_work(pk, request.user, 'Access denied.')
        corrections = (
            WorkCorrection.objects
            .filter(work=work)
            .select_related('author__user')
            .order_by('created_at')
        )
        return Response(WorkCorrectionSerializer(corrections, many=True).data)

    def post(self, request, pk):
        work = get_accessible_work(pk, request.user, 'Access denied.')
        teacher = getattr(request.user, 'teacher_profile', None)
        if not teacher:
            return Response(
                {'detail': 'Только преподаватели могут добавлять правки.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        if work.supervisor_id == teacher.id:
            author_role = WorkCorrection.AuthorRole.SUPERVISOR
        elif teacher.is_norm_controller:
            author_role = WorkCorrection.AuthorRole.NORM_CONTROLLER
        else:
            return Response(
                {'detail': 'Вы не являетесь руководителем данной работы.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = WorkCorrectionWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        correction = WorkCorrection(
            work=work,
            author=teacher,
            author_role=author_role,
            items=serializer.validated_data['items'],
        )
        correction.save()
        correction = WorkCorrection.objects.select_related('author__user').get(pk=correction.pk)
        return Response(WorkCorrectionSerializer(correction).data, status=status.HTTP_201_CREATED)


class WorkCorrectionUpdateView(APIView):
    def patch(self, request, correction_id):
        teacher = getattr(request.user, 'teacher_profile', None)
        if not teacher:
            return Response({'detail': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)
        correction = get_object_or_404(
            WorkCorrection.objects.select_related('author__user', 'work'),
            pk=correction_id,
            author=teacher,
        )
        serializer = WorkCorrectionWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        correction.items = serializer.validated_data['items']
        correction.save()
        return Response(WorkCorrectionSerializer(correction).data)
