

class Transaction(object):

    fieldspec = (
        ('leverandoer_ident', 4),
        ('trans_type', 2),
        ('time_stamp', 13),
        ('bruger_nummer', 4),
        ('omraad_nummer', 3),
        ('betal_art', 3),
        ('paalign_aar', 4),
        ('debitor_nummer', 10),
        ('sag_nummer', 2),
    )

    # List of default values
    leverandoer_ident = "KAS"
    time_stamp = None
    # TODO: This is not the correct value
    bruger_nummer = 1234
    omraad_nummer = None
    betal_art = 209
    paalign_aar = None
    debitor_nummer = None
    sag_nummer = '00'  # Hardcoded to 20 according to spec

    def __init__(self, **kwargs):
        for field_name, _ in self.fieldspec:
            if field_name in kwargs:
                setattr(self, field_name, str(kwargs[field_name]))

    def make_transaction(self, **kwargs):

        data = self.get_data()
        data.update(kwargs)

        data['debitor_nummer'] = data['cpr_nummer']
        data['person_nummer'] = data['cpr_nummer']

        fields = []

        for field_name, width in self.fieldspec:
            value = data[field_name]

            if value is None:
                raise ValueError("Value for %s cannot be None" % (field_name))

            value = str(value)

            if len(value) > width:
                raise ValueError(
                    "Value '%s' for field %s is wider than %d characters" % (
                        value,
                        field_name,
                        width
                    )
                )

            fields.append(value.rjust(width))

        # TODO: Change this to join on the empty string when development/debugging is done
        return '|'.join(fields)

    def get_data(self):
        data = {}

        for field_name, _ in self.fieldspec:
            data[field_name] = getattr(self, field_name)

        return data

    @classmethod
    def format_timestamp(cls, datetime):
        return '{:0%Y%m%d%H%M}'.format(datetime)

    @classmethod
    def format_date(cls, date):
        return '{:%Y%m%d}'.format(date)

    @classmethod
    def format_omraade_nummer(cls, date):
        return '{:%Y}'.format(date)[1:]

    @classmethod
    def format_amount(cls, amount):

        sign = '-' if amount < 0 else '+'

        return str(abs(amount)).rjust(10, '0') + sign

    def __str__(self):
        return str(self.get_data())


class FixWidthFieldLineTranactionType10(Transaction):
    fieldspec = Transaction.fieldspec + (
        ('person_nummer', 10),  # Comma is needed when only one value in tuple
    )

    person_nummer = None

    trans_type = '10'


class FixWidthFieldLineTranactionType24(Transaction):

    fieldspec = Transaction.fieldspec + (
        ('individ_type', 2),
        ('rate_nummer', 3),
        ('rate_beloeb', 11),
        ('belob_type', 1),
        ('rentefri_beloeb', 11),
        ('opkraev_kode', 1),
        ('opkraev_dato', 8),
        ('forfald_dato', 8),
        ('betal_dato', 8),
        ('rentefri_dato', 8),
        ('tekst_nummer', 3),
        ('rate_spec', 3),
        ('slet_mark', 1),
        ('faktura_no', 35),
        ('stiftelse_dato', 8),
        ('fra_periode', 8),
        ('til_periode', 8),
        ('aedring_aarsag_kode', 4),
        ('aedring_aarsag_tekst', 100),
        ('afstem_noegle', 35)
    )

    trans_type = '24'  # Hardcoded to 24 according to spec

    individ_type = '20'  # Hardcoded to 20 according to spec
    rate_nummer = '999'  # Hardcoded to 999 according to spec
    rate_beloeb = None
    belob_type = '1'  # Hardcoded to 1 according to spec
    rentefri_beloeb = '0000000000+'  # Hardcoded since the amount is in 'rate_beloeb'
    opkraev_kode = '1'  # Hardcoded to nettoopkraevning
    opkraev_dato = None
    forfald_dato = None
    betal_dato = None
    rentefri_dato = None
    tekst_nummer = '000'  # Hardcoded to 000 according to spec
    rate_spec = ''  # Hardcoded to <empty> according to spec
    slet_mark = ''  # Hardcoded to <empty> according to spec
    faktura_no = ''  # Hardcoded to <empty> according to spec
    stiftelse_dato = None
    fra_periode = None
    til_periode = None
    aedring_aarsag_kode = ''  # Hardcoded to <empty> according to spec
    aedring_aarsag_tekst = ''  # Hardcoded to <empty> according to spec
    afstem_noegle = None


class FixWidthFieldLineTranactionType26(Transaction):
    fieldspec = Transaction.fieldspec + (
        ('individ_type', 2),
        ('rate_nummer', 3),
        ('line_number', 3),
        ('rate_text', 60),
    )

    trans_type = 26

    individ_type = '20'  # Hardcoded to 20 according to spec
    rate_nummer = '999'  # Hardcoded to 999 according to spec
    line_number = "nul"  # Hardcoded to "nul" (yes, 3 charaters) according to spec
    rate_text = None


class TransactionWriter(object):

    transaction_10 = None
    transaction_24 = None
    transaction_26 = None
    transaction_list = ''

    def __init__(self, ref_timestamp, tax_year):

        time_stamp = Transaction.format_timestamp(ref_timestamp)
        omraad_nummer = Transaction.format_omraade_nummer(ref_timestamp)

        init_data = {
            'time_stamp': time_stamp,
            'omraad_nummer': omraad_nummer,
            'paalign_aar': tax_year,
            'rate_text': 'KAS %s' % (tax_year),

            # TODO: Fix all of these dates!
            'opkraev_dato': Transaction.format_date(ref_timestamp),
            'forfald_dato': Transaction.format_date(ref_timestamp),
            'betal_dato': Transaction.format_date(ref_timestamp),
            'rentefri_dato': Transaction.format_date(ref_timestamp),
            'stiftelse_dato': Transaction.format_date(ref_timestamp),
            'fra_periode': Transaction.format_date(ref_timestamp),
            'til_periode': Transaction.format_date(ref_timestamp),
        }

        self.transaction_10 = FixWidthFieldLineTranactionType10(**init_data)
        self.transaction_24 = FixWidthFieldLineTranactionType24(**init_data)
        self.transaction_26 = FixWidthFieldLineTranactionType26(**init_data)

    def make_transaction(self, cpr_nummer, rate_beloeb, afstem_noegle):
        data = {
            "cpr_nummer": cpr_nummer,
            "rate_beloeb": Transaction.format_amount(rate_beloeb),
            'afstem_noegle': afstem_noegle,
        }
        return '\r\n'.join([
            self.transaction_10.make_transaction(**data),
            self.transaction_24.make_transaction(**data),
            self.transaction_26.make_transaction(**data),
        ])


# afstem_noegle = '44edf2b0-9e2d-40fa-8087-cb37cfbdb66'  # SET PROPERTY HERE Skal vaere unik pr. dataleverandoer identifikation og pr. G19-transaktiontype og pr. kommune (hordcoded based on random uuid)
# cpr_nummer = '2507919858'  # TEST-CPR-NUMMER som brugt i eksempel fra dokumentation
# tilbagebetaling = 200

# # Construct the writer
# transaction_creator = TransactionCreator(ref_timestamp=datetime.now(), tax_year=2020)
# print(transaction_creator.make_transaction(cpr_nummer=cpr_nummer, rate_beloeb=tilbagebetaling, afstem_noegle=afstem_noegle))
