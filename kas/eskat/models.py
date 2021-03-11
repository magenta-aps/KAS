# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.forms.models import model_to_dict
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


class AbstractModels:

    # This is only here because we got it from the eSkat integration. It is not used as all
    # imports will use the KasBeregningerX view, which has the connection to CPR numbers we need.
    class KasBeregninger(models.Model):
        pt_census_guid = models.UUIDField(primary_key=True)
        pension_crt_calc_guid = models.UUIDField()
        pension_crt_lock_batch_guid = models.UUIDField(blank=True, null=True)
        reg_date = models.DateTimeField()
        is_locked = models.CharField(max_length=1, blank=True, null=True)
        no = models.IntegerField(blank=True, null=True)
        capital_return = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
        sum_negative_capital_return = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
        used_negative_capital_return = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
        capital_return_base = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
        capital_return_tax = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
        crt_payment = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
        police_payment = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
        deficit_crt = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
        surplus_crt_payment = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
        surplus_police_payment = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
        total_surplus = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
        result_surplus_crt_payment = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
        annotation = models.TextField(blank=True, null=True)
        is_locking_allowed = models.CharField(max_length=4, blank=True, null=True)

        class Meta:
            abstract = True

    class KasBeregningerX(models.Model):
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
        pension_crt_calc_guid = models.UUIDField(primary_key=True)
        pension_crt_lock_batch_guid = models.UUIDField(blank=True, null=True)
        reg_date = models.DateTimeField()
        is_locked = models.CharField(max_length=1, blank=True, null=True)
        no = models.IntegerField(blank=True, null=True)
        capital_return = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
        sum_negative_capital_return = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
        used_negative_capital_return = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
        capital_return_base = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
        capital_return_tax = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
        crt_payment = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
        police_payment = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
        deficit_crt = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
        surplus_crt_payment = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
        surplus_police_payment = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
        total_surplus = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
        result_surplus_crt_payment = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
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

    class R75PrivatePension(models.Model):
        pt_census_guid = models.UUIDField()
        tax_year = models.IntegerField()
        cpr = models.TextField()
        r75_ctl_sekvens_guid = models.UUIDField(primary_key=True)
        r75_ctl_indeks_guid = models.UUIDField()
        idx_nr = models.IntegerField()
        res = models.TextField(blank=True, null=True)
        pkt = models.TextField(blank=True, null=True)
        beloeb = models.TextField(blank=True, null=True)
        dato = models.TextField(blank=True, null=True)

        class Meta:
            abstract = True


class EskatModels:

    class KasBeregninger(AbstractModels.KasBeregninger):

        class Meta:
            managed = False  # Created from a view. Don't remove.
            db_table = 'kas_beregninger'

    class KasBeregningerX(AbstractModels.KasBeregningerX):

        class Meta:
            managed = False  # Created from a view. Don't remove.
            db_table = 'kas_beregninger_x'

    class KasMandtal(AbstractModels.KasMandtal):

        class Meta:
            managed = False  # Created from a view. Don't remove.
            db_table = 'kas_mandtal'

    class R75PrivatePension(AbstractModels.R75PrivatePension):

        class Meta:
            managed = False  # Created from a view. Don't remove.
            db_table = 'r75_private_pension'


class MockModels:

    class MockKasBeregningerX(AbstractModels.KasBeregningerX):
        pass

    class MockKasMandtal(AbstractModels.KasMandtal):
        pass

    class MockR75PrivatePension(AbstractModels.R75PrivatePension):
        pass


# Add methods that can be used to access correct source data models
# in both production and test/development.
def get_kas_beregninger_x_model():
    if settings.ENVIRONMENT != "production":
        return MockModels.MockKasBeregningerX
    else:
        return EskatModels.KasBeregningerX


def get_kas_mandtal_model():
    if settings.ENVIRONMENT != "production":
        return MockModels.MockKasMandtal
    else:
        return EskatModels.KasMandtal


def get_r75_private_pension_model():
    if settings.ENVIRONMENT != "production":
        return MockModels.MockR75PrivatePension
    else:
        return EskatModels.R75PrivatePension


class ImportedKasBeregningerX(AbstractModels.KasBeregningerX):

    history = HistoricalRecords()

    @classmethod
    def import_year(cls, year):
        qs = get_kas_beregninger_x_model().objects.filter(
            skatteaar=year
        )
        for x in qs:
            try:
                existing = cls.objects.get(pk=x.pk)
                if existing.reg_date != x.reg_date:
                    for k, v in model_to_dict(x).items():
                        setattr(existing, k, v)
                    existing._change_reason = "Updated by import"
                    existing.save()

            except cls.DoesNotExist:
                new_obj = cls(**model_to_dict(x))
                new_obj.change_reason = "Created by import"
                new_obj.save()


class ImportedKasMandtal(AbstractModels.KasMandtal):

    history = HistoricalRecords()

    @classmethod
    def import_year(cls, year, job=None, progress_factor=1, progress_start=0):
        qs = get_kas_mandtal_model().objects.filter(
            skatteaar=year
        )
        # In case we share progress with another function, we want to only fill part of the progress, e.g. up to 50%
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
                new_obj.change_reason = "Created by import"
                new_obj.save()
                created += 1
            if job is not None:
                job.set_progress_pct(progress_start + (i / count) * (100 * progress_factor))
        if job is not None:
            job.set_progress_pct(progress_start + (100 * progress_factor))
        return created, updated


class ImportedR75PrivatePension(AbstractModels.R75PrivatePension):

    history = HistoricalRecords()

    @classmethod
    def import_year(cls, year, job=None, progress_factor=1, progress_start=0):
        qs = get_r75_private_pension_model().objects.filter(
            tax_year=year
        )
        count = qs.count()
        created, updated = (0, 0)
        for i, x in enumerate(qs):
            try:
                existing = cls.objects.get(pk=x.pk)
                if existing.dato != x.dato:
                    for k, v in model_to_dict(x).items():
                        setattr(existing, k, v)
                    existing._change_reason = "Updated by import"
                    existing.save()
                    updated += 1

            except cls.DoesNotExist:
                new_obj = cls(**model_to_dict(x))
                new_obj.change_reason = "Created by import"
                new_obj.save()
                created += 1

            if job is not None:
                job.set_progress_pct(progress_start + (i / count) * (100 * progress_factor))
        if job is not None:
            job.set_progress_pct(progress_start + (100 * progress_factor))
        return created, updated
