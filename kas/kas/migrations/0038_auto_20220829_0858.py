# Generated by Django 3.2.12 on 2022-08-29 06:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kas', '0037_auto_20220628_1313'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalperson',
            name='is_test_person',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='person',
            name='is_test_person',
            field=models.BooleanField(default=False),
        ),
    ]
