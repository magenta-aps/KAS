# Generated by Django 2.2.18 on 2021-05-18 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kas', '0008_pensioncompanysummary'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalpolicytaxyear',
            name='efterbehandling',
            field=models.BooleanField(default=False, verbose_name='Kræver efterbehandling'),
        ),
        migrations.AddField(
            model_name='historicalpolicytaxyear',
            name='slutlignet',
            field=models.BooleanField(default=False, verbose_name='Slutlignet'),
        ),
        migrations.AddField(
            model_name='policytaxyear',
            name='efterbehandling',
            field=models.BooleanField(default=False, verbose_name='Kræver efterbehandling'),
        ),
        migrations.AddField(
            model_name='policytaxyear',
            name='slutlignet',
            field=models.BooleanField(default=False, verbose_name='Slutlignet'),
        ),
        migrations.AddField(
            model_name='taxyear',
            name='periode',
            field=models.TextField(choices=[('selvangivelse', 'Selvangivelsesperiode'), ('ligning', 'Ligningsperiod'), ('efterbehandling', 'Efterbehandlingsperiode')], default='selvangivelse'),
        ),
    ]
