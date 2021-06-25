# -*- coding: utf-8 -*-

from datetime import date
from operator import abs

from django.core.files.base import ContentFile
from django.db.models import Sum
from fpdf import FPDF

from kas.models import PersonTaxYear, FinalSettlement


class TaxFinalStatementPDF(FPDF):

    std_document_width = 171
    left_margin = 17.0
    default_line_width = 0.2

    contact_info_table_cell = {'h': 5, 'w1': 50, 'w2': 40}
    contact_info_table = {'x': 100, 'y': 27.0}
    address_field = {'w': 70, 'x': 17, 'y': 37}
    signature_table_cell = {'w': 57, 'h': 10}

    tablerowheight = 8
    std_text_space = 5
    std_table_font_size = 8.5
    std_font_name = 'arial'
    table_header_height = 10
    table_header_font_size = 10

    element_height_1 = 5
    element_height_2 = 60
    element_height_3 = 15
    element_height_4 = 30
    element_height_5 = 15

    sender_name = 'Skattestyrelsen'
    sender_address = 'Postboks 1605'
    sender_postnumber = '3900 Nuuk'

    header_text = {'gl': 'Pigisanit pissarsiat ilaasa akileraarutaat (KAS) pillugit {}-mut inaarummik naatsorsuut',
                   'dk': 'Slutopgørelse vedrørende skat af visse kapitalafkast (KAS) for {}'}
    header_subtext = {'gl': 'Ulloq: {}',
                      'dk': 'Dato {}'}
    header_table_1 = {'gl': 'Inuup normua: ', 'dk': 'Personnummer: '}
    header_table_2 = {'gl': 'Pigisanit pissarsiat akileraarutaat: ', 'dk': 'Kapitalafkastskat: '}
    header_table_3 = {'gl': 'Attavissaq: Akileraartarnermut Aqutsisoqarfik, \nPostboks 1605, 3900 Nuuk. \nTlf. 346510, '
                            'E-mail:tax@nanoq.gl',
                      'dk': 'Kontakt: Skattestyrelsen,\nPostboks 1605, 3900 Nuuk. \nTlf. 346510, Email:tax@nanoq.gl'}
    header_table_4 = {'gl': 'Ullut akileraartussaaffiit', 'dk': 'Antal skattepligtsdage'}
    initial_text = {'gl': "Inaarummik naatsorsuutip imaraa pigisannit siorna pissarsiavit akileraarutaasa (KAS) naatsorsorneqarnerat. Soraarnerussutisiaqarnissamut police-it tamarmik immikkut naatsorsorneqarput. ",
                    'dk': "Slutopgørelsen indeholder en opgørelse af Deres kapitalafkastskat (KAS) for sidste år. "
                          "Opgørelsen er foretaget for hver pensionspolice. "}
    initial_text_append = {'gl': "Police-imi pissarsiassaraluit minusiuppata, taakku police-ip taassuma ukiuni tulliuttuni 10-ni pissarsiassartaanit plusiusunit ilanngaatissanngorlugit nuunneqarsinnaapput.",
                           'dk': "Negative afkast kan fremføres til modregning i de følgende 10 års positive afkast af samme police."}
    policy_table_header_1 = {'gl': 'Soraarnerussutisiaqarnissamut sillimmasiisarfik: {}', 'dk': 'Pensionsselskab: {}'}
    policy_table_header_2 = {'gl': 'Policenormu: {}', 'dk': 'Policenummer: {}'}
    policy_row_text_1 = {'gl': 'Pigisanit pissarsiat', 'dk': 'Kapitalafkast'}
    policy_row_text_2 = {'gl': 'Ullunut akileraartussaaffinnut naatsorsukkat ({1}-init {0}-t)',
                         'dk': 'Justeret for antal skattepligtsdage i året ({0} af {1})'}
    policy_row_text_negative_payout = {'gl': 'Pissarsiassaraluit minusit kingusinnerusukkut ilanngaatissat ',
                                       'dk': 'Negativt afkast til fremførsel'}
    policy_row_text_3 = {'gl': 'Pissarsiassaraluit minusit ilanngaatigineqartut ({})',
                         'dk': 'Modregning af negativt afkast ({})'}
    policy_row_text_4 = {'gl': 'Akileraarusigassat (pigisanit pissarsiat ilanngareerlugit)',
                         'dk': 'Beskatningsgrundlag (kapitalafkast efter modregning)'}
    policy_row_text_5 = {'gl': 'Pigisanit pissarsiat akileraarutaat (akileraarusigassat 15,3%-iat)',
                         'dk': 'Kapitalafkastskat (15,3% af beskatningsgrundlag)'}
    policy_row_text_6 = {'gl': 'Akileraarut nunami allami akiligaq ilanngaatigineqartoq', 'dk': 'Nedslag for betalt skat i udlandet'}
    policy_row_text_summary = {'gl': 'Pigisanit pissarsiat akileraarutaat', 'dk': 'Kapitalafkastskat'}
    policy_row_text_comapny_handles = {'gl': 'Akilernissaa {}-p isumagissavaa', 'dk': 'Afregnes af {}'}

    summary_text_header = {'gl': 'Eqikkaaneq',
                           'dk': 'Opsummering'}
    summary_table1_header = {'gl': 'Akiligassaq soraarnerussutisiaqarnissamut sillimmasiisarfivit isumagisassaa',
                             'dk': 'Afregnes af Deres pensionsselskab'}
    summary_table2_header = {'gl': 'Illit akiligassat',
                             'dk': 'Indbetales af Dem'}
    summary_table1_text1 = {'gl': 'Pigisanit pissarsiat akileraarutaat 15,3%\n{0} - {1}',
                            'dk': 'Kapitalafkastskat 15,3% for\n{0} - {1}'}
    summary_table1_summary = {'gl': 'Pigisanit pissarsiat akileraarutaat',
                              'dk': 'Kapitalafkastskat'}
    summary_table2_text3 = {'gl': 'Pigisanit pissarsiat akileraarutaat akilerallagaq',
                            'dk': 'Modtaget indbetaling af foreløbig kapitalafkastskat'}
    summary_table2_summary = {'gl': 'Pigisanit pissarsiat akileraarutaat akiligassaq',
                              'dk': 'Kapitalafkastskat til betaling'}
    text_tailing_0 = {'gl': 'Akileraartarnermut Aqutsisoqarfiup soraarnerussutisiaqarnissamut sillimmasiisarfiit aamma soraarnerussutisiaqarnissamut aningaasaateqarfiit ilaat, '
                            'pigisanit pissarsiat akileraarutaannik sullitamik soraarnerussutisiaqarnissamut aaqqissuussaannit nuussisarnissamik isumaqatigiissuteqarfigai. '
                            'Soraarnerussutisiaqarnissamut sillimmasiisarfigisat soraarnerussutisiaqar-\nnissamulluunniit aningaasaateqarfigisat taamatut isumaqatigiissuteqarsimappat, '
                            'aningaasat qanoq amerlatigisut akilerneqarnissaat takussutissami uani "Akiligassaq soraarnerussutisiaqarnissamut sillimmasiisarfivit isumagisassaa" takusinnaavat.',
                      'dk': 'Skattestyrelsen har indgået aftaler med nogle pensionsselskaber og pensionskasser om, at de afregner kapitalafkastskatten fra deres kunders pensionsordninger. '
                            'Hvis Deres pensionsselskab eller pensionskasse har indgået en sådan aftale, kan De i boksen med teksten "Afregnes af Deres pensionsselskab" se, hvor meget der vil blive afregnet.'}
    text_tailing_1 = {'gl': 'Aningaasat takussutissami uani "Illit akiligassat" allaqqasut illit nammineerlutit akilissavatit. ',
                      'dk': 'De skal selv indbetale det beløb, som fremgår af boksen med teksten "Indbetales af Dem". '}
    text_tailing_2 = {'gl': 'Aningaasat takussutissami allaqqasut 0-iuppata minusiuppataluunniit (-) qanoq iliuuseqassanngilatit.',
                      'dk': 'Er beløbet i boksen 0 eller negativt (-) skal De ikke foretage Dem yderligere.'}
    text_tailing_3 = {'gl': 'Kingusinnerpaamik 20. september {0} akiliiffigineqassaaq Akileraartarnermut Aqutsisoqarfiup aningaaserivimmi kontua 6471 - 1508196, illit inuttut normut/KAS/Ukioq akileraarfik nalunaarlugit. Soorlu ima 1234567890KAS2020.',
                      'dk': 'Indbetaling skal ske til Skattestyrelsens bankkonto 6471 - 1508196 med angivelse af Deres Cpr-nummer/KAS/Skatteår senest den 20. september {0}. Eksempelvis 1234567890KAS2020'}
    text_tailing_4 = {'gl': 'Akiliiffissatut killiliussaq qaangerneqarpat akileraartarneq akiliisitsiniartarnerlu pillugit inatsisini maleruagassat malillugit ernialersuisoqassaaq.',
                      'dk': 'Overskrides sidste frist for indbetaling, vil der blive tilskrevet renter efter reglerne i skatte- og inddrivelseslovgivningen.'}
    text_tailing_5 = {'gl': 'Pigisanit pissarsiat akileraarutaannik akiliivallaarsimaguit aningaasat akiliivallaarutaasut ilinnut tunniunneqassapput. Illit soraarnerussutisiaqarnissamut sillimmasiisarfiit pigisanit pissarsiat akileraarutaannik akiliivallaarsimappat aningaasat akiliivallaarutaasut soraarnerussutisiaqarnissamut aaqqissuussannut ikineqassapput. ',
                      'dk': 'Har De indbetalt for meget i kapitalafkastskat, vil den overskydende skat blive udbetalt til Dem. Har Deres pensionsselskab indbetalt for meget kapitalafkastskat, vil den overskydende skat blive indbetalt på Deres pensionsordning.'}
    text_tailing_6 = {'gl': 'Pigisanit pissarsiat ilaasa akileraarutaat (KAS) pillugit inaarummik naatsorsuummut tunngatillugu naammagittaalliuut allakkatigoorlunilu tunngavilersugaasoq qaammatit pingasut qaangiutinnginneranni, akileraaruserinermik ingerlatsineq pillugu Inatsisartut inatsisaanni maleruagassat malillugit uunga nassiunneqassaaq: Akileraarusiinernik aalajangiisartut, Postboks 1037, 3900 Nuuk.',
                      'dk': 'Klage over slutopgørelse vedrørende skat af visse kapitalafkast (KAS) skal efter reglerne i landstingslov om forvaltning af skatter, inden 3 måneder fremsendes skriftligt og begrundet til Skatterådet, Postboks 1037, 3900 Nuuk.'}
    text_tailing_7 = {'gl': 'Akileraarusiinernik aalajangiisartut naammagittaalliorfiginnginneranni Akileraartarnermut Aqutsisoqarfimmut saaffiginneqqaarit, inaarummimmi naatsorsuummut apeqqutissariunnakkatit tassani akissuteqarfigineqarsinnaassammata.',
                      'dk': 'Inden klage til Skatterådet bør De henvende Dem til Skattestyrelsen, som vil kunne besvare eventuelle spørgsmål De måtte have vedrørende slutopgørelsen.'}

    tax_return_date_limit = '-'
    full_reciever_address = ''
    days_in_year = 0
    taxable_days_in_year = 365
    page_counter = 1

    def __init__(self, person_tax_year, *args, **kwargs):
        self._person_tax_year = person_tax_year
        super(TaxFinalStatementPDF, self).__init__(*args, **kwargs)
        self._prepayment = self._person_tax_year.transaction_set.filter(type='prepayment').aggregate(amount=Sum('amount'))['amount'] or 0
        self._pretty_policies = []
        for policy in person_tax_year.policytaxyear_set.filter(active=True, slutlignet=True):
            available_deduction_data = policy.calculate_available_yearly_deduction()

            calculation_result = policy.perform_calculation(initial_amount=policy.prefilled_amount or 0,
                                                            taxable_days_in_year=person_tax_year.number_of_days or 0,
                                                            days_in_year=self._person_tax_year.tax_year.days_in_year or 0,
                                                            available_deduction_data=available_deduction_data)

            self._pretty_policies.append({'company': (policy.pension_company.name or '-'),
                                          'policy': (policy.policy_number or '-'),
                                          'active_amount': policy.active_amount,
                                          'taxable_days_in_year': calculation_result.get('taxable_days_in_year'),
                                          'year_adjusted_amount': calculation_result.get('year_adjusted_amount'),
                                          'prefilled_amount': policy.prefilled_amount or 0,
                                          'available_negative_return': policy.available_negative_return,
                                          'taxable_amount': calculation_result.get('taxable_amount'),
                                          'tax_with_deductions': calculation_result.get('tax_with_deductions'),
                                          'full_tax': calculation_result.get('full_tax'),
                                          'available_reductions': available_deduction_data,
                                          'foreign_paid_amount_actual': policy.foreign_paid_amount_actual,
                                          'tax_after_foreign_paid_deduction': calculation_result.get('full_tax') - policy.foreign_paid_amount_actual,
                                          'agreement_present': policy.pension_company.agreement_present
                                          })

    def header(self):
        self.yposition = 40
        self.set_xy(self.left_margin, self.yposition)

    def footer(self):
        self.set_font(self.std_font_name, '', 11)
        self.set_xy(self.left_margin, self.h - 17)
        self.cell(h=5.0, align='C', w=30.0, txt=self._person_tax_year.person.cpr, border=0)
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

        self.set_font(self.std_font_name, 'B', 11.0)
        self.set_xy(self.left_margin, 8)
        self.multi_cell(h=self.contact_info_table_cell.get('h'), align='L', w=170,
                        txt=self.header_text.get(language).format(self._person_tax_year.tax_year.year), border=0)

        self.set_font(self.std_font_name, '', 9.0)
        self.yposition = self.get_y()
        self.set_xy(self.left_margin, 15)
        self.multi_cell(h=self.contact_info_table_cell.get('h'), align='L', w=170,
                        txt=self.header_subtext.get(language).format(date.today().strftime('%d-%m-%Y')), border=0)

        self.set_font(self.std_font_name, '', self.std_table_font_size)
        # Adressing reciever
        self.set_xy(self.address_field.get('x'), self.address_field.get('y'))
        self.multi_cell(self.address_field.get('w'), 3, border=0,
                        txt=self._person_tax_year.person.name+"\n"+self._person_tax_year.person.postal_address)

        # Adressing department
        self.set_xy(self.address_field.get('x'), self.address_field.get('y')+12)
        self.multi_cell(self.address_field.get('w'), 4, border=0,
                        txt=self.sender_name+"\n"+self.sender_address+"\n"+self.sender_postnumber)
        self.line(self.address_field.get('x'), self.address_field.get('y')+12,
                  self.address_field.get('x')+self.address_field.get('w')-30, self.address_field.get('y')+22)
        self.line(self.address_field.get('x'), self.address_field.get('y')+22,
                  self.address_field.get('x')+self.address_field.get('w')-30, self.address_field.get('y')+12)

        self.set_xy(self.contact_info_table.get('x'), self.contact_info_table.get('y'))
        self.cell(h=self.contact_info_table_cell.get('h'), align='L', w=self.contact_info_table_cell.get('w1'),
                  txt=self.header_table_1[language], border=1)
        self.set_xy(self.contact_info_table.get('x'),
                    self.contact_info_table.get('y')+self.contact_info_table_cell.get('h'))
        self.cell(h=self.contact_info_table_cell.get('h'), align='L', w=self.contact_info_table_cell.get('w1'),
                  txt=self.header_table_2[language], border=1)

        self.set_xy(self.contact_info_table.get('x')+self.contact_info_table_cell.get('w1'),
                    self.contact_info_table.get('y'))
        self.cell(h=self.contact_info_table_cell.get('h'), align='L', w=self.contact_info_table_cell.get('w2'),
                  txt=self._person_tax_year.person.cpr, border=1)
        self.set_xy(self.contact_info_table.get('x')+self.contact_info_table_cell.get('w1'),
                    self.contact_info_table.get('y')+self.contact_info_table_cell.get('h'))
        self.cell(h=self.contact_info_table_cell.get('h'), align='L', w=self.contact_info_table_cell.get('w2'),
                  txt='15,3%', border=1)
        self.set_xy(self.contact_info_table.get('x'),
                    self.contact_info_table.get('y')+2*self.contact_info_table_cell.get('h'))
        self.multi_cell(self.contact_info_table_cell.get('w1')+self.contact_info_table_cell.get('w2'), 5, self.header_table_3[language], border=1, align='L')

        self.set_xy(self.contact_info_table.get('x'),
                    self.contact_info_table.get('y')+5*self.contact_info_table_cell.get('h'))
        self.cell(h=self.contact_info_table_cell.get('h'), align='L', w=self.contact_info_table_cell.get('w1'),
                  txt=self.header_table_4[language], border=1)

        self.set_xy(self.contact_info_table.get('x')+self.contact_info_table_cell.get('w1'),
                    self.contact_info_table.get('y')+5*self.contact_info_table_cell.get('h'))
        self.cell(h=self.contact_info_table_cell.get('h'), align='L', w=self.contact_info_table_cell.get('w2'),
                  txt=str(self._person_tax_year.number_of_days), border=1)

        self.yposition = 80
        self.set_xy(self.left_margin, self.yposition)

        self.set_font(self.std_font_name, '', self.std_table_font_size)
        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(self.std_document_width, 5, align='L', txt=self.initial_text[language], border=0)
        self.yposition = self.get_y()
        self.yposition += self.std_text_space

        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(self.std_document_width, 5, align='L', txt=self.initial_text_append[language], border=0)
        self.yposition = self.get_y()
        self.yposition += self.std_text_space

        c1w = 135
        c2w = 30
        any_policys_added = False

        for policy in self._pretty_policies:
            self.yposition = self.get_y()
            self.yposition += 15
            if self.get_y() > 190:
                self.add_page()
            self.set_font(self.std_font_name, 'B', self.table_header_font_size)
            self.set_xy(self.left_margin, self.yposition)
            self.multi_cell(h=self.table_header_height, align='L', w=c1w+c2w, txt=self.policy_table_header_1[language].format(policy.get('company')), border=1)
            self.yposition = self.get_y()
            self.set_xy(self.left_margin, self.yposition)
            self.multi_cell(h=self.table_header_height, align='L', w=c1w+c2w, txt=self.policy_table_header_2[language].format(policy.get('policy')), border=1)
            self.yposition = self.get_y()

            self.set_font(self.std_font_name, '', self.std_table_font_size)

            self.set_xy(self.left_margin, self.yposition)
            self.multi_cell(h=self.tablerowheight, align='L', w=c1w, txt=self.policy_row_text_1[language], border=1)
            self.set_xy(self.left_margin+c1w, self.yposition)
            prefilled_amount = policy.get('prefilled_amount')
            self.multi_cell(h=self.tablerowheight, align='R', w=c2w, txt="{:,}".format(prefilled_amount).replace(",", "."), border=1)
            self.yposition = self.get_y()

            self.set_xy(self.left_margin, self.yposition)
            self.multi_cell(h=self.tablerowheight, align='L', w=c1w, txt=self.policy_row_text_2[language].format(self._person_tax_year.number_of_days, self._person_tax_year.tax_year.days_in_year), border=1)
            self.set_xy(self.left_margin+c1w, self.yposition)
            year_adjusted_amount = policy.get('year_adjusted_amount')
            self.multi_cell(h=self.tablerowheight, align='R', w=c2w, txt="{:,}".format(year_adjusted_amount).replace(",", "."), border=1)
            self.yposition = self.get_y()

            if year_adjusted_amount < 0:
                # If we got a negative amount this is the last row to write on a policy, this indicate the amount to be used in future years
                self.set_font(self.std_font_name, 'B', self.std_table_font_size)
                self.set_xy(self.left_margin, self.yposition)
                self.multi_cell(h=self.tablerowheight, align='L', w=c1w, txt=self.policy_row_text_negative_payout[language], border=1)
                self.set_xy(self.left_margin+c1w, self.yposition)
                year_adjusted_amount = policy.get('year_adjusted_amount')
                self.multi_cell(h=self.tablerowheight, align='R', w=c2w, txt="{:,}".format(abs(year_adjusted_amount)).replace(",", "."), border=1)
                self.yposition = self.get_y()
            else:
                # If there is not a negative amount, we need to deliver calculations
                available_reductions = policy.get('available_reductions')
                if available_reductions:
                    for reduction in available_reductions:
                        self.set_xy(self.left_margin, self.yposition)
                        self.multi_cell(h=self.tablerowheight, align='L', w=c1w, txt=self.policy_row_text_3[language].format(reduction), border=1)
                        self.set_xy(self.left_margin+c1w, self.yposition)
                        self.multi_cell(h=self.tablerowheight, align='R', w=c2w, txt="{:,}".format(-abs(available_reductions.get(reduction))).replace(",", "."), border=1)
                        self.yposition = self.get_y()

                self.set_xy(self.left_margin, self.yposition)
                self.multi_cell(h=self.tablerowheight, align='L', w=c1w, txt=self.policy_row_text_4[language], border=1)
                self.set_xy(self.left_margin+c1w, self.yposition)
                taxable_amount = policy.get('taxable_amount')
                self.multi_cell(h=self.tablerowheight, align='R', w=c2w, txt="{:,}".format(taxable_amount).replace(",", "."), border=1)
                self.yposition = self.get_y()

                self.set_xy(self.left_margin, self.yposition)
                self.multi_cell(h=self.tablerowheight, align='L', w=c1w, txt=self.policy_row_text_5[language], border=1)
                self.set_xy(self.left_margin+c1w, self.yposition)
                full_tax = policy.get('full_tax')
                self.multi_cell(h=self.tablerowheight, align='R', w=c2w, txt="{:,}".format(full_tax).replace(",", "."), border=1)
                self.yposition = self.get_y()

                foreign_paid_amount_actual = policy.get('foreign_paid_amount_actual')
                if foreign_paid_amount_actual != 0:
                    # If there is a foreign paid amount, we need to show that information
                    self.set_xy(self.left_margin, self.yposition)
                    self.multi_cell(h=self.tablerowheight, align='L', w=c1w, txt=self.policy_row_text_6[language], border=1)
                    self.set_xy(self.left_margin+c1w, self.yposition)
                    foreign_paid_amount_actual = policy.get('foreign_paid_amount_actual') or 0
                    self.multi_cell(h=self.tablerowheight, align='R', w=c2w, txt="{:,}".format(-abs(foreign_paid_amount_actual)).replace(",", "."), border=1)
                    self.yposition = self.get_y()

                self.set_font(self.std_font_name, 'B', self.table_header_font_size)
                self.set_xy(self.left_margin, self.yposition)
                self.multi_cell(h=self.tablerowheight, align='L', w=c1w, txt=self.policy_row_text_summary[language], border=1)
                self.set_xy(self.left_margin+c1w, self.yposition)
                tax_after_foreign_paid_deduction = policy.get('tax_after_foreign_paid_deduction')
                self.multi_cell(h=self.tablerowheight, align='R', w=c2w, txt="{:,}".format(tax_after_foreign_paid_deduction).replace(",", "."), border=1)
                self.yposition = self.get_y()
                self.set_font(self.std_font_name, '', self.std_table_font_size)

            self.yposition = self.get_y()
            self.set_xy(self.left_margin, self.yposition)
            if policy.get('agreement_present'):
                self.set_font('arial', 'B', self.table_header_font_size)
                self.set_xy(self.left_margin, self.yposition)
                self.multi_cell(h=self.table_header_height, align='L', w=c1w+c2w, txt=self.policy_row_text_comapny_handles[language].format(policy.get('company')), border=1)
                self.yposition += self.get_y()
                self.set_font(self.std_font_name, '', self.std_table_font_size)

            any_policys_added = True

        if any_policys_added:
            self.add_page()

        self.yposition = self.get_y()
        self.set_font(self.std_font_name, 'B', self.table_header_font_size)
        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(self.std_document_width, 5, align='L', txt=self.summary_text_header[language], border=0)
        self.yposition = self.get_y()
        self.yposition += self.std_text_space

        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(self.std_document_width, 5, align='L', txt=self.summary_table1_header[language], border=0)
        self.yposition = self.get_y()
        self.set_font(self.std_font_name, '', self.std_table_font_size)

        policy_sum_with_agreement = 0
        for policy in self._pretty_policies:
            if policy.get('agreement_present'):
                self.set_xy(self.left_margin, self.yposition)
                self.multi_cell(h=self.tablerowheight/2, align='L', w=c1w, txt=self.summary_table1_text1[language].format(policy.get('company'), policy.get('policy')), border=1)
                self.set_xy(self.left_margin+c1w, self.yposition)
                tax_with_deductions = policy.get('tax_with_deductions')
                policy_sum_with_agreement += tax_with_deductions
                self.multi_cell(h=self.tablerowheight, align='R', w=c2w, txt="{:,}".format(tax_with_deductions).replace(",", "."), border=1)
                self.yposition = self.get_y()

        self.set_font(self.std_font_name, 'B', self.table_header_font_size)
        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(h=self.tablerowheight, align='L', w=c1w, txt=self.summary_table1_summary[language], border=1)
        self.set_xy(self.left_margin+c1w, self.yposition)
        self.multi_cell(h=self.tablerowheight, align='R', w=c2w, txt="{:,}".format(policy_sum_with_agreement).replace(",", "."), border=1)
        self.yposition = self.get_y()
        self.yposition += self.std_text_space

        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(self.std_document_width, 5, align='L', txt=self.summary_table2_header[language], border=0)
        self.yposition = self.get_y()
        self.set_font(self.std_font_name, '', self.std_table_font_size)

        sum_tax_after_foreign_paid_deduction = 0
        for policy in self._pretty_policies:
            tax_after_foreign_paid_deduction = policy.get('tax_after_foreign_paid_deduction')
            if not policy.get('agreement_present') and tax_after_foreign_paid_deduction > 0:
                self.set_xy(self.left_margin, self.yposition)
                self.multi_cell(h=self.tablerowheight/2, align='L', w=c1w, txt=self.summary_table1_text1[language].format(policy.get('company'), policy.get('policy')), border=1)
                self.set_xy(self.left_margin+c1w, self.yposition)
                tax_after_foreign_paid_deduction = policy.get('tax_after_foreign_paid_deduction')
                sum_tax_after_foreign_paid_deduction = sum_tax_after_foreign_paid_deduction+tax_after_foreign_paid_deduction
                self.multi_cell(h=self.tablerowheight, align='R', w=c2w, txt="{:,}".format(tax_after_foreign_paid_deduction).replace(",", "."), border=1)
                self.yposition = self.get_y()

        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(h=self.tablerowheight, align='L', w=c1w, txt=self.summary_table2_text3[language], border=1)
        self.set_xy(self.left_margin+c1w, self.yposition)
        self.multi_cell(h=self.tablerowheight, align='R', w=c2w, txt="{:,}".format(self._prepayment), border=1)
        self.yposition = self.get_y()

        self.set_font(self.std_font_name, 'B', self.table_header_font_size)
        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(h=self.tablerowheight, align='L', w=c1w, txt=self.summary_table2_summary[language], border=1)
        self.set_xy(self.left_margin+c1w, self.yposition)
        self.multi_cell(h=self.tablerowheight, align='R', w=c2w, txt="{:,}".format(sum_tax_after_foreign_paid_deduction+self._prepayment).replace(",", "."), border=1)
        self.yposition = self.get_y()
        self.yposition += self.std_text_space
        self.set_font(self.std_font_name, '', self.std_table_font_size)

        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(self.std_document_width, 5, align='L', txt=self.text_tailing_0[language], border=0)
        self.yposition = self.get_y()
        self.yposition += self.std_text_space

        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(self.std_document_width, 5, align='L', txt=self.text_tailing_1[language], border=0)
        self.yposition = self.get_y()
        self.yposition += self.std_text_space

        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(self.std_document_width, 5, align='L', txt=self.text_tailing_2[language], border=0)
        self.yposition = self.get_y()
        self.yposition += self.std_text_space

        self.set_font(self.std_font_name, 'B', self.std_table_font_size)
        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(self.std_document_width, 5, align='L', txt=self.text_tailing_3[language].format(self._person_tax_year.tax_year.year+1), border=0)
        self.yposition = self.get_y()
        self.yposition += self.std_text_space

        self.set_font(self.std_font_name, '', self.std_table_font_size)
        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(self.std_document_width, 5, align='L', txt=self.text_tailing_4[language], border=0)
        self.yposition = self.get_y()
        self.yposition += self.std_text_space

        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(self.std_document_width, 5, align='L', txt=self.text_tailing_5[language], border=0)
        self.yposition = self.get_y()
        self.yposition += self.std_text_space

        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(self.std_document_width, 5, align='L', txt=self.text_tailing_6[language], border=0)
        self.yposition = self.get_y()
        self.yposition += self.std_text_space

        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(self.std_document_width, 5, align='L', txt=self.text_tailing_7[language], border=0)
        self.yposition = self.get_y()
        self.yposition += self.std_text_space

    @classmethod
    def generate_pdf(cls, person_tax_year: PersonTaxYear):
        pdf_generator = cls(person_tax_year=person_tax_year)
        pdf_generator.print_tax_slip('gl')
        pdf_generator.print_tax_slip('dk')
        policy_file_name = f'Y_FINAL_{person_tax_year.tax_year.year}_{person_tax_year.person.cpr}.pdf'
        final_settlement = FinalSettlement(person_tax_year=person_tax_year)
        final_settlement.pdf.save(content=ContentFile(pdf_generator.output(dest='S').encode('latin-1')), name=policy_file_name)
        return final_settlement
