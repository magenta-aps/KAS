# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models.functions import Length
from django.forms.models import model_to_dict
from django.utils.formats import date_format
from simple_history.models import HistoricalRecords

"""
There are four types of models in this module:

1) AbstractModels, containing the field definitions for all the other tables
2) EskatModels, models connecting to the real eSkat database
3) MockModels, models containing local mockup data for the eSkat database
4) Imported* models, containing data that has been imported from eSkat, using
   either the real eSkat models or the mockup models as a source.

The `get_*_model()` methods returns the correct eSkat source model for the given
environment: In production the real eSkat models will be returned and for all
other environments the mockup tables will be returned.

Unless dealing with import logic it should only be neccessary to use the `Imported*`
models.
"""


class AbstractKasBeregningerX(models.Model):
    pension_crt_calc_guid = models.UUIDField(primary_key=True)
    pt_census_guid = models.UUIDField()
    cpr = models.TextField()
    bank_reg_nr = models.TextField(blank=True, null=True)
    bank_konto_nr = models.TextField(blank=True, null=True)
    kommune_no = models.IntegerField(blank=True, null=True)
    kommune = models.TextField(blank=True, null=True)
    skatteaar = models.IntegerField()
    navn = models.TextField(blank=True, null=True)
    adresselinje1 = models.TextField(blank=True, null=True)
    adresselinje2 = models.TextField(blank=True, null=True)
    adresselinje3 = models.TextField(blank=True, null=True)
    adresselinje4 = models.TextField(blank=True, null=True)
    adresselinje5 = models.TextField(blank=True, null=True)
    fuld_adresse = models.TextField(blank=True, null=True)
    cpr_dashed = models.TextField(blank=True, null=True)
    pension_crt_lock_batch_guid = models.UUIDField(blank=True, null=True)
    reg_date = models.DateTimeField()
    is_locked = models.CharField(max_length=1, blank=True, null=True)
    no = models.IntegerField(blank=True, null=True)
    capital_return = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )
    sum_negative_capital_return = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )
    used_negative_capital_return = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )
    capital_return_base = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )
    capital_return_tax = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )
    crt_payment = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )
    police_payment = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )
    deficit_crt = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )
    surplus_crt_payment = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )
    surplus_police_payment = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )
    total_surplus = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )
    result_surplus_crt_payment = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )
    annotation = models.TextField(blank=True, null=True)
    is_locking_allowed = models.CharField(max_length=4, blank=True, null=True)

    class Meta:
        abstract = True


class KasBeregningerX(AbstractKasBeregningerX):
    # Kas beregninger i eskat.
    class Meta:
        managed = False
        db_table = "kas_beregninger_x"
        ordering = ["skatteaar", "cpr", "bank_reg_nr"]


class MockKasBeregningerX(AbstractKasBeregningerX):
    class Meta:
        ordering = ["skatteaar", "cpr"]


class ImportedKasBeregningerX(models.Model):
    pension_crt_calc_guid = models.UUIDField(primary_key=True)
    cpr = models.TextField()
    skatteaar = models.IntegerField()
    # Dette er det eneste felt der er relevant for 2018/2019 data
    capital_return_tax = models.DecimalField(
        max_digits=12, decimal_places=2, blank=False, null=False, default=0
    )
    person_tax_year = models.OneToOneField(
        "kas.PersonTaxYear", on_delete=models.CASCADE, null=True
    )
    history = HistoricalRecords()

    class Meta:
        indexes = [
            models.Index(fields=["cpr", "skatteaar"]),
        ]
        ordering = ["skatteaar", "cpr"]


def get_kas_beregninger_x_model():
    if settings.ENVIRONMENT in ("production", "staging"):
        return KasBeregningerX
    elif settings.ENVIRONMENT == "development":
        return MockKasBeregningerX


