from datetime import datetime


class Transaction(object):

    leverandoer_ident = ''  # Common property on transaction 10 and 24
    time_stamp = ''
    bruger_nummer = ''
    omraad_nummer = ''
    betal_art = ''
    paalign_aar = ''
    debitor_nummer = ''
    person_nummer = ''
    sag_nummer = '00'  # Hardcoded to 20 according to spec

    def __init__(self, leverandoer_ident, time_stamp, bruger_nummer, omraad_nummer, betal_art, paalign_aar):
        self.leverandoer_ident = leverandoer_ident
        self.time_stamp = time_stamp
        self.bruger_nummer = bruger_nummer
        self.omraad_nummer = omraad_nummer
        self.betal_art = betal_art
        self.paalign_aar = paalign_aar

    def make_transaction(self, cpr_nummer):
        self.debitor_nummer = cpr_nummer
        self.person_nummer = cpr_nummer  # debitor_nummer and person_nummer gets the same value in transaction 10

    def __str__(self):
        return ''.join([getattr(self, field_name).ljust(width)
                        for field_name, width in self.transaktion])


class FixWidthFieldLineTranactionType10(Transaction):
    transaktion10 = (('leverandoer_ident', 4),
                     ('trans_type', 2),
                     ('time_stamp', 13),
                     ('bruger_nummer', 4),
                     ('omraad_nummer', 3),
                     ('betal_art', 3),
                     ('paalign_aar', 4),
                     ('debitor_nummer', 10),
                     ('sag_nummer', 2),
                     ('person_nummer', 10))

    trans_type = '10'

    def __init__(self, *args, **kw):
        Transaction.__init__(self, *args, **kw)

    def make_transaction(self, cpr_nummer):
        super().make_transaction(cpr_nummer=cpr_nummer)

    def __str__(self):
        return ''.join([getattr(self, field_name).ljust(width)
                        for field_name, width in self.transaktion10])

    def get_transaction(self):
        return ''.join([getattr(self, field_name).ljust(width)
                        for field_name, width in self.transaktion10])


class FixWidthFieldLineTranactionType24(Transaction):

    transaktion24 = (('leverandoer_ident', 4),
                     ('trans_type', 2),
                     ('time_stamp', 13),
                     ('bruger_nummer', 4),
                     ('omraad_nummer', 3),
                     ('betal_art', 3),
                     ('paalign_aar', 4),
                     ('debitor_nummer', 10),
                     ('sag_nummer', 2),
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
                     ('afstem_noegle', 35))

    individ_type = '20'  # Hardcoded to 20 according to spec
    trans_type = '24'  # Hardcoded to 24 according to spec
    rate_nummer = '999'  # Hardcoded to 999 according to spec
    belob_type = '1'  # Hardcoded to 1 according to spec
    rate_beloeb = None
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
    afstem_noegle = ''

    def __init__(self, betalingsdatoer, afstem_noegle, *args, **kw):
        Transaction.__init__(self, *args, **kw)
        self.opkraev_dato = betalingsdatoer
        self.forfald_dato = betalingsdatoer
        self.betal_dato = betalingsdatoer
        self.rentefri_dato = betalingsdatoer
        self.stiftelse_dato = betalingsdatoer
        self.fra_periode = betalingsdatoer
        self.til_periode = betalingsdatoer
        self.afstem_noegle = afstem_noegle

    def make_transaction(self, cpr_nummer, rate_beloeb):
        super().make_transaction(cpr_nummer=cpr_nummer)
        self.rate_beloeb = str(abs(rate_beloeb)).rjust(10, '0') + ('-' if rate_beloeb < 0 else '+')

    def __str__(self):
        return ''.join([getattr(self, field_name).rjust(width)
                        for field_name, width in self.transaktion24])

    def get_transaction(self):
        return ''.join([getattr(self, field_name).rjust(width)
                        for field_name, width in self.transaktion24])


class TransactionCreator(object):

    leverandoer_ident = '4733'  # SET PROPERTY HERE
    trans_type = 'trans_type'
    time_stamp = 'time_stamp'
    bruger_nummer = '4142'  # SET PROPERTY HERE
    omraad_nummer = None
    betal_art = '999'  # SET PROPERTY HERE
    afstem_noegle = '44edf2b0-9e2d-40fa-8087-cb37cfbdb66'  # SET PROPERTY HERE Skal vaere unik pr. dataleverandoer identifikation og pr. G19-transaktiontype og pr. kommune (hordcoded based on random uuid)
    paalign_aar = None
    individ_type = 'individ_type'
    person_nummer = 'person_nummer'
    other = 'other'
    transaction_10 = None
    transaction_24 = None
    transaction_list = ''

    def set_parameters(self, leverandoer_ident=''):
        self.leverandoer_ident = leverandoer_ident

    def __init__(self, omraad_nummer='', time_stamp='', paalign_aar='', debitor_nummer='', betalingsdatoer=''):
        self.omraad_nummer = omraad_nummer
        self.time_stamp = time_stamp
        self.paalign_aar = paalign_aar
        self.debitor_nummer = debitor_nummer
        self.transaction_10 = FixWidthFieldLineTranactionType10(leverandoer_ident=self.leverandoer_ident, time_stamp=self.time_stamp,
                                                                bruger_nummer=self.bruger_nummer, omraad_nummer=self.omraad_nummer,
                                                                betal_art=self.betal_art, paalign_aar=self.paalign_aar)

        self.transaction_24 = FixWidthFieldLineTranactionType24(leverandoer_ident=self.leverandoer_ident, time_stamp=self.time_stamp,
                                                                bruger_nummer=self.bruger_nummer, omraad_nummer=self.omraad_nummer,
                                                                betal_art=self.betal_art, paalign_aar=self.paalign_aar, betalingsdatoer=betalingsdatoer, afstem_noegle=self.afstem_noegle)

    def make_transaction(self, cpr_nummer, rate_beloeb):
        self.transaction_10.make_transaction(cpr_nummer=cpr_nummer)
        self.transaction_24.make_transaction(cpr_nummer=cpr_nummer, rate_beloeb=rate_beloeb)
        persontransaction = str('\n'.join([str(self.transaction_10.get_transaction()), str(self.transaction_24.get_transaction())]))
        self.transaction_list += persontransaction + '\n'

    def __str__(self):
        return '\n'.join([str(self.transaction_10), str(self.transaction_24)])

    def get_transaction(self):
        return self.transaction_list


# BELOW IS THE CALLING
omraad_nummer = '021'
# current date and time
now = datetime.now()
timestamp = '{:0%Y%m%d%H%M}'.format(now)
betalingsdatoer = '{:%Y%m%d}'.format(now)
ligningsaar = '2020'
cpr_nummer = '2507919858'  # TEST-CPR-NUMMER som brugt i eksempel fra dokumentation

tilbagebetaling = 200


# Construct the writer
transaction_creator = TransactionCreator(omraad_nummer=omraad_nummer, time_stamp=timestamp, paalign_aar=ligningsaar, betalingsdatoer=betalingsdatoer)
transaction_creator.make_transaction(cpr_nummer=cpr_nummer, rate_beloeb=tilbagebetaling)
transaction_creator.make_transaction(cpr_nummer=cpr_nummer, rate_beloeb=tilbagebetaling)
transaction_creator.make_transaction(cpr_nummer=cpr_nummer, rate_beloeb=tilbagebetaling)

transactionfile = transaction_creator.get_transaction()

print(transactionfile)
