# Generated by Django 2.2 on 2019-08-03 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0020_groupstatus_brief'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee_certification',
            name='admin_accept',
            field=models.BooleanField(default=False),
        ),
    ]
