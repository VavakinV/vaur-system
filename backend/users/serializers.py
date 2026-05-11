from django.contrib.auth import get_user_model, password_validation
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

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


class BaseMeSerializer(FullNameSerializerMixin, serializers.ModelSerializer):
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
        read_only_fields = fields


class StudentMeSerializer(BaseMeSerializer):
    group_id = serializers.IntegerField(source='student_profile.group_number_id', read_only=True)
    group_number = serializers.CharField(source='student_profile.group_number.number', read_only=True)

    class Meta(BaseMeSerializer.Meta):
        fields = BaseMeSerializer.Meta.fields + (
            'group_id',
            'group_number',
        )


class TeacherMeSerializer(BaseMeSerializer):
    department_id = serializers.IntegerField(source='teacher_profile.department_id', read_only=True)
    department_name = serializers.CharField(source='teacher_profile.department.name', read_only=True)
    student_limit = serializers.IntegerField(source='teacher_profile.student_limit', read_only=True)
    is_norm_controller = serializers.BooleanField(source='teacher_profile.is_norm_controller', read_only=True)

    class Meta(BaseMeSerializer.Meta):
        fields = BaseMeSerializer.Meta.fields + (
            'department_id',
            'department_name',
            'student_limit',
            'is_norm_controller',
        )


class BaseMePatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'last_name',
            'first_name',
            'middle_name',
            'contacts',
        )

    def validate_email(self, value):
        user = self.instance
        if User.objects.exclude(pk=user.pk).filter(email__iexact=value).exists():
            raise serializers.ValidationError('User with this email already exists.')
        return value


class StudentMePatchSerializer(BaseMePatchSerializer):
    pass


class TeacherMePatchSerializer(BaseMePatchSerializer):
    pass


class StudentSerializer(FullNameSerializerMixin, serializers.ModelSerializer):
    group_number = serializers.CharField(source='group.number', read_only=True)

    class Meta:
        model = Student
        fields = (
            'full_name',
            'group_id',
            'group_number',
        )


class UserDetailFieldsMixin(serializers.Serializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    middle_name = serializers.CharField(source='user.middle_name', read_only=True)
    contacts = serializers.CharField(source='user.contacts', read_only=True)


class StudentDetailSerializer(UserDetailFieldsMixin, StudentSerializer):

    class Meta(StudentSerializer.Meta):
        fields = StudentSerializer.Meta.fields + (
            'email',
            'last_name',
            'first_name',
            'middle_name',
            'contacts',
        )


class TeacherSerializer(FullNameSerializerMixin, serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Teacher
        fields = (
            'full_name',
            'department_id',
            'department_name',
            'is_norm_controller',
        )


class TeacherDetailSerializer(UserDetailFieldsMixin, TeacherSerializer):

    class Meta(TeacherSerializer.Meta):
        fields = TeacherSerializer.Meta.fields + (
            'email',
            'last_name',
            'first_name',
            'middle_name',
            'contacts',
        )


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'
