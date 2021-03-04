from django.utils.translation import gettext as _


def get_job_types():
    """
    :returns a registry dictionary with label and form_class for each job type
    """
    from worker.forms import MandtalImportJobForm
    return {
        'ImportMandtalJob': {
            'label': _('Import af mandtal'),  # translated label
            'form_class': MandtalImportJobForm,  # form class used in the start job workflow
            'result_template': 'worker/jobs_results/mandtal.html',
        }
    }
