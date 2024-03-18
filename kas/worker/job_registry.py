import importlib

from django.conf import settings
from django.utils.translation import gettext as _


def get_job_types():
    """
    :returns available jobs based on environment
    """
    from prisme.forms import PrePaymentFileModelForm

    from worker.forms import (  # isort: skip
        AutoligningsYearForm,  # R75ImportSpreadsheetJobForm,
        ConfirmForm,
        LegacyYearsForm,
        MandtalImportJobForm,
        R75ImportJobForm,
        R75ImportSpreadsheetJobForm,
        WorkerPensionCompanySummaryFileForm,
        YearAndTitleForm,
        YearPkForm,
    )

    jobs = {
        "Autoligning": {
            "label": _("Kør autoligning"),
            "form_class": AutoligningsYearForm,  # form class used to start job
            "result_template": "worker/includes/autoligning.html",
            "function": "kas.jobs.autoligning",
        },
        "ImportPrePaymentFile": {
            "label": _("Import af forudindbetalinger"),  # translated label
            "form_class": PrePaymentFileModelForm,
            "result_template": "worker/includes/forudindbetalinger.html",
            "function": "prisme.jobs.import_pre_payment_file",
        },
        "ImportMandtalJob": {
            "label": _("Import af mandtal"),  # translated label
            "form_class": MandtalImportJobForm,  # form class used to start job
            "result_template": "worker/includes/mandtal.html",
            "function": "kas.jobs.import_mandtal",
        },
        "ImportR75Job": {
            "label": _("Import af data fra R75"),  # translated label
            "form_class": R75ImportJobForm,  # form class used to start job
            "result_template": "worker/includes/r75.html",
            "function": "kas.jobs.import_r75",
        },
        "ForceFinalize": {
            "label": _("Forcering af slutligning på alle udestående policer"),
            "form_class": YearPkForm,
            "function": "kas.jobs.force_finalize_settlement",
            "result_template": "worker/includes/raw.html",
        },
        "GenerateReportsForYear": {
            "label": _("Generering af KAS selvangivelser for et givet år"),
            "form_class": YearAndTitleForm,
            "function": "kas.jobs.generate_reports_for_year",
            "result_template": "worker/includes/raw.html",
        },
        "DispatchTaxYear": {
            "label": _("Afsendelse af KAS selvangivelser for et givet år"),
            "form_class": YearPkForm,
            "function": "kas.jobs.dispatch_tax_year",
            "result_template": "worker/includes/raw.html",
        },
        "DispatchTaxYearDebug": {
            "label": _("Test-afsendelse af KAS selvangivelser for et givet år"),
            "form_class": YearPkForm,
            "function": "kas.jobs.dispatch_tax_year_debug",
            "result_template": "worker/includes/raw.html",
        },
        "GenerateFinalSettlements": {
            "label": _("Generering af KAS slutopgørelser for et givet år"),
            "form_class": YearPkForm,
            "function": "kas.jobs.generate_final_settlements_for_year",
            "result_template": "worker/includes/status_only.html",
        },
        "GeneratePensionCompanySummary": {
            "label": _("Generering af årssummationsfil for et pensionsselskab"),
            "form_class": WorkerPensionCompanySummaryFileForm,
            "function": "kas.jobs.generate_pension_company_summary_file",
            "result_template": "worker/includes/status_only.html",
        },
        "GenerateBatchAndTransactions": {
            "label": _("Generering af Transaktioner og batch for et givent år"),
            "form_class": YearPkForm,
            "function": "kas.jobs.generate_batch_and_transactions_for_year",
            "result_template": "worker/includes/status_only.html",
        },
        "DispatchFinalSettlements": {
            "label": _("Afsendelse af KAS slutopgørelser for et givet år"),
            "form_class": YearAndTitleForm,
            "function": "kas.jobs.dispatch_final_settlements_for_year",
            "result_template": "worker/includes/status_only.html",
        },
        "DispatchFinalSettlement": {
            "label": _("Afsendelse af KAS slutopgørelse"),
            "form_class": ConfirmForm,
            "function": "kas.jobs.dispatch_final_settlement",
            "result_template": "worker/includes/status_only.html",
            "not_in_dropdown": True,
        },
        "SendBatch": {
            "label": _("Sender et Q10 batch"),
            "form_class": ConfirmForm,
            "result_template": "worker/includes/status_only.html",
            "function": "prisme.jobs.send_batch",
            "not_in_dropdown": True,
        },
        "MergeCompanies": {
            "label": _("Flet pensionsselskaber"),
            "not_in_dropdown": True,
            "result_template": "worker/includes/status_only.html",
        },
        "ImportLegacyCalculations": {
            "label": _("Importere kas beregninger for tidligere år (2018/2019)"),
            "form_class": LegacyYearsForm,
            "result_template": "worker/includes/status_only.html",
            "function": "eskat.jobs.importere_kas_beregninger_for_legacy_years",
        },
        "GeneratePseudoFinalSettlements": {
            "label": _("Generering af pseudo slutopgørelser (2018/2019)"),
            "form_class": ConfirmForm,
            "result_template": "worker/includes/status_only.html",
            "function": "kas.jobs.generate_pseudo_settlements_and_transactions_for_legacy_years",  # noqa
        },
        "ImportSpreadsheetR75Job": {
            "label": _("Import af data fra R75 i regneark"),
            "form_class": R75ImportSpreadsheetJobForm,
            "result_template": "worker/includes/r75.html",
            "function": "kas.jobs.import_spreadsheet_r75",
        },
        # 'DispatchAgterskrivelser': {
        #     'label': _('Afsendelse af Agterskrivelser for et givet år'),
        #     'form_class': YearPkForm,
        #     'function': 'kas.jobs.dispatch_agterskrivelser_for_year',
        # },
    }
    if settings.ENVIRONMENT in ("development", "staging"):
        jobs.update(
            {
                "ResetTaxYear": {
                    "label": _("Reset data for skatteår"),  # translated label
                    "form_class": YearPkForm,  # form class used to start job
                    "result_template": "worker/includes/status_only.html",
                    "function": "kas.jobs.reset_tax_year",
                },
            }
        )

    if settings.ENVIRONMENT == "development":
        # include jobs to generate mock data
        jobs.update(
            {
                "GenerateSampleData": {
                    "label": _("Generate sample data"),  # translated label
                    "form_class": ConfirmForm,  # form class used to start job
                    "result_template": "worker/includes/status_only.html",
                    "function": "eskat.jobs.generate_sample_data",
                },
            }
        )

    return jobs


def resolve_job_function(string):
    module_string, function_name = string.rsplit(".", 1)
    module = importlib.import_module(module_string)
    function = getattr(module, function_name)
    return function
