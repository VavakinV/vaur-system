import django.core.validators
from django.db import migrations, models

import works.models


class Migration(migrations.Migration):

    dependencies = [
        ('works', '0002_drop_legacy_worktype_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='work',
            name='document',
            field=models.FileField(
                blank=True,
                null=True,
                upload_to=works.models.work_document_upload_to,
                validators=[django.core.validators.FileExtensionValidator(['docx'])],
                verbose_name='Файл работы',
            ),
        ),
        migrations.AddField(
            model_name='work',
            name='document_original_name',
            field=models.CharField(blank=True, max_length=255, verbose_name='Оригинальное имя файла'),
        ),
    ]
