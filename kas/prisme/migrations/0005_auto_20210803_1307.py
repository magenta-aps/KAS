# Generated by Django 2.2.18 on 2021-08-03 11:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prisme', '0004_auto_20210716_1033'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prisme10qbatch',
            name='status',
            field=models.IntegerField(choices=[(1, 'Ikke afsendt'), (2, 'Afsendelse fejlet'), (3, 'Afsendt'), (5, 'Annulleret')], default=1),
        ),
    ]
