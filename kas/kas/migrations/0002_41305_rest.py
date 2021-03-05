# Generated by Django 2.2.18 on 2021-02-16 12:43

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('kas', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='policydocument',
            old_name='policy',
            new_name='policy_tax_year',
        ),
        migrations.AlterField(
            model_name='pensioncompany',
            name='address',
            field=models.TextField(blank=True, help_text='Adresse', verbose_name='Adresse'),
        ),
        migrations.AlterField(
            model_name='pensioncompany',
            name='cvr',
            field=models.IntegerField(unique=True, validators=[django.core.validators.MinValueValidator(limit_value=1), django.core.validators.MaxValueValidator(limit_value=99999999)]),
        ),
        migrations.AlterField(
            model_name='pensioncompany',
            name='email',
            field=models.TextField(blank=True, help_text='E-mail', null=True, verbose_name='E-mail'),
        ),
        migrations.AlterField(
            model_name='pensioncompany',
            name='name',
            field=models.TextField(blank=True, db_index=True, help_text='Navn', max_length=255, verbose_name='Navn'),
        ),
        migrations.AlterField(
            model_name='pensioncompany',
            name='phone',
            field=models.TextField(blank=True, help_text='Telefon', null=True, verbose_name='Telefon'),
        ),
        migrations.AlterField(
            model_name='person',
            name='cpr',
            field=models.TextField(db_index=True, help_text='CPR nummer', max_length=10, unique=True, validators=[django.core.validators.RegexValidator(regex='\\d{10}')], verbose_name='CPR nummer'),
        ),
        migrations.AlterField(
            model_name='persontaxyear',
            name='end_date',
            field=models.DateField(null=True, verbose_name='Slutdato'),
        ),
        migrations.AlterField(
            model_name='persontaxyear',
            name='number_of_days',
            field=models.IntegerField(null=True, verbose_name='Antal dage'),
        ),
        migrations.AlterField(
            model_name='persontaxyear',
            name='start_date',
            field=models.DateField(null=True, verbose_name='Startdato'),
        ),
        migrations.AlterField(
            model_name='policytaxyear',
            name='applied_deduction_from_previous_years',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, validators=[django.core.validators.MinValueValidator(limit_value=0)], verbose_name='Anvendt fradrag fra tidligere år'),
        ),
        migrations.AlterField(
            model_name='policytaxyear',
            name='calculated_result',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, verbose_name='Beregnet resultat'),
        ),
        migrations.AlterField(
            model_name='policytaxyear',
            name='deduction_from_previous_years',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, validators=[django.core.validators.MinValueValidator(limit_value=0)], verbose_name='Fradrag fra tidligere år'),
        ),
        migrations.AlterField(
            model_name='policytaxyear',
            name='estimated_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, validators=[django.core.validators.MinValueValidator(limit_value=0)], verbose_name='Skønsbeløb angivet af Skattestyrelsen'),
        ),
        migrations.AlterField(
            model_name='policytaxyear',
            name='foreign_paid_amount_actual',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, validators=[django.core.validators.MinValueValidator(limit_value=0)], verbose_name='Faktisk betalt kapitalafkastskat i udlandet'),
        ),
        migrations.AlterField(
            model_name='policytaxyear',
            name='foreign_paid_amount_self_reported',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, validators=[django.core.validators.MinValueValidator(limit_value=0)], verbose_name='Selvangivet beløb for betalt kapitalafkastskat i udlandet'),
        ),
        migrations.AlterField(
            model_name='policytaxyear',
            name='modified_by',
            field=models.CharField(default='unknown', max_length=255, verbose_name='Modificeret af'),
        ),
        migrations.AlterField(
            model_name='policytaxyear',
            name='note',
            field=models.TextField(null=True, verbose_name='Note'),
        ),
        migrations.AlterField(
            model_name='policytaxyear',
            name='pension_company',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, to='kas.PensionCompany'),
        ),
        migrations.AlterField(
            model_name='policytaxyear',
            name='person_tax_year',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, to='kas.PersonTaxYear'),
        ),
        migrations.AlterField(
            model_name='policytaxyear',
            name='prefilled_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(limit_value=0)], verbose_name='Beløb rapporteret fra forsikringsselskab'),
        ),
        migrations.AlterField(
            model_name='policytaxyear',
            name='preliminary_paid_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(limit_value=0)], verbose_name='Foreløbigt betalt kapitalafkast'),
        ),
        migrations.AlterField(
            model_name='policytaxyear',
            name='self_reported_amount',
            field=models.DecimalField(decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(limit_value=0)], verbose_name='Selvangivet beløb'),
        ),
        migrations.AlterField(
            model_name='taxyear',
            name='year',
            field=models.IntegerField(db_index=True, help_text='Skatteår', unique=True, validators=[django.core.validators.MinValueValidator(limit_value=2000)], verbose_name='Skatteår'),
        ),
        migrations.AlterUniqueTogether(
            name='persontaxyear',
            unique_together={('tax_year', 'person')},
        ),
        migrations.AlterUniqueTogether(
            name='policytaxyear',
            unique_together={('person_tax_year', 'pension_company', 'policy_number')},
        ),
    ]
