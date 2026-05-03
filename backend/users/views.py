from drf_spectacular.utils import OpenApiResponse, extend_schema
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
    EmailOrUsernameTokenObtainPairSerializer,
    LoginSerializer,
    LogoutSerializer,
    MeSerializer,
    MessageSerializer,
    RefreshTokenSerializer,
    RegisterResponseSerializer,
    RegisterSerializer,
    GroupSerializer,
)

from users.models import Group


USERS_TAG = ['Users']
GROUPS_TAG = ['Groups']


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=USERS_TAG,
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
        tags=USERS_TAG,
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
        tags=USERS_TAG,
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
        tags=USERS_TAG,
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
    @extend_schema(
        tags=USERS_TAG,
        operation_id='auth_me',
        description='Return the authenticated user profile.',
        responses={200: MeSerializer, 401: OpenApiResponse(description='Authentication required')},
    )
    def get(self, request):
        serializer = MeSerializer(request.user)
        return Response(serializer.data)


class GroupView(APIView):
    @extend_schema(
        tags=GROUPS_TAG,
        operation_id="groups_get",
        description="Get groups list or group by id",
        responses={
            200: GroupSerializer,
        },
    )
    def get(self, request, pk=None):
        if pk:
            group = Group.objects.get(pk=pk)
            return group
        
        groups = Group.objects.all()
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
        
