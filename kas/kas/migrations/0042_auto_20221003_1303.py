# Generated by Django 3.2.12 on 2022-10-03 11:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("kas", "0041_alter_finalsettlement_pseudo_amount"),
    ]

    operations = [
        migrations.AddField(
            model_name="previousyearnegativepayout",
            name="protected_against_recalculations",
            field=models.BooleanField(
                default=False, verbose_name="Beskyt mod genberegning"
            ),
        ),
        migrations.CreateModel(
            name="HistoricalPreviousYearNegativePayout",
            fields=[
                (
                    "id",
                    models.IntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                ("history_change_reason", models.TextField(null=True)),
                (
                    "transferred_negative_payout",
                    models.BigIntegerField(
                        blank=True, default=0, verbose_name="Overført negativt afkast"
                    ),
                ),
                (
                    "protected_against_recalculations",
                    models.BooleanField(
                        default=False, verbose_name="Beskyt mod genberegning"
                    ),
                ),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField()),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                        max_length=1,
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "used_for",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="kas.policytaxyear",
                    ),
                ),
                (
                    "used_from",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="kas.policytaxyear",
                    ),
                ),
            ],
            options={
                "verbose_name": "historical previous year negative payout",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": "history_date",
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.AlterField(
            model_name="historicalpolicytaxyear",
            name="preliminary_paid_amount",
            field=models.BigIntegerField(
                blank=True,
                default=0,
                null=True,
                validators=[django.core.validators.MinValueValidator(limit_value=0)],
                verbose_name="Foreløbigt betalt kapitalafkast",
            ),
        ),
        migrations.AlterField(
            model_name="policytaxyear",
            name="preliminary_paid_amount",
            field=models.BigIntegerField(
                blank=True,
                default=0,
                null=True,
                validators=[django.core.validators.MinValueValidator(limit_value=0)],
                verbose_name="Foreløbigt betalt kapitalafkast",
            ),
        ),
    ]
