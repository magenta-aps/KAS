# Generated by Django 3.2.12 on 2022-06-13 10:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("kas", "0041_alter_finalsettlement_pseudo_amount"),
        ("eskat", "0006_auto_20220613_1113"),
    ]

    operations = [
        migrations.AlterField(
            model_name="historicalimportedkasberegningerx",
            name="person_tax_year",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="kas.persontaxyear",
            ),
        ),
    ]
