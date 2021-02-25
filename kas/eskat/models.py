from django.db import models
from django.conf import settings


class AbstractModels:

    class KasBeregninger(models.Model):
        pt_census_guid = models.TextField(primary_key=True)  # This field type is a guess.
        pension_crt_calc_guid = models.TextField()  # This field type is a guess.
        pension_crt_lock_batch_guid = models.TextField(blank=True, null=True)  # This field type is a guess.
        reg_date = models.TextField()  # This field type is a guess.
        is_locked = models.CharField(max_length=1, blank=True, null=True)
        no = models.IntegerField(blank=True, null=True)
        capital_return = models.FloatField(blank=True, null=True)
        sum_negative_capital_return = models.FloatField(blank=True, null=True)
        used_negative_capital_return = models.FloatField(blank=True, null=True)
        capital_return_base = models.FloatField(blank=True, null=True)
        capital_return_tax = models.FloatField(blank=True, null=True)
        crt_payment = models.FloatField(blank=True, null=True)
        police_payment = models.FloatField(blank=True, null=True)
        deficit_crt = models.FloatField(blank=True, null=True)
        surplus_crt_payment = models.FloatField(blank=True, null=True)
        surplus_police_payment = models.FloatField(blank=True, null=True)
        total_surplus = models.FloatField(blank=True, null=True)
        result_surplus_crt_payment = models.FloatField(blank=True, null=True)
        annotation = models.TextField(blank=True, null=True)  # This field type is a guess.
        is_locking_allowed = models.TextField(blank=True, null=True)  # This field type is a guess.

        class Meta:
            abstract = True

    class KasBeregningerX(models.Model):
        pt_census_guid = models.TextField(primary_key=True)  # This field type is a guess.
        cpr = models.TextField()  # This field type is a guess.
        bank_reg_nr = models.TextField(blank=True, null=True)  # This field type is a guess.
        bank_konto_nr = models.TextField(blank=True, null=True)  # This field type is a guess.
        kommune_no = models.FloatField(blank=True, null=True)
        kommune = models.TextField(blank=True, null=True)  # This field type is a guess.
        skatteaar = models.FloatField()
        navn = models.TextField(blank=True, null=True)  # This field type is a guess.
        adresselinje1 = models.TextField(blank=True, null=True)  # This field type is a guess.
        adresselinje2 = models.TextField(blank=True, null=True)  # This field type is a guess.
        adresselinje3 = models.TextField(blank=True, null=True)  # This field type is a guess.
        adresselinje4 = models.TextField(blank=True, null=True)  # This field type is a guess.
        adresselinje5 = models.TextField(blank=True, null=True)  # This field type is a guess.
        fuld_adresse = models.TextField(blank=True, null=True)  # This field type is a guess.
        cpr_dashed = models.TextField(blank=True, null=True)  # This field type is a guess.
        pension_crt_calc_guid = models.TextField()  # This field type is a guess.
        pension_crt_lock_batch_guid = models.TextField(blank=True, null=True)  # This field type is a guess.
        reg_date = models.TextField()  # This field type is a guess.
        is_locked = models.CharField(max_length=1, blank=True, null=True)
        no = models.IntegerField(blank=True, null=True)
        capital_return = models.FloatField(blank=True, null=True)
        sum_negative_capital_return = models.FloatField(blank=True, null=True)
        used_negative_capital_return = models.FloatField(blank=True, null=True)
        capital_return_base = models.FloatField(blank=True, null=True)
        capital_return_tax = models.FloatField(blank=True, null=True)
        crt_payment = models.FloatField(blank=True, null=True)
        police_payment = models.FloatField(blank=True, null=True)
        deficit_crt = models.FloatField(blank=True, null=True)
        surplus_crt_payment = models.FloatField(blank=True, null=True)
        surplus_police_payment = models.FloatField(blank=True, null=True)
        total_surplus = models.FloatField(blank=True, null=True)
        result_surplus_crt_payment = models.FloatField(blank=True, null=True)
        annotation = models.TextField(blank=True, null=True)  # This field type is a guess.
        is_locking_allowed = models.TextField(blank=True, null=True)  # This field type is a guess.

        class Meta:
            abstract = True

    class KasMandtal(models.Model):
        pt_census_guid = models.TextField(primary_key=True)  # This field type is a guess.
        cpr = models.TextField()  # This field type is a guess.
        bank_reg_nr = models.TextField(blank=True, null=True)  # This field type is a guess.
        bank_konto_nr = models.TextField(blank=True, null=True)  # This field type is a guess.
        kommune_no = models.FloatField(blank=True, null=True)
        kommune = models.TextField(blank=True, null=True)  # This field type is a guess.
        skatteaar = models.FloatField()
        navn = models.TextField(blank=True, null=True)  # This field type is a guess.
        adresselinje1 = models.TextField(blank=True, null=True)  # This field type is a guess.
        adresselinje2 = models.TextField(blank=True, null=True)  # This field type is a guess.
        adresselinje3 = models.TextField(blank=True, null=True)  # This field type is a guess.
        adresselinje4 = models.TextField(blank=True, null=True)  # This field type is a guess.
        adresselinje5 = models.TextField(blank=True, null=True)  # This field type is a guess.
        fuld_adresse = models.TextField(blank=True, null=True)  # This field type is a guess.
        cpr_dashed = models.TextField(blank=True, null=True)  # This field type is a guess.

        class Meta:
            abstract = True

    class R75PrivatePension(models.Model):
        pt_census_guid = models.TextField(primary_key=True)  # This field type is a guess.
        tax_year = models.FloatField()
        cpr = models.TextField()  # This field type is a guess.
        r75_ctl_sekvens_guid = models.TextField()  # This field type is a guess.
        r75_ctl_indeks_guid = models.TextField()  # This field type is a guess.
        idx_nr = models.IntegerField()
        res = models.TextField(blank=True, null=True)  # This field type is a guess.
        pkt = models.TextField(blank=True, null=True)  # This field type is a guess.
        beloeb = models.TextField(blank=True, null=True)  # This field type is a guess.
        dato = models.TextField(blank=True, null=True)  # This field type is a guess.

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

    class MockKasBeregninger(AbstractModels.KasBeregninger):
        pass

    class MockKasBeregningerX(AbstractModels.KasBeregningerX):
        pass

    class MockKasMandtal(AbstractModels.KasMandtal):
        pass

    class MockR75PrivatePension(AbstractModels.R75PrivatePension):
        pass


if settings.ENVIRONMENT == "production":
    KasBeregninger = EskatModels.KasBeregninger
    KasBeregningerX = EskatModels.KasBeregningerX
    KasMandtal = EskatModels.KasMandtal
    R75PrivatePension = EskatModels.R75PrivatePension
else:
    KasBeregninger = MockModels.MockKasBeregninger
    KasBeregningerX = MockModels.MockKasBeregningerX
    MockKasMandtal = MockModels.MockKasMandtal
    MockR75PrivatePension = MockModels.MockR75PrivatePension
