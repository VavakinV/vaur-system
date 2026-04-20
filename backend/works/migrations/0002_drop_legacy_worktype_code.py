from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('works', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql='ALTER TABLE works_worktype DROP COLUMN IF EXISTS code;',
            reverse_sql='ALTER TABLE works_worktype ADD COLUMN IF NOT EXISTS code varchar(255);',
        ),
    ]
