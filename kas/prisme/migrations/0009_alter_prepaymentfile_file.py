# Generated by Django 3.2.12 on 2022-05-04 13:23

import django.core.validators
from django.db import migrations, models
import prisme.models


class Migration(migrations.Migration):

    dependencies = [
        ('prisme', '0008_auto_20220316_1521'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prepaymentfile',
            name='file',
            field=models.FileField(upload_to=prisme.models.payment_file_by_year, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['csv'])]),
        ),
    ]
