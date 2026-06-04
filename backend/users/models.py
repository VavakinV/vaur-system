from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError
from django.db import models


class CustomUserManager(UserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.Role.TEACHER)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return super().create_superuser(username, email=email, password=password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'student', 'Student'
        TEACHER = 'teacher', 'Teacher'

    email = models.EmailField(unique=True, verbose_name='Адрес электронной почты')
    last_name = models.CharField(max_length=50, verbose_name='Фамилия')
    first_name = models.CharField(max_length=50, verbose_name='Имя')
    middle_name = models.CharField(max_length=50, blank=True, null=True, verbose_name='Отчество')
    contacts = models.CharField(max_length=300, blank=True, null=True, verbose_name='Контакты')
    role = models.CharField(max_length=20, choices=Role.choices, verbose_name='Роль')
    dt_created = models.DateTimeField(auto_now_add=True)

    REQUIRED_FIELDS = ['email', 'role']
    objects = CustomUserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return ' '.join(filter(None, parts))

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_teacher(self):
        return self.role == self.Role.TEACHER


class Group(models.Model):
    number = models.CharField(max_length=10, verbose_name='Номер группы')

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.number


class Student(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile',
        limit_choices_to={'role': User.Role.STUDENT},
        verbose_name='Пользователь',
    )
    group_number = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name='Группа')

    class Meta:
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенты'

    def clean(self):
        super().clean()
        if self.user_id and self.user.role != User.Role.STUDENT:
            raise ValidationError({'user': 'Пользователь должен иметь роль student.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return str(self.user)


class Department(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название кафедры')

    class Meta:
        verbose_name = 'Кафедра'
        verbose_name_plural = 'Кафедры'

    def __str__(self):
        return self.name


class Teacher(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='teacher_profile',
        limit_choices_to={'role': User.Role.TEACHER},
        verbose_name='Пользователь',
    )
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='Кафедра')
    student_limit = models.PositiveIntegerField(null=True, blank=True, verbose_name='Максимум студентов')
    is_norm_controller = models.BooleanField(default=False, verbose_name='Является нормоконтролером')

    class Meta:
        verbose_name = 'Преподаватель'
        verbose_name_plural = 'Преподаватели'

    def clean(self):
        super().clean()
        if self.user_id and self.user.role != User.Role.TEACHER:
            raise ValidationError({'user': 'Пользователь должен иметь роль teacher.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return str(self.user)
