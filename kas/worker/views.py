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

    def get_context_data(self, **kwargs):
        ctx = super(StartJobView, self).get_context_data(**kwargs)
        ctx.update({
            'pretty_job_title': get_job_types()[self.kwargs['job_type']]['label']
        })
        return ctx

    def get_form_class(self):
        try:
            return get_job_types()[self.kwargs['job_type']]['form_class']
        except IndexError:
            raise Http404('No such job type')

    def form_valid(self, form):
        function = None
        if self.kwargs['job_type'] == 'ImportMandtalJob':
            from kas.jobs import import_mandtal
            function = import_mandtal
        if self.kwargs['job_type'] == 'ImportR75Job':
            from kas.jobs import import_r75
            function = import_r75
        if function:
            Job.schedule_job(function=function,
                             job_type=self.kwargs['job_type'],
                             created_by=self.request.user,
                             job_kwargs=form.cleaned_data)
        return super(StartJobView, self).form_valid(form)

    def get_success_url(self):
        return reverse('worker:job_list')
