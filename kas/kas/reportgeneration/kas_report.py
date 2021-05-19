# -*- coding: utf-8 -*-

import math

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

    document_header = {'gl': '', 'dk': ''}

    text2 = {'gl': 'Soraarnerussutisiaqarnissamut aaqqissuussinerit nunani allaniittut ilaat pillugit nammineerluni '
                   'nalunaarsuineq {}', 'dk': 'Selvangivelse af visse udenlandske pensionsordninger for {}'}
    text4 = {'gl': 'Nassitsinissamut killissarititaq {}', 'dk': 'Indsendelsesfrist senest {}'}
    text5 = {'gl': 'Inuup normua: ', 'dk': 'Personnummer: '}
    text6 = {'gl': 'Pigisanit pissarsiat akileraarutaat: ', 'dk': 'Kapitalafkastskat: '}
    text7 = {'gl': 'Attavissaq: Akileraartarnermut Aqutsisoqarfik, \nPostboks 1605, 3900 Nuuk. \nTlf. 346510, '
                   'E-mail:tax@nanoq.gl',
             'dk': 'Kontakt: Skattestyrelsen,\nPostboks 1605, 3900 Nuuk. \nTlf. 346510, Email:tax@nanoq.gl'}
    text8 = {'gl': 'Nittartagaq iserfissaq', 'dk': 'Tast selv internet'}
    text8A = {'gl': 'Ullut akileraartussaaffiit', 'dk': 'Antal skattepligtsdage'}
    text10 = {'gl': 'Soraarnerussutisiaqarnissamut aaqqissuussinerit nunani allaniittut ilaat pillugit nammineerluni '
                    'nalunaarsuineq.',
              'dk': 'Selvangivelse af visse udenlandske pensionsordninger.'}
    text11 = {'gl': "Danskit soraarnerussutisiaqarnissamut sillimmasiisarfiini aamma soraarnerussutisiaqarnissamut "
                    "aningaasaateqarfiini inuunermut sillimmasiissutivit soraarnerussutisiaqarnissamullu "
                    "aaqqissuussavit ukiumi pineqartumi iluanaarutaat, kiisalu soraarnerussutisiaqarnissamut "
                    "aaqqissuussinernut nunani allaniittunut illit namminerisamik akiliutitit "
                    "nammineerluni nalunaarsuiffimmi uani nalunaarsussavatit. ",
              'dk': "I denne selvangivelse skal du oplyse årets afkast fra dine livsforsikringer og pensionsordninger "
                    "i danske pensionsforsikringsselskaber og pensionskasser, samt dine private indbetalinger til "
                    "udenlandske pensionsordninger."}
    text12 = {'gl': "Soraarnerussutisiaqarnissamut aaqqissuussinermut Kalaallit Nunaata avataaniittumut "
                    "nammineerlutit akiliisimaguit akilersimasatit, soraarnerussutisiaqarnissamut aaqqissuussinernut "
                    "nunani allaniittunut nammineerluni akiliutaasimasut nalunaarneqarfissaannut nammineerlutit "
                    "nalunaarsussavatit. Paasissutissat taakku soraarnerussutisiaqarnissamut aaqqissuussinermut "
                    "peqataasussaatitaaneq pillugu ukiumoortumik naatsorsuummi atorneqartussaapput.",
              'dk': "Indbetaler du selv til en pensionsordning uden for Grønland, skal du selvangive dine "
                    "indbetalinger i feltet om egen indbetalinger til pensionsordninger i andre lande. Oplysningerne "
                    "skal bruges til årsopgørelsen vedrørende obligatorisk pension."}
    text13 = {'gl': "Taakku saniatigut nalunaarutissaraatit danskit soraarnerussutisiaqarnissamut "
                    "sillimmasiisarfiini aamma soraarnerussutisiaqarnissamut aningaasaateqarfiini inuunermut "
                    "sillimmasiissutivit soraarnerussutisiaqarnissamullu aaqqissuussavit ukiumi pineqartumi "
                    "iluanaarutaat. Nalunaarutiginnittuussaanermi pineqanngillat soraarnerussutisiaqarnissamut "
                    "aaqqissuussinerit inuunermullu sillimmasiissutit, danskit soraarnerussutisiaqarnissamut "
                    "aaqqissuussinernit iluanaarutinik akileraarusiisarnermik inatsisaanni (PAL-lovimi) pineqartut. "
                    "Illit soraarnerussutisiaqarnissamut aaqqissuussinerit inuunermulluunniit sillimmasiissutit "
                    "danskit soraarnerussutisiaqarnissamut aaqqissuussinernit iluanaarutinik akileraarusiisarnermik "
                    "inatsisaanni pineqartunut ilaanersoq nalornissutigigukku illit soraarnerussutisiaqarnissamut "
                    "aningaasaateqarfigisat inuunermulluunniit sillimasiisarfigisat saaffigisinnaavat.",
              'dk': "Derudover skal du oplyse årets afkast fra dine livsforsikringer og pensionsordninger i danske "
                    "pensionsforsikringsselskaber og pensionskasser. Oplysningspligten gælder ikke pensionsordninger "
                    "og livsforsikringer, som omfattes af den danske pensionsafkastbeskatningslov (PAL-loven). "
                    "Hvis du er i tvivl om din pensionsordning eller livsforsikring er omfattet af den danske "
                    "pensionsafkastbeskatningslov kan du kontakte din pensionskasse eller dit livsforsikringsselskab."}
    text13A = {'gl': "",
               'dk': ""}
    text13B = {'gl': "Nammineerluni nalunaarsuiffimmi uani paasissutissanik naqeriikkanik allassimasoqarpat, "
                     "paasissutissat eqqortuunersut illit misissugassaraat. ",
               'dk': "Hvis der på denne selvangivelse er fortrykte oplysninger, skal du kontrollere om oplysningerne "
                     "er rigtige. "}
    text13C = {'gl': "Allanngortitassaappata ilassutissaqaruilluunniit nammineerluni nalunaarsuiffik immersussavat "
                     "atsiorlugulu, kingusinnerpaamillu {} Akileraartarnermut Aqutsisoqarfimmut nassiullugu "
                     "imaluunniit taakku www.sullissivik.gl-ikkut nalunaarutigalugit.",
               'dk': "Har du ændringer eller tilføjelser, skal du udfylde og underskrive selvangivelsen og indsende "
                     "den til Skattestyrelsen eller indberette dem via www.sullissivik.gl senest den {}."}
    text13D = {'gl': "Paasissutissat naqeriikkat isumaqatigigukkit ilassutissaqanngikkuillu qanoq "
                     "iliuuseqartariaqanngilatit.",
               'dk': "Er du enig i de fortrykte oplysninger og har du ikke noget at tilføje, behøver du ikke at "
                     "foretage dig yderligere."}
    text13E = {'gl': "Akileraartarnermut Aqutsisoqarfiup soraarnerussutisiaqarnissamut aaqqissuussiviit ataasiakkaat, "
                     "sullitamik pigisanit pissarsiat akileraarutaattut akiligassaannik unerartitsillutillu "
                     "akiliussinissaat pillugu isumaqatigiissuteqarfigai. Akiliineq illit "
                     "soraarnerussutisiaqarnissamut aaqqissuussivinnit isumagineqassappat tamanna ataani "
                     "allassimassaaq. Taamaattoqartillugu pigisanit pissarsianit akileraarut illit nammineerlutit "
                     "akilissanngilat. ",
               'dk': "Skattestyrelsen har indgået aftale med enkelte pensionsselskaber om, at de indeholder og "
                     "indbetaler kapitalafkastskatten på vegne af deres kunder. Sker betalingen via dit "
                     "pensionsselskab, fremgår det nedenfor. I disse tilfælde skal du ikke indbetale "
                     "kapitalafkastskatten selv."}
    text14 = {'gl': "Inuunermut sillimmasiissutinit soraarnerussutisiaqarnissamullu aaqqissuussinernit iluanaarutit "
                    "pillugit inaarummik naatsorsuut {} Akileraartarnermut Aqutsisoqarfiup {}-mi augustip "
                    "naalernerani nassiutissavaa.",
              'dk': "Du vil modtage slutopgørelse {} fra Skattestyrelsen ultimo august {}. "}
    text15 = {'gl': 'Pigisanit pissarsiat PBL (DK) § 53 A', 'dk': 'Kapitalafkast PBL (DK) § 53 A'}

    text17A = {'gl': 'Immersugassap aqqa\n ', 'dk': 'Feltnavn\n '}
    text17B = {'gl': 'Naqeriigaq\n ', 'dk': 'Fortrykt\n '}
    text17C = {'gl': 'Soraarnerussutisiaqarnissamut aaqqissuussivik', 'dk': 'Pensionsselskab\n '}
    text17D = {'gl': 'Policenormu\n ', 'dk': 'Policenummer\n '}
    text17E = {'gl': 'Nammineerluni nalunaarutigineqartoq', 'dk': 'Selvangivet\n '}

    text18 = {'gl': 'Immersugassap normua', 'dk': 'Felt nr.\n '}
    text25 = {'gl': 'Aningaasat koruuninngorlugit', 'dk': 'Beløb i kroner'}
    text26 = {'gl': 'Paasissutissat Pigisanit pissarsiat ilaasa akileraaruserneqartarnerat pillugu Inatsisartut '
                    'inatsisaanni § 9-mi aalajangersakkat malillugit akisussaassuseqarluni nalunaarneqartussaapput',
              'dk': 'Oplysninger afgives under ansvar i henhold til bestemmelserne i § 9 i '
                    'Inatsisartutlov om beskatning af visse kapitalafkast'}
    text26A = {'gl': '',
               'dk': ''}
    text26B = {'gl': 'Soraarnerussutisiaqarnissamut aaqqissuussinernut nunani allaniittunut, Danmark ilanngullugu, nammineerluni akiliutit. '
                     'Nuna soraarnerussutisiaqarnissamut aaqqissuussinerup pilersinneqarfia, kiisalu aningaasat '
                     'akiliutigineqartut amerlassusiat nalunaakkit',
               'dk': 'Privat indbetaling til pensionsordninger i andre lande, herunder Danmark. Angiv landet, som pensionsordningen er '
                     'hjemmehørende i, samt størrelsen på det indbetalte beløb'}
    text26C = {'gl': '',
               'dk': ''}
    text26D = {'gl': '* Soraarnerussutisiaqarnissamut aaqqissuussinermut uunga tunngatillugu akileraarut '
                     'soraarnerussutisiaqarnissamut aaqqissuussivimmit ingerlaannaartumik akilerneqassaaq',
               'dk': '* Skatten for denne pensionsordning betales automatisk af pensionsselskabet'}
    text26DA = {'gl': 'Soraarnerussutisiaqarnissamut aaqqissuussinerit nunani allaniittut ilaannit iluanaarutit '
                      'pillugit paasissutissat naqeriigaanngitsut uani nammineerlutit nalunaarutigisinnaavatit.',
                'dk': 'Her kan du selvangive oplysninger om afkast af visse udenlandske pensionsordninger, '
                      'som ikke er fortrykte.'}
    text26E = {'gl': 'Soraarnerussutisiaqarnissamut aaqqissuussinerit nunani allaniittut ilaat pillugit '
                     'nammineerluni nalunaarsuinermut atatillugu paasissutissanik allanik nammineerluni '
                     'nalunaagassaqarpa?',
               'dk': 'Er der yderligere information, som skal selvangives i forbindelse med udfyldelsen af '
                     'Selvangivelse for visse udenlandske pensionsordninger? '}

    text27 = {'gl': 'Sumiiffik / Oqarasuaat', 'dk': 'Sted/tlf'}
    text28 = {'gl': 'Ulloq', 'dk': 'Dato'}
    text29 = {'gl': 'Atsiorneq', 'dk': 'Underskrift'}
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
    fully_tax_liable = True
    tax_days_adjust_factor = 1.0
    taxable_days_in_year = 365
    page_counter = 1
    policies = ['']

    def set_parameters(self, tax_year='-', tax_return_date_limit='', request_pay='', pay_date='', person_number='-',
                       reciever_name='', reciever_address_l1='', reciever_address_l2='', reciever_address_l3='',
                       reciever_address_l4='', reciever_address_l5='', fully_tax_liable=True,
                       tax_days_adjust_factor=1.0, taxable_days_in_year=365, policies=None):
        self.tax_year = tax_year
        self.tax_return_date_limit = tax_return_date_limit
        self.request_pay = request_pay
        self.pay_date = pay_date
        self.person_number = person_number
        self.reciever_name = reciever_name
        if policies is None:
            policies = []

        self.full_reciever_address = "\n".join([x for x in (
            reciever_address_l1,
            reciever_address_l2,
            reciever_address_l3,
            reciever_address_l4,
            reciever_address_l5,
        ) if x])

        self.fully_tax_liable = fully_tax_liable
        self.tax_days_adjust_factor = tax_days_adjust_factor
        self.taxable_days_in_year = taxable_days_in_year
        self.policies = policies
        self.default_line_width = self.line_width

    def header(self):
        self.yposition = 40
        self.set_xy(self.left_margin, self.yposition)

    def footer(self):
        self.set_font('arial', '', 11)
        self.set_xy(self.left_margin, self.h - 17)
        self.cell(h=5.0, align='C', w=30.0, txt=self.person_number, border=0)
        self.set_xy(self.std_document_width-5, self.h - 17)
        self.cell(h=5.0, align='R', w=10, txt=str(self.page_counter), border=0)
        self.page_counter += 1
        self.set_xy(self.left_margin, self.yposition)

    def print_tax_slip(self, language):
        """
        Calling this method appends content to the report in progress, starting from a new page
        :param language:
        :return:
        """
        self.add_page()
        self.page_counter = 1
        self.set_fill_color(180, 180, 180)

        self.set_font('arial', 'B', 15.0)
        self.set_xy(125.0, 8.0)
        self.cell(h=self.contact_info_table_cell.get('h'), align='R', w=75.0, txt=self.document_header.get(language),
                  border=0)

        self.set_font('arial', 'B', 12.0)
        self.set_xy(self.left_margin, 8.0)
        self.multi_cell(h=self.contact_info_table_cell.get('h'), align='L', w=170,
                        txt=self.text2.get(language).format(self.tax_year), border=0)

        self.set_font('arial', '', 9.0)
        self.set_xy(self.left_margin, 20.0)
        self.cell(h=0, align='L', w=75.0,
                  txt=self.text4[language].format(self.tax_return_date_limit), border=0)

        self.set_font('arial', '', 8.5)
        # Adressing reciever
        self.set_xy(self.address_field.get('x'), self.address_field.get('y'))
        self.multi_cell(self.address_field.get('w'), 3, border=0,
                        txt=self.reciever_name+"\n"+self.full_reciever_address)

        # Adressing department
        self.set_xy(self.address_field.get('x'), self.address_field.get('y')+12)
        self.multi_cell(self.address_field.get('w'), 4, border=0,
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

        self.set_xy(self.contact_info_table.get('x'),
                    self.contact_info_table.get('y')+6*self.contact_info_table_cell.get('h'))
        self.cell(h=self.contact_info_table_cell.get('h'), align='L', w=self.contact_info_table_cell.get('w'),
                  txt=self.text8A[language], border=1)

        self.set_xy(self.contact_info_table.get('x')+self.contact_info_table_cell.get('w'),
                    self.contact_info_table.get('y')+6*self.contact_info_table_cell.get('h'))
        self.cell(h=self.contact_info_table_cell.get('h'), align='L', w=self.contact_info_table_cell.get('w'),
                  txt=str(self.taxable_days_in_year), border=1)

        self.yposition = 80
        self.set_xy(self.left_margin, self.yposition)

        self.set_font('arial', 'B', 8.5)
        self.multi_cell(self.std_document_width, 5, self.text10[language], border=0)
        self.yposition = self.get_y()

        self.set_font('arial', '', 8.5)
        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(self.std_document_width, 5, align='L', txt=self.text11[language], border=0)
        self.yposition = self.get_y()
        self.yposition += 5

        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(self.std_document_width, 5, align='L', txt=self.text12[language], border=0)
        self.yposition = self.get_y()
        self.yposition += 5

        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(self.std_document_width, 5, align='L', txt=self.text13[language], border=0)
        self.yposition = self.get_y()

        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(self.std_document_width, 5, align='L', txt=self.text13A[language], border=0)
        self.yposition = self.get_y()

        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(self.std_document_width, 5, align='L', txt=self.text13B[language], border=0)
        self.yposition = self.get_y()

        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(self.std_document_width, 5, align='L', txt=self.text13C[language].
                        format(self.tax_return_date_limit),
                        border=0)
        self.yposition = self.get_y()
        self.yposition += 5

        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(self.std_document_width, 5, align='L', txt=self.text13D[language], border=0)
        self.yposition = self.get_y()
        self.yposition += 5

        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(self.std_document_width, 5, align='L', txt=self.text13E[language].
                        format(self.request_pay, self.pay_date),
                        border=0)
        self.yposition = self.get_y()
        self.yposition += 5

        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(self.std_document_width, 5, align='L', txt=self.text14[language].
                        format(self.tax_year, self.request_pay),
                        border=0)
        self.yposition = self.get_y()

        self.yposition += 20

        year_adjusted_text = ''
        if not self.fully_tax_liable:
            year_adjusted_text = self.text26A[language].format(self.tax_days_adjust_factor*100)

        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(self.std_document_width, 5, txt=year_adjusted_text, border=0, align='L')
        self.yposition = self.get_y()

        self.add_page()

        c1w = 65
        c2w = 50
        c3w = 50
        policys_per_page = 4
        policy_index = 0
        any_policys_added = False
        rowheight = 10
        columnheaderheight = 5

        for policy in self.policies:

            if policy_index == policys_per_page:
                self.add_page()
                policy_index = 0
            policy_index += 1
            headerheight = 10
            self.set_font('arial', 'B', 12)
            self.set_xy(self.left_margin, self.yposition)
            self.multi_cell(h=headerheight, align='C', w=c1w+c2w+c3w, txt=policy.get('policy'), border=1)
            self.yposition += headerheight

            self.set_font('arial', 'B', 10)
            self.set_xy(self.left_margin, self.yposition)
            self.multi_cell(h=columnheaderheight, align='C', w=c1w, txt=self.text17A[language], border=1)
            self.set_xy(self.left_margin+c1w, self.yposition)
            self.multi_cell(h=columnheaderheight, align='C', w=c2w, txt=self.text17B[language], border=1)
            self.set_xy(self.left_margin+c1w+c2w, self.yposition)
            self.multi_cell(h=columnheaderheight, align='C', w=c3w, txt=self.text17E[language], border=1)
            self.yposition += 10

            self.set_font('arial', '', 8.5)

            self.set_xy(self.left_margin, self.yposition)
            self.multi_cell(h=rowheight, align='L', w=c1w, txt=self.text15[language], border=1)
            self.set_xy(self.left_margin+c1w, self.yposition)
            actual_amount = policy.get('prefilled_amount')
            self.tax_days_adjust_factor = 0.8
            if not self.fully_tax_liable:
                actual_amount = math.floor(float(actual_amount) * self.tax_days_adjust_factor)
            self.multi_cell(h=rowheight, align='C', w=c2w, txt="{:,}".format(actual_amount).replace(",", "."), border=1)
            self.set_xy(self.left_margin+c1w+c2w, self.yposition)
            self.multi_cell(h=rowheight, align='L', w=c3w, txt='', border=1)
            self.yposition += rowheight
            self.set_xy(self.left_margin, self.yposition)
            if policy.get('agreement_present'):
                self.multi_cell(self.std_document_width, 5, align='L', txt=self.text26D[language], border=0)
            self.yposition += 15
            any_policys_added = True

        if any_policys_added:
            self.add_page()

        self.multi_cell(self.std_document_width, 5, align='L', txt=self.text26DA[language], border=0)
        self.yposition = self.get_y()
        self.yposition += 5

        self.set_font('arial', 'B', 10)
        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(h=columnheaderheight, align='C', w=c1w, txt=self.text17C[language], border=1)
        self.set_xy(self.left_margin+c1w, self.yposition)
        self.multi_cell(h=columnheaderheight, align='C', w=c2w, txt=self.text17D[language], border=1)
        self.set_xy(self.left_margin+c1w+c2w, self.yposition)
        self.multi_cell(h=columnheaderheight, align='C', w=c3w, txt=self.text17E[language], border=1)
        self.yposition += rowheight
        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(h=rowheight, align='L', w=c1w, txt='', border=1)
        self.set_xy(self.left_margin+c1w, self.yposition)
        self.multi_cell(h=rowheight, align='C', w=c2w, txt='', border=1)
        self.set_xy(self.left_margin+c1w+c2w, self.yposition)
        self.multi_cell(h=rowheight, align='C', w=c3w, txt='', border=1)
        self.yposition += rowheight
        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(h=rowheight, align='L', w=c1w, txt='', border=1)
        self.set_xy(self.left_margin+c1w, self.yposition)
        self.multi_cell(h=rowheight, align='C', w=c2w, txt='', border=1)
        self.set_xy(self.left_margin+c1w+c2w, self.yposition)
        self.multi_cell(h=rowheight, align='C', w=c3w, txt='', border=1)
        self.yposition = self.get_y()
        self.yposition += 15

        self.set_font('arial', '', 8.5)
        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(self.std_document_width, 5, align='L', txt=self.text26E[language], border=1)
        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(self.std_document_width, 50, txt='', border=1)
        self.yposition = self.get_y()
        self.yposition += 20

        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(self.std_document_width, 5, align='L', txt=self.text26B[language], border=1)
        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(self.std_document_width, 30, txt='', border=1)
        self.yposition = self.get_y()
        self.yposition += 20

        elementheight = 30
        self.set_xy(self.left_margin, self.yposition)
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
        self.set_line_width(self.default_line_width)
        self.yposition += elementheight

        self.yposition += 10

    def write_tax_slip_to_disk(self, path):
        self.output(path, 'F')

    def perform_complete_write_of_one_person_tax_year(self, person_tax_year, title):
        """
        Calling this method appends reportcontent to the pdf-file in progress, and saves the result to person_tax_year
        :param destination_path:
        :param person_tax_year:
        :param title:
        :return:
        """
        tax_year = person_tax_year.tax_year.year
        tax_return_date_limit = f'1. maj {(person_tax_year.tax_year.year+1)}'
        request_pay = f' {(person_tax_year.tax_year.year+1)}'
        pay_date = f'1. september {(person_tax_year.tax_year.year+1)}'
        person_number = person_tax_year.person.cpr
        reciever_name = person_tax_year.person.name
        reciever_address_line_1 = person_tax_year.person.address_line_1
        reciever_address_line_2 = person_tax_year.person.address_line_2
        reciever_address_line_3 = person_tax_year.person.address_line_3
        reciever_address_line_4 = person_tax_year.person.address_line_4
        reciever_address_line_5 = person_tax_year.person.address_line_5
        fully_tax_liable = person_tax_year.fully_tax_liable
        tax_days_adjust_factor = 1 if person_tax_year.fully_tax_liable else 0
        taxable_days_in_year = person_tax_year.number_of_days

        policies = []

        list_of_policies = PolicyTaxYear.objects.active().filter(
            person_tax_year=person_tax_year
        )

        policy_file_name = f'Y_{tax_year}_{person_number}.pdf'

        firstPolicy = False

        for policy in list_of_policies:

            if not firstPolicy:
                calculation_result = policy.perform_calculation(initial_amount=policy.prefilled_amount)
                tax_days_adjust_factor = calculation_result.get('tax_days_adjust_factor')
                firstPolicy = True

            single_policy = {
                'policy': ((policy.pension_company.name or ' - ')+' - '+policy.policy_number),
                'preliminary_paid_amount': policy.preliminary_paid_amount,
                'prefilled_amount': policy.prefilled_amount,
                'agreement_present': policy.pension_company.agreement_present,
                'year_adjusted_amount': policy.year_adjusted_amount,
                'available_negative_return': policy.available_negative_return
            }

            policies.append(single_policy)

        self.set_parameters(tax_year, tax_return_date_limit, request_pay, pay_date, person_number,
                            reciever_name, reciever_address_line_1, reciever_address_line_2,
                            reciever_address_line_3, reciever_address_line_4,
                            reciever_address_line_5, fully_tax_liable, tax_days_adjust_factor,
                            taxable_days_in_year, policies)

        self.print_tax_slip('gl')
        self.print_tax_slip('dk')

        ts = TaxSlipGenerated(persontaxyear=person_tax_year, title=title)
        ts.file.save(content=ContentFile(self.output(dest='S').encode('latin-1')), name=policy_file_name)
        person_tax_year.tax_slip = ts
        person_tax_year.save()


class TaxSlipHandling(FPDF):

    def perform_complete_write_of_one_tax_year(self, tax_year, title):

        list_of_person_tax_year = PersonTaxYear.objects.filter(
            tax_year__year=tax_year
        )

        for person_tax_year in list_of_person_tax_year:
            pdf_document = TaxPDF()
            pdf_document.perform_complete_write_of_one_person_tax_year(person_tax_year=person_tax_year, title=title)
