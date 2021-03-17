# Generated by Django 2.2.18 on 2021-03-16 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('worker', '0005_auto_20210315_1807'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='job_type',
            field=models.TextField(choices=[('ImportMandtalJob', 'Import af mandtal'), ('ImportR75Job', 'Import af data fra R75'), ('GenerateReportsForYear', 'Generere KAS selvangivelser'), ('DispatchTaxYear', 'Afsendelse af Kas opgørelse for et given år'), ('ImportEskatMockup', 'Import af mockup data for eSkat'), ('ClearTestData', 'Nulstil test-data')]),
        ),
    ]