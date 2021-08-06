# Generated by Django 2.2.18 on 2021-08-06 11:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prisme', '0004_auto_20210806_1249'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prisme10qbatch',
            name='status',
            field=models.CharField(choices=[('created', 'Ikke afsendt'), ('delivering', 'Afsender'), ('failed', 'Afsendelse fejlet'), ('delivered', 'Afsendt'), ('cancelled', 'Annulleret')], default='created', max_length=15),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='status',
            field=models.TextField(blank=True, choices=[('created', 'Oprettet'), ('ready', 'Klar til overførsel'), ('transferred', 'Overført'), ('cancelled', 'Annulleret')], default='created'),
        ),
    ]
