# Generated by Django 5.0.4 on 2024-09-08 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("integrations", "0006_rename_integrations_integration_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="integration",
            name="is_active",
            field=models.BooleanField(default=False),
        ),
    ]
