# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.forms.models import model_to_dict
from simple_history.models import HistoricalRecords


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


# Add aliases that can be used to access data both in produktion and
# test/development.
if settings.ENVIRONMENT == "production":

    KasBeregningerX = EskatModels.KasBeregningerX
    KasMandtal = EskatModels.KasMandtal
    R75PrivatePension = EskatModels.R75PrivatePension
else:
    KasBeregningerX = MockModels.MockKasBeregningerX
    KasMandtal = MockModels.MockKasMandtal
    R75PrivatePension = MockModels.MockR75PrivatePension


class ImportedKasBeregningerX(AbstractModels.KasBeregningerX):

    history = HistoricalRecords()

    @classmethod
    def import_year(cls, year):
        qs = KasBeregningerX.objects.filter(skatteaar=year)
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
    def import_year(cls, year):
        qs = KasMandtal.objects.filter(skatteaar=year)
        for x in qs:
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

            except cls.DoesNotExist:
                new_obj = cls(**model_to_dict(x))
                new_obj.change_reason = "Created by import"
                new_obj.save()


class ImportedR75PrivatePension(AbstractModels.R75PrivatePension):

    history = HistoricalRecords()

    @classmethod
    def import_year(cls, year):
        qs = R75PrivatePension.objects.filter(tax_year=year)
        for x in qs:
            try:
                existing = cls.objects.get(pk=x.pk)
                if existing.dato != x.dato:
                    for k, v in model_to_dict(x).items():
                        setattr(existing, k, v)
                    existing._change_reason = "Updated by import"
                    existing.save()

            except cls.DoesNotExist:
                new_obj = cls(**model_to_dict(x))
                new_obj.change_reason = "Created by import"
                new_obj.save()
