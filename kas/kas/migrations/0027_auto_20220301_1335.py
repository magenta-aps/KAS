# Generated by Django 2.2.26 on 2022-03-01 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("kas", "0026_auto_20220221_1310"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalperson",
            name="status",
            field=models.TextField(
                choices=[
                    ("Undefined", ""),
                    ("Invalid", "Ugyldig"),
                    ("Alive", ""),
                    ("Dead", "Afdød"),
                ],
                default="Undefined",
            ),
        ),
        migrations.AddField(
            model_name="person",
            name="status",
            field=models.TextField(
                choices=[
                    ("Undefined", ""),
                    ("Invalid", "Ugyldig"),
                    ("Alive", ""),
                    ("Dead", "Afdød"),
                ],
                default="Undefined",
            ),
        ),
    ]
