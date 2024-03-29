# Generated by Django 3.2.12 on 2022-05-18 13:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kas', '0031_migrate_files'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='finalsettlement',
            options={},
        ),
        migrations.AddField(
            model_name='finalsettlement',
            name='pseudo',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='finalsettlement',
            name='pseudo_amount',
            field=models.DecimalField(decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AddConstraint(
            model_name='finalsettlement',
            constraint=models.UniqueConstraint(condition=models.Q(('pseudo', True)), fields=('person_tax_year', 'pseudo'), name='idx_pseudo_true'),
        ),
    ]
