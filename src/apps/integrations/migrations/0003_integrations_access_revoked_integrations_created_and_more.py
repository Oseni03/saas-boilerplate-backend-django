# Generated by Django 5.0.4 on 2024-09-07 03:31

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("integrations", "0002_alter_thirdparty_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="integrations",
            name="access_revoked",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="integrations",
            name="created",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="integrations",
            name="updated",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
