# Generated by Django 3.2.12 on 2022-10-31 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("kas", "0045_auto_20221024_1458"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalpersontaxyear",
            name="corrected_r75_data",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="persontaxyear",
            name="corrected_r75_data",
            field=models.BooleanField(default=False),
        ),
    ]
