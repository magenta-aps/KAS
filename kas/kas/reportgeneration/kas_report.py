# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.files.base import ContentFile
from fpdf import FPDF

from kas.models import PersonTaxYear, PolicyTaxYear, TaxSlipGenerated


class TaxPDF(FPDF):
    std_document_width = 171
    left_margin = 17.0
    default_line_width = 0.2

    contact_info_table_cell = {"h": 5, "w": 50}
    contact_info_table = {"x": 90.0, "y": 27.0}
    address_field = {"w": 70, "x": 17, "y": 37}
    signature_table_cell = {"w": 57, "h": 10}

    element_height_1 = 5
    element_height_2 = 60
    element_height_3 = 15
    element_height_4 = 30
    element_height_5 = 15

    sender_name = "Skattestyrelsen"
    sender_address = "Postboks 1605"
    sender_postnumber = "3900 Nuuk"

    document_header = {"gl": "", "dk": ""}

    text2 = {
        "gl": "Soraarnerussutisiaqarnissamut aaqqissuussinerit nunani allaniittut ilaat pillugit nammineerluni "
        "nalunaarsuineq {}",
        "dk": "Selvangivelse af visse udenlandske pensionsordninger for {}",
    }
    text4 = {
        "gl": "Nassitsinissamut killissarititaq {}",
        "dk": "Indsendelsesfrist senest {}",
    }
    text5 = {"gl": "Inuup normua: ", "dk": "Personnummer: "}
    text6 = {"gl": "Pigisanit pissarsiat akileraarutaat: ", "dk": "Kapitalafkastskat: "}
    text7 = {
        "gl": "Attavissaq: Akileraartarnermut Aqutsisoqarfik, \nPostboks 1605, 3900 Nuuk. \nTlf. 346510, "
        "E-mail:tax@nanoq.gl",
        "dk": "Kontakt: Skattestyrelsen,\nPostboks 1605, 3900 Nuuk. \nTlf. 346510, Email:tax@nanoq.gl",
    }
    text8 = {"gl": "Nittartagaq iserfissaq", "dk": "Tast selv internet"}
    text8A = {"gl": "Ullut akileraartussaaffiit", "dk": "Antal skattepligtsdage"}
    text10 = {
        "gl": "Soraarnerussutisiaqarnissamut aaqqissuussinerit nunani allaniittut ilaat pillugit nammineerluni "
        "nalunaarsuineq.",
        "dk": "Selvangivelse af visse udenlandske pensionsordninger.",
    }
    text11 = {
        "gl": "Danskit soraarnerussutisiaqarnissamut sillimmasiisarfiini aamma soraarnerussutisiaqarnissamut "
        "aningaasaateqarfiini inuunermut sillimmasiissutivit soraarnerussutisiaqarnissamullu "
        "aaqqissuussavit ukiumi pineqartumi iluanaarutaat, kiisalu soraarnerussutisiaqarnissamut "
        "aaqqissuussinernut nunani allaniittunut illit namminerisamik akiliutitit "
        "nammineerluni nalunaarsuiffimmi uani nalunaarsussavatit. ",
        "dk": "I denne selvangivelse skal du oplyse årets afkast fra dine livsforsikringer og pensionsordninger "
        "i danske pensionsforsikringsselskaber og pensionskasser, samt dine private indbetalinger til "
        "udenlandske pensionsordninger.",
    }
    text12 = {
        "gl": "Soraarnerussutisiaqarnissamut aaqqissuussinermut Kalaallit Nunaata avataaniittumut "
        "nammineerlutit akiliisimaguit akilersimasatit, soraarnerussutisiaqarnissamut aaqqissuussinernut "
        "nunani allaniittunut nammineerluni akiliutaasimasut nalunaarneqarfissaannut nammineerlutit "
        "nalunaarsussavatit. Paasissutissat taakku soraarnerussutisiaqarnissamut aaqqissuussinermut "
        "peqataasussaatitaaneq pillugu ukiumoortumik naatsorsuummi atorneqartussaapput.",
        "dk": "Indbetaler du selv til en pensionsordning uden for Grønland, skal du selvangive dine "
        "indbetalinger i feltet om egen indbetalinger til pensionsordninger i andre lande. Oplysningerne "
        "skal bruges til årsopgørelsen vedrørende obligatorisk pension.",
    }
    text13 = {
        "gl": "Taakku saniatigut nalunaarutissaraatit danskit soraarnerussutisiaqarnissamut "
        "sillimmasiisarfiini aamma soraarnerussutisiaqarnissamut aningaasaateqarfiini inuunermut "
        "sillimmasiissutivit soraarnerussutisiaqarnissamullu aaqqissuussavit ukiumi pineqartumi "
        "iluanaarutaat. Nalunaarutiginnittuussaanermi pineqanngillat soraarnerussutisiaqarnissamut "
        "aaqqissuussinerit inuunermullu sillimmasiissutit, danskit soraarnerussutisiaqarnissamut "
        "aaqqissuussinernit iluanaarutinik akileraarusiisarnermik inatsisaanni (PAL-lovimi) pineqartut. "
        "Illit soraarnerussutisiaqarnissamut aaqqissuussinerit inuunermulluunniit sillimmasiissutit "
        "danskit soraarnerussutisiaqarnissamut aaqqissuussinernit iluanaarutinik akileraarusiisarnermik "
        "inatsisaanni pineqartunut ilaanersoq nalornissutigigukku illit soraarnerussutisiaqarnissamut "
        "aningaasaateqarfigisat inuunermulluunniit sillimasiisarfigisat saaffigisinnaavat.",
        "dk": "Derudover skal du oplyse årets afkast fra dine livsforsikringer og pensionsordninger i danske "
        "pensionsforsikringsselskaber og pensionskasser. Oplysningspligten gælder ikke pensionsordninger "
        "og livsforsikringer, som omfattes af den danske pensionsafkastbeskatningslov (PAL-loven). "
        "Hvis du er i tvivl om din pensionsordning eller livsforsikring er omfattet af den danske "
        "pensionsafkastbeskatningslov kan du kontakte din pensionskasse eller dit livsforsikringsselskab.",
    }
    text13A = {"gl": "", "dk": ""}
    text13B = {
        "gl": "Nammineerluni nalunaarsuiffimmi uani paasissutissanik naqeriikkanik allassimasoqarpat, "
        "paasissutissat eqqortuunersut illit misissugassaraat. ",
        "dk": "Hvis der på denne selvangivelse er fortrykte oplysninger, skal du kontrollere om oplysningerne "
        "er rigtige. ",
    }
    text13C = {
        "gl": "Allanngortitassaappata ilassutissaqaruilluunniit nammineerluni nalunaarsuiffik immersussavat "
        "atsiorlugulu, kingusinnerpaamillu {} Akileraartarnermut Aqutsisoqarfimmut nassiullugu "
        "imaluunniit taakku www.sullissivik.gl-ikkut nalunaarutigalugit.",
        "dk": "Har du ændringer eller tilføjelser, skal du udfylde og underskrive selvangivelsen og indsende "
        "den til Skattestyrelsen eller indberette dem via www.sullissivik.gl senest den {}.",
    }
    text13D = {
        "gl": "Paasissutissat naqeriikkat isumaqatigigukkit ilassutissaqanngikkuillu qanoq "
        "iliuuseqartariaqanngilatit.",
        "dk": "Er du enig i de fortrykte oplysninger og har du ikke noget at tilføje, behøver du ikke at "
        "foretage dig yderligere.",
    }
    text13E = {
        "gl": "Akileraartarnermut Aqutsisoqarfiup soraarnerussutisiaqarnissamut aaqqissuussiviit ataasiakkaat, "
        "sullitamik pigisanit pissarsiat akileraarutaattut akiligassaannik unerartitsillutillu "
        "akiliussinissaat pillugu isumaqatigiissuteqarfigai. Akiliineq illit "
        "soraarnerussutisiaqarnissamut aaqqissuussivinnit isumagineqassappat tamanna ataani "
        "allassimassaaq. Taamaattoqartillugu pigisanit pissarsianit akileraarut illit nammineerlutit "
        "akilissanngilat. ",
        "dk": "Skattestyrelsen har indgået aftale med enkelte pensionsselskaber om, at de indeholder og "
        "indbetaler kapitalafkastskatten på vegne af deres kunder. Sker betalingen via dit "
        "pensionsselskab, fremgår det nedenfor. I disse tilfælde skal du ikke indbetale "
        "kapitalafkastskatten selv.",
    }
    text14 = {
        "gl": "Inuunermut sillimmasiissutinit soraarnerussutisiaqarnissamullu aaqqissuussinernit iluanaarutit "
        "pillugit inaarummik naatsorsuut {} Akileraartarnermut Aqutsisoqarfiup {}-mi augustip "
        "naalernerani nassiutissavaa.",
        "dk": "Du vil modtage slutopgørelse {} fra Skattestyrelsen ultimo august {}. ",
    }
    text15 = {
        "gl": "Pigisanit pissarsiat PBL (DK) § 53 A",
        "dk": "Kapitalafkast PBL (DK) § 53 A",
    }

    text17A = {"gl": "Immersugassap aqqa", "dk": "Feltnavn"}
    text17B = {"gl": "Naqeriigaq", "dk": "Fortrykt"}
    text17C = {
        "gl": "Soraarnerussutisiaqarnissamut aaqqissuussivik",
        "dk": "Pensionsselskab",
    }
    text17D = {"gl": "Policenormu", "dk": "Policenummer"}
    text17E = {"gl": "Nammineerluni nalunaarutigineqartoq", "dk": "Selvangivet"}
    text17F = {
        "gl": "Ullunut akileraarfinnut agguarneqarnera",
        "dk": "Forholdsmæssigt i skattepligtsperioden",
    }

    text18 = {"gl": "Immersugassap normua", "dk": "Felt nr."}
    text25 = {"gl": "Aningaasat koruuninngorlugit", "dk": "Beløb i kroner"}
    text26 = {
        "gl": "Paasissutissat Pigisanit pissarsiat ilaasa akileraaruserneqartarnerat pillugu Inatsisartut "
        "inatsisaanni § 9-mi aalajangersakkat malillugit akisussaassuseqarluni nalunaarneqartussaapput",
        "dk": "Oplysninger afgives under ansvar i henhold til bestemmelserne i § 9 i "
        "Inatsisartutlov om beskatning af visse kapitalafkast",
    }
    text26B = {
        "gl": "Soraarnerussutisiaqarnissamut aaqqissuussinernut nunani allaniittunut, Danmark ilanngullugu, nammineerluni akiliutit. "
        "Nuna soraarnerussutisiaqarnissamut aaqqissuussinerup pilersinneqarfia, kiisalu aningaasat "
        "akiliutigineqartut amerlassusiat nalunaakkit, uppernarsaat ilanngunneqassaq",
        "dk": "Privat indbetaling til pensionsordninger i andre lande, herunder Danmark. Angiv landet, som pensionsordningen er "
        "hjemmehørende i, samt størrelsen på det indbetalte beløb, dokumentation vedhæftes",
    }
    text26D = {
        "gl": "* Soraarnerussutisiaqarnissamut aaqqissuussinermut uunga tunngatillugu akileraarut "
        "soraarnerussutisiaqarnissamut aaqqissuussivimmit ingerlaannaartumik akilerneqassaaq",
        "dk": "* Skatten for denne pensionsordning betales automatisk af pensionsselskabet",
    }
    text26DA = {
        "gl": "Soraarnerussutisiaqarnissamut aaqqissuussinerit nunani allaniittut ilaannit iluanaarutit "
        "pillugit paasissutissat naqeriigaanngitsut uani nammineerlutit nalunaarutigisinnaavatit.",
        "dk": "Her kan du selvangive oplysninger om afkast af visse udenlandske pensionsordninger, "
        "som ikke er fortrykte.",
    }
    text26E = {
        "gl": "Soraarnerussutisiaqarnissamut aaqqissuussinerit nunani allaniittut ilaat pillugit "
        "nammineerluni nalunaarsuinermut atatillugu paasissutissanik allanik nammineerluni "
        "nalunaagassaqarpa?",
        "dk": "Er der yderligere information, som skal selvangives i forbindelse med udfyldelsen af "
        "Selvangivelse for visse udenlandske pensionsordninger? ",
    }

    text27 = {"gl": "Sumiiffik / Oqarasuaat", "dk": "Sted/tlf"}
    text28 = {"gl": "Ulloq", "dk": "Dato"}
    text29 = {"gl": "Atsiorneq", "dk": "Underskrift"}
    text_yes = {"gl": "Aap", "dk": "Ja"}
    text_no = {"gl": "Naamik", "dk": "Nej"}

    tax_year = "-"
    tax_return_date_limit = "-"
    person_number = "-"
    receiver_name = "-"
    receiver_postal_address = ""
    taxable_days_in_year = 365
    page_counter = 1
    policies = [""]

    def set_parameters(
        self,
        tax_year="-",
        tax_return_date_limit="",
        request_pay="",
        pay_date="",
        person_number="-",
        receiver_name="",
        receiver_postal_address="",
        taxable_days_in_year=365,
        policies=None,
    ):
        self.tax_year = tax_year
        self.tax_return_date_limit = tax_return_date_limit
        self.request_pay = request_pay
        self.pay_date = pay_date
        self.person_number = person_number
        self.receiver_name = receiver_name or ""
        if policies is None:
            policies = []

        self.receiver_postal_address = receiver_postal_address or ""
        self.taxable_days_in_year = taxable_days_in_year
        self.policies = policies
        self.default_line_width = self.line_width

    def header(self):
        self.yposition = 40
        self.set_xy(self.left_margin, self.yposition)

    def footer(self):
        self.set_font("helvetica", "", 11)
        self.set_xy(self.left_margin, self.h - 17)
        self.cell(h=5.0, align="C", w=30.0, txt=self.person_number, border=0)
        self.set_xy(self.std_document_width - 5, self.h - 17)
        self.cell(h=5.0, align="R", w=10, txt=str(self.page_counter), border=0)
        self.page_counter += 1
        self.set_xy(self.left_margin, self.yposition)

    def count_rows(self, text, width):
        n_rows = 0
        for line in text.split("\n"):
            n_rows += int(self.get_string_width(line) / width) + 1
        return n_rows

    @staticmethod
    def listify(item):
        return item if isinstance(item, list) else [item]

    def write_multi_cell_row(
        self,
        col_texts,
        col_widths=None,
        fontsize=9,
        align="C",
        height=5,
        border=1,
        left_border=None,
        top_border=None,
        **kwargs,
    ):
        # Makes sure defaults are set, and that arguments, which are iterated over, are lists
        length = len(self.listify(col_texts))
        if not col_widths:
            col_widths = [self.std_document_width]
        col_widths = self.listify(col_widths)
        col_texts = self.listify(col_texts)
        align = self.listify(align) * (length // len(self.listify(align)))
        border = self.listify(border) * (length // len(self.listify(border)))
        if left_border is None:
            left_border = self.left_margin
        if top_border:
            self.yposition = top_border
        else:
            top_border = self.yposition

        # Calculate no. of rows required for cells
        required_rows = 0
        txt = []
        for i, width in enumerate(col_widths):
            col_text = col_texts[i]
            if isinstance(col_text, int):
                txt_item = "{:,}".format(col_text).replace(",", ".")
            elif isinstance(col_texts[i], float):
                txt_item = "{:,f}".format(col_text).replace(",", ".")
            else:
                txt_item = str(col_text)
            cell_rows = self.count_rows(txt_item, width)
            if cell_rows > required_rows:
                required_rows = cell_rows
            txt.append(txt_item)
        # write to cells
        for i, width in enumerate(col_widths):
            self.set_xy(left_border, top_border)
            # There seems to be some sort of invisible padding, hence the "-2"
            cell_rows = self.count_rows(txt[i], width - 2)
            if cell_rows < required_rows:
                txt[i] += "\n " * (required_rows - cell_rows)
            self.multi_cell(
                h=height,
                align=align[i],
                w=width,
                txt=txt[i],
                border=border[i],
            )
            left_border += width
        self.yposition += height * required_rows
        return None

    def print_tax_slip(self, language):
        """
        Calling this method appends content to the report in progress, starting from a new page
        :param language:
        :return:
        """
        self.add_page()
        self.page_counter = 1
        self.set_fill_color(180, 180, 180)

        self.set_font("helvetica", "B", 15.0)
        self.set_xy(125.0, 8.0)
        self.cell(
            h=self.contact_info_table_cell.get("h"),
            align="R",
            w=75.0,
            txt=self.document_header.get(language),
            border=0,
        )

        self.set_font("helvetica", "B", 12.0)

        # Set yposition for first cell
        self.yposition = 8
        self.write_multi_cell_row(
            self.text2.get(language).format(self.tax_year),
            align="L",
            border=0,
        )

        self.set_font("helvetica", "", 9.0)
        self.write_multi_cell_row(
            self.text4[language].format(self.tax_return_date_limit),
            align="L",
            border=0,
        )

        self.set_font("helvetica", "", 8.5)
        # Adressing reciever
        self.write_multi_cell_row(
            [self.receiver_name + "\n" + self.receiver_postal_address],
            col_widths=self.address_field.get("w"),
            height=3,
            align="L",
            border=0,
            left_border=self.address_field.get("x"),
            top_border=self.address_field.get("y"),
        )

        # Adressing department
        self.write_multi_cell_row(
            self.sender_name
            + "\n"
            + self.sender_address
            + "\n"
            + self.sender_postnumber,
            col_widths=self.address_field.get("w"),
            height=4,
            align="L",
            border=0,
            left_border=self.address_field.get("x"),
            top_border=self.address_field.get("y") + 12,
        )

        # Generates the cross over sender address
        self.line(
            self.address_field.get("x"),
            self.address_field.get("y") + 12,
            self.address_field.get("x") + self.address_field.get("w") - 30,
            self.address_field.get("y") + 22,
        )
        self.line(
            self.address_field.get("x"),
            self.address_field.get("y") + 22,
            self.address_field.get("x") + self.address_field.get("w") - 30,
            self.address_field.get("y") + 12,
        )

        # Write the contact information box
        self.write_multi_cell_row(
            [
                self.text5[language],
                self.person_number,
            ],
            col_widths=[
                self.contact_info_table_cell.get("w"),
                self.contact_info_table_cell.get("w"),
            ],
            align="L",
            height=self.contact_info_table_cell.get("h"),
            left_border=self.contact_info_table.get("x"),
            top_border=self.contact_info_table.get("y"),
        )
        self.write_multi_cell_row(
            [
                self.text6[language],
                "{:.2%}".format(settings.KAS_TAX_RATE).replace(",", "."),
            ],
            col_widths=[
                self.contact_info_table_cell.get("w"),
                self.contact_info_table_cell.get("w"),
            ],
            align="L",
            height=self.contact_info_table_cell.get("h"),
            left_border=self.contact_info_table.get("x"),
        )

        self.write_multi_cell_row(
            self.text7[language],
            col_widths=2 * self.contact_info_table_cell.get("w"),
            align="L",
            left_border=self.contact_info_table.get("x"),
        )
        self.write_multi_cell_row(
            [
                self.text8[language],
                "sullissivik.gl",
            ],
            col_widths=[
                self.contact_info_table_cell.get("w"),
                self.contact_info_table_cell.get("w"),
            ],
            align="L",
            height=self.contact_info_table_cell.get("h"),
            left_border=self.contact_info_table.get("x"),
        )
        self.write_multi_cell_row(
            [
                self.text8A[language],
                str(self.taxable_days_in_year),
            ],
            col_widths=[
                self.contact_info_table_cell.get("w"),
                self.contact_info_table_cell.get("w"),
            ],
            align="L",
            height=self.contact_info_table_cell.get("h"),
            left_border=self.contact_info_table.get("x"),
        )

        # Set yposition for main text
        self.yposition = 80

        self.set_font("helvetica", "B", 8.5)
        self.write_multi_cell_row(self.text10[language], align="L", border=0)
        text_fields = [
            self.text11[language],
            "   ",
            self.text12[language],
            "   ",
            self.text13[language],
            self.text13A[language],
            self.text13B[language],
            self.text13C[language].format(self.tax_return_date_limit),
            "   ",
            self.text13D[language],
            "   ",
            self.text13E[language].format(self.request_pay, self.pay_date),
            "   ",
            self.text14[language].format(self.tax_year, self.request_pay),
        ]
        self.set_font("helvetica", "", 8.5)
        for field in text_fields:
            self.write_multi_cell_row(field, align="L", border=0)

        self.add_page()

        """
        Spacing parameters five_col_x for 5 cells, and three_col_x for 3 cells.
        Denotes cell width. Gathered in a list for use in write_multi_cell_row()
        """
        five_col_2 = 21
        five_col_3 = 34
        five_col_4 = 38
        five_col_5 = 28
        five_col_1 = (
            self.std_document_width - five_col_2 - five_col_3 - five_col_4 - five_col_5
        )
        five_cols = [five_col_1, five_col_2, five_col_3, five_col_4, five_col_5]

        three_col_2 = 52
        three_col_3 = 52
        three_col_1 = self.std_document_width - three_col_2 - three_col_3
        three_cols = [three_col_1, three_col_2, three_col_3]
        policys_per_page = 4
        policy_index = 0
        any_policys_added = False
        rowheight = 10
        headerheight = 10
        columnheaderheight = 5

        # Write out policies
        for policy in self.policies:
            if policy_index == policys_per_page:
                self.add_page()
                policy_index = 0
            policy_index += 1
            self.set_font("helvetica", "B", 12)
            self.write_multi_cell_row(
                policy.get("policy"),
                height=headerheight,
            )

            self.set_font("helvetica", "B", 9)

            # Create function, which, given widths and text, creates and write to cols
            self.write_multi_cell_row(
                [
                    self.text17A[language],
                    self.text17B[language],
                    self.text8A[language],
                    self.text17F[language],
                    self.text17E[language],
                ],
                col_widths=five_cols,
                height=columnheaderheight,
            )

            self.set_font("helvetica", "", 8.5)

            self.write_multi_cell_row(
                [
                    self.text15[language],
                    policy.get("prefilled_amount"),
                    self.taxable_days_in_year,
                    policy.get("year_adjusted_amount"),
                    "   ",
                ],
                col_widths=five_cols,
                align=["L", "C", "C", "C", "C"],
                height=rowheight,
            )

            if policy.get("pension_company_pays"):
                self.write_multi_cell_row(
                    self.text26D[language],
                    align="L",
                    border=[0],
                    height=columnheaderheight,
                )

            # Space before next policy
            self.yposition += 2 * columnheaderheight
            any_policys_added = True

        if any_policys_added:
            self.add_page()

        self.write_multi_cell_row(
            self.text26DA[language],
            align="L",
            border=0,
        )

        self.yposition += columnheaderheight
        self.set_font("helvetica", "B", 9)
        self.write_multi_cell_row(
            [
                self.text17C[language],
                self.text17D[language],
                self.text17E[language],
            ],
            col_widths=three_cols,
        )
        # Changes the number of blank rows for text17C/D/E.
        number_of_extra_taxslip_rows = 2
        for i in range(number_of_extra_taxslip_rows):
            self.write_multi_cell_row(
                [
                    "   ",
                    "   ",
                    "   ",
                ],
                col_widths=three_cols,
                height=rowheight,
            )

        self.yposition += columnheaderheight
        self.set_font("helvetica", "", 8.5)

        self.write_multi_cell_row(self.text26E[language], align="L")
        self.write_multi_cell_row("   ", height=40)
        self.yposition += 10

        self.write_multi_cell_row(self.text26B[language], align="L")
        self.write_multi_cell_row("   ", height=15)

        self.yposition += 15

        self.write_multi_cell_row(self.text26[language], align="L")
        self.write_multi_cell_row(
            [
                self.text27[language],
                self.text28[language],
                self.text29[language],
            ],
            col_widths=3 * [self.signature_table_cell.get("w")],
            height=self.signature_table_cell.get("h"),
            align=3 * ["L"],
        )
        self.write_multi_cell_row(
            ["   ", "   ", "   "],
            col_widths=3 * [self.signature_table_cell.get("w")],
            height=self.signature_table_cell.get("h"),
        )

    def write_tax_slip_to_disk(self, path):
        self.output(path, "F")

    def perform_complete_write_of_one_person_tax_year(self, person_tax_year, title):
        """
        Calling this method appends reportcontent to the pdf-file in progress, and saves the result to person_tax_year
        :param destination_path:
        :param person_tax_year:
        :param title:
        :return:
        """
        tax_year = person_tax_year.tax_year.year
        tax_return_date_limit = f"1. maj {(person_tax_year.tax_year.year+1)}"
        request_pay = f" {(person_tax_year.tax_year.year+1)}"
        pay_date = f"1. september {(person_tax_year.tax_year.year+1)}"
        person_number = person_tax_year.person.cpr
        receiver_name = person_tax_year.person.name
        receiver_postal_address = person_tax_year.person.postal_address
        taxable_days_in_year = person_tax_year.number_of_days
        policies = []

        list_of_policies = PolicyTaxYear.objects.active().filter(
            person_tax_year=person_tax_year
        )

        policy_file_name = f"Y_{tax_year}_{person_number}.pdf"

        for policy in list_of_policies:
            single_policy = {
                "policy": (
                    (policy.pension_company.name or " - ")
                    + " - "
                    + policy.policy_number
                ),
                "preliminary_paid_amount": policy.preliminary_paid_amount,
                "prefilled_amount": (
                    policy.prefilled_amount_edited
                    if policy.prefilled_amount_edited is not None
                    else policy.prefilled_amount
                ),
                "pension_company_pays": policy.pension_company_pays,
                "year_adjusted_amount": policy.year_adjusted_amount,
                "available_negative_return": policy.available_negative_return,
            }

            policies.append(single_policy)

        self.set_parameters(
            tax_year,
            tax_return_date_limit,
            request_pay,
            pay_date,
            person_number,
            receiver_name,
            receiver_postal_address,
            taxable_days_in_year,
            policies,
        )

        self.print_tax_slip("gl")
        self.print_tax_slip("dk")

        ts = TaxSlipGenerated(persontaxyear=person_tax_year, title=title)
        ts.save()
        ts.file.save(content=ContentFile(self.output()), name=policy_file_name)
        person_tax_year.tax_slip = ts
        person_tax_year.save()


class TaxSlipHandling(FPDF):
    def perform_complete_write_of_one_tax_year(self, tax_year, title):
        list_of_person_tax_year = PersonTaxYear.objects.filter(tax_year__year=tax_year)

        for person_tax_year in list_of_person_tax_year:
            pdf_document = TaxPDF()
            pdf_document.perform_complete_write_of_one_person_tax_year(
                person_tax_year=person_tax_year, title=title
            )
