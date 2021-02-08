# -*- coding: iso-8859-1 -*-

import os
import sys
from fpdf import FPDF


class TaxPDF(FPDF):

    person_number = '-'
    reciever_name = '-'
    reciever_address = '-'
    reciever_postnumber = '-'
    sender_name = '-'
    sender_address = '-'
    sender_postnumber = '-'
    nemid_kode = '-'

    def set_parameters(self, person_number='-', reciever_name='', reciever_address='', reciever_postnumber='', sender_name='',
                       sender_address='', sender_postnumber='', nemid_kode=''):
        self.person_number = person_number
        self.reciever_name = reciever_name
        self.reciever_address = reciever_address
        self.reciever_postnumber = reciever_postnumber
        self.sender_name = sender_name
        self.sender_address = sender_address
        self.sender_postnumber = sender_postnumber
        self.nemid_kode = nemid_kode

    def footer(self):
        self.set_xy(15.0, self.h - 30)
        self.cell(ln=0, h=5.0, align='C', w=30.0, txt=self.person_number, border=0)

    def print_tax_slip(self):

        self.add_page()

        self.set_font('helvetica', 'B', 15.0)
        self.set_xy(105.0, 8.0)
        self.cell(ln=0, h=22.0, align='R', w=75.0, txt='Bilag til S1/S1U', border=0)

        self.set_font('helvetica', '', 13.0)
        self.set_xy(20.0, 8.0)
        self.cell(ln=0, h=22.0, align='L', w=75.0, txt='Bilag til Selvangivelse for 2019', border=0)

        self.set_font('helvetica', '', 10.0)
        self.set_xy(20.0, 12.0)
        self.cell(ln=0, h=22.0, align='L', w=75.0, txt='Bilag vedrørende beskatning af visse kapitalafkast', border=0)
        self.set_xy(20.0, 15.0)
        self.cell(ln=0, h=22.0, align='L', w=75.0, txt='Indsendelsesfrist senest 1. maj 2020', border=0)

        self.set_font('helvetica', '', 12.0)

        # Adressing reciever
        self.set_xy(30.0, 37.0)
        self.multi_cell(60, 5, border=0, txt=self.reciever_name+"\n"+self.reciever_address+"\n"+self.reciever_postnumber)

        # Adressing department
        self.set_xy(30.0, 57.0)
        self.multi_cell(60, 5, border=0, txt=self.sender_name+"\n"+self.sender_address+"\n"+self.sender_postnumber)
        self.line(30, 57, 90, 72)
        self.line(30, 72, 90, 57)

        self.set_xy(100.0, 27.0)
        self.rotate = 10
        self.cell(ln=0, h=5.0, align='L', w=40.0, txt='Personnummer: ', border=1)
        self.set_xy(100.0, 32.0)
        self.cell(ln=1, h=5.0, align='L', w=40.0, txt='Kapitalafkastskat: ', border=1)

        self.set_xy(140.0, 27.0)
        self.cell(ln=0, h=5.0, align='L', w=40.0, txt=self.person_number, border=1)
        self.set_xy(140.0, 32.0)
        self.cell(ln=0, h=5.0, align='L', w=40.0, txt='15,3%', border=1)
        self.set_xy(100.0, 37.0)
        self.cell(ln=0, h=5.0, align='L', w=80.0, txt='Selvbetjeningsinformation', border=1)

        self.set_xy(100.0, 42.0)
        self.cell(ln=0, h=5.0, align='L', w=40.0, txt='Tast selv internet', border=1)
        self.set_xy(100.0, 47.0)
        self.cell(ln=0, h=5.0, align='L', w=40.0, txt='www.silisivik.gl', border=1)
        self.set_xy(100.0, 52.0)
        self.cell(ln=0, h=5.0, align='L', w=40.0, txt='www.aka.gl', border=1)

        self.set_xy(140.0, 42.0)
        self.cell(ln=0, h=5.0, align='L', w=40.0, txt='Tast selv kode', border=1)
        self.set_xy(140.0, 47.0)
        self.cell(ln=1, h=5.0, align='L', w=40.0, txt=self.nemid_kode, border=1)
        self.set_xy(100.0, 52.0)

        self.set_xy(15.0, 95.0)

        self.cell(ln=0, h=5.0, align='L', w=170.0,
                  txt='Vejledning til bilag vedrørende beskatning af visse kapitalafkast', border=1)

        yposition = 100
        elementheight = 40
        self.set_xy(15.0, yposition)
        self.rect(15.0, yposition, 170.0, elementheight)
        self.multi_cell(170, 5, "Lorem ipsum, or lipsum as it is sometimes known, is dummy text used in laying out "
                                "print, graphic or web designs. The passage is attributed to an unknown typesetter in "
                                "the 15th century who is thought to have scrambled parts of Cicero's De Finibus "
                                "Bonorum et Malorum for use in a type specimen book.", 0)
        yposition += elementheight

        elementheight = 15
        self.set_xy(15.0, yposition)
        self.rect(15.0, yposition, 170.0, elementheight)
        self.multi_cell(170, 5, "Hvis de er uneig i indholdet bla bla bla bla bla bla bla bla bla bla bla bla bla "
                                "bla bla bla bla bla bla bla bla bla bla", 0)
        yposition += elementheight

        elementheight = 30
        self.set_xy(15.0, yposition)
        self.rect(15.0, yposition, 170.0, elementheight)
        self.multi_cell(170, 5, "Hvis de er uneig i indholdet bla bla bla bla bla bla bla bla bla bla bla bla "
                                "bla bla bla bla bla bla bla bla bla bla bla", 0)
        yposition += elementheight

        elementheight = 15
        self.set_xy(15.0, yposition)
        self.rect(15.0, yposition, 170.0, elementheight)
        self.multi_cell(170, 5, "Hvis de er uneig i indholdet bla bla bla bla bla bla bla bla bla bla bla bla "
                                "bla bla bla bla bla bla bla bla bla bla bla", 0)
        yposition += elementheight

        self.set_font('helvetica', '', 10.0)
        yposition += 15

        elementheight = 5

        self.set_xy(80.0, yposition)
        self.cell(ln=0, h=elementheight, align='L', w=75.0, txt='Beløb i kroner', border=0)
        self.set_xy(120.0, yposition)
        self.cell(ln=0, h=elementheight, align='L', w=75.0, txt='Beløb i kroner', border=0)
        self.set_xy(160.0, yposition)
        self.cell(ln=0, h=elementheight, align='L', w=75.0, txt='Felt nr.', border=0)

        yposition += elementheight

        yposition += 10

        self.set_xy(15.0, yposition)
        self.cell(ln=0, h=elementheight, align='L', w=75.0, txt='Kapitalafkast  PBL (DK) 	§ 53 A', border=0)

        self.set_xy(160.0, yposition)
        self.cell(ln=0, h=elementheight, align='L', w=75.0, txt='201', border=0)

        yposition += elementheight

        self.line(15, yposition, 60, yposition)
        self.line(80, yposition, 110, yposition)
        self.line(120, yposition, 150, yposition)

        self.output('./invoice.pdf', 'F')


if sys.platform.startswith("linux"):
    os.system("xdg-open ./invoice.pdf")
else:
    os.system("./invoice.pdf")


foo = TaxPDF()
foo.set_parameters('1234567890', 'Mads Møller Johansen', 'Sanamut aqqut 21, lejl 102',
                   '3900 Nuuk', 'Skattestyrelsen', 'Postboks 1605', '3900 Nuuk', '1234')
foo.print_tax_slip()
