from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.views.generic import TemplateView, DetailView
from django.views.generic.edit import FormView, CreateView
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated

from kas.view_mixins import BootstrapTableMixin
from worker.forms import JobTypeSelectForm, MandtalImportJobForm
from worker.models import job_types, Job
from worker.serializers import JobSerializer


class JobListTemplateView(BootstrapTableMixin, TemplateView):
    template_name = 'worker/job_list.html'


class JobDetailView(DetailView):
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'
    model = Job


class JobListAPIView(ListAPIView):
    serializer_class = JobSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [OrderingFilter]
    ordering_fields = ['created_at', 'status', 'progress']
    ordering = ['-created_at']

    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        return Job.objects.filter(parent__isnull=True).select_related('created_by')


class JobTypeSelectFormView(LoginRequiredMixin, FormView):
    template_name = 'worker/job_type_select.html'
    form_class = JobTypeSelectForm

    def form_valid(self, form):
        return HttpResponseRedirect(reverse('worker:job_start', kwargs={'job_type': form.cleaned_data['job_type']}))


class StartJobView(LoginRequiredMixin, CreateView):
    template_name = 'worker/job_create_form.html'

    def get_context_data(self, **kwargs):
        ctx = super(StartJobView, self).get_context_data(**kwargs)
        ctx.update({
            'pretty_job_title': job_types[self.kwargs['job_type']]
        })
        return ctx

    def get_form_kwargs(self):
        kwargs = super(StartJobView, self).get_form_kwargs()
        kwargs.update({
            'instance': Job(created_by=self.request.user)
        })
        return kwargs

    def get_form_class(self):
        if self.kwargs['job_type'] not in job_types:
            raise Http404('No such job type')
        if self.kwargs['job_type'] == 'ImportMandtalJob':
            return MandtalImportJobForm
        raise Http404('No such job type')

    def form_valid(self, form):
        Job.schedule_job(job_type=self.kwargs['job_type'], f=None, kwargs=form.cleaned_data)
        return super(StartJobView, self).form_valid(form)

    def get_success_url(self):
        return reverse('worker:job_list')
