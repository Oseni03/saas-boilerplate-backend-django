# Generated by Django 5.0.4 on 2024-08-17 16:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("customers", "0003_paymentmethod"),
    ]

    operations = [
        migrations.DeleteModel(
            name="PaymentMethod",
        ),
    ]
