# Generated by Django 3.2.12 on 2023-01-11 09:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kas', '0048_auto_20230105_1019'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalpolicytaxyear',
            name='base_calculation_amount',
            field=models.BigIntegerField(blank=True, null=True, verbose_name='Nuværende beløb til grund for skatteberegningen'),
        ),
        migrations.AddField(
            model_name='policytaxyear',
            name='base_calculation_amount',
            field=models.BigIntegerField(blank=True, null=True, verbose_name='Nuværende beløb til grund for skatteberegningen'),
        ),
    ]