class AbstractModels:
    # This is only here because we got it from the eSkat integration. It is not
    # used as all imports will use the KasBeregningerX view, which has the
    # connection to CPR numbers we need.
    class KasBeregninger(models.Model):
        pt_census_guid = models.UUIDField(primary_key=True)
        pension_crt_calc_guid = models.UUIDField()
        pension_crt_lock_batch_guid = models.UUIDField(blank=True, null=True)
        reg_date = models.DateTimeField()
        is_locked = models.CharField(max_length=1, blank=True, null=True)
        no = models.IntegerField(blank=True, null=True)
        capital_return = models.DecimalField(
            max_digits=12, decimal_places=2, blank=True, null=True
        )
        sum_negative_capital_return = models.DecimalField(
            max_digits=12, decimal_places=2, blank=True, null=True
        )
        used_negative_capital_return = models.DecimalField(
            max_digits=12, decimal_places=2, blank=True, null=True
        )
        capital_return_base = models.DecimalField(
            max_digits=12, decimal_places=2, blank=True, null=True
        )
        capital_return_tax = models.DecimalField(
            max_digits=12, decimal_places=2, blank=True, null=True
        )
        crt_payment = models.DecimalField(
            max_digits=12, decimal_places=2, blank=True, null=True
        )
        police_payment = models.DecimalField(
            max_digits=12, decimal_places=2, blank=True, null=True
        )
        deficit_crt = models.DecimalField(
            max_digits=12, decimal_places=2, blank=True, null=True
        )
        surplus_crt_payment = models.DecimalField(
            max_digits=12, decimal_places=2, blank=True, null=True
        )
        surplus_police_payment = models.DecimalField(
            max_digits=12, decimal_places=2, blank=True, null=True
        )
        total_surplus = models.DecimalField(
            max_digits=12, decimal_places=2, blank=True, null=True
        )
        result_surplus_crt_payment = models.DecimalField(
            max_digits=12, decimal_places=2, blank=True, null=True
        )
        annotation = models.TextField(blank=True, null=True)
        is_locking_allowed = models.CharField(max_length=4, blank=True, null=True)

        class Meta:
            abstract = True

    class KasMandtal(models.Model):
        pt_census_guid = models.UUIDField(primary_key=True)
        cpr = models.TextField()
        bank_reg_nr = models.TextField(blank=True, null=True)
        bank_konto_nr = models.TextField(blank=True, null=True)
        kommune_no = models.IntegerField(blank=True, null=True)
        kommune = models.TextField(blank=True, null=True)
        skatteaar = models.IntegerField()
        navn = models.TextField(blank=True, null=True)
        adresselinje1 = models.TextField(blank=True, null=True)
        adresselinje2 = models.TextField(blank=True, null=True)
        adresselinje3 = models.TextField(blank=True, null=True)
        adresselinje4 = models.TextField(blank=True, null=True)
        adresselinje5 = models.TextField(blank=True, null=True)
        fuld_adresse = models.TextField(blank=True, null=True)
        cpr_dashed = models.TextField(blank=True, null=True)
        skatteomfang = models.TextField(blank=True, null=True)
        skattedage = models.IntegerField(blank=True, null=True)

        class Meta:
            abstract = True

        def __str__(self):
            return "%s - %s" % (self.navn, self.skatteaar)

    # R75Idx4500230: Data from index 4500230 in R75. Contains policies and
    # their return as reported by pension companies.
    class R75Idx4500230(models.Model):
        pt_census_guid = models.UUIDField()
        tax_year = models.IntegerField()
        cpr = models.TextField()
        r75_ctl_sekvens_guid = models.UUIDField(primary_key=True)
        r75_ctl_indeks_guid = models.UUIDField()
        idx_nr = models.IntegerField()
        res = models.TextField(blank=True, null=True)
        ktd = models.TextField(blank=True, null=True)
        ktt = models.TextField(blank=True, null=True)
        kontotype = models.TextField(blank=True, null=True)
        ibn = models.TextField(blank=True, null=True)
        esk = models.TextField(blank=True, null=True)
        ejerstatuskode = models.TextField(blank=True, null=True)
        indestaaende = models.TextField(blank=True, null=True, db_column="indestående")
        renteindtaegt = models.TextField(
            blank=True, null=True, db_column="renteindtægt"
        )
        r75_dato = models.TextField(blank=True, null=True)

        class Meta:
            abstract = True

        def __str__(self):
            return "%s - %s/%s/%s - %s kr" % (
                self.cpr,
                self.tax_year,
                self.ktd,
                self.res,
                self.renteindtaegt,
            )


class EskatModels:
    class KasBeregninger(AbstractModels.KasBeregninger):
        class Meta:
            managed = False  # Created from a view. Don't remove.
            db_table = "kas_beregninger"

    class KasMandtal(AbstractModels.KasMandtal):
        class Meta:
            managed = False  # Created from a view. Don't remove.
            db_table = "kas_mandtal"

    # R75Idx4500230: Data from index 4500230 in R75. Contains policies and
    # their return as reported by pension companies.
    class R75Idx4500230(AbstractModels.R75Idx4500230):
        class Meta:
            managed = False  # Created from a view. Don't remove.
            db_table = "r75_idx_4500230"

    class R75SpreadsheetImport(AbstractModels.R75Idx4500230):
        class Meta:
            ordering = ["tax_year", "cpr"]

        file = models.ForeignKey(
            "R75SpreadsheetFile",
            on_delete=models.SET_NULL,
            null=True,
        )
        company_pay_override = models.BooleanField(default=False)


class MockModels:
    class MockKasMandtal(AbstractModels.KasMandtal):
        class Meta:
            ordering = ["skatteaar", "cpr"]

    # R75Idx4500230: Data from index 4500230 in R75. Contains policies and
    # their return as reported by pension companies.
    class MockR75Idx4500230(AbstractModels.R75Idx4500230):
        class Meta:
            ordering = ["tax_year", "cpr"]


# Add methods that can be used to access correct source data models
# in both production and test/development.
def get_kas_mandtal_model():
    if settings.ENVIRONMENT in ("production", "staging"):
        return EskatModels.KasMandtal
    elif settings.ENVIRONMENT == "development":
        return MockModels.MockKasMandtal


