# -*- coding: iso-8859-1 -*-

import os
from fpdf import FPDF


modtagernavn = 'Mads Møller Johansen'
modtagernadd = 'Sanamut aqqut 21, lejl 102'
modtagerpostnummer = '3900 Nuuk'

afsnavn = 'Skattestyrelsen'
afsadd = 'Postboks 1605'
afspostnummer = '3900 Nuuk'

personnummer = '1234567890'
nemidkode = '1234'

pdf = FPDF()
pdf.add_page()

pdf.set_font('helvetica', 'B', 15.0)
pdf.set_xy(105.0, 8.0)
pdf.cell(ln=0, h=22.0, align='R', w=75.0, txt='Bilag til S1/S1U', border=0)

pdf.set_font('helvetica', '', 13.0)
pdf.set_xy(20.0, 8.0)
pdf.cell(ln=0, h=22.0, align='L', w=75.0, txt='Bilag til Selvangivelse for 2019', border=0)

pdf.set_font('helvetica', '', 10.0)
pdf.set_xy(20.0, 12.0)
pdf.cell(ln=0, h=22.0, align='L', w=75.0, txt='Bilag vedrørende beskatning af visse kapitalafkast', border=0)
pdf.set_xy(20.0, 15.0)
pdf.cell(ln=0, h=22.0, align='L', w=75.0, txt='Indsendelsesfrist senest 1. maj 2020', border=0)


pdf.set_font('helvetica', '', 12.0)
#pdf.set_xy(105.0, 8.0)

spacing=1.5
col_width = pdf.w / 3.25
row_height = pdf.font_size
item = "bla bla bla"

#Adressing
pdf.set_xy(30.0, 37.0)
pdf.multi_cell(60,5,border=0,txt=modtagernavn+"\n"+modtagernadd+"\n"+modtagerpostnummer)


#Adressing
pdf.set_xy(30.0, 57.0)
pdf.multi_cell(60,5,border=0,txt=afsnavn+"\n"+afsadd+"\n"+afspostnummer)
pdf.line(30,57,90,72);
pdf.line(30,72,90,57);



pdf.set_xy(100.0, 27.0)
pdf.cell(ln=0, h=5.0, align='L', w=40.0, txt='Personnummer: ', border=1)
pdf.set_xy(100.0, 32.0)
pdf.cell(ln=1, h=5.0, align='L', w=40.0, txt='Kapitalafkastskat: ', border=1)

pdf.set_xy(140.0, 27.0)
pdf.cell(ln=0, h=5.0, align='L', w=40.0, txt=personnummer, border=1)
pdf.set_xy(140.0, 32.0)
pdf.cell(ln=0, h=5.0, align='L', w=40.0, txt='15,3%', border=1)
pdf.set_xy(100.0, 37.0)
pdf.cell(ln=0, h=5.0, align='L', w=80.0, txt='Selvbetjeningsinformation', border=1)

pdf.set_xy(100.0, 42.0)
pdf.cell(ln=0, h=5.0, align='L', w=40.0, txt='Tast selv internet', border=1)
pdf.set_xy(100.0, 47.0)
pdf.cell(ln=0, h=5.0, align='L', w=40.0, txt='www.silisivik.gl', border=1)
pdf.set_xy(100.0, 52.0)
pdf.cell(ln=0, h=5.0, align='L', w=40.0, txt='www.aka.gl', border=1)

pdf.set_xy(140.0, 42.0)
pdf.cell(ln=0, h=5.0, align='L', w=40.0, txt='Tast selv kode', border=1)
pdf.set_xy(140.0, 47.0)
pdf.cell(ln=1, h=5.0, align='L', w=40.0, txt=nemidkode, border=1)
pdf.set_xy(100.0, 52.0)

pdf.set_xy(15.0, 95.0)

pdf.cell(ln=0, h=5.0, align='L', w=170.0, txt='Vejledning til bilag vedrørende beskatning af visse kapitalafkast', border=1)

yposition = 100;
elementheight = 40
pdf.set_xy(15.0, yposition)
pdf.rect(15.0, yposition, 170.0, elementheight)
pdf.multi_cell(170, 5, "Lorem ipsum, or lipsum as it is sometimes known, is dummy text used in laying out print, graphic or web designs. The passage is attributed to an unknown typesetter in the 15th century who is thought to have scrambled parts of Cicero's De Finibus Bonorum et Malorum for use in a type specimen book.", 0)
yposition += elementheight

elementheight = 20
pdf.set_xy(15.0, yposition)
pdf.rect(15.0, yposition, 170.0, elementheight)
pdf.multi_cell(170, 5, "Hvis de er uneig i indholdet bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla", 0)
yposition += elementheight

elementheight = 30
pdf.set_xy(15.0, yposition)
pdf.rect(15.0, yposition, 170.0, elementheight)
pdf.multi_cell(170, 5, "Hvis de er uneig i indholdet bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla", 0)
yposition += elementheight

elementheight = 20
pdf.set_xy(15.0, yposition)
pdf.rect(15.0, yposition, 170.0, elementheight)
pdf.multi_cell(170, 5, "Hvis de er uneig i indholdet bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla", 0)


pdf.set_xy(15.0, pdf.h - 30)
pdf.cell(ln=0, h=5.0, align='L', w=40.0, txt=personnummer, border=0)



pdf.output('./invoice.pdf', 'F')

import sys
if sys.platform.startswith("linux"):
    os.system("xdg-open ./invoice.pdf")
else:
    os.system("./invoice.pdf")
