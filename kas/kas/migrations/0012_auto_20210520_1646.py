# Generated by Django 2.2.18 on 2021-05-20 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kas', '0011_notes'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalpolicytaxyear',
            name='next_processing_date',
            field=models.DateField(null=True, verbose_name='Næste behandlingsdato'),
        ),
        migrations.AddField(
            model_name='policytaxyear',
            name='next_processing_date',
            field=models.DateField(null=True, verbose_name='Næste behandlingsdato'),
        ),
    ]
