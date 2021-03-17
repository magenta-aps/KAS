# -*- coding: utf-8 -*-

import math

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
             'dk': 'Kontakt: Skattestyrelsen,\nPostboks 1605, 3900 Nuuk. Tlf. 346510,\nEmail:tax@nanoq.gl'}
    text8 = {'gl': 'Nittartagaq iserfissaq', 'dk': 'Tast selv internet'}
    text9 = {'gl': 'Kode isissutissaq', 'dk': 'Tast selv kode'}
    text10 = {'gl': 'GL-Vejledning til selvangivelse af visse udenlandske pensionsordninger (som fx afkast fra '
                    'pensionsordninger og livsforsikringer)',
              'dk': 'Vejledning til selvangivelse af visse udenlandske pensionsordninger (som fx afkast fra '
                    'pensionsordninger og livsforsikringer)'}
    text11 = {'gl': "GI denne selvangivelse skal du oplyse årets afkast fra dine pensionsordninger og livsforsikringer "
                    "i danske pensionskasser og pensionsforsikringsselskaber. Oplysningspligten gælder ikke "
                    "pensionsordninger og livsforsikringer, som omfattes af den danske pensionsafkastbeskatningslov. "
                    "Hvis du er i tvivl om din pensionsordning eller livsforsikring er omfattet af den danske "
                    "pensionsafkastbeskatningslov (Pal-loven) kan du kontakte din pensionskasse eller dit "
                    "livsforsikringsselskab. ",
              'dk': "I denne selvangivelse skal du oplyse årets afkast fra dine pensionsordninger og livsforsikringer "
                    "i danske pensionskasser og pensionsforsikringsselskaber. Oplysningspligten gælder ikke "
                    "pensionsordninger og livsforsikringer, som omfattes af den danske pensionsafkastbeskatningslov. "
                    "Hvis du er i tvivl om din pensionsordning eller livsforsikring er omfattet af den danske "
                    "pensionsafkastbeskatningslov (Pal-loven) kan du kontakte din pensionskasse eller dit "
                    "livsforsikringsselskab. "}
    text12 = {'gl': "GL - Hvis der på selvangivelsen af visse udenlandske pensionsordninger er fortrykte oplysninger, "
                    "skal du kontrollere om de fortrykte oplysninger er rigtige.  Hvis der er fejl i oplysningerne "
                    "eller der mangler oplysninger, skal du selvangive disse herunder. ",
              'dk': "Hvis der på selvangivelsen af visse udenlandske pensionsordninger er fortrykte oplysninger, "
                    "skal du kontrollere om de fortrykte oplysninger er rigtige.  Hvis der er fejl i oplysningerne "
                    "eller der mangler oplysninger, skal du selvangive disse herunder. "}
    text13 = {'gl': "GL - Har du ændringer eller tilføjelser, skal du udfylde og underskrive selvangivelsen og "
                    "indsende den til Skattestyrelsen eller indberette ændringerne via www.sullissivik.gl "
                    "senest den {}.  ",
              'dk': "Har du ændringer eller tilføjelser, skal du udfylde og underskrive selvangivelsen og "
                    "indsende den til Skattestyrelsen eller indberette ændringerne via www.sullissivik.gl "
                    "senest den {}.  "}
    text13A = {'gl': "GL - Er du enig i de fortrykte oplysninger og har du ikke noget at tilføje, behøver du ikke at "
                     "foretage dig yderligere. Opmærksomheden henledes på, at den omstændighed at en skattepligtig "
                     "ikke får tilsendt selvangivelse, ikke fritager den skattepligtige for pligten til at indgive "
                     "selvangivelse.  ",
               'dk': "Er du enig i de fortrykte oplysninger og har du ikke noget at tilføje, behøver du ikke at "
                     "foretage dig yderligere. Opmærksomheden henledes på, at den omstændighed at en skattepligtig "
                     "ikke får tilsendt selvangivelse, ikke fritager den skattepligtige for pligten til at indgive "
                     "selvangivelse.  "}
    text13B = {'gl': "GL - Skattestyrelsen har indgået aftale med enkelte pensionsselskaber om, at de indeholder og "
                     "indbetaler kapitalafkastskatten på vegne af deres kunder. Sker betalingen via dit "
                     "pensionsselskab, fremgår det af kolonnen nedenfor. I disse tilfælde skal du ikke indbetale "
                     "kapitalafkast selv. ",
               'dk': "Skattestyrelsen har indgået aftale med enkelte pensionsselskaber om, at de indeholder og "
                     "indbetaler kapitalafkastskatten på vegne af deres kunder. Sker betalingen via dit "
                     "pensionsselskab, fremgår det af kolonnen nedenfor. I disse tilfælde skal du ikke indbetale "
                     "kapitalafkast selv. "}
    text13C = {'gl': "GL - Hvis du har spørgsmål om din pensionsordning, skal du henvende dig i dit penge- eller "
                     "pensionsinstitut. Læs mere om beskatning af kapitalafkast på vores hjemmeside www.aka.gl",
               'dk': "Hvis du har spørgsmål om din pensionsordning, skal du henvende dig i dit penge- eller "
                     "pensionsinstitut. Læs mere om beskatning af kapitalafkast på vores hjemmeside www.aka.gl"}

    text14 = {'gl': "GL - Du vil modtage slutopgørelse fra Skattestyrelsen {}. "
                    "Vær opmærksom på at Skattestyrelsen opkræver beregnet kapitalafkast til betaling {}. ",
              'dk': "Du vil modtage slutopgørelse fra Skattestyrelse {}. "
                    "Vær opmærksom på at Skattestyrelsen opkræver beregnet kapitalafkast til betaling {}. "}
    text15 = {'gl': 'Pigisanit pissarsiat PBL (DK) § 53 A', 'dk': 'Kapitalafkast PBL (DK) § 53 A'}
    text16 = {'gl': 'Aningaasat\n koruuninngorlugit', 'dk': 'Beløb i kroner'}

    text17A = {'gl': 'GL-Feltnavn\n ', 'dk': 'Feltnavn\n '}
    text17B = {'gl': 'GL-Fortrykt\n ', 'dk': 'Fortrykt\n '}
    text17C = {'gl': 'GL-Selvangivet\n ', 'dk': 'Selvangivet\n '}

    text18 = {'gl': 'Sammisap \nnormua', 'dk': 'Felt nr.\n '}
    text25 = {'gl': 'Aningaasat koruuninngorlugit', 'dk': 'Beløb i kroner'}
    text26 = {'gl': 'Paasissutissat Pigisanit pissarsiat ilaasa akileraaruserneqartarnerat pillugu Inatsisartut '
                    'inatsisaanni § 9-mi aalajangersakkat malillugit akisussaassuseqarluni nalunaarneqartussaapput.',
              'dk': 'Oplysninger afgives under ansvar i henhold til bestemmelserne i § 9 i '
                    'Inatsisartutlov om beskatning af visse kapitalafkast'}
    text26A = {'gl': 'GL-De har ikke haft bopæl i Grønland i hele året og derfor skal de ikke betale skat for hele '
                     'året. Skatten beregnes forholdmessigt efter antallet af dage med bopæl i landet ud af det '
                     'aktuelle antal dage i året. I nedenstående indberetninger angives det beregningsgrundlag, '
                     'der benyttes som basis for fastsættelse af skatten. De er fastsat til at være skattepligtig i {}% '
                     'af året)',
               'dk': 'De har ikke haft bopæl i Grønland i hele året og derfor skal de ikke betale skat for hele året. '
                     'Skatten beregnes forholdmessigt efter antallet af dage med bopæl i landet ud af det aktuelle '
                     'antal dage i året. I nedenstående indberetninger angives det beregningsgrundlag, '
                     'der benyttes som basis for fastsættelse af skatten. De er fastsat til at være skattepligtig i {}% '
                     'af året'}
    text26B = {'gl': 'GL - Egen indbetaling til pensionsordninger i andre lande, angiv landet, som pensionsordningen '
                     'er hjemmehørende i, samt størrelsen på det indskudte beløb',
               'dk': 'Egen indbetaling til pensionsordninger i andre lande, angiv landet, som pensionsordningen er '
                     'hjemmehørende i, samt størrelsen på det indskudte beløb'}
    text26C = {'gl': 'GL - Fremført negativt afkast fra tidligere år',
               'dk': 'Fremført negativt afkast fra tidligere år'}
    text26D = {'gl': '* GL-Skatten for denne pensionsordning betales automatisk af pensionsselskabet',
               'dk': '* Skatten for denne pensionsordning betales automatisk af pensionsselskabet'}
    text26E = {'gl': 'GL-Er der yderligere information, som skal selvangives i forbindelse med udfyldelsen '
                     'af KAS-selvangivelse',
               'dk': 'Er der yderligere information, som skal selvangives i forbindelse med udfyldelsen af '
                     'KAS-selvangivelse'}

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
    fully_tax_liable = True
    tax_days_adjust_factor = 1.0
    policies = ['']

    def set_parameters(self, tax_year='-', tax_return_date_limit='', request_pay='', pay_date='', person_number='-',
                       reciever_name='', reciever_address_l1='', reciever_address_l2='', reciever_address_l3='',
                       reciever_address_l4='', reciever_address_l5='', fully_tax_liable=True,
                       tax_days_adjust_factor=1.0, policies=['']):
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

        self.fully_tax_liable = fully_tax_liable
        self.tax_days_adjust_factor = tax_days_adjust_factor
        self.policies = policies
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

        self.set_fill_color(180, 180, 180)

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

        self.set_font('arial', 'B', 8.5)
        self.multi_cell(self.std_document_width, 5, self.text10[language], border=0)
        self.yposition = self.get_y()

        self.set_font('arial', '', 8.5)
        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(self.std_document_width, 5, self.text11[language].format(self.tax_return_date_limit), border=0)
        self.yposition = self.get_y()

        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(self.std_document_width, 5, self.text12[language], border=0)
        self.yposition = self.get_y()

        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(self.std_document_width, 5, self.text13[language].format(self.tax_return_date_limit), border=0)
        self.yposition = self.get_y()

        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(self.std_document_width, 5, self.text13A[language].format(self.request_pay, self.pay_date),
                        border=0)
        self.yposition = self.get_y()

        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(self.std_document_width, 5, self.text13B[language].format(self.request_pay, self.pay_date),
                        border=0)
        self.yposition = self.get_y()

        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(self.std_document_width, 5, self.text13C[language].format(self.request_pay, self.pay_date),
                        border=0)
        self.yposition = self.get_y()

        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(self.std_document_width, 5, self.text14[language].format(self.request_pay, self.pay_date),
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

        c1w = 73
        c2w = 30
        c3w = 30
        c4w = 27
        policys_per_page = 4
        policy_index = 0

        for policy in self.policies:

            if policy_index == policys_per_page:
                self.add_page()
                policy_index = 0
            policy_index += 1
            headerheight = 10
            columnheaderheight = 5
            self.set_font('arial', 'B', 12)
            self.set_xy(self.left_margin, self.yposition)
            self.multi_cell(h=headerheight, align='C', w=c1w+c2w+c3w+c4w, txt=policy.get('policy'), border=1)
            self.yposition += headerheight

            self.set_font('arial', 'B', 10)
            self.set_xy(self.left_margin, self.yposition)
            self.multi_cell(h=columnheaderheight, align='L', w=c1w, txt=self.text17A[language], border=1)
            self.set_xy(self.left_margin+c1w, self.yposition)
            self.multi_cell(h=columnheaderheight, align='C', w=c2w, txt=self.text17B[language], border=1)
            self.set_xy(self.left_margin+c1w+c2w, self.yposition)
            self.multi_cell(h=columnheaderheight, align='C', w=c3w, txt=self.text17C[language], border=1)
            self.set_xy(self.left_margin+c1w+c2w+c3w, self.yposition)
            self.multi_cell(h=columnheaderheight, align='C', w=c4w, txt=self.text18[language], border=1)
            self.yposition += 10

            self.set_font('arial', '', 8.5)
            rowheight = 10
            self.set_xy(self.left_margin, self.yposition)
            self.multi_cell(h=rowheight, align='L', w=c1w, txt=self.text15[language], border=1)
            self.set_xy(self.left_margin+c1w, self.yposition)
            actual_amount = policy.get('prefilled_amount')
            self.tax_days_adjust_factor = 0.8
            if not self.fully_tax_liable:
                actual_amount = math.floor(float(actual_amount) * self.tax_days_adjust_factor)
            self.multi_cell(h=rowheight, align='C', w=c2w, txt=str(actual_amount), border=1)
            self.set_xy(self.left_margin+c1w+c2w, self.yposition)
            self.multi_cell(h=rowheight, align='L', w=c3w, txt='', border=1)
            self.set_xy(self.left_margin+c1w+c2w+c3w, self.yposition)
            self.multi_cell(h=rowheight, align='C', w=c4w, txt='KAS-201', border=1)
            self.yposition += rowheight
            self.set_xy(self.left_margin, self.yposition)
            self.multi_cell(h=rowheight, align='L', w=c1w, txt=self.text26C[language], border=1)
            self.set_xy(self.left_margin+c1w, self.yposition)
            available_negative_return = policy.get('available_negative_return')
            if available_negative_return is None:
                available_negative_return = 0
            self.multi_cell(h=rowheight, align='C', w=c2w, txt=str(available_negative_return), border=1)
            self.set_xy(self.left_margin+c1w+c2w, self.yposition)
            self.multi_cell(h=rowheight, align='C', w=c3w, txt='', border=1, fill=False)
            self.set_xy(self.left_margin+c1w+c2w+c3w, self.yposition)
            self.multi_cell(h=rowheight, align='L', w=c4w, txt='', border=1)
            self.yposition = self.get_y()
            self.set_xy(self.left_margin, self.yposition)
            if policy.get('agreement_present'):
                self.multi_cell(self.std_document_width, 5, txt=self.text26D[language], border=0)
            self.yposition += 15

        self.add_page()
        self.multi_cell(self.std_document_width, 5, '', border=0)
        self.yposition = self.get_y()

        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(self.std_document_width, 5, txt=self.text26E[language], border=1)
        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(self.std_document_width, 60, txt='', border=1)
        self.yposition = self.get_y()
        self.yposition += 20

        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(self.std_document_width, 5, txt=self.text26B[language], border=1)
        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(self.std_document_width, 40, txt='', border=1)
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

        self.set_font('arial', 'B', 13.0)
        self.set_xy(self.left_margin, self.yposition)
        self.cell(h=10, align='L', w=self.std_document_width, txt=self.text30[language], border=0)

    def write_tax_slip_to_disk(self, path):
        self.output(path, 'F')

    def perform_complete_write_of_one_person_tax_year(self, destination_path, person_tax_year):

        tax_year = person_tax_year.tax_year.year
        tax_return_date_limit = f'1. maj {(person_tax_year.tax_year.year+1)}'
        request_pay = f'ultimo august {(person_tax_year.tax_year.year+1)}'
        pay_date = f'1. september {(person_tax_year.tax_year.year+1)}'
        person_number = person_tax_year.person.cpr
        reciever_name = person_tax_year.person.name
        reciever_address_line_1 = person_tax_year.person.address_line_1
        reciever_address_line_2 = person_tax_year.person.address_line_2
        reciever_address_line_3 = person_tax_year.person.address_line_3
        reciever_address_line_4 = person_tax_year.person.address_line_4
        reciever_address_line_5 = person_tax_year.person.address_line_5
        fully_tax_liable = person_tax_year.fully_tax_liable
        tax_days_adjust_factor = person_tax_year.fully_tax_liable

        policies = []

        list_of_policies = PolicyTaxYear.objects.filter(
            person_tax_year=person_tax_year
        )

        policy_file_name = f'{destination_path}Y_{tax_year}_{person_number}.pdf'

        firstPolicy = False

        for policy in list_of_policies:

            if not firstPolicy:
                tax_days_adjust_factor = policy.perform_calculation(initial_amount=policy.prefilled_amount)\
                    .get('tax_days_adjust_factor')
                firstPolicy = True

            single_policy = {
                'policy': (policy.pension_company.name+' - '+policy.policy_number),
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
                            reciever_address_line_5, fully_tax_liable, tax_days_adjust_factor, policies)

        self.print_tax_slip('gl')
        self.print_tax_slip('dk')
        self.write_tax_slip_to_disk(policy_file_name)

        ts = TaxSlipGenerated.objects.create(file=policy_file_name)
        ts.save()
        person_tax_year.tax_slip = ts
        person_tax_year.save()


class TaxSlipHandling(FPDF):

    def perform_complete_write_of_one_tax_year(self, destination_path, tax_year):

        list_of_person_tax_year = PersonTaxYear.objects.filter(
            tax_year__year=tax_year
        )

        for person_tax_year in list_of_person_tax_year:
            pdf_document = TaxPDF()
            pdf_document.perform_complete_write_of_one_person_tax_year(destination_path=destination_path,
                                                                       person_tax_year=person_tax_year)
