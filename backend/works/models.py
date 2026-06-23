from pathlib import Path
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone

from users.models import Department, Student, Teacher


def work_document_upload_to(instance, filename):
    suffix = Path(filename).suffix.lower()
    return f'works/{instance.pk or "new"}/{uuid4().hex}{suffix}'


class WorkType(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Название типа работы')

    class Meta:
        verbose_name = 'Тип работы'
        verbose_name_plural = 'Типы работ'

    def __str__(self):
        return self.name


class Work(models.Model):
    class NormControlStatus(models.TextChoices):
        PASSED = 'passed', 'Пройден'
        NEEDS_CHANGES = 'needs_changes', 'Есть исправления'
        PENDING = 'pending', 'В ожидании'
        NOT_SENT = 'not_sent', 'Не отправлено'


    class Status(models.TextChoices):
        DONE = 'done', 'Сдана'
        NOT_SENT = 'not_sent', 'Не отправлена'
        IN_PROGRESS = 'in_progress', 'В работе'
        STUDENT_EDIT = 'student_edit', 'Правки от студента'
        SUPERVISOR_EDIT = 'supervisor_edit', 'Правки от руководителя'
        NORMCONTROLLER_EDIT = 'normcontroller_edit', 'Правки от нормоконтролера'


    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='works',
        verbose_name='Студент',
    )
    supervisor = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name='supervised_works',
        verbose_name='Руководитель',
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='works',
        verbose_name='Кафедра',
    )
    work_type = models.ForeignKey(
        WorkType,
        on_delete=models.PROTECT,
        related_name='works',
        verbose_name='Тип работы',
    )
    topic = models.CharField(max_length=255, verbose_name='Тема работы')
    document = models.FileField(
        upload_to=work_document_upload_to,
        validators=[FileExtensionValidator(['docx'])],
        null=True,
        blank=True,
        verbose_name='Файл работы',
    )
    document_original_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Оригинальное имя файла',
    )
    document_updated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата обновления файла',
    )
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.NOT_SENT,
        verbose_name='Статус работы',
    )
    norm_control_status = models.CharField(
        max_length=20,
        choices=NormControlStatus.choices,
        default=NormControlStatus.NOT_SENT,
        verbose_name='Статус нормоконтроля',
    )

    class Meta:
        verbose_name = 'Работа'
        verbose_name_plural = 'Работы'

    def clean(self):
        super().clean()
        if self.document and not self.document.name.lower().endswith('.docx'):
            raise ValidationError({'document': 'Можно загружать только файлы .docx.'})

    def save(self, *args, **kwargs):
        if self.document and not self.document._committed:
            self.document_original_name = Path(self.document.name).name
            self.document_updated_at = timezone.now()
        elif not self.document:
            self.document_original_name = ''
            self.document_updated_at = None

        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.topic


class WorkCorrection(models.Model):
    class AuthorRole(models.TextChoices):
        SUPERVISOR = 'supervisor', 'Руководитель'
        NORM_CONTROLLER = 'norm_controller', 'Нормоконтролер'

    work = models.ForeignKey(
        Work,
        on_delete=models.CASCADE,
        related_name='corrections',
        verbose_name='Работа',
    )
    author = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name='work_corrections',
        verbose_name='Автор правок',
    )
    author_role = models.CharField(
        max_length=20,
        choices=AuthorRole.choices,
        verbose_name='Роль автора',
    )
    items = models.JSONField(default=list, verbose_name='Список правок')
    is_resolved = models.BooleanField(default=False, verbose_name='Правки учтены')
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата устранения правок')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Правки к работе'
        verbose_name_plural = 'Правки к работам'
        ordering = ('-created_at',)

    def clean(self):
        super().clean()

        if not isinstance(self.items, list) or not self.items:
            raise ValidationError({'items': 'Ожидается непустой список строк.'})

        normalized_items = []
        for item in self.items:
            if not isinstance(item, str):
                raise ValidationError({'items': 'Каждая правка должна быть строкой.'})

            value = item.strip()
            if not value:
                raise ValidationError({'items': 'Пустые строки в списке правок недопустимы.'})

            normalized_items.append(value)

        self.items = normalized_items

        if self.author_id and self.work_id:
            expected_role = None
            if self.author_id == self.work.supervisor_id:
                expected_role = self.AuthorRole.SUPERVISOR
            elif self.author.is_norm_controller:
                expected_role = self.AuthorRole.NORM_CONTROLLER

            if expected_role is None:
                raise ValidationError({'author': 'Автором правок может быть только руководитель работы или нормоконтролер.'})

            if self.author_role != expected_role:
                raise ValidationError({'author_role': f'Для выбранного автора допустима только роль "{expected_role}".'})

        if self.is_resolved and self.resolved_at is None:
            self.resolved_at = timezone.now()
        elif not self.is_resolved:
            self.resolved_at = None

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'Правки к "{self.work}" от {self.author}'


class WorkRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'В ожидании'
        REJECTED = 'rejected', 'Отклонено'
        ACCEPTED = 'accepted', 'Одобрена'

    student = models.ForeignKey(
        Student, on_delete=models.CASCADE,
        related_name='work_requests', verbose_name='Студент',
    )
    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE,
        related_name='received_requests', verbose_name='Преподаватель',
    )
    type = models.ForeignKey(WorkType, on_delete=models.CASCADE, verbose_name='Тип работы')
    topic = models.CharField(max_length=150, verbose_name='Тема работы')
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Статус заявки',
    )
    created_at = models.DateField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ('-created_at',)