# Generated by Django 2.2.18 on 2021-11-09 15:22

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kas', '0016_taxyear_rate_text_for_transactions'),
    ]

    operations = [
        migrations.AddField(
            model_name='finalsettlement',
            name='extra_payment_for_previous_missing',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(limit_value=0)], verbose_name='Ekstra beløb til betaling der dækker en delmængde af en tidligere ikke-betalt regning'),
        ),
        migrations.AddField(
            model_name='finalsettlement',
            name='interest_on_remainder',
            field=models.DecimalField(decimal_places=2, default='0.0', max_digits=5, verbose_name='Procentsats for hvor mange renter der skal lægges til for meget / for lidt opkrævet'),
        ),
    ]
