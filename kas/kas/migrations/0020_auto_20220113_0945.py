# Generated by Django 2.2.18 on 2022-01-13 08:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("kas", "0019_auto_20220107_1344"),
    ]

    operations = [
        migrations.AlterField(
            model_name="historicalpolicytaxyear",
            name="pension_company",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="kas.PensionCompany",
                verbose_name="Pensionsselskab",
            ),
        ),
        migrations.AlterField(
            model_name="policytaxyear",
            name="pension_company",
            field=models.ForeignKey(
                blank=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="kas.PensionCompany",
                verbose_name="Pensionsselskab",
            ),
        ),
    ]
