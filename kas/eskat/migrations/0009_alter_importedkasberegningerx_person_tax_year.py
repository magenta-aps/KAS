# Generated by Django 3.2.12 on 2022-06-13 12:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("eskat", "0008_alter_importedkasberegningerx_person_tax_year"),
    ]

    operations = [
        migrations.AlterField(
            model_name="importedkasberegningerx",
            name="person_tax_year",
            field=models.OneToOneField(
                null=True, on_delete=django.db.models.deletion.CASCADE, to="kas.persontaxyear"
            ),
        ),
    ]
