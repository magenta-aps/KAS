# -*- coding: utf-8 -*-

import os
import sys
from fpdf import FPDF


class TaxPDF(FPDF):

    right_margin = 170
    left_margin = 15.0
    contact_info_table_cell_height = 5.0
    contact_info_table_cell_width = 40.0

    contact_info_table_x_pos = 100.0
    contact_info_table_y_pos = 27.0

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

    def set_parameters(self, tax_year='-', tax_return_date_limit='', person_number='-', reciever_name='',
                       reciever_address='', reciever_postnumber='', sender_name='',
                       sender_address='', sender_postnumber='', nemid_kode=''):
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

    def footer(self):
        self.set_xy(self.left_margin, self.h - 30)
        self.cell(h=5.0, align='C', w=30.0, txt=self.person_number, border=0)

    def add_page(self):
        super().add_page()
        self.yposition = 40

    def print_tax_slip(self):

        self.add_page()

        self.set_font('helvetica', 'B', 15.0)
        self.set_xy(105.0, 8.0)
        self.cell(h=self.contact_info_table_cell_height, align='R', w=75.0, txt='Bilag til S1/S1U', border=0)

        self.set_font('helvetica', '', 13.0)
        self.set_xy(20.0, 8.0)
        self.cell(h=self.contact_info_table_cell_height, align='L', w=75.0,
                  txt='Bilag til Selvangivelse for '+self.tax_year, border=0)

        self.set_font('helvetica', '', 10.0)
        self.set_xy(20.0, 12.0)
        self.cell(ln=0, h=22.0, align='L', w=75.0, txt='Bilag vedrørende beskatning af visse kapitalafkast', border=0)
        self.set_xy(20.0, 15.0)
        self.cell(h=self.contact_info_table_cell_height, align='L', w=75.0,
                  txt='Indsendelsesfrist senest '+self.tax_return_date_limit, border=0)

        self.set_font('helvetica', '', 10)
        # Adressing reciever
        self.set_xy(30.0, 37.0)
        self.multi_cell(60, 5, border=0,
                        txt=self.reciever_name+"\n"+self.reciever_address+"\n"+self.reciever_postnumber)

        # Adressing department
        self.set_xy(30.0, 57.0)
        self.multi_cell(60, 5, border=0, txt=self.sender_name+"\n"+self.sender_address+"\n"+self.sender_postnumber)
        self.line(30, 57, 90, 72)
        self.line(30, 72, 90, 57)

        self.set_xy(self.contact_info_table_x_pos, self.contact_info_table_y_pos)
        self.cell(h=self.contact_info_table_cell_height, align='L', w=self.contact_info_table_cell_width,
                  txt='Personnummer: ', border=1)
        self.set_xy(self.contact_info_table_x_pos, self.contact_info_table_y_pos+self.contact_info_table_cell_height)
        self.cell(h=self.contact_info_table_cell_height, align='L', w=self.contact_info_table_cell_width,
                  txt='Kapitalafkastskat: ', border=1)

        self.set_xy(self.contact_info_table_x_pos+self.contact_info_table_cell_width, self.contact_info_table_y_pos)
        self.cell(h=self.contact_info_table_cell_height, align='L', w=self.contact_info_table_cell_width,
                  txt=self.person_number, border=1)
        self.set_xy(self.contact_info_table_x_pos+self.contact_info_table_cell_width,
                    self.contact_info_table_y_pos+self.contact_info_table_cell_height)
        self.cell(h=self.contact_info_table_cell_height, align='L', w=self.contact_info_table_cell_width,
                  txt='15,3%', border=1)
        self.set_xy(self.contact_info_table_x_pos, self.contact_info_table_y_pos+2*self.contact_info_table_cell_height)
        self.cell(h=self.contact_info_table_cell_height, align='L', w=2*self.contact_info_table_cell_width,
                  txt='Selvbetjeningsinformation', border=1)

        self.set_xy(self.contact_info_table_x_pos, self.contact_info_table_y_pos+3*self.contact_info_table_cell_height)
        self.cell(h=self.contact_info_table_cell_height, align='L', w=self.contact_info_table_cell_width,
                  txt='Tast selv internet', border=1)
        self.set_xy(self.contact_info_table_x_pos, self.contact_info_table_y_pos+4*self.contact_info_table_cell_height)
        self.cell(h=self.contact_info_table_cell_height, align='L', w=self.contact_info_table_cell_width,
                  txt='www.silisivik.gl', border=1)
        self.set_xy(self.contact_info_table_x_pos, self.contact_info_table_y_pos+5*self.contact_info_table_cell_height)
        self.cell(h=self.contact_info_table_cell_height, align='L', w=self.contact_info_table_cell_width,
                  txt='www.aka.gl', border=1)

        self.set_xy(self.contact_info_table_x_pos+self.contact_info_table_cell_width,
                    self.contact_info_table_y_pos+3*self.contact_info_table_cell_height)
        self.cell(h=self.contact_info_table_cell_height, align='L', w=self.contact_info_table_cell_width,
                  txt='Tast selv kode', border=1)
        self.set_xy(self.contact_info_table_x_pos+self.contact_info_table_cell_width,
                    self.contact_info_table_y_pos+4*self.contact_info_table_cell_height)
        self.cell(h=self.contact_info_table_cell_height, align='L', w=self.contact_info_table_cell_width,
                  txt=self.nemid_kode, border=1)

        self.set_xy(self.left_margin, 95.0)

        self.cell(h=5.0, align='L', w=170.0,
                  txt='Vejledning til bilag vedrørende beskatning af visse kapitalafkast', border=1)

        self.yposition = 100
        elementheight = 40
        self.set_xy(15.0, self.yposition)
        self.rect(self.left_margin, self.yposition, self.right_margin, elementheight)
        self.multi_cell(170, 5, "Lorem ipsum, or lipsum as it is sometimes known, is dummy text used in laying out "
                                "print, graphic or web designs. The passage is attributed to an unknown typesetter in "
                                "the 15th century who is thought to have scrambled parts of Cicero's De Finibus "
                                "Bonorum et Malorum for use in a type specimen book.", 0)
        self.yposition += elementheight

        elementheight = 15
        self.set_xy(self.left_margin, self.yposition)
        self.rect(self.left_margin, self.yposition, self.right_margin, elementheight)
        self.multi_cell(170, 5, "Hvis de er uneig i indholdet bla bla bla bla bla bla bla bla bla bla bla bla bla "
                                "bla bla bla bla bla bla bla bla bla bla", 0)
        self.yposition += elementheight

        elementheight = 30
        self.set_xy(self.left_margin, self.yposition)
        self.rect(self.left_margin, self.yposition, self.right_margin, elementheight)
        self.multi_cell(170, 5, "Hvis de er uneig i indholdet bla bla bla bla bla bla bla bla bla bla bla bla "
                                "bla bla bla bla bla bla bla bla bla bla bla", 0)
        self.yposition += elementheight

        elementheight = 15
        self.set_xy(self.left_margin, self.yposition)
        self.rect(self.left_margin, self.yposition, self.right_margin, elementheight)
        self.multi_cell(170, 5, "Hvis de er uneig i indholdet bla bla bla bla bla bla bla bla bla bla bla bla "
                                "bla bla bla bla bla bla bla bla bla bla bla", 0)
        self.yposition += elementheight

        self.set_font('helvetica', '', 8.5)
        self.yposition += 15

        elementheight = 5

        self.set_xy(80.0, self.yposition)
        self.cell(h=elementheight, align='L', w=75.0, txt='Beløb i kroner', border=0)
        self.set_xy(120.0, self.yposition)
        self.cell(h=elementheight, align='L', w=75.0, txt='Beløb i kroner', border=0)
        self.set_xy(160.0, self.yposition)
        self.cell(h=elementheight, align='L', w=75.0, txt='Felt nr.', border=0)
        self.yposition += elementheight

        self.yposition += 10

        self.set_xy(self.left_margin, self.yposition)
        self.cell(h=elementheight, align='L', w=75.0, txt='Kapitalafkast  PBL (DK) 	§ 53 A', border=0)

        self.set_xy(160.0, self.yposition)
        self.cell(h=elementheight, align='L', w=75.0, txt='201', border=0)
        self.yposition += elementheight

        self.line(15, self.yposition, 60, self.yposition)
        self.line(80, self.yposition, 110, self.yposition)
        self.line(120, self.yposition, 150, self.yposition)
        self.yposition += 20

        self.set_xy(self.left_margin, self.yposition)
        self.cell(h=elementheight, align='L', w=75.0, txt='Kapitalafkastskat', border=0)

        self.set_xy(50, self.yposition)
        self.multi_cell(60, 3, 'Har de betalt foreløbig bla bla bla bla bla bla bla bla bla '
                               'bla bla bla bla bla bla bla', 0)

        self.set_xy(120.0, self.yposition-10)
        self.cell(h=elementheight, align='L', w=75.0, txt='Beløb i kroner', border=0)
        self.line(120, self.yposition+5, 150, self.yposition+5)
        self.set_xy(160.0, self.yposition)
        self.cell(h=elementheight, align='L', w=75.0, txt='205', border=0)

        self.add_page()

        elementheight = 15
        self.set_xy(self.left_margin, self.yposition)
        self.rect(self.left_margin, self.yposition, 170.0, elementheight)
        self.cell(h=elementheight, align='L', w=75.0,
                  txt='Er kapitalafkastskatten hævet fra pensionsordning?', border=1)
        self.set_xy(110, self.yposition)
        self.cell(h=elementheight, align='L', w=75.0, txt='Ja', border=0)
        self.set_xy(150, self.yposition)
        self.cell(h=elementheight, align='L', w=75.0, txt='Nej', border=0)
        self.rect(120.0, self.yposition+5, 5, 5)
        self.rect(160.0, self.yposition+5, 5, 5)
        self.yposition += elementheight

        self.yposition += 30

        self.set_xy(self.left_margin, self.yposition)
        self.multi_cell(30, 3, 'Kapitalafkastskat i udlandet', 0)

        self.set_xy(50, self.yposition)
        self.multi_cell(60, 3, 'Anmoder de om nedslag bla bla bla bla bla bla bla bla bla '
                               'bla bla bla bla bla bla bla', 0)

        elementheight = 25
        self.set_xy(120.0, self.yposition-10)
        self.cell(h=elementheight-25, align='L', w=75.0, txt='Beløb i kroner', border=0)
        self.line(120, self.yposition+5, 150, self.yposition+5)
        self.set_xy(160.0, self.yposition)
        self.cell(h=elementheight-20, align='L', w=75.0, txt='208', border=0)
        self.yposition += elementheight

        elementheight = 30
        self.set_xy(self.left_margin, self.yposition)
        self.rect(self.left_margin, self.yposition, self.right_margin, elementheight)
        self.cell(h=10, align='L', w=self.right_margin,
                  txt='Oplysninger afgives under ansvar i henhold til bestemmelserne i § 9 i '
                      'Inatsisartutlov om beskatning af visse kapitalafkast', border=1)
        self.set_xy(self.left_margin, self.yposition+10)
        self.cell(h=10, align='L', w=56.0, txt='Sted/tlf', border=1)
        self.set_xy(self.left_margin+56, self.yposition+10)
        self.cell(h=10, align='L', w=56.0, txt='Dato', border=1)
        self.set_xy(self.left_margin+56+56, self.yposition+10)
        self.cell(h=10, align='L', w=58.0, txt='Underskrift', border=1)
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
        self.cell(h=10, align='L', w=self.right_margin, txt='Indsendes sammen med Selvangivelsen S1/S1U', border=0)

        self.output('./invoice.pdf', 'F')


def main():
    tax_slip = TaxPDF()
    tax_slip.set_parameters("2020", '1. maj 2020', '1234567890', 'Mads Møller Johansen', 'Sanamut aqqut 21, lejl 102',
                            '3900 Nuuk', 'Skattestyrelsen', 'Postboks 1605', '3900 Nuuk', '1234')
    tax_slip.print_tax_slip()
    if sys.platform.startswith("linux"):
        os.system("xdg-open ./invoice.pdf")
    else:
        os.system("./invoice.pdf")


if __name__ == "__main__":
    main()
