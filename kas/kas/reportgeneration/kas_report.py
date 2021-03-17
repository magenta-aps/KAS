# -*- coding: utf-8 -*-

from django.core.files.base import ContentFile
from fpdf import FPDF

from kas.models import PolicyTaxYear, PersonTaxYear, TaxSlipGenerated


class TaxPDF(FPDF):

    std_document_width = 171
    left_margin = 17.0
    default_line_width = 0.2
    contact_info_table_cell = {'h': 5, 'w': 50}

    contact_info_table = {'x': 90.0, 'y': 27.0}

    address_field = {'w': 70, 'x': 17, 'y': 37}

    signature_table_cell = {'w': 57, 'h': 10}

    element_height_1 = 5
    element_height_2 = 60
    element_height_3 = 15
    element_height_4 = 30
    element_height_5 = 15

    sender_name = 'Skattestyrelsen'
    sender_address = 'Postboks 1605'
    sender_postnumber = '3900 Nuuk'

    document_header = {'gl': 'GL-OVERSKRIFT', 'dk': 'DK-OVERSKRIFT'}
    text2 = {'gl': '{}-imut nammineerluni nalunaarsuinermut ilanngussaq ', 'dk': 'Bilag til Selvangivelse for {}'}
    text3 = {'gl': 'Pigisanit pissarsiat ilaasa akileraaruserneqartarnerat pillugu ilanngussaq',
             'dk': 'Bilag vedrørende beskatning af visse kapitalafkast'}
    text4 = {'gl': 'Nassitsinissamut killissarititaq {}', 'dk': 'Indsendelsesfrist senest {}'}
    text5 = {'gl': 'Inuup-normua: ', 'dk': 'Personnummer: '}
    text6 = {'gl': 'Pigisanit pissarsiat akileraarutaat: ', 'dk': 'Kapitalafkastskat: '}
    text7 = {'gl': 'Akileraaruseriffik, oqarasuaat mail-ilu:\n'
                   'Akileraartarnermut Aqutsisoqarfik,\n'
                   'Postboks 1605, 3900 Nuuk. tlf. 346510, Email:tax@nanoq.gl',
             'dk': 'Kontakt: Skattestyrelsen,\n Postboks 1605, 3900 Nuuk. Tlf. 346510,\n Email:tax@nanoq.gl'}
    text8 = {'gl': 'Nittartagaq iserfissaq', 'dk': 'Tast selv internet'}
    text9 = {'gl': 'Kode isissutissaq', 'dk': 'Tast selv kode'}
    text10 = {'gl': 'Uunga ilitsersuut Pigisanit pissarsiat ilaasa akileraaruserneqartarnerat pillugu ilanngussaq',
              'dk': 'Vejledning til bilag vedrørende beskatning af visse kapitalafkast'}
    text11 = {'gl': "Pigisanit pissarsiat ilaasa akileraaruserneqartarnerat pillugu ilanngussaq paasissutissanik "
                    "naqeriikkanik imaqarpat paasis-sutissat naqeriikkat eqqortuunerat qulakkiissavat. "
                    "Inuunermik sillimmasiissutinit aamma soraarnerussutisiaqarnissamut aaqqissuussinernit, "
                    "aningaasarsianit akileraarutit pillugit Inatsisartut inatsisaanni § 39 a, imm. 1-imi 2-milu "
                    "piumasaqaatinik naammassinnittunit, tassungalu ilutigitillugu aammattaaq "
                    "soraarnerussutisiaqarnissamut aaqqissuussinerit il.il. "
                    "akileraaruserneqartarnerat pillugu danskit inatsisaanni § 20, imm. 4-mi pineqartunit "
                    "pissarsiaqarsimaguit, aamma/imaluunniit inuunermik sillimmasiissutinit aamma "
                    "soraarnerussutisiaqarnissamut aaqqissuussinernit, soraarnerussutisiaqarnissamut "
                    "aaqqissuussinerit il.il. akileraaruserneqartarnerat pillugu danskit inatsisaanni 53 A-mi "
                    "pineqartunit pissarsiaqarsimaguit, taakkulu paasissutissani naqeriikkani ilaanngippata, "
                    "taava Pigisanit pissarsiat ilaasa akileraaruserneqartarnerat pillugu ilanngussami "
                    "nalunaarutigissavatit. Pigisanit pissarsiat ilaasa akileraaruserneqartarnerat pillugu "
                    "ilanngussamut allannguutissaqaruit ilassutissaqaruilluunniit, "
                    "taava taanna immersoriarlugu atsioriarlugulu Akileraartarnermut Aqutsisoqarfimmut nassiutissavat, "
                    "imaluunniit allannguutit Akileraartarnermut Aqutsisoqarfiup www.aka.gl -ikkut nammineerluni "
                    "iserfissiaatigut imaluunniit www.sullissivik.gl -ikkut nalunaarutigissavatit kingusinnerpaamik "
                    "ulloq {}.",
              'dk': "Hvis der på Bilag vedrørende beskatning af visse kapitalafkast er fortrykte oplysninger, "
                    "skal De kontrollere om de fortrykte oplysninger er rigtige. Hvis De har haft kapitalafkast af "
                    "livsforsikringer og pensionsordninger, der opfylder betingelserne i § 39 a, "
                    "stk. 1 og 2, i landstingslov om indkomstskat, som samtidig er omfattet af § 20, stk. 4 i den "
                    "danske lov om beskatning af pensionsordninger m.v. og/eller kapitalafkast af livsforsikringer og "
                    "pensionsordninger omfattet af § 53 A i den danske lov om beskatning af pensionsordninger m.v., "
                    "udover de fortrykte oplysninger, skal De oplyse dette på Bilag vedrørende beskatning af "
                    "visse kapitalafkast. Har De ændringer eller tilføjelser, skal De derfor udfylde og underskrive "
                    "Bilag vedrørende beskatning af visse kapitalafkast og indsende den til Skattestyrelsen "
                    "eller indberette ændringerne via Skattestyrelsens tast-selv løsning på www.aka.gl eller "
                    "www.sullissivik.gl senest den {}."}
    text12 = {'gl': "Pigisanit pissarsiat ilaasa akileraaruserneqartarnerat pillugu ilanngussami naqeriikkat "
                    "isumaqataaffigigukkit qanoq iliuuseqaqqittariaqanngilatit.",
              'dk': "Hvis De er enig i indholdet af det fortrykte Bilag vedrørende beskatning af visse kapitalafkast, "
                    "behøver De ikke foretage Dem yderligere."}
    text13 = {'gl': "Pigisanit pissarsiat akileraarutaannik akiliigallarsimaguit aningaasallu akileraarutip "
                    "akilernissaanut atugassat soraarnerussutisiaqarnissamut aaqqissuussinermit tiguneqarsimappata, "
                    "taava pigisanit pissarsiat akileraarutaannut akiliutaavallaarsimajunnartut "
                    "soraarnerussutisiaqarnissamut aaqqissuussinermut, akileraarutip tiguneqarfianut ikineqassapput. "
                    "Aningaasat pigisanit pissarsiat akileraarutaasa akilernissaannut atugassat "
                    "soraarnerussutisiaqarnissamut aaqqissuussinermit tigusimanngikkukkit, taava pigisanit pissarsiat "
                    "akileraarutaannut akiliutaavallaarsimajunnartut aningaaserivimmi kontumut, "
                    "Nammineerluni nalunaarsuiffimmi S1 -imi illit nalunaarutigisimasannut ikineqassapput. "
                    "Pigisanit pissarsiat akileraarutaannik akiliigallarnissamut periarfissaqarputit ulloq "
                    "1. maj 2021 tikillugu.",
              'dk': "Hvis De har indbetalt forløbig kapitalafkastskat og beløbet til indbetaling af skatten er "
                    "hævet på pensionsordningen, indsættes eventuel overskydende kapitalafkastskat på den "
                    "pensionsordning, hvor skatten er hævet. Hvis De ikke har hævet beløbet til indbetaling af "
                    "kapitalafkastskatten på pensionsordningen, udbetales eventuel overskydende kapitalafkastskat "
                    "til den bankkonto De har oplyst på Selvangivelsen S1 . De har mulighed for at betale forløbig "
                    "kapitalafkastskat indtil {}."}
    text14 = {'gl': "Pigisanit pissarsiat akileraarutissaattut naatsorsugaq {} -imi "
                    "akiligassanngortussaq, piffissaagallartillugulu {} kingusinnerpaamik "
                    "akilerneqartussaq Akileraartarnermut Aqutsisoqarfiup akiligassiissutigissavaa.",
              'dk': "Skattestyrelsen opkræver beregnet kapitalafkastskat til betaling med forfald til betaling den "
                    "{} og sidste rettidige betalingsdag den {}."}
    text15 = {'gl': 'Pigisanit pissarsiat \nPBL (DK) § 53 A', 'dk': 'Kapitalafkast \nPBL (DK) § 53 A'}
    text16 = {'gl': 'Aningaasat\n koruuninngorlugit', 'dk': 'Beløb i kroner'}
    text17 = {'gl': 'Aningaasat\n koruuninngorlugit', 'dk': 'Beløb i kroner'}
    text18 = {'gl': 'Sammisap \nnormua', 'dk': 'Felt nr.\n '}
    text19 = {'gl': 'Pigisanit pissarsiat akileraarutaat', 'dk': 'Kapitalafkastskat'}
    text20 = {'gl': 'Pigisanit pissarsiat akileraarutaannik akiliigallarsimaguit aningaasartaat uani allassavatit. '
                    'Uppernarsaatissap ilanngullugu nassiunnissaa eqqaamajuk.',
              'dk': 'Har de betalt forløbig kapitalafkastskat angives beløbet her. '
                    'Husk at vedlægge dokumentation.'}
    text22 = {'gl': 'Pigisanit pissarsiat akileraarutaat soraarnerussutisiaqarnissamut '
                    'aaqqissuussinermit tiguneqarpat ?',
              'dk': 'Er kapitalafkastskatten hævet fra pensionsordning?\n  '}
    text23 = {'gl': 'Pigisanit pissarsiat akileraarutaat nunani allani akilersimasat',
              'dk': 'Betalt kapitalafkastskat i udlandet'}
    text24 = {'gl': 'Akileraarutissavit, pigisanit pissarsiat akileraarutaannik nunani allani akiliisimanerit '
                    'pissutigalugu appartinneqarnissaat kissaatigigukku akileraarutit akilerneqarsimasut '
                    'nulanaarneqassapput uppernarsaatissaallu nammineerluni nalunaarsuinermut ilanngullugit '
                    'nassiunneqassallutik.', 'dk': '  \n  \nAnmoder De om nedslag for betalt kapitalafkastskat i udlandet '
                                                   'angives den betalte skat og dokumentation vedlægges selvangivelsen'}
    text25 = {'gl': 'Aningaasat koruuninngorlugit', 'dk': 'Beløb i kroner'}
    text26 = {'gl': 'Paasissutissat Pigisanit pissarsiat ilaasa akileraaruserneqartarnerat pillugu Inatsisartut '
                    'inatsisaanni § 9-mi aalajangersakkat malillugit akisussaassuseqarluni nalunaarneqartussaapput.',
              'dk': 'Oplysninger afgives under ansvar i henhold til bestemmelserne i § 9 i '
                    'Inatsisartutlov om beskatning af visse kapitalafkast'}
    text27 = {'gl': 'Sumiiffik / Oqarasuaat', 'dk': 'Sted/tlf'}
    text28 = {'gl': 'Ulloq', 'dk': 'Dato'}
    text29 = {'gl': 'Atsiorneq', 'dk': 'Underskrift'}
    text30 = {'gl': 'GL INDSEND INFO',
              'dk': 'DK INDSEND INFO'}
    text_yes = {'gl': 'Aap', 'dk': 'Ja'}
    text_no = {'gl': 'Naamik', 'dk': 'Nej'}

    tax_year = '-'
    tax_return_date_limit = '-'
    person_number = '-'
    reciever_name = '-'
    reciever_address_l1 = '-'
    reciever_address_l2 = '-'
    reciever_address_l3 = '-'
    reciever_address_l4 = '-'
    reciever_address_l5 = '-'
    full_reciever_address = ''
    nemid_kode = '-'
    policys = ['']

    def set_parameters(self, tax_year='-', tax_return_date_limit='', request_pay='', pay_date='', person_number='-',
                       reciever_name='', reciever_address_l1='', reciever_address_l2='', reciever_address_l3='',
                       reciever_address_l4='', reciever_address_l5='', policys=['']):
        self.tax_year = tax_year
        self.tax_return_date_limit = tax_return_date_limit
        self.request_pay = request_pay
        self.pay_date = pay_date
        self.person_number = person_number
        self.reciever_name = reciever_name
        if reciever_address_l1 is not None:
            self.full_reciever_address += reciever_address_l1 + '\n'
        if reciever_address_l2 is not None:
            self.full_reciever_address += reciever_address_l2 + '\n'
        if reciever_address_l3 is not None:
            self.full_reciever_address += reciever_address_l3 + '\n'
        if reciever_address_l4 is not None:
            self.full_reciever_address += reciever_address_l4 + '\n'
        if reciever_address_l5 is not None:
            self.full_reciever_address += reciever_address_l5

        self.policys = policys
        self.default_line_width = self.line_width

    def header(self):
        self.yposition = 40
        self.set_xy(self.left_margin, self.yposition)

    def footer(self):
        self.set_font('arial', '', 11)
        self.set_xy(self.left_margin, self.h - 17)
        self.cell(h=5.0, align='C', w=30.0, txt=self.person_number, border=0)
        self.set_xy(self.left_margin, self.yposition)

    def print_tax_slip(self, language):
        self.add_page()

        self.set_font('arial', 'B', 15.0)
        self.set_xy(125.0, 8.0)
        self.cell(h=self.contact_info_table_cell.get('h'), align='R', w=75.0, txt=self.document_header.get(language),
                  border=0)

        self.set_font('arial', 'B', 12.0)
        self.set_xy(10.0, 8.0)
        self.cell(h=self.contact_info_table_cell.get('h'), align='L', w=75.0,
                  txt=self.text2.get(language).format(self.tax_year), border=0)

        self.set_font('arial', 'B', 9.0)
        self.set_xy(10.0, 17.0)
        self.cell(h=0, align='L', w=75.0, txt=self.text3[language], border=0)
        self.set_font('arial', '', 9.0)
        self.set_xy(10.0, 20.0)
        self.cell(h=0, align='L', w=75.0,
                  txt=self.text4[language].format(self.tax_return_date_limit), border=0)

        self.set_font('arial', '', 8.5)
        # Adressing reciever
        self.set_xy(self.address_field.get('x'), self.address_field.get('y'))
        self.multi_cell(self.address_field.get('w'), 3, border=0,
                        txt=self.reciever_name or ''+"\n"+self.full_reciever_address)

        # Adressing department
        self.set_xy(self.address_field.get('x'), self.address_field.get('y')+12)
        self.multi_cell(self.address_field.get('w'), 3, border=0,
                        txt=self.sender_name+"\n"+self.sender_address+"\n"+self.sender_postnumber)
        self.line(self.address_field.get('x'), self.address_field.get('y')+12,
                  self.address_field.get('x')+self.address_field.get('w')-30, self.address_field.get('y')+22)
        self.line(self.address_field.get('x'), self.address_field.get('y')+22,
                  self.address_field.get('x')+self.address_field.get('w')-30, self.address_field.get('y')+12)

        self.set_xy(self.contact_info_table.get('x'), self.contact_info_table.get('y'))
        self.cell(h=self.contact_info_table_cell.get('h'), align='L', w=self.contact_info_table_cell.get('w'),
                  txt=self.text5[language], border=1)
        self.set_xy(self.contact_info_table.get('x'),
                    self.contact_info_table.get('y')+self.contact_info_table_cell.get('h'))
        self.cell(h=self.contact_info_table_cell.get('h'), align='L', w=self.contact_info_table_cell.get('w'),
                  txt=self.text6[language], border=1)

        self.set_xy(self.contact_info_table.get('x')+self.contact_info_table_cell.get('w'),
                    self.contact_info_table.get('y'))
        self.cell(h=self.contact_info_table_cell.get('h'), align='L', w=self.contact_info_table_cell.get('w'),
                  txt=self.person_number, border=1)
        self.set_xy(self.contact_info_table.get('x')+self.contact_info_table_cell.get('w'),
                    self.contact_info_table.get('y')+self.contact_info_table_cell.get('h'))
        self.cell(h=self.contact_info_table_cell.get('h'), align='L', w=self.contact_info_table_cell.get('w'),
                  txt='15,3%', border=1)
        self.set_xy(self.contact_info_table.get('x'),
                    self.contact_info_table.get('y')+2*self.contact_info_table_cell.get('h'))
        self.multi_cell(2*self.contact_info_table_cell.get('w'), 5, self.text7[language], border=1, align='L')

        self.set_xy(self.contact_info_table.get('x'),
                    self.contact_info_table.get('y')+5*self.contact_info_table_cell.get('h'))
        self.cell(h=self.contact_info_table_cell.get('h'), align='L', w=self.contact_info_table_cell.get('w'),
                  txt=self.text8[language], border=1)

        self.set_xy(self.contact_info_table.get('x')+self.contact_info_table_cell.get('w'),
                    self.contact_info_table.get('y')+5*self.contact_info_table_cell.get('h'))
        self.cell(h=self.contact_info_table_cell.get('h'), align='L', w=self.contact_info_table_cell.get('w'),
                  txt='www.sullissivik.gl', border=1)

        self.yposition = 80
        self.set_xy(self.left_margin, self.yposition)

        self.cell(h=self.element_height_1, align='L', w=self.std_document_width,
                  txt=self.text10[language], border=1)
        self.yposition += self.element_height_1

        elementheight = self.element_height_2
        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(self.std_document_width, 5, self.text11[language].format(self.tax_return_date_limit), 1)
        self.yposition = self.get_y()

        elementheight = self.element_height_3
        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(self.std_document_width, 5, self.text12[language], 1)
        self.yposition = self.get_y()

        elementheight = self.element_height_4
        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(self.std_document_width, 5, self.text13[language].format(self.tax_return_date_limit), 1)
        self.yposition = self.get_y()

        elementheight = self.element_height_5
        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(self.std_document_width, 5, self.text14[language].format(self.request_pay, self.pay_date), 1)
        self.yposition = self.get_y()

        self.set_font('arial', '', 8.5)
        self.yposition += 15

        c1w = 45
        c2w = 20
        c3w = 20
        c4w = 20
        c5w = 48
        c6w = 17

        headerheight = 5
        rowheight = 10
        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(h=headerheight, align='L', w=c1w, txt=self.text15[language], border=1)
        self.set_xy(self.left_margin+c1w, self.yposition)
        self.multi_cell(h=headerheight, align='C', w=c2w, txt='Acc. \nnegativ', border=1)
        self.set_xy(self.left_margin+c1w+c2w, self.yposition)
        self.multi_cell(h=headerheight, align='C', w=c3w, txt='Fortrykt\n ', border=1)
        self.set_xy(self.left_margin+c1w+c2w+c3w, self.yposition)
        self.multi_cell(h=headerheight, align='C', w=c4w, txt='Selvangivet\n ', border=1)
        self.set_xy(self.left_margin+c1w+c2w+c3w+c4w, self.yposition)
        self.multi_cell(h=headerheight, align='L', w=c5w, txt='Hævet fra pension\n ', border=1)
        self.set_xy(self.left_margin+c1w+c2w+c3w+c4w+c5w, self.yposition)
        self.multi_cell(h=headerheight, align='C', w=c6w, txt=self.text18[language], border=1)
        self.yposition += 10

        for policy in self.policys:
            self.set_font('arial', '', 8.5)
            self.set_xy(self.left_margin, self.yposition)
            self.cell(h=rowheight, align='L', w=c1w, txt=policy.get('policy'), border=1)
            self.set_xy(self.left_margin+c1w, self.yposition)
            self.cell(h=rowheight, align='C', w=c2w, txt='', border=1)
            self.set_xy(self.left_margin+c1w+c2w, self.yposition)
            self.cell(h=rowheight, align='L', w=c3w, txt=policy.get('value', ''), border=1)
            self.set_xy(self.left_margin+c1w+c2w+c3w, self.yposition)
            self.cell(h=rowheight, align='L', w=c4w, txt='', border=1)
            self.set_xy(self.left_margin+c1w+c2w+c3w+c4w, self.yposition)
            self.cell(h=rowheight, align='L', w=c5w, txt='', border=1)
            self.set_xy(self.left_margin+c1w+c2w+c3w+c4w+c5w, self.yposition)
            self.cell(h=rowheight, align='C', w=c6w, txt='KAS-201', border=1)

            self.set_xy(125, self.yposition)
            self.cell(h=rowheight, align='L', w=20.0, txt=self.text_yes[language], border=0)
            self.set_xy(150, self.yposition)
            self.cell(h=rowheight, align='L', w=20.0, txt=self.text_no[language], border=0)
            self.rect(135.0, self.yposition+2, 5, 5)
            self.rect(162.0, self.yposition+2, 5, 5)
            self.yposition += rowheight

        self.set_xy(self.left_margin, self.yposition)
        self.cell(h=rowheight, align='L', w=c1w, txt='Total', border=1)
        self.set_xy(self.left_margin+c1w, self.yposition)
        self.cell(h=rowheight, align='C', w=c2w, txt='', border=1)
        self.set_xy(self.left_margin+c1w+c2w, self.yposition)
        self.cell(h=rowheight, align='L', w=c3w, txt='', border=1)
        self.set_xy(self.left_margin+c1w+c2w+c3w, self.yposition)
        self.cell(h=rowheight, align='L', w=c4w, txt='', border=1)
        self.set_xy(self.left_margin+c1w+c2w+c3w+c4w, self.yposition)
        self.cell(h=rowheight, align='L', w=c5w, txt='', border=1)
        self.set_xy(self.left_margin+c1w+c2w+c3w+c4w+c5w, self.yposition)
        self.cell(h=rowheight, align='C', w=c6w, txt='KAS-201', border=1)

        self.yposition += 80

        self.set_font('arial', '', 8.5)
        self.set_xy(self.left_margin, self.yposition)
        self.cell(h=elementheight, align='L', w=75.0, txt='', border=0)
        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(h=4, align='L', w=35.0, txt=self.text19[language], border=0)

        self.set_xy(50, self.yposition-5)
        self.multi_cell(h=5, align='L', w=60, txt=self.text20[language], border=0)

        self.set_xy(120.0, self.yposition-10)
        self.multi_cell(h=2, align='C', w=25.0, txt=self.text16[language], border=0)
        self.line(120, self.yposition+10, 150, self.yposition+10)
        self.set_xy(160.0, self.yposition)
        self.cell(h=elementheight, align='L', w=75.0, txt='KAS-205', border=0)
        self.yposition += elementheight

        self.yposition += 30

        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(h=4, align='L', w=35.0, txt=self.text23[language], border=0)

        self.set_xy(55, self.yposition-15)
        self.multi_cell(h=5, align='L', w=60, txt=self.text24[language], border=0)

        elementheight = 45
        self.set_xy(120.0, self.yposition-10)
        self.multi_cell(h=2, align='C', w=25.0, txt=self.text16[language], border=0)
        self.line(120, self.yposition+10, 150, self.yposition+10)
        self.set_line_width(1)
        self.set_xy(160.0, self.yposition)
        self.cell(h=elementheight-30, align='L', w=75.0, txt='KAS-208', border=0)
        self.yposition += elementheight

        elementheight = 30
        self.set_xy(self.left_margin, self.yposition)
        frametop = self.get_y()
        self.set_line_width(self.default_line_width)
        self.multi_cell(h=5, align='L', w=self.std_document_width, txt=self.text26[language], border=1)
        self.yposition = self.get_y()
        self.set_xy(self.left_margin, self.yposition)
        self.cell(h=self.signature_table_cell.get('h'), align='L', w=self.signature_table_cell.get('w'),
                  txt=self.text27[language], border=1)
        self.set_xy(self.left_margin+self.signature_table_cell.get('w'), self.yposition)
        self.cell(h=self.signature_table_cell.get('h'), align='L', w=self.signature_table_cell.get('w'),
                  txt=self.text28[language], border=1)
        self.set_xy(self.left_margin+self.signature_table_cell.get('w')*2, self.yposition)
        self.cell(h=self.signature_table_cell.get('h'), align='L', w=self.signature_table_cell.get('w'),
                  txt=self.text29[language], border=1)
        self.set_xy(self.left_margin, self.yposition+10)
        self.cell(h=self.signature_table_cell.get('h'), w=self.signature_table_cell.get('w'), border=1)
        self.set_xy(self.left_margin+self.signature_table_cell.get('w'), self.yposition+10)
        self.cell(h=self.signature_table_cell.get('h'), w=self.signature_table_cell.get('w'), border=1)
        self.set_xy(self.left_margin+self.signature_table_cell.get('w')*2, self.yposition+10)
        self.cell(h=self.signature_table_cell.get('h'), w=self.signature_table_cell.get('w'), border=1)
        self.set_line_width(1)
        framebottom = self.get_y()
        self.rect(self.left_margin, frametop, self.std_document_width, framebottom-frametop+10)
        self.set_line_width(self.default_line_width)
        self.yposition += elementheight

        self.yposition += 10

        self.set_font('arial', 'B', 13.0)
        self.set_xy(self.left_margin, self.yposition)
        self.cell(h=10, align='L', w=self.std_document_width, txt=self.text30[language], border=0)

    def write_tax_slip_to_disk(self, path):
        self.output(path, 'F')

    def perform_complete_write_of_one_person_tax_year(self, destination_path, person_tax_year):

        tax_year = person_tax_year.tax_year.year
        tax_return_date_limit = f'1. maj {(person_tax_year.tax_year.year+1)}'
        request_pay = f'1. september {(person_tax_year.tax_year.year+1)}'
        pay_date = f'20. september {(person_tax_year.tax_year.year+1)}'
        person_number = person_tax_year.person.cpr
        reciever_name = person_tax_year.person.name
        reciever_address_line_1 = person_tax_year.person.address_line_1
        reciever_address_line_2 = person_tax_year.person.address_line_2
        reciever_address_line_3 = person_tax_year.person.address_line_3
        reciever_address_line_4 = person_tax_year.person.address_line_4
        reciever_address_line_5 = person_tax_year.person.address_line_5

        policies = []

        list_of_policies = PolicyTaxYear.objects.filter(
            person_tax_year=person_tax_year
        )

        policy_file_name = f'{destination_path}Y_{tax_year}_{person_number}.pdf'

        for policy in list_of_policies:
            policies.append({'policy': policy.pension_company.name or ''+'-'+policy.policy_number})

        policies.append({'policy': ''})

        self.set_parameters(tax_year, tax_return_date_limit, request_pay, pay_date, person_number,
                            reciever_name, reciever_address_line_1, reciever_address_line_2,
                            reciever_address_line_3, reciever_address_line_4,
                            reciever_address_line_5, policies)
        self.print_tax_slip('gl')
        self.print_tax_slip('dk')
        self.write_tax_slip_to_disk(policy_file_name)

        ts = TaxSlipGenerated()
        ts.file.save(content=ContentFile(self.output(dest='S').encode('latin-1')), name=policy_file_name)
        person_tax_year.tax_slip = ts
        person_tax_year.save()

    def perform_complete_write_of_one_tax_year(self, destination_path, tax_year):

        list_of_person_tax_year = PersonTaxYear.objects.filter(
            tax_year__year=tax_year
        )

        for person_tax_year in list_of_person_tax_year:
            self.perform_complete_write_of_one_person_tax_year(destination_path=destination_path, person_tax_year=person_tax_year)
