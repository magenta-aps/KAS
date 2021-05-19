# Generated by Django 2.2.18 on 2021-05-19 10:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('worker', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='job_type',
            field=models.TextField(choices=[('ImportMandtalJob', 'Import af mandtal'), ('ImportR75Job', 'Import af data fra R75'), ('GenerateReportsForYear', 'Generere KAS selvangivelser'), ('DispatchTaxYear', 'Afsendelse af KAS selvangivelser for et givent år'), ('GenerateFinalSettlements', 'Generering af slutopgørelser for et given år'), ('DispatchFinalSettlements', 'Afsendelse af slutopgørelser for et given år'), ('ImportEskatMockup', 'Import af mockup data for eSkat'), ('ClearTestData', 'Nulstil test-data'), ('ResetToMockupOnly', 'Nulstil til KUN mockup data'), ('ImportAllMockupMandtal', 'Imporer alle mockup mandtal'), ('ImportAllMockupR75', 'Imporer alle mockup r75')]),
        ),
    ]
