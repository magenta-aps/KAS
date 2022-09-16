# Generated by Django 2.2.18 on 2021-03-23 18:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='KasBeregninger',
            fields=[
                ('pt_census_guid', models.UUIDField(primary_key=True, serialize=False)),
                ('pension_crt_calc_guid', models.UUIDField()),
                ('pension_crt_lock_batch_guid', models.UUIDField(blank=True, null=True)),
                ('reg_date', models.DateTimeField()),
                ('is_locked', models.CharField(blank=True, max_length=1, null=True)),
                ('no', models.IntegerField(blank=True, null=True)),
                ('capital_return', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('sum_negative_capital_return', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('used_negative_capital_return', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('capital_return_base', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('capital_return_tax', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('crt_payment', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('police_payment', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('deficit_crt', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('surplus_crt_payment', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('surplus_police_payment', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('total_surplus', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('result_surplus_crt_payment', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('annotation', models.TextField(blank=True, null=True)),
                ('is_locking_allowed', models.CharField(blank=True, max_length=4, null=True)),
            ],
            options={
                'db_table': 'kas_beregninger',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='KasBeregningerX',
            fields=[
                ('pt_census_guid', models.UUIDField()),
                ('cpr', models.TextField()),
                ('bank_reg_nr', models.TextField(blank=True, null=True)),
                ('bank_konto_nr', models.TextField(blank=True, null=True)),
                ('kommune_no', models.IntegerField(blank=True, null=True)),
                ('kommune', models.TextField(blank=True, null=True)),
                ('skatteaar', models.IntegerField()),
                ('navn', models.TextField(blank=True, null=True)),
                ('adresselinje1', models.TextField(blank=True, null=True)),
                ('adresselinje2', models.TextField(blank=True, null=True)),
                ('adresselinje3', models.TextField(blank=True, null=True)),
                ('adresselinje4', models.TextField(blank=True, null=True)),
                ('adresselinje5', models.TextField(blank=True, null=True)),
                ('fuld_adresse', models.TextField(blank=True, null=True)),
                ('cpr_dashed', models.TextField(blank=True, null=True)),
                ('pension_crt_calc_guid', models.UUIDField(primary_key=True, serialize=False)),
                ('pension_crt_lock_batch_guid', models.UUIDField(blank=True, null=True)),
                ('reg_date', models.DateTimeField()),
                ('is_locked', models.CharField(blank=True, max_length=1, null=True)),
                ('no', models.IntegerField(blank=True, null=True)),
                ('capital_return', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('sum_negative_capital_return', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('used_negative_capital_return', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('capital_return_base', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('capital_return_tax', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('crt_payment', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('police_payment', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('deficit_crt', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('surplus_crt_payment', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('surplus_police_payment', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('total_surplus', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('result_surplus_crt_payment', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('annotation', models.TextField(blank=True, null=True)),
                ('is_locking_allowed', models.CharField(blank=True, max_length=4, null=True)),
            ],
            options={
                'db_table': 'kas_beregninger_x',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='KasMandtal',
            fields=[
                ('pt_census_guid', models.UUIDField(primary_key=True, serialize=False)),
                ('cpr', models.TextField()),
                ('bank_reg_nr', models.TextField(blank=True, null=True)),
                ('bank_konto_nr', models.TextField(blank=True, null=True)),
                ('kommune_no', models.IntegerField(blank=True, null=True)),
                ('kommune', models.TextField(blank=True, null=True)),
                ('skatteaar', models.IntegerField()),
                ('navn', models.TextField(blank=True, null=True)),
                ('adresselinje1', models.TextField(blank=True, null=True)),
                ('adresselinje2', models.TextField(blank=True, null=True)),
                ('adresselinje3', models.TextField(blank=True, null=True)),
                ('adresselinje4', models.TextField(blank=True, null=True)),
                ('adresselinje5', models.TextField(blank=True, null=True)),
                ('fuld_adresse', models.TextField(blank=True, null=True)),
                ('cpr_dashed', models.TextField(blank=True, null=True)),
                ('skatteomfang', models.TextField(blank=True, null=True)),
                ('skattedage', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'kas_mandtal',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='R75Idx4500230',
            fields=[
                ('pt_census_guid', models.UUIDField()),
                ('tax_year', models.IntegerField()),
                ('cpr', models.TextField()),
                ('r75_ctl_sekvens_guid', models.UUIDField(primary_key=True, serialize=False)),
                ('r75_ctl_indeks_guid', models.UUIDField()),
                ('idx_nr', models.IntegerField()),
                ('res', models.TextField(blank=True, null=True)),
                ('ktd', models.TextField(blank=True, null=True)),
                ('ktt', models.TextField(blank=True, null=True)),
                ('kontotype', models.TextField(blank=True, null=True)),
                ('ibn', models.TextField(blank=True, null=True)),
                ('esk', models.TextField(blank=True, null=True)),
                ('ejerstatuskode', models.TextField(blank=True, null=True)),
                ('indestaaende', models.TextField(blank=True, db_column='indestående', null=True)),
                ('renteindtaegt', models.TextField(blank=True, db_column='renteindtægt', null=True)),
                ('r75_dato', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'r75_idx_4500230',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ImportedKasBeregningerX',
            fields=[
                ('pt_census_guid', models.UUIDField()),
                ('cpr', models.TextField()),
                ('bank_reg_nr', models.TextField(blank=True, null=True)),
                ('bank_konto_nr', models.TextField(blank=True, null=True)),
                ('kommune_no', models.IntegerField(blank=True, null=True)),
                ('kommune', models.TextField(blank=True, null=True)),
                ('skatteaar', models.IntegerField()),
                ('navn', models.TextField(blank=True, null=True)),
                ('adresselinje1', models.TextField(blank=True, null=True)),
                ('adresselinje2', models.TextField(blank=True, null=True)),
                ('adresselinje3', models.TextField(blank=True, null=True)),
                ('adresselinje4', models.TextField(blank=True, null=True)),
                ('adresselinje5', models.TextField(blank=True, null=True)),
                ('fuld_adresse', models.TextField(blank=True, null=True)),
                ('cpr_dashed', models.TextField(blank=True, null=True)),
                ('pension_crt_calc_guid', models.UUIDField(primary_key=True, serialize=False)),
                ('pension_crt_lock_batch_guid', models.UUIDField(blank=True, null=True)),
                ('reg_date', models.DateTimeField()),
                ('is_locked', models.CharField(blank=True, max_length=1, null=True)),
                ('no', models.IntegerField(blank=True, null=True)),
                ('capital_return', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('sum_negative_capital_return', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('used_negative_capital_return', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('capital_return_base', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('capital_return_tax', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('crt_payment', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('police_payment', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('deficit_crt', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('surplus_crt_payment', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('surplus_police_payment', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('total_surplus', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('result_surplus_crt_payment', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('annotation', models.TextField(blank=True, null=True)),
                ('is_locking_allowed', models.CharField(blank=True, max_length=4, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ImportedKasMandtal',
            fields=[
                ('pt_census_guid', models.UUIDField(primary_key=True, serialize=False)),
                ('cpr', models.TextField()),
                ('bank_reg_nr', models.TextField(blank=True, null=True)),
                ('bank_konto_nr', models.TextField(blank=True, null=True)),
                ('kommune_no', models.IntegerField(blank=True, null=True)),
                ('kommune', models.TextField(blank=True, null=True)),
                ('skatteaar', models.IntegerField()),
                ('navn', models.TextField(blank=True, null=True)),
                ('adresselinje1', models.TextField(blank=True, null=True)),
                ('adresselinje2', models.TextField(blank=True, null=True)),
                ('adresselinje3', models.TextField(blank=True, null=True)),
                ('adresselinje4', models.TextField(blank=True, null=True)),
                ('adresselinje5', models.TextField(blank=True, null=True)),
                ('fuld_adresse', models.TextField(blank=True, null=True)),
                ('cpr_dashed', models.TextField(blank=True, null=True)),
                ('skatteomfang', models.TextField(blank=True, null=True)),
                ('skattedage', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ImportedR75PrivatePension',
            fields=[
                ('pt_census_guid', models.UUIDField()),
                ('tax_year', models.IntegerField()),
                ('cpr', models.TextField()),
                ('r75_ctl_sekvens_guid', models.UUIDField(primary_key=True, serialize=False)),
                ('r75_ctl_indeks_guid', models.UUIDField()),
                ('idx_nr', models.IntegerField()),
                ('res', models.TextField(blank=True, null=True)),
                ('ktd', models.TextField(blank=True, null=True)),
                ('ktt', models.TextField(blank=True, null=True)),
                ('kontotype', models.TextField(blank=True, null=True)),
                ('ibn', models.TextField(blank=True, null=True)),
                ('esk', models.TextField(blank=True, null=True)),
                ('ejerstatuskode', models.TextField(blank=True, null=True)),
                ('indestaaende', models.TextField(blank=True, db_column='indestående', null=True)),
                ('renteindtaegt', models.TextField(blank=True, db_column='renteindtægt', null=True)),
                ('r75_dato', models.TextField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MockKasBeregningerX',
            fields=[
                ('pt_census_guid', models.UUIDField()),
                ('cpr', models.TextField()),
                ('bank_reg_nr', models.TextField(blank=True, null=True)),
                ('bank_konto_nr', models.TextField(blank=True, null=True)),
                ('kommune_no', models.IntegerField(blank=True, null=True)),
                ('kommune', models.TextField(blank=True, null=True)),
                ('skatteaar', models.IntegerField()),
                ('navn', models.TextField(blank=True, null=True)),
                ('adresselinje1', models.TextField(blank=True, null=True)),
                ('adresselinje2', models.TextField(blank=True, null=True)),
                ('adresselinje3', models.TextField(blank=True, null=True)),
                ('adresselinje4', models.TextField(blank=True, null=True)),
                ('adresselinje5', models.TextField(blank=True, null=True)),
                ('fuld_adresse', models.TextField(blank=True, null=True)),
                ('cpr_dashed', models.TextField(blank=True, null=True)),
                ('pension_crt_calc_guid', models.UUIDField(primary_key=True, serialize=False)),
                ('pension_crt_lock_batch_guid', models.UUIDField(blank=True, null=True)),
                ('reg_date', models.DateTimeField()),
                ('is_locked', models.CharField(blank=True, max_length=1, null=True)),
                ('no', models.IntegerField(blank=True, null=True)),
                ('capital_return', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('sum_negative_capital_return', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('used_negative_capital_return', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('capital_return_base', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('capital_return_tax', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('crt_payment', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('police_payment', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('deficit_crt', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('surplus_crt_payment', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('surplus_police_payment', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('total_surplus', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('result_surplus_crt_payment', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('annotation', models.TextField(blank=True, null=True)),
                ('is_locking_allowed', models.CharField(blank=True, max_length=4, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MockKasMandtal',
            fields=[
                ('pt_census_guid', models.UUIDField(primary_key=True, serialize=False)),
                ('cpr', models.TextField()),
                ('bank_reg_nr', models.TextField(blank=True, null=True)),
                ('bank_konto_nr', models.TextField(blank=True, null=True)),
                ('kommune_no', models.IntegerField(blank=True, null=True)),
                ('kommune', models.TextField(blank=True, null=True)),
                ('skatteaar', models.IntegerField()),
                ('navn', models.TextField(blank=True, null=True)),
                ('adresselinje1', models.TextField(blank=True, null=True)),
                ('adresselinje2', models.TextField(blank=True, null=True)),
                ('adresselinje3', models.TextField(blank=True, null=True)),
                ('adresselinje4', models.TextField(blank=True, null=True)),
                ('adresselinje5', models.TextField(blank=True, null=True)),
                ('fuld_adresse', models.TextField(blank=True, null=True)),
                ('cpr_dashed', models.TextField(blank=True, null=True)),
                ('skatteomfang', models.TextField(blank=True, null=True)),
                ('skattedage', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MockR75Idx4500230',
            fields=[
                ('pt_census_guid', models.UUIDField()),
                ('tax_year', models.IntegerField()),
                ('cpr', models.TextField()),
                ('r75_ctl_sekvens_guid', models.UUIDField(primary_key=True, serialize=False)),
                ('r75_ctl_indeks_guid', models.UUIDField()),
                ('idx_nr', models.IntegerField()),
                ('res', models.TextField(blank=True, null=True)),
                ('ktd', models.TextField(blank=True, null=True)),
                ('ktt', models.TextField(blank=True, null=True)),
                ('kontotype', models.TextField(blank=True, null=True)),
                ('ibn', models.TextField(blank=True, null=True)),
                ('esk', models.TextField(blank=True, null=True)),
                ('ejerstatuskode', models.TextField(blank=True, null=True)),
                ('indestaaende', models.TextField(blank=True, db_column='indestående', null=True)),
                ('renteindtaegt', models.TextField(blank=True, db_column='renteindtægt', null=True)),
                ('r75_dato', models.TextField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HistoricalImportedR75PrivatePension',
            fields=[
                ('pt_census_guid', models.UUIDField()),
                ('tax_year', models.IntegerField()),
                ('cpr', models.TextField()),
                ('r75_ctl_sekvens_guid', models.UUIDField(db_index=True)),
                ('r75_ctl_indeks_guid', models.UUIDField()),
                ('idx_nr', models.IntegerField()),
                ('res', models.TextField(blank=True, null=True)),
                ('ktd', models.TextField(blank=True, null=True)),
                ('ktt', models.TextField(blank=True, null=True)),
                ('kontotype', models.TextField(blank=True, null=True)),
                ('ibn', models.TextField(blank=True, null=True)),
                ('esk', models.TextField(blank=True, null=True)),
                ('ejerstatuskode', models.TextField(blank=True, null=True)),
                ('indestaaende', models.TextField(blank=True, db_column='indestående', null=True)),
                ('renteindtaegt', models.TextField(blank=True, db_column='renteindtægt', null=True)),
                ('r75_dato', models.TextField(blank=True, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical imported r75 private pension',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalImportedKasMandtal',
            fields=[
                ('pt_census_guid', models.UUIDField(db_index=True)),
                ('cpr', models.TextField()),
                ('bank_reg_nr', models.TextField(blank=True, null=True)),
                ('bank_konto_nr', models.TextField(blank=True, null=True)),
                ('kommune_no', models.IntegerField(blank=True, null=True)),
                ('kommune', models.TextField(blank=True, null=True)),
                ('skatteaar', models.IntegerField()),
                ('navn', models.TextField(blank=True, null=True)),
                ('adresselinje1', models.TextField(blank=True, null=True)),
                ('adresselinje2', models.TextField(blank=True, null=True)),
                ('adresselinje3', models.TextField(blank=True, null=True)),
                ('adresselinje4', models.TextField(blank=True, null=True)),
                ('adresselinje5', models.TextField(blank=True, null=True)),
                ('fuld_adresse', models.TextField(blank=True, null=True)),
                ('cpr_dashed', models.TextField(blank=True, null=True)),
                ('skatteomfang', models.TextField(blank=True, null=True)),
                ('skattedage', models.IntegerField(blank=True, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical imported kas mandtal',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalImportedKasBeregningerX',
            fields=[
                ('pt_census_guid', models.UUIDField()),
                ('cpr', models.TextField()),
                ('bank_reg_nr', models.TextField(blank=True, null=True)),
                ('bank_konto_nr', models.TextField(blank=True, null=True)),
                ('kommune_no', models.IntegerField(blank=True, null=True)),
                ('kommune', models.TextField(blank=True, null=True)),
                ('skatteaar', models.IntegerField()),
                ('navn', models.TextField(blank=True, null=True)),
                ('adresselinje1', models.TextField(blank=True, null=True)),
                ('adresselinje2', models.TextField(blank=True, null=True)),
                ('adresselinje3', models.TextField(blank=True, null=True)),
                ('adresselinje4', models.TextField(blank=True, null=True)),
                ('adresselinje5', models.TextField(blank=True, null=True)),
                ('fuld_adresse', models.TextField(blank=True, null=True)),
                ('cpr_dashed', models.TextField(blank=True, null=True)),
                ('pension_crt_calc_guid', models.UUIDField(db_index=True)),
                ('pension_crt_lock_batch_guid', models.UUIDField(blank=True, null=True)),
                ('reg_date', models.DateTimeField()),
                ('is_locked', models.CharField(blank=True, max_length=1, null=True)),
                ('no', models.IntegerField(blank=True, null=True)),
                ('capital_return', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('sum_negative_capital_return', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('used_negative_capital_return', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('capital_return_base', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('capital_return_tax', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('crt_payment', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('police_payment', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('deficit_crt', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('surplus_crt_payment', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('surplus_police_payment', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('total_surplus', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('result_surplus_crt_payment', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('annotation', models.TextField(blank=True, null=True)),
                ('is_locking_allowed', models.CharField(blank=True, max_length=4, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical imported kas beregninger x',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
