# Generated by Django 2.2.18 on 2021-05-27 09:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prisme', '0002_auto_20210517_1046'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='type',
            field=models.TextField(choices=[('charge', 'Opkrævning'), ('repayment', 'Tilbagebetaling'), ('adjustment', 'Justering'), ('prepayment', 'Forudindbetaling')]),
        ),
    ]
