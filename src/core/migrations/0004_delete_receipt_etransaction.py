# Generated by Django 5.0.4 on 2024-04-26 15:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_alter_receipt_file"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Receipt_eTransaction",
        ),
    ]
