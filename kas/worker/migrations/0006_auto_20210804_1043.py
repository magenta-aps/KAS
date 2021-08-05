# Generated by Django 2.2.18 on 2021-08-04 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('worker', '0005_auto_20210715_1018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='job_type',
            field=models.TextField(choices=[('Autoligning', 'Kør autoligning'), ('ImportPrePaymentFile', 'Import af forudindbetalinger'), ('ImportMandtalJob', 'Import af mandtal'), ('ImportR75Job', 'Import af data fra R75'), ('ForceFinalize', 'Forcering af slutligning på alle udestående policer'), ('GenerateReportsForYear', 'Generere KAS selvangivelser'), ('DispatchTaxYear', 'Afsendelse af KAS selvangivelser for et givent år'), ('GenerateFinalSettlements', 'Generering af KAS slutopgørelser for et givet år'), ('GenerateBatchAndTransactions', 'Generering af Transaktioner og batch for et givent år'), ('DispatchFinalSettlements', 'Afsendelse af KAS slutopgørelser for et givet år'), ('ImportEskatMockup', 'Import af mockup data for eSkat'), ('ClearTestData', 'Nulstil test-data'), ('ResetToMockupOnly', 'Nulstil til KUN mockup data'), ('ImportAllMockupMandtal', 'Imporer alle mockup mandtal'), ('ImportAllMockupR75', 'Imporer alle mockup r75')]),
        ),
    ]
