# Generated by Django 3.2.12 on 2022-10-21 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kas', '0043_auto_20221018_1406'),
    ]

    operations = [
        migrations.AddField(
            model_name='finalsettlement',
            name='indifference_limited',
            field=models.BooleanField(default=False),
        ),
    ]
