from drf_spectacular.utils import OpenApiResponse, PolymorphicProxySerializer, extend_schema
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.serializers import (
    AccessTokenSerializer,
    AuthTokensSerializer,
    BaseMeSerializer,
    EmailOrUsernameTokenObtainPairSerializer,
    LoginSerializer,
    LogoutSerializer,
    MessageSerializer,
    RefreshTokenSerializer,
    RegisterResponseSerializer,
    RegisterSerializer,
    GroupSerializer,
    StudentMePatchSerializer,
    StudentMeSerializer,
    TeacherDetailSerializer,
    TeacherMePatchSerializer,
    TeacherMeSerializer,
    StudentDetailSerializer,
    TeacherSerializer,
    StudentSerializer,
)

from django.shortcuts import get_object_or_404

from users.models import User, Group


AUTH_TAG = ['Auth']
USERS_TAG = ['Users']
GROUPS_TAG = ['Groups']

ME_READ_SERIALIZERS = {
    User.Role.STUDENT: StudentMeSerializer,
    User.Role.TEACHER: TeacherMeSerializer,
}

ME_WRITE_SERIALIZERS = {
    User.Role.STUDENT: StudentMePatchSerializer,
    User.Role.TEACHER: TeacherMePatchSerializer,
}

USER_DETAIL_SERIALIZERS = {
    User.Role.STUDENT: StudentDetailSerializer,
    User.Role.TEACHER: TeacherDetailSerializer,
}

USER_SERIALIZERS = {
    User.Role.STUDENT: StudentSerializer,
    User.Role.TEACHER: TeacherSerializer,
}


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=AUTH_TAG,
        operation_id='auth_register',
        description='Register a new student account and return JWT tokens.',
        request=RegisterSerializer,
        responses={201: RegisterResponseSerializer},
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        response_data = RegisterResponseSerializer.from_user(user)
        return Response(response_data, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = EmailOrUsernameTokenObtainPairSerializer

    @extend_schema(
        tags=AUTH_TAG,
        operation_id='auth_login',
        description='Authenticate by username or email and return a JWT access/refresh token pair.',
        request=LoginSerializer,
        responses={
            200: AuthTokensSerializer,
            401: OpenApiResponse(description='Invalid credentials'),
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class RefreshView(TokenRefreshView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=AUTH_TAG,
        operation_id='auth_refresh',
        description='Exchange a refresh token for a new access token.',
        request=RefreshTokenSerializer,
        responses={
            200: AccessTokenSerializer,
            401: OpenApiResponse(description='Invalid refresh token'),
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class LogoutView(APIView):
    @extend_schema(
        tags=AUTH_TAG,
        operation_id='auth_logout',
        description='Blacklist the provided refresh token so it can no longer be used.',
        request=LogoutSerializer,
        responses={
            200: MessageSerializer,
            400: OpenApiResponse(description='Invalid or expired refresh token'),
            401: OpenApiResponse(description='Authentication required'),
        },
    )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            token = RefreshToken(serializer.validated_data['refresh'])
            if str(token['user_id']) != str(request.user.id):
                raise PermissionDenied('You can only revoke your own refresh token.')
            token.blacklist()
        except PermissionDenied:
            raise
        except (KeyError, TokenError):
            return Response(
                {'detail': 'Invalid or expired refresh token.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)


class MeView(APIView):
    def get_read_serializer_class(self, user):
        return ME_READ_SERIALIZERS[user.role]

    def get_write_serializer_class(self, user):
        return ME_WRITE_SERIALIZERS[user.role]

    @extend_schema(
        tags=USERS_TAG,
        operation_id='users_me',
        description='Return the authenticated user profile.',
        responses={
            200: PolymorphicProxySerializer(
                component_name='MeResponse',
                serializers=[StudentMeSerializer, TeacherMeSerializer],
                resource_type_field_name='role',
            ),
            401: OpenApiResponse(description='Authentication required'),
        },
    )
    def get(self, request):
        serializer_class = self.get_read_serializer_class(request.user)
        return Response(serializer_class(request.user).data)

    @extend_schema(
        tags=USERS_TAG,
        operation_id='users_me_patch',
        description='Patch current user fields.',
        request=PolymorphicProxySerializer(
            component_name='MePatchRequest',
            serializers=[StudentMePatchSerializer, TeacherMePatchSerializer],
            resource_type_field_name=None,
        ),
        responses={
            200: PolymorphicProxySerializer(
                component_name='MePatchResponse',
                serializers=[StudentMeSerializer, TeacherMeSerializer],
                resource_type_field_name='role',
            ),
            401: OpenApiResponse(description='Authentication required'),
        },
    )
    def patch(self, request):
        serializer_class = self.get_write_serializer_class(request.user)
        serializer = serializer_class(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response_serializer_class = self.get_read_serializer_class(request.user)
        return Response(response_serializer_class(request.user).data, status=status.HTTP_200_OK)


class UserDetailView(APIView):
    @extend_schema(
        tags=USERS_TAG,
        operation_id='user_detail_get',
        description='Return the user detail information by id.',
        responses={
            200: PolymorphicProxySerializer(
                component_name='UserDetailResponse',
                serializers=[StudentDetailSerializer, TeacherDetailSerializer],
                resource_type_field_name='role',
            ),
            401: OpenApiResponse(description='Authentication required'),
            404: OpenApiResponse(description='User not found'),
        },
    )
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        profile = user.student_profile if user.role == User.Role.STUDENT else user.teacher_profile
        serializer = USER_DETAIL_SERIALIZERS[user.role](profile)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserView(APIView):
    @extend_schema(
        tags=USERS_TAG,
        operation_id='user_get',
        description='Return the user profile by id.',
        responses={
            200: PolymorphicProxySerializer(
                component_name='UserResponse',
                serializers=[StudentSerializer, TeacherSerializer],
                resource_type_field_name='role',
            ),
            401: OpenApiResponse(description='Authentication required'),
            404: OpenApiResponse(description='User not found'),
        },
    )
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        profile = user.student_profile if user.role == User.Role.STUDENT else user.teacher_profile
        serializer = USER_SERIALIZERS[user.role](profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

class GroupView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        tags=GROUPS_TAG,
        operation_id="groups_get",
        description="Get groups list or group by id",
        responses={
            200: GroupSerializer,
            404: OpenApiResponse(description="Group not found"),
        },
    )
    def get(self, request, pk=None):
        if pk:
            group = Group.objects.get(pk=pk)
            serializer = GroupSerializer(group)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        groups = Group.objects.all()
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
