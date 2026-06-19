import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_user_contacts'),
        ('works', '0005_work_status_alter_work_norm_control_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workrequest',
            name='student',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='work_requests',
                to='users.student',
                verbose_name='Студент',
            ),
        ),
        migrations.AlterField(
            model_name='workrequest',
            name='teacher',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='received_requests',
                to='users.teacher',
                verbose_name='Преподаватель',
            ),
        ),
        migrations.AddField(
            model_name='workrequest',
            name='status',
            field=models.CharField(
                choices=[('pending', 'В ожидании'), ('rejected', 'Отклонено'), ('accepted', 'Одобрена')],
                default='pending',
                max_length=20,
                verbose_name='Статус заявки',
            ),
        ),
    ]
