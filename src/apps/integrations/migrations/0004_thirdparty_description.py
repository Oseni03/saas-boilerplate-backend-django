# Generated by Django 5.0.4 on 2024-09-07 10:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "integrations",
            "0003_integrations_access_revoked_integrations_created_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="thirdparty",
            name="description",
            field=models.TextField(default="Little description"),
            preserve_default=False,
        ),
    ]
