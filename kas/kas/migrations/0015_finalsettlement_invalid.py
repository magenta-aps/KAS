# Generated by Django 2.2.18 on 2021-06-07 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kas', '0014_fix_assessed_amount_and_used_negative_amounts'),
    ]

    operations = [
        migrations.AddField(
            model_name='finalsettlement',
            name='invalid',
            field=models.BooleanField(default=False, verbose_name='Slutopgørelse er ikke gyldig'),
        ),
        migrations.AlterModelOptions(
            name='finalsettlement',
            options={'ordering': ('-created_at',)},
        ),
        migrations.AlterModelOptions(
            name='taxslipgenerated',
            options={'ordering': ('-created_at',)},
        ),
    ]
