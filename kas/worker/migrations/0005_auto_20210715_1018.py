# Generated by Django 2.2.18 on 2021-07-15 08:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('worker', '0004_auto_20210715_0931'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='job_type',
            field=models.TextField(choices=[('Autoligning', 'Kør autoligning'), ('ImportPrePaymentFile', 'Import af forudindbetalinger'), ('ImportMandtalJob', 'Import af mandtal'), ('ImportR75Job', 'Import af data fra R75'), ('ForceFinalize', 'Forcering af slutligning på alle udestående policer'), ('GenerateReportsForYear', 'Generere KAS selvangivelser'), ('DispatchTaxYear', 'Afsendelse af KAS selvangivelser for et givent år'), ('GenerateFinalSettlements', 'Generering af KAS slutopgørelser for et givet år'), ('DispatchFinalSettlements', 'Afsendelse af KAS slutopgørelser for et givet år'), ('ImportEskatMockup', 'Import af mockup data for eSkat'), ('ClearTestData', 'Nulstil test-data'), ('ResetToMockupOnly', 'Nulstil til KUN mockup data'), ('ImportAllMockupMandtal', 'Imporer alle mockup mandtal'), ('ImportAllMockupR75', 'Imporer alle mockup r75')]),
        ),
    ]
