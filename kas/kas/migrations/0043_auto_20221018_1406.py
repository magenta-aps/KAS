# Generated by Django 3.2.12 on 2022-10-18 12:06

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kas', '0042_auto_20221003_1303'),
    ]

    operations = [
        migrations.AlterField(
            model_name='finalsettlement',
            name='pseudo_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AlterField(
            model_name='historicalpolicytaxyear',
            name='preliminary_paid_amount',
            field=models.BigIntegerField(blank=True, default=0, null=True, validators=[django.core.validators.MinValueValidator(limit_value=0)], verbose_name='Foreløbigt betalt kapitalafkast'),
        ),
        migrations.AlterField(
            model_name='policytaxyear',
            name='preliminary_paid_amount',
            field=models.BigIntegerField(blank=True, default=0, null=True, validators=[django.core.validators.MinValueValidator(limit_value=0)], verbose_name='Foreløbigt betalt kapitalafkast'),
        ),
    ]
