# Generated by Django 3.2.12 on 2022-04-05 09:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('worker', '0008_auto_20220114_1113'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='arguments',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='job',
            name='checkpoint',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='job',
            name='result',
            field=models.JSONField(default=dict),
        ),
    ]
