# Generated by Django 2.2.18 on 2021-05-25 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kas', '0012_auto_20210520_1646'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalpolicytaxyear',
            name='next_processing_date',
            field=models.DateField(blank=True, null=True, verbose_name='Næste behandlingsdato'),
        ),
        migrations.AlterField(
            model_name='policytaxyear',
            name='next_processing_date',
            field=models.DateField(blank=True, null=True, verbose_name='Næste behandlingsdato'),
        ),
    ]
