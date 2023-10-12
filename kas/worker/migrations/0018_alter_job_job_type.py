# Generated by Django 3.2.12 on 2023-10-09 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('worker', '0017_alter_job_job_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='job_type',
            field=models.TextField(choices=[('Autoligning', 'Kør autoligning'), ('ImportPrePaymentFile', 'Import af forudindbetalinger'), ('ImportMandtalJob', 'Import af mandtal'), ('ImportR75Job', 'Import af data fra R75'), ('ForceFinalize', 'Forcering af slutligning på alle udestående policer'), ('GenerateReportsForYear', 'Generering af KAS selvangivelser for et givet år'), ('DispatchTaxYear', 'Afsendelse af KAS selvangivelser for et givet år'), ('DispatchTaxYearDebug', 'Test-afsendelse af KAS selvangivelser for et givet år'), ('GenerateFinalSettlements', 'Generering af KAS slutopgørelser for et givet år'), ('GeneratePensionCompanySummary', 'Generering af årssummationsfil for et pensionsselskab'), ('GenerateBatchAndTransactions', 'Generering af Transaktioner og batch for et givent år'), ('DispatchFinalSettlements', 'Afsendelse af KAS slutopgørelser for et givet år'), ('DispatchFinalSettlement', 'Afsendelse af KAS slutopgørelse'), ('SendBatch', 'Sender et Q10 batch'), ('MergeCompanies', 'Flet pensionsselskaber'), ('ImportLegacyCalculations', 'Importere kas beregninger for tidligere år (2018/2019)'), ('GeneratePseudoFinalSettlements', 'Generering af pseudo slutopgørelser (2018/2019)'), ('ImportSpreadsheetR75Job', 'Import af data fra R75 i regneark'), ('ResetTaxYear', 'Reset data for skatteår'), ('GenerateSampleData', 'Generate sample data')]),
        ),
    ]