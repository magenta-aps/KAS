# Generated by Django 3.2.12 on 2022-11-07 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("kas", "0046_auto_20221031_1448"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalpersontaxyear",
            name="future_r75_data",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="persontaxyear",
            name="future_r75_data",
            field=models.BooleanField(default=False),
        ),
    ]
