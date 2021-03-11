# Generated by Django 2.2.18 on 2021-03-08 11:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('worker', '0002_auto_20210303_1429'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='job_type',
            field=models.TextField(choices=[('ImportMandtalJob', 'Import af mandtal'), ('ImportR75Job', 'Import af data fra R75')]),
        ),
    ]
