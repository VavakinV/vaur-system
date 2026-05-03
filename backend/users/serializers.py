from django.contrib.auth import get_user_model, password_validation
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.mixins import FullNameSerializerMixin
from users.models import Group, Student, Teacher


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    group_number = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        write_only=True,
        required=True,
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'password',
            'last_name',
            'first_name',
            'middle_name',
            'contacts',
            'group_number',
        )

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)
        group = attrs.get('group_number')
        if group is None:
            raise serializers.ValidationError({'group_number': 'This field is required.'})

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop('password')
        group = validated_data.pop('group_number')

        user = User(role=User.Role.STUDENT, **validated_data)
        user.set_password(password)
        user.save()

        Student.objects.create(user=user, group_number=group)

        return user


class AuthTokensSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField()

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if not attrs.get('username') and not attrs.get('email'):
            raise serializers.ValidationError(
                {'username': 'Provide either username or email.'}
            )
        return attrs


class EmailOrUsernameTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.USERNAME_FIELD
    email = serializers.EmailField(required=False)

    default_error_messages = {
        **TokenObtainPairSerializer.default_error_messages,
        'missing_identifier': 'Provide either username or email.',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.username_field].required = False

    def validate(self, attrs):
        identifier = attrs.get(self.username_field) or attrs.get('email')
        if not identifier:
            raise serializers.ValidationError(
                {self.username_field: self.error_messages['missing_identifier']}
            )

        user = User.objects.filter(email__iexact=identifier).only(self.username_field).first()
        normalized_attrs = {
            self.username_field: getattr(user, self.username_field) if user else identifier,
            'password': attrs['password'],
        }
        return super().validate(normalized_attrs)


class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class AccessTokenSerializer(serializers.Serializer):
    access = serializers.CharField()


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class MessageSerializer(serializers.Serializer):
    detail = serializers.CharField()


class RegisterResponseSerializer(FullNameSerializerMixin, serializers.ModelSerializer):
    access = serializers.CharField()
    refresh = serializers.CharField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'full_name',
            'last_name',
            'first_name',
            'middle_name',
            'contacts',
            'role',
            'access',
            'refresh',
        )

    @staticmethod
    def from_user(user):
        refresh = RefreshToken.for_user(user)
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': str(user),
            'last_name': user.last_name,
            'first_name': user.first_name,
            'middle_name': user.middle_name,
            'contacts': user.contacts,
            'role': user.role,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }


class MeSerializer(FullNameSerializerMixin, serializers.ModelSerializer):    
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'full_name',
            'last_name',
            'first_name',
            'middle_name',
            'contacts',
            'role',
            'is_staff',
            'is_superuser',
        )


class StudentDetailSerializer(FullNameSerializerMixin, serializers.ModelSerializer):
    group_number = serializers.CharField(
        source='group.number',
        read_only=True,
    )
    
    class Meta:
        model = Student
        fields = (
            'email',
            'full_name',
            'last_name',
            'first_name',
            'middle_name',
            'contacts',
            'group_id',
            'group_number',
        )


class TeacherDetailSerializer(FullNameSerializerMixin, serializers.ModelSerializer):
    department_name = serializers.CharField(
        source='department.name',
        read_only=True,
    )
    
    class Meta:
        model = Teacher
        fields = (
            'email',
            'full_name',
            'last_name',
            'first_name',
            'middle_name',
            'contacts',
            'department_id',
            'department_name',
            'is_norm_controller',
        )


class StudentSerializer(FullNameSerializerMixin, serializers.ModelSerializer):
    group_number = serializers.CharField(
        source='group.number',
        read_only=True,
    )
    
    class Meta:
        model = Student
        fields = (
            'full_name',
            'group_id',
            'group_number',
        )


class TeacherSerializer(FullNameSerializerMixin, serializers.ModelSerializer):
    department_name = serializers.CharField(
        source='department.name',
        read_only=True,
    )
    
    class Meta:
        model = Teacher
        fields = (
            'full_name',
            'department_id',
            'department_name',
            'is_norm_controller',
        )
        

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'
