# -*- coding: utf-8 -*-

import os
import sys

from fpdf import FPDF


class TaxPDF(FPDF):

    std_document_width = 170
    left_margin = 17.0
    contact_info_table_cell_height = 5.0
    contact_info_table_cell_width = 40.0

    contact_info_table_x_pos = 100.0
    contact_info_table_y_pos = 27.0

    address_field_width = 70
    address_field_x_pos = 17
    address_field_y_pos = 37

    element_height_1 = 5
    element_height_2 = 40
    element_height_3 = 15
    element_height_4 = 30
    element_height_5 = 15

    document_header = ['GL Bilag til S1/S1U', 'Bilag til S1/S1U']
    text2 = ['GL Bilag til Selvangivelse for ', 'Bilag til Selvangivelse for ']
    text3 = ['GL Bilag vedrørende beskatning af visse kapitalafkast',
             'Bilag vedrørende beskatning af visse kapitalafkast']
    text4 = ['GL Indsendelsesfrist senest ', 'Indsendelsesfrist senest ']
    text5 = ['GL Personnummer: ', 'Personnummer: ']
    text6 = ['GL Kapitalafkastskat: ', 'Kapitalafkastskat: ']
    text7 = ['GL Selvbetjeningsinformation', 'Selvbetjeningsinformation']
    text8 = ['GL Tast selv internet', 'Tast selv internet']
    text9 = ['GL Tast selv kode', 'Tast selv kode']
    text10 = ['GL Vejledning til bilag vedrørende beskatning af visse kapitalafkast',
              'Vejledning til bilag vedrørende beskatning af visse kapitalafkast']
    text11 = ["GL Lorem ipsum, or lipsum as it is sometimes known, is dummy text used in laying out "
              "print, graphic or web designs. The passage is attributed to an unknown typesetter in "
              "the 15th century who is thought to have scrambled parts of Cicero's De Finibus "
              "Bonorum et Malorum for use in a type specimen book.",
              "Lorem ipsum, or lipsum as it is sometimes known, is dummy text used in laying out "
              "print, graphic or web designs. The passage is attributed to an unknown typesetter in "
              "the 15th century who is thought to have scrambled parts of Cicero's De Finibus "
              "Bonorum et Malorum for use in a type specimen book."]
    text12 = ["GL Hvis de er uneig i indholdet bla bla bla bla bla bla bla bla bla bla bla bla bla "
              "bla bla bla bla bla bla bla bla bla bla",
              "Hvis de er uneig i indholdet bla bla bla bla bla bla bla bla bla bla bla bla bla "
              "bla bla bla bla bla bla bla bla bla bla"]
    text13 = ["GL Hvis de er uneig i indholdet bla bla bla bla bla bla bla bla bla bla bla bla "
              "bla bla bla bla bla bla bla bla bla bla bla",
              "Hvis de er uneig i indholdet bla bla bla bla bla bla bla bla bla bla bla bla "
              "bla bla bla bla bla bla bla bla bla bla bla"]
    text14 = ["GL Hvis de er uneig i indholdet bla bla bla bla bla bla bla bla bla bla bla bla "
              "bla bla bla bla bla bla bla bla bla bla bla",
              "Hvis de er uneig i indholdet bla bla bla bla bla bla bla bla bla bla bla bla "
              "bla bla bla bla bla bla bla bla bla bla bla"]
    text15 = ['GL Kapitalafkast PBL (DK) § 53 A', 'Kapitalafkast PBL (DK) § 53 A']
    text16 = ['GL Beløb i kroner', 'Beløb i kroner']
    text17 = ['GL Beløb i kroner', 'Beløb i kroner']
    text18 = ['GL Felt nr.', 'Felt nr.']
    text19 = ['GL Kapitalafkastskat', 'Kapitalafkastskat']
    text20 = ['Har de betalt foreløbig bla bla bla bla bla bla bla bla bla '
              'bla bla bla bla bla bla bla', 'Har de betalt foreløbig bla bla bla bla bla bla bla bla bla '
                                             'bla bla bla bla bla bla bla']
    text21 = ['GL Beløb i kroner', 'Beløb i kroner']
    text22 = ['GL Er kapitalafkastskatten hævet fra pensionsordning?',
              'Er kapitalafkastskatten hævet fra pensionsordning?']
    text23 = ['GL Kapitalafkastskat i udlandet', 'Kapitalafkastskat i udlandet']
    text24 = ['GL Anmoder de om nedslag bla bla bla bla bla bla bla bla bla '
              'bla bla bla bla bla bla bla', 'Anmoder de om nedslag bla bla bla bla bla bla bla bla bla '
                                             'bla bla bla bla bla bla bla']
    text25 = ['GL Beløb i kroner', 'Beløb i kroner']
    text26 = ['GL Oplysninger afgives under ansvar i henhold til bestemmelserne i § 9 i '
              'Inatsisartutlov om beskatning af visse kapitalafkast',
              'Oplysninger afgives under ansvar i henhold til bestemmelserne i § 9 i '
              'Inatsisartutlov om beskatning af visse kapitalafkast']
    text27 = ['GL Sted/tlf', 'Sted/tlf']
    text28 = ['GL Dato', 'Dato']
    text29 = ['GL Underskrift', 'Underskrift']
    text30 = ['GL Indsendes sammen med Selvangivelsen S1/S1U', 'Indsendes sammen med Selvangivelsen S1/S1U']
    text_yes = ['Aap', 'Ja']
    text_no = ['GL nej', 'Nej']

    tax_year = '-'
    tax_return_date_limit = '-'
    person_number = '-'
    reciever_name = '-'
    reciever_address = '-'
    reciever_postnumber = '-'
    sender_name = '-'
    sender_address = '-'
    sender_postnumber = '-'
    nemid_kode = '-'
    policys = ['']

    def set_parameters(self, tax_year='-', tax_return_date_limit='', person_number='-', reciever_name='',
                       reciever_address='', reciever_postnumber='', sender_name='',
                       sender_address='', sender_postnumber='', nemid_kode='', policys=['']):
        self.tax_year = tax_year
        self.tax_return_date_limit = tax_return_date_limit
        self.person_number = person_number
        self.reciever_name = reciever_name
        self.reciever_address = reciever_address
        self.reciever_postnumber = reciever_postnumber
        self.sender_name = sender_name
        self.sender_address = sender_address
        self.sender_postnumber = sender_postnumber
        self.nemid_kode = nemid_kode
        self.policys = policys

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
        self.set_xy(105.0, 8.0)
        self.cell(h=self.contact_info_table_cell_height, align='R', w=75.0, txt=self.document_header[language],
                  border=0)

        self.set_font('arial', '', 13.0)
        self.set_xy(20.0, 8.0)
        self.cell(h=self.contact_info_table_cell_height, align='L', w=75.0,
                  txt=self.text2[language]+self.tax_year, border=0)

        self.set_font('arial', '', 10.0)
        self.set_xy(20.0, 12.0)
        self.cell(ln=0, h=22.0, align='L', w=75.0, txt=self.text3[language], border=0)
        self.set_xy(20.0, 15.0)
        self.cell(h=self.contact_info_table_cell_height, align='L', w=75.0,
                  txt=self.text4[language]+self.tax_return_date_limit, border=0)

        self.set_font('arial', '', 8.5)
        # Adressing reciever
        self.set_xy(self.address_field_x_pos, self.address_field_y_pos)
        self.multi_cell(self.address_field_width, 3, border=0,
                        txt=self.reciever_name+"\n"+self.reciever_address+"\n"+self.reciever_postnumber)

        # Adressing department
        self.set_xy(self.address_field_x_pos, self.address_field_y_pos+12)
        self.multi_cell(self.address_field_width, 3, border=0,
                        txt=self.sender_name+"\n"+self.sender_address+"\n"+self.sender_postnumber)
        self.line(self.address_field_x_pos, self.address_field_y_pos+12, self.address_field_x_pos+self.address_field_width-30, self.address_field_y_pos+22)
        self.line(self.address_field_x_pos, self.address_field_y_pos+22, self.address_field_x_pos+self.address_field_width-30, self.address_field_y_pos+12)

        self.set_xy(self.contact_info_table_x_pos, self.contact_info_table_y_pos)
        self.cell(h=self.contact_info_table_cell_height, align='L', w=self.contact_info_table_cell_width,
                  txt=self.text5[language], border=1)
        self.set_xy(self.contact_info_table_x_pos, self.contact_info_table_y_pos+self.contact_info_table_cell_height)
        self.cell(h=self.contact_info_table_cell_height, align='L', w=self.contact_info_table_cell_width,
                  txt=self.text6[language], border=1)

        self.set_xy(self.contact_info_table_x_pos+self.contact_info_table_cell_width, self.contact_info_table_y_pos)
        self.cell(h=self.contact_info_table_cell_height, align='L', w=self.contact_info_table_cell_width,
                  txt=self.person_number, border=1)
        self.set_xy(self.contact_info_table_x_pos+self.contact_info_table_cell_width,
                    self.contact_info_table_y_pos+self.contact_info_table_cell_height)
        self.cell(h=self.contact_info_table_cell_height, align='L', w=self.contact_info_table_cell_width,
                  txt='15,3%', border=1)
        self.set_xy(self.contact_info_table_x_pos, self.contact_info_table_y_pos+2*self.contact_info_table_cell_height)
        self.cell(h=self.contact_info_table_cell_height, align='L', w=2*self.contact_info_table_cell_width,
                  txt=self.text7[language], border=1)

        self.set_xy(self.contact_info_table_x_pos, self.contact_info_table_y_pos+3*self.contact_info_table_cell_height)
        self.cell(h=self.contact_info_table_cell_height, align='L', w=self.contact_info_table_cell_width,
                  txt=self.text8[language], border=1)
        self.set_xy(self.contact_info_table_x_pos, self.contact_info_table_y_pos+4*self.contact_info_table_cell_height)
        self.cell(h=self.contact_info_table_cell_height, align='L', w=self.contact_info_table_cell_width,
                  txt='www.silisivik.gl', border=1)
        self.set_xy(self.contact_info_table_x_pos, self.contact_info_table_y_pos+5*self.contact_info_table_cell_height)
        self.cell(h=self.contact_info_table_cell_height, align='L', w=self.contact_info_table_cell_width,
                  txt='www.aka.gl', border=1)

        self.set_xy(self.contact_info_table_x_pos+self.contact_info_table_cell_width,
                    self.contact_info_table_y_pos+3*self.contact_info_table_cell_height)
        self.cell(h=self.contact_info_table_cell_height, align='L', w=self.contact_info_table_cell_width,
                  txt=self.text9[language], border=1)
        self.set_xy(self.contact_info_table_x_pos+self.contact_info_table_cell_width,
                    self.contact_info_table_y_pos+4*self.contact_info_table_cell_height)
        self.cell(h=self.contact_info_table_cell_height, align='L', w=self.contact_info_table_cell_width,
                  txt=self.nemid_kode, border=1)

        self.yposition = 80
        self.set_xy(self.left_margin, self.yposition)

        self.cell(h=self.element_height_1, align='L', w=170.0,
                  txt=self.text10[language], border=1)
        self.yposition += self.element_height_1

        elementheight = self.element_height_2
        self.set_xy(self.left_margin, self.yposition)
        self.rect(self.left_margin, self.yposition, self.std_document_width, elementheight)
        self.multi_cell(self.std_document_width, 5, self.text11[language], 0)
        self.yposition += elementheight

        elementheight = self.element_height_3
        self.set_xy(self.left_margin, self.yposition)
        self.rect(self.left_margin, self.yposition, self.std_document_width, elementheight)
        self.multi_cell(self.std_document_width, 5, self.text12[language], 0)
        self.yposition += elementheight

        elementheight = self.element_height_4
        self.set_xy(self.left_margin, self.yposition)
        self.rect(self.left_margin, self.yposition, self.std_document_width, elementheight)
        self.multi_cell(self.std_document_width, 5, self.text13[language], 0)
        self.yposition += elementheight

        elementheight = self.element_height_5
        self.set_xy(self.left_margin, self.yposition)
        self.rect(self.left_margin, self.yposition, self.std_document_width, elementheight)
        self.multi_cell(self.std_document_width, 5, self.text14[language], 0)
        self.yposition += elementheight

        self.set_font('arial', '', 8.5)
        self.yposition += 15

        elementheight = 5

        self.set_xy(self.left_margin, self.yposition)
        self.cell(h=elementheight, align='L', w=75.0, txt=self.text15[language], border=0)
        self.set_xy(80.0, self.yposition)
        self.cell(h=elementheight, align='L', w=75.0, txt=self.text16[language], border=0)
        self.set_xy(120.0, self.yposition)
        self.cell(h=elementheight, align='L', w=75.0, txt=self.text17[language], border=0)
        self.set_xy(160.0, self.yposition)
        self.cell(h=elementheight, align='L', w=75.0, txt=self.text18[language], border=0)
        self.yposition += elementheight

        self.yposition += 10

        for policy in self.policys:
            self.set_font('arial', '', 8.5)
            self.set_xy(self.left_margin, self.yposition)
            self.cell(h=elementheight, align='L', w=75.0, txt=policy, border=0)

            self.set_xy(160.0, self.yposition)
            self.cell(h=elementheight, align='L', w=75.0, txt='201', border=0)
            self.yposition += elementheight

            self.line(80, self.yposition, 110, self.yposition)
            self.line(120, self.yposition, 150, self.yposition)
            self.yposition += 20

        self.set_font('arial', '', 8.5)
        self.set_xy(self.left_margin, self.yposition)
        self.cell(h=elementheight, align='L', w=75.0, txt='', border=0)
        self.set_xy(self.left_margin, self.yposition)
        self.cell(h=elementheight, align='L', w=75.0, txt=self.text19[language], border=0)

        self.set_xy(50, self.yposition)
        self.multi_cell(60, 3, self.text20[language], 0)

        self.set_xy(120.0, self.yposition-10)
        self.cell(h=elementheight, align='L', w=75.0, txt=self.text21[language], border=0)
        self.line(120, self.yposition+5, 150, self.yposition+5)
        self.set_xy(160.0, self.yposition)
        self.cell(h=elementheight, align='L', w=75.0, txt='205', border=0)
        self.yposition += elementheight

        self.yposition += 20

        elementheight = 15
        self.set_xy(self.left_margin, self.yposition)
        self.rect(self.left_margin, self.yposition, 170.0, elementheight)
        self.cell(h=elementheight, align='L', w=75.0,
                  txt=self.text22[language], border=1)
        self.set_xy(110, self.yposition)
        self.cell(h=elementheight, align='L', w=75.0, txt=self.text_yes[language], border=0)
        self.set_xy(150, self.yposition)
        self.cell(h=elementheight, align='L', w=75.0, txt=self.text_no[language], border=0)
        self.rect(120.0, self.yposition+5, 5, 5)
        self.rect(160.0, self.yposition+5, 5, 5)
        self.yposition += elementheight

        self.yposition += 30

        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(30, 3, self.text23[language], 0)

        self.set_xy(50, self.yposition)
        self.multi_cell(60, 3, self.text24[language], 0)

        elementheight = 25
        self.set_xy(120.0, self.yposition-10)
        self.cell(h=elementheight-25, align='L', w=75.0, txt=self.text25[language], border=0)
        self.line(120, self.yposition+5, 150, self.yposition+5)
        self.set_xy(160.0, self.yposition)
        self.cell(h=elementheight-20, align='L', w=75.0, txt='208', border=0)
        self.yposition += elementheight

        elementheight = 30
        self.set_xy(self.left_margin, self.yposition)
        self.rect(self.left_margin, self.yposition, self.std_document_width, elementheight)
        self.cell(h=10, align='L', w=self.std_document_width,
                  txt=self.text26[language], border=1)
        self.set_xy(self.left_margin, self.yposition+10)
        self.cell(h=10, align='L', w=56.0, txt=self.text27[language], border=1)
        self.set_xy(self.left_margin+56, self.yposition+10)
        self.cell(h=10, align='L', w=56.0, txt=self.text28[language], border=1)
        self.set_xy(self.left_margin+56+56, self.yposition+10)
        self.cell(h=10, align='L', w=58.0, txt=self.text29[language], border=1)
        self.set_xy(self.left_margin, self.yposition+20)
        self.cell(h=10, w=56.0, border=1)
        self.set_xy(self.left_margin+56, self.yposition+20)
        self.cell(h=10, w=56.0, border=1)
        self.set_xy(self.left_margin+56+56, self.yposition+20)
        self.cell(h=10, w=58.0, border=1)
        self.yposition += elementheight

        self.yposition += 10

        self.set_font('helvetica', '', 13.0)
        self.set_xy(self.left_margin, self.yposition)
        self.cell(h=10, align='L', w=self.std_document_width, txt=self.text30[language], border=0)

    def write_tax_slip_to_disk(self, path):
        self.output(path, 'F')


def main():
    tax_slip = TaxPDF()
    tax_slip.set_parameters("2020", '1. maj 2020', '1234567890', 'Mads Møller Johansen', 'Sanamut aqqut 21, lejl 102',
                            '3900 Nuuk', 'Skattestyrelsen', 'Postboks 1605', '3900 Nuuk', '1234',
                            ['ATP-12345678', 'PFA-12345678', 'Something else-12345678'])
    tax_slip.print_tax_slip(0)
    tax_slip.print_tax_slip(1)
    tax_slip.write_tax_slip_to_disk('./invoice.pdf')
    if sys.platform.startswith("linux"):
        os.system("xdg-open ./invoice.pdf")
    else:
        os.system("./invoice.pdf")


if __name__ == "__main__":
    main()
