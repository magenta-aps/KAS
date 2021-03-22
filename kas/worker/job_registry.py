from django.utils.translation import gettext as _

import importlib


def get_job_types():
    """
    :returns a registry dictionary with label and form_class for each job type
    """
    from worker.forms import MandtalImportJobForm, R75ImportJobForm, DispatchTaxYearForm, ConfirmForm, YearPkForm
    return {
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
        'GenerateReportsForYear': {
            'label': _('Generere KAS selvangivelser'),
            'form_class': YearPkForm,
            'function': 'kas.jobs.generate_reports_for_year'
        },
        'DispatchTaxYear': {
            'label': ('Afsendelse af KAS selvangivelser for et givent år'),
            'form_class': DispatchTaxYearForm,
            'function': 'kas.jobs.dispatch_tax_year',
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
