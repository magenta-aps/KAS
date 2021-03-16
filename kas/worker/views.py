from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.views.generic import TemplateView, DetailView
from django.views.generic.edit import FormView
from rest_framework.authentication import SessionAuthentication
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from worker.job_registry import get_job_types
from kas.view_mixins import BootstrapTableMixin
from worker.forms import JobTypeSelectForm
from worker.models import Job
from worker.serializers import JobSerializer

import importlib


class JobListTemplateView(BootstrapTableMixin, TemplateView):
    template_name = 'worker/job_list.html'


class JobDetailView(DetailView):
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'
    model = Job


class JobListAPIView(ListAPIView):
    authentication_classes = [SessionAuthentication]
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


class StartJobView(LoginRequiredMixin, FormView):
    template_name = 'worker/job_create_form.html'

    cached_job_data = None

    def job_data(self):
        if self.cached_job_data is None:
            self.cached_job_data = get_job_types()[self.kwargs['job_type']]
        return self.cached_job_data

    def get_context_data(self, **kwargs):
        ctx = super(StartJobView, self).get_context_data(**kwargs)
        ctx.update({
            'job_data': self.job_data(),
            'pretty_job_title': self.job_data()['label']
        })
        return ctx

    def get_form_class(self):
        try:
            return self.job_data()['form_class']
        except IndexError:
            raise Http404('No such job type')

    def form_valid(self, form):
        function = None

        # Todo: Raise a validation error if something goes wrong here?
        function_string = self.job_data().get('function', None)
        if function_string:
            module_string, function_name = function_string.rsplit('.', 1)
            module = importlib.import_module(module_string)
            function = getattr(module, function_name)

        if function:
            Job.schedule_job(function=function,
                             job_type=self.kwargs['job_type'],
                             created_by=self.request.user,
                             job_kwargs=form.cleaned_data)
        return super(StartJobView, self).form_valid(form)

    def get_success_url(self):
        return reverse('worker:job_list')
