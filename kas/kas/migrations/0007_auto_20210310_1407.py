# Generated by Django 2.2.18 on 2021-03-10 13:07

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('kas', '0006_previousyearnegativepayout'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='policytaxyear',
            name='applied_deduction_from_previous_years',
        ),
        migrations.AddField(
            model_name='pensioncompany',
            name='agreement_present',
            field=models.BooleanField(default=False, verbose_name='Foreligger der en aftale med skattestyrelsen'),
        ),
        migrations.AddField(
            model_name='pensioncompany',
            name='reg_nr',
            field=models.PositiveSmallIntegerField(null=True, unique=True, verbose_name='Reg. nr.'),
        ),
        migrations.AlterField(
            model_name='pensioncompany',
            name='address',
            field=models.TextField(blank=True, help_text='Adresse', null=True, verbose_name='Adresse'),
        ),
        migrations.AlterField(
            model_name='pensioncompany',
            name='cvr',
            field=models.IntegerField(null=True, unique=True, validators=[django.core.validators.MinValueValidator(limit_value=1), django.core.validators.MaxValueValidator(limit_value=99999999)]),
        ),
        migrations.AlterField(
            model_name='pensioncompany',
            name='name',
            field=models.TextField(blank=True, db_index=True, help_text='Navn', max_length=255, null=True, verbose_name='Navn'),
        ),
        migrations.AlterField(
            model_name='previousyearnegativepayout',
            name='used_for',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='payouts_used', to='kas.PolicyTaxYear'),
        ),
        migrations.AlterField(
            model_name='previousyearnegativepayout',
            name='used_from',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='payouts_using', to='kas.PolicyTaxYear'),
        ),
        migrations.CreateModel(
            name='HistoricalPolicyTaxYear',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('policy_number', models.CharField(max_length=40)),
                ('prefilled_amount', models.BigIntegerField(blank=True, null=True, verbose_name='Beløb rapporteret fra forsikringsselskab')),
                ('estimated_amount', models.BigIntegerField(default=0, verbose_name='Skønsbeløb angivet af Skattestyrelsen')),
                ('self_reported_amount', models.BigIntegerField(null=True, verbose_name='Selvangivet beløb')),
                ('active_amount', models.SmallIntegerField(choices=[(1, 'Beløb rapporteret fra forsikringsselskab'), (2, 'Skønsbeløb angivet af Skattestyrelsen'), (3, 'Selvangivet beløb')], default=1, verbose_name='Beløb brugt til beregning')),
                ('year_adjusted_amount', models.BigIntegerField(default=0, verbose_name='Beløb justeret for dage i skatteår')),
                ('calculation_model', models.SmallIntegerField(choices=[(1, 'Standard'), (2, 'Alternativ')], default=1, verbose_name='Beregningsmodel')),
                ('preliminary_paid_amount', models.BigIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(limit_value=0)], verbose_name='Foreløbigt betalt kapitalafkast')),
                ('from_pension', models.BooleanField(default=False, verbose_name='Er kapitalafkastskatten hævet fra pensionsordning')),
                ('foreign_paid_amount_self_reported', models.BigIntegerField(blank=True, default=0, validators=[django.core.validators.MinValueValidator(limit_value=0)], verbose_name='Selvangivet beløb for betalt kapitalafkastskat i udlandet')),
                ('foreign_paid_amount_actual', models.BigIntegerField(blank=True, default=0, validators=[django.core.validators.MinValueValidator(limit_value=0)], verbose_name='Faktisk betalt kapitalafkastskat i udlandet')),
                ('calculated_full_tax', models.BigIntegerField(blank=True, default=0, verbose_name='Beregnet skat uden fradrag')),
                ('calculated_result', models.BigIntegerField(blank=True, default=0, verbose_name='Beregnet resultat')),
                ('modified_by', models.CharField(default='unknown', max_length=255, verbose_name='Modificeret af')),
                ('locked', models.BooleanField(default=False, help_text='Låst', verbose_name='Låst')),
                ('note', models.TextField(null=True, verbose_name='Note')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('pension_company', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='kas.PensionCompany')),
                ('person_tax_year', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='kas.PersonTaxYear')),
            ],
            options={
                'verbose_name': 'historical policy tax year',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
