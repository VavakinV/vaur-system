from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('works', '0006_workrequest_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='work',
            name='document_updated_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Дата обновления файла'),
        ),
    ]
