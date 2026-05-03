from django.db import models
from users.models import User


class NotificationType(models.Model):
    name = models.CharField(max_length=40)

    class Meta:
        verbose_name = 'Тип уведомлений'
        verbose_name_plural = 'Типы уведомлений'
        ordering = ('name',)


class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Получатель', related_name='recipient_notification_set')
    actor = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Отправитель', related_name='actor_notification_set')
    type = models.ForeignKey(NotificationType, on_delete=models.CASCADE, verbose_name='Тип уведомления (тема)')
    message = models.CharField(max_length=300, verbose_name='Текст уведомления')
    target_object_link = models.CharField(max_length=100, null=True, blank=True, verbose_name='Ссылка на объект уведомления')
    is_read = models.BooleanField(default=False, verbose_name='Просмотрено')
    dt_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        ordering = ('-dt_created',)
