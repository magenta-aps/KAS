from django.utils.translation import gettext as _

import importlib


def get_job_types():
    """
    :returns a registry dictionary with label and form_class for each job type
    """
    from worker.forms import MandtalImportJobForm, R75ImportJobForm, YearAndTitleForm, ConfirmForm, YearPkForm, \
        AutoligningsYearForm
    from prisme.forms import PrePaymentFileModelForm

    return {
        'Autoligning': {
            'label': _('Kør autoligning'),
            'form_class': AutoligningsYearForm,  # form class used in the start job workflow
            'result_template': 'worker/includes/autoligning.html',
            'function': 'kas.jobs.autoligning',

        },
        'ImportPrePaymentFile': {
            'label': _('Import af forudindbetalinger'),  # translated label
            'form_class': PrePaymentFileModelForm,
            'result_template': 'worker/includes/forudindbetalinger.html',
            'function': 'prisme.jobs.import_pre_payment_file'
        },
        'ImportMandtalJob': {
            'label': _('Import af mandtal'),  # translated label
            'form_class': MandtalImportJobForm,  # form class used in the start job workflow
            'result_template': 'worker/includes/mandtal.html',
            'function': 'kas.jobs.import_mandtal',
            'test_only': False,
        },

        'ImportR75Job': {
            'label': _('Import af data fra R75'),  # translated label
            'form_class': R75ImportJobForm,  # form class used in the start job workflow
            'result_template': 'worker/includes/r75.html',
            'function': 'kas.jobs.import_r75',
            'test_only': False,
        },
        'ForceFinalize': {
            'label': _('Forcering af slutligning på alle udestående policer'),
            'form_class': YearPkForm,
            'function': 'kas.jobs.force_finalize_settlement'
        },
        'GenerateReportsForYear': {
            'label': _('Generere KAS selvangivelser'),
            'form_class': YearAndTitleForm,
            'function': 'kas.jobs.generate_reports_for_year'
        },
        'DispatchTaxYear': {
            'label': _('Afsendelse af KAS selvangivelser for et givent år'),
            'form_class': YearPkForm,
            'function': 'kas.jobs.dispatch_tax_year',
        },
        'GenerateFinalSettlements': {
            'label': _('Generering af slutopgørelser for et given år'),
            'form_class': YearAndTitleForm,
            'function': 'kas.jobs.generate_final_settlements_for_year'
        },
        'DispatchFinalSettlements': {
            'label': _('Afsendelse af slutopgørelser for et given år'),
            'form_class': YearPkForm,
            'function': 'kas.jobs.dispatch_final_settlements_for_year'
        },
        'ImportEskatMockup': {
            'label': _('Import af mockup data for eSkat'),  # translated label
            'form_class': ConfirmForm,  # form class used in the start job workflow
            'result_template': 'worker/includes/status_only.html',
            'function': 'eskat.jobs.import_eskat_mockup',
            'test_only': True,
        },
        'ClearTestData': {
            'label': _('Nulstil test-data'),
            'form_class': ConfirmForm,
            'result_template': 'worker/includes/status_only.html',
            'function': 'kas.jobs.clear_test_data',
            'test_only': True,
        },
        'ResetToMockupOnly': {
            'label': _('Nulstil til KUN mockup data'),
            'form_class': ConfirmForm,
            'result_template': 'worker/includes/status_only.html',
            'function': 'kas.jobs.reset_to_mockup_data',
            'test_only': True,
        },
        'ImportAllMockupMandtal': {
            'label': _('Imporer alle mockup mandtal'),
            'form_class': ConfirmForm,
            'result_template': 'worker/includes/status_only.html',
            'function': 'kas.jobs.import_all_mandtal',
            'test_only': True,
            'not_in_dropdown': True,
        },
        'ImportAllMockupR75': {
            'label': _('Imporer alle mockup r75'),
            'form_class': ConfirmForm,
            'result_template': 'worker/includes/status_only.html',
            'function': 'kas.jobs.import_all_r75',
            'test_only': True,
            'not_in_dropdown': True,
        },
    }


def resolve_job_function(string):

    module_string, function_name = string.rsplit('.', 1)
    module = importlib.import_module(module_string)
    function = getattr(module, function_name)

    return function
