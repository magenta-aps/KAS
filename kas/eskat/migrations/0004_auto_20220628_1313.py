# Generated by Django 3.2.12 on 2022-06-28 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eskat', '0003_r75spreadsheetfile_r75spreadsheetimport'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalimportedr75privatepension',
            name='company_pay_override',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='importedr75privatepension',
            name='company_pay_override',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='r75spreadsheetimport',
            name='company_pay_override',
            field=models.BooleanField(default=False),
        ),
    ]
