from django.utils.translation import gettext as _


def get_job_types():
    """
    :returns a registry dictionary with label and form_class for each job type
    """
    from worker.forms import MandtalImportJobForm, R75ImportJobForm
    return {
        'ImportMandtalJob': {
            'label': _('Import af mandtal'),  # translated label
            'form_class': MandtalImportJobForm,  # form class used in the start job workflow
            'result_template': 'worker/includes/mandtal.html',
        },
        'ImportR75Job': {
            'label': _('Import af data fra R75'),  # translated label
            'form_class': R75ImportJobForm,  # form class used in the start job workflow
            'result_template': 'worker/includes/r75.html',
        }
    }