def get_r75_private_pension_model():
    if settings.ENVIRONMENT in ("production", "staging"):
        return EskatModels.R75Idx4500230
    elif settings.ENVIRONMENT == "development":
        return MockModels.MockR75Idx4500230


class ImportedKasMandtal(AbstractModels.KasMandtal):
    history = HistoricalRecords()

    class Meta:
        ordering = ["skatteaar", "cpr"]

    @classmethod
    def import_year(
        cls,
        year,
        job=None,
        progress_factor=1,
        progress_start=0,
        source_model=None,
        cpr_limit=None,
    ):
        if source_model is None:
            source_model = get_kas_mandtal_model()

        qs = source_model.objects.filter(skatteaar=year)

        if cpr_limit is not None:
            qs = qs.filter(cpr=cpr_limit)

        # In case we share progress with another function, we want to only
        # fill part of the progress, e.g. up to 50%
        count = qs.count()
        created, updated = (0, 0)

        for i, x in enumerate(qs.iterator()):
            try:
                existing = cls.objects.get(pk=x.pk)
                # No timestamp field to check here, so compare dicts

                existing_dict = model_to_dict(existing)
                new_dict = model_to_dict(x)
                if existing_dict != new_dict:
                    for k, v in new_dict.items():
                        setattr(existing, k, v)
                    existing._change_reason = "Updated by import"
                    existing.save()
                    updated += 1

            except cls.DoesNotExist:
                new_obj = cls(**model_to_dict(x))
                new_obj._change_reason = "Created by import"
                new_obj.save()
                created += 1

            if job is not None and i % 1000 == 0:
                progress = progress_start + (i / count) * (100 * progress_factor)
                job.set_progress_pct(progress)

        if job is not None:
            job.set_progress_pct(progress_start + (100 * progress_factor))

        # When an ImportedKasMandtal exists that does not have a corresponding
        # source item, the source has been deleted from their database, and
        # we must set our object to zero
        orphan_qs = ImportedKasMandtal.objects.filter(skatteaar=year)
        if cpr_limit is not None:
            orphan_qs = orphan_qs.filter(cpr=cpr_limit)
        orphan_qs = orphan_qs.exclude(
            pk__in=list(
                # We could use qs.values_list("pk", flat=True) here, but if
                # qs and orphan_qs are not subject to the same filtering
                # (e.g. qs is filtered more than orphan_qs) we risk finding
                # too many objects in orphan_qs and thus nuking the
                # ImportedKasMandtal table. Better to be safe.
                source_model.objects.filter(skatteaar=year).values_list("pk", flat=True)
            )
        )
        cleared = orphan_qs.update(skattedage=0, skatteomfang="ikke fuld skattepligtig")

        return created, updated, cleared


class ImportedR75PrivatePension(AbstractModels.R75Idx4500230):
    class Meta:
        ordering = ["tax_year", "cpr"]

    history = HistoricalRecords()

    company_pay_override = models.BooleanField(default=False)

    @classmethod
    def import_year(
        cls, year, job=None, progress_factor=1, progress_start=0, source_model=None
    ):
        if source_model is None:
            source_model = get_r75_private_pension_model()

        qs = source_model.objects.filter(tax_year=year)
        qs = qs.annotate(res_length=Length("res")).filter(res_length__gt=4)
        count = qs.count()
        created, updated = (0, 0)

        for i, x in enumerate(qs.iterator()):
            # Get dict from model instance x, but only fields
            # we have in our current model.
            modelfield_names = {field.name for field in cls._meta.get_fields()}
            data = {k: v for k, v in model_to_dict(x).items() if k in modelfield_names}

            try:
                existing = cls.objects.get(pk=x.pk)
                if existing.r75_dato != x.r75_dato:
                    for k, v in data.items():
                        setattr(existing, k, v)
                    existing._change_reason = "Updated by import"
                    existing.save()
                    updated += 1

            except cls.DoesNotExist:
                new_obj = cls(**data)
                new_obj._change_reason = "Created by import"
                new_obj.save()
                created += 1

            if job is not None and i % 100 == 0:
                progress = progress_start + (i / count) * (100 * progress_factor)
                job.set_progress_pct(progress)

        if job is not None:
            job.set_progress_pct(progress_start + (100 * progress_factor))

        return created, updated


def r75_spreadsheet_file_path(instance, filename):
    return f"r75_spreadsheets/{instance.uploaded_at.year}/{filename}.xlsx"


class R75SpreadsheetFile(models.Model):
    class Meta:
        ordering = ["uploaded_at"]

    uploaded_by = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(
        upload_to=r75_spreadsheet_file_path,
        validators=[FileExtensionValidator(allowed_extensions=["xlsx"])],
    )

    def __str__(self):
        return "R75 regneark uploadet {date} af {by}".format(
            date=date_format(self.uploaded_at, "SHORT_DATETIME_FORMAT"),
            by=self.uploaded_by,
        )
