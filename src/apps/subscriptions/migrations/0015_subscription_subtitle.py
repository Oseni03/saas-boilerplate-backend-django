# Generated by Django 5.0.4 on 2024-08-14 18:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("subscriptions", "0014_subscription_features"),
    ]

    operations = [
        migrations.AddField(
            model_name="subscription",
            name="subtitle",
            field=models.TextField(blank=True, null=True),
        ),
    ]
