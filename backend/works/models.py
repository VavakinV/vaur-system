from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from users.models import Department, Student, Teacher


class WorkType(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Название типа работы')
    code = models.CharField(max_length=50, unique=True, verbose_name='Код типа работы')

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
    norm_control_status = models.CharField(
        max_length=20,
        choices=NormControlStatus.choices,
        default=NormControlStatus.PENDING,
        verbose_name='Статус нормоконтроля',
    )

    class Meta:
        verbose_name = 'Работа'
        verbose_name_plural = 'Работы'

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
