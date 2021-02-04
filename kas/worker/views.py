from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse_lazy

from django.views.generic import TemplateView
from django.views.generic.detail import BaseDetailView
from django.views.generic.edit import BaseFormView

from worker.jobs import slow_job, slow_job_with_children, job_with_exception
from worker.models import Job
from worker.forms import JobControlForm


class IndexTemplateView(TemplateView):
    template_name = 'worker/job.html'

    def get_context_data(self, **kwargs):
        ctx = super(IndexTemplateView, self).get_context_data(**kwargs)

        try:
            latest_job = Job.objects.all().order_by('-created_at')[0]
        except IndexError:
            latest_job = None

        ctx.update({
            'latest_job': latest_job,
            'form': JobControlForm(data={'action': 'create', 'job_type': 'slow_job',
                                         'redirect_url': reverse_lazy('worker:index')}),

            'children_form': JobControlForm(data={'action': 'create', 'job_type': 'slow_job_with_children',
                                                  'redirect_url': reverse_lazy('worker:index')}),
            'exception_form': JobControlForm(data={'action': 'create', 'job_type': 'job_with_exception',
                                                   'redirect_url': reverse_lazy('worker:index')}),

        })
        return ctx


class JobControlView(BaseFormView):
    form_class = JobControlForm

    def form_invalid(self, form):
        return HttpResponseRedirect(form.cleaned_data['redirect_url'])

    def form_valid(self, form):
        if form.cleaned_data['action'] == 'create':
            if form.cleaned_data['job_type'] == 'slow_job':
                Job.schedule_job(form.cleaned_data['job_type'], slow_job)
            elif form.cleaned_data['job_type'] == 'slow_job_with_children':
                Job.schedule_job(form.cleaned_data['job_type'], slow_job_with_children)
            elif form.cleaned_data['job_type'] == 'job_with_exception':
                Job.schedule_job(form.cleaned_data['job_type'], job_with_exception)
        return HttpResponseRedirect(form.cleaned_data['redirect_url'])


class JobDetailView(BaseDetailView):
    # could a rest view
    model = Job
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(data=self.get_object().to_dict())
