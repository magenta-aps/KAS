import os
from typing import List

from django.core.files.base import ContentFile
from django.utils import translation
from django.utils.translation import gettext as _
from fpdf import FPDF
from kas.models import PersonTaxYear, PolicyTaxYear, Agterskrivelse
from project.utils import first_not_none


class AgterskrivelsePDF(FPDF):
    std_font_name = "arial"
    std_document_width = 171
    container_width = 139
    left_margin = 17.0
    right_margin = std_document_width + left_margin
    std_document_height = 276

    def __init__(self, person_tax_year, policy_tax_years, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.person_tax_year = person_tax_year
        self.policy_tax_years = policy_tax_years

    def print(self, lang):
        translation.activate(lang)
        try:
            self.add_page()
            self.page_counter = 1
            self.set_fill_color(180, 180, 180)
            self.set_font(self.std_font_name, "", 10.0)

            self.image(
                os.path.dirname(os.path.abspath(__file__)) + "/vandmærke.png",
                x=30,
                y=150,
                w=180.7,
                h=147.0,
            )
            self.image(
                os.path.dirname(os.path.abspath(__file__)) + "/logo.png",
                x=self.right_margin - 60,
                y=10,
                w=60,
                h=20,
            )

            self.block(
                0, 10, 100, None, "Akileraartarnermut Aqutsisoqarfik\nSkattestyrelsen"
            )
            self.block(0, 36, None, None, self.person_tax_year.person.name)
            self.block(0, 41, None, None, self.person_tax_year.person.postal_address)
            self.block(0, 85, None, None, _("Partshøring"), bold=True, align="C")
            self.block(
                0,
                90,
                None,
                None,
                _("Meddelelse om beskatningsgrundlag af afkastet {year}").format(
                    year=self.person_tax_year.tax_year.year
                ),
                bold=True,
            )
            self.block(
                0,
                105,
                None,
                None,
                _(
                    "Skattestyrelsen agter, i henhold til § 12 i Landstingslov nr. 11 af 2. november 2006 om forvaltning af skatter, at foretage nedenfor angivne ansættelse af Deres beskatnings\\-grundlag af afkastet."
                ),
            )

            self.pos = 130
            line_height = 5
            left_width = 112
            right_pos = 112
            for i, other_policy in enumerate(
                self.person_tax_year.active_policies_qs.exclude(
                    pk__in=[
                        policy_tax_year.pk for policy_tax_year in self.policy_tax_years
                    ]
                )
            ):
                selvangivet_beskatningsgrundlag = first_not_none(
                    other_policy.self_reported_amount,
                    other_policy.prefilled_adjusted_amount,
                )
                ansat_beskatningsgrundlag = first_not_none(
                    other_policy.assessed_amount,
                    other_policy.self_reported_amount,
                    other_policy.prefilled_adjusted_amount,
                )
                self.block(
                    right_pos,
                    self.pos,
                    30,
                    None,
                    f"{selvangivet_beskatningsgrundlag} kr.",
                    align="R",
                )
                height = self.block(
                    0,
                    self.pos,
                    left_width,
                    None,
                    _(
                        "Selvangivet beskatningsgrundlag af afkastet, {selskab} POLICE NR. {policenr}:"
                    ).format(
                        selskab=other_policy.pension_company.name,
                        policenr=other_policy.policy_number,
                    ),
                )
                self.pos += height + line_height

                height = self.block(
                    0,
                    self.pos,
                    left_width,
                    None,
                    _("Ansat beskatningsgrundlag af afkastet:"),
                )
                self.block(
                    right_pos,
                    self.pos,
                    30,
                    None,
                    f"{ansat_beskatningsgrundlag} kr.",
                    underline=True,
                    align="R",
                )
                self.pos += height + 2 * line_height

            self.pos += line_height

            for policy in self.policy_tax_years:
                topdanmark_beskatningsgrundlag = policy.prefilled_adjusted_amount
                selvangivet_beskatningsgrundlag = policy.self_reported_amount or 0
                ansat_beskatningsgrundlag = first_not_none(
                    policy.assessed_amount,
                    policy.self_reported_amount,
                    policy.prefilled_adjusted_amount,
                )
                height = self.block(
                    0,
                    self.pos,
                    left_width,
                    None,
                    _("Selvangivet beskatningsgrundlag af afkastet:"),
                )
                self.block(
                    right_pos,
                    self.pos,
                    30,
                    None,
                    f"{selvangivet_beskatningsgrundlag} kr.",
                    align="R",
                )
                self.pos += height

                self.block(
                    right_pos,
                    self.pos,
                    30,
                    None,
                    f"{topdanmark_beskatningsgrundlag} kr.",
                    underline=True,
                    align="R",
                )
                height = self.block(
                    0,
                    self.pos,
                    left_width,
                    None,
                    _(
                        "Ej medregnet afkast fra {selskab} POLICE NR. {policenr}:"
                    ).format(
                        selskab=policy.pension_company.name,
                        policenr=policy.policy_number,
                    ),
                )
                self.pos += height + line_height

                self.block(
                    0,
                    self.pos,
                    left_width,
                    None,
                    _("Ansat beskatningsgrundlag af afkastet:"),
                )
                self.block(
                    right_pos,
                    self.pos,
                    30,
                    None,
                    f"{ansat_beskatningsgrundlag} kr.",
                    underline=True,
                    align="R",
                )
                self.pos += height + 2 * line_height

            height = self.block(
                0,
                self.pos,
                None,
                None,
                _(
                    """Afkast fra Topdanmark POLICE NR. {policenr} er skattepligtig i henhold til § 1 i Inatsisartutlov nr. 37 af 23. november 2017 med senere ændringer.

Kan De godkende forslaget til ansættelse af Deres beskatningsgrundlag af afkastet, be\\-høver De intet at foretage Dem.

Ønsker De at gøre indsigelse mod forslaget til ansættelsen, skal dette ske inden 4 uger fra dato ved skriftlig eller mundtlig henvendelse til Skattestyrelsen.

Såfremt De ikke gør indsigelse inden nævnte frist, vil ansættelsen blive foretaget som ovenfor.

Klage over Skattestyrelsens ansættelse skal inden 3 måneder fra modtagelsen af den afgørelse der klages over indgives til Skatterådet, Postboks 1037, 3900 Nuuk - oed@nanoq.gl"""
                ).format(
                    policenr=", ".join(
                        [policy.policy_number for policy in self.policy_tax_years]
                    )
                ),
            )
            self.pos += height + 2 * line_height

            height = self.block(
                0,
                self.pos,
                None,
                None,
                _("Klagen skal være skriftlig og begrundet.")
                + "\n" * 2
                + _("Med venlig hilsen"),
            )
            self.pos += height + 2 * line_height
            self.image(
                os.path.dirname(os.path.abspath(__file__)) + "/mathias.jpg",
                x=self.left_margin,
                y=self.pos,
                w=36.8,
                h=16.6,
            )

            self.block(0, self.pos + 22, 70, None, "Mathias Geisler")
        finally:
            translation.deactivate()

    def footer(self):
        self.block(
            0,
            281.5,
            None,
            None,
            """Allakkat Akileraartarnermut Aqutsisoqarfimmut nassiunneqassapput inunnut ataasiakkaanuunngitsoq
        Al korrespondance bedes stilet til Skattestyrelsen og ikke til enkeltpersoner""",
            size=7,
            align="C",
            break_page=False,
        )
        self.block(
            153,
            276,
            29,
            None,
            str(self.page_no()) + "/{nb}",
            size=7,
            align="R",
            break_page=False,
        )

    def break_page(self, y, height):
        if y + height >= self.std_document_height:
            self.pos = y = y - self.std_document_height + 21
            self.add_page()
        return y

    def block(
        self,
        x,
        y,
        width,
        height,
        text,
        bold=False,
        italic=False,
        underline=False,
        size=10.0,
        align="L",
        link=None,
        break_page=True,
    ):
        if width is None:
            width = self.container_width
        if height is None:
            height = 5
        if break_page:
            y = self.break_page(y, height)
        if text is None:
            text = ""
        self.set_xy(self.left_margin + x, y)
        style = ""
        for letter, use in (("B", bold), ("I", italic), ("U", underline)):
            if use:
                style += letter
        self.set_font(self.std_font_name, style, size)
        lines = list(self.break_text(text, width - 2))
        text = "\n".join(lines)
        if link:
            self.cell(width, height, text, align=align, link=link)
        else:
            self.multi_cell(width, height, text, align=align)
        height = len(lines) * 5
        if break_page and y + height >= self.std_document_height:
            self.pos = y - self.std_document_height + 6
            # Do not call add_page(); it is implicit
        return height

    def break_text(self, text, width):
        output_line = ""
        for line in text.split("\n"):
            # Split text into list of lists. First split by space, then split by optional-word-break marker
            words = [x.split("\\-") for x in line.split(" ")]
            for word in words:
                for i, wordpart in enumerate(word):
                    # can we possibly end this wordpart with a dash (splitting a word)?
                    group_has_more = len(word) > 1 and i < len(word) - 1
                    # wordpart with space before if not first on the line and first in a word
                    sp_wordpart = (
                        (" " + wordpart) if len(output_line) and i == 0 else wordpart
                    )
                    # Check if string so far fits within width (accounting for possible dash at the end)
                    if (
                        self.get_string_width(
                            output_line + sp_wordpart + ("-" if group_has_more else "")
                        )
                        < width
                    ):
                        # candidate fits in line, append to output
                        output_line += sp_wordpart
                    else:
                        # candidate doesn't fit, we need to end this line and start a new one
                        if i > 0:
                            # not first part in word (and prior part did fit with a dash). Put a dash on the line
                            output_line += "-"
                        # return current line and go to next line
                        yield output_line
                        # add to next line the word-part that didn't fit
                        output_line = wordpart
            # Explicit newline or end-of-string encountered
            yield output_line
            output_line = ""

    @classmethod
    def generate_pdf(
        cls, person_tax_year: PersonTaxYear, policy_tax_years: List[PolicyTaxYear]
    ):
        agterskrivelse = Agterskrivelse(person_tax_year=person_tax_year)
        pdf_generator = cls(
            person_tax_year=person_tax_year,
            policy_tax_years=policy_tax_years,
        )

        for lang in ("kl", "da"):
            pdf_generator.print(lang)
        policy_file_name = f"AGTERSKRIVELSE_{person_tax_year.tax_year.year}_{person_tax_year.person.cpr}.pdf"
        agterskrivelse.pdf.save(
            content=ContentFile(pdf_generator.output()), name=policy_file_name
        )
        for policy_tax_year in policy_tax_years:
            policy_tax_year.agterskrivelse = agterskrivelse
            policy_tax_year.save(update_fields=("agterskrivelse",))
        return agterskrivelse
