# Generated by Django 5.0.4 on 2024-08-15 18:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("subscriptions", "0017_alter_subscriptionprice_trial_period_days"),
    ]

    operations = [
        migrations.AddField(
            model_name="usersubscription",
            name="client_secret",
            field=models.CharField(blank=True, max_length=120, null=True),
        ),
        migrations.AddField(
            model_name="usersubscription",
            name="current_period_end",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="usersubscription",
            name="current_period_start",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
