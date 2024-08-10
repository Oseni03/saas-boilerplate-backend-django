# Generated by Django 4.2 on 2023-08-08 12:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('notifications', '0002_notification_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='issuer',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='notifications_issued',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
