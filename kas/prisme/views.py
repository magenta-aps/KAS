from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import dateformat
from django.views.generic import CreateView, UpdateView, ListView, View, FormView
from django.views.generic.detail import SingleObjectMixin

from kas.view_mixins import CreateOrUpdateViewWithNotesAndDocuments

from prisme.forms import TransActionForm
from prisme.models import Transaction, Prisme10QBatch
from prisme.forms import BatchSendForm

from worker.models import Job
from worker.job_registry import resolve_job_function

from project.view_mixin import IsStaffMixin


class TransactionCreateView(LoginRequiredMixin, CreateOrUpdateViewWithNotesAndDocuments, CreateView):
    """
    The PK pased in from the urls belongs to the person_tax_year we want to create the transaction for.
    """
    model = Transaction
    form_class = TransActionForm

    @property
    def back_url(self):
        person_tax_year = self.get_person_tax_year()
        return reverse('kas:person_in_year', kwargs={'year': person_tax_year.year, 'person_id': person_tax_year.person.id})

    def get_form_kwargs(self):
        """
        Set person_tax_year as passed in by the url and set created_by to the current user
        """
        kwargs = super(TransactionCreateView, self).get_form_kwargs()
        kwargs.update({
            'instance': Transaction(person_tax_year=self.get_person_tax_year(),
                                    source_object=self.request.user)
        })
        return kwargs

    def get_context_data(self, **kwargs):
        return super().get_context_data(**{
            'back_url': self.back_url,
            **kwargs,
        })


class TransactionUpdateView(LoginRequiredMixin, CreateOrUpdateViewWithNotesAndDocuments, UpdateView):
    """
    In this example the PK passed in from the urls.py belongs to the Transaction (standard behavior of get_object).
    So we need to override get_person_tax_year using self.object.
    Since self.object is set after calling get_object we can use this as reference to the Transaction being edited.
    """
    model = Transaction
    form_class = TransActionForm

    def get_person_tax_year(self):
        return self.object.person_tax_year

    @property
    def back_url(self):
        person_tax_year = self.get_person_tax_year()
        return reverse('kas:person_in_year', kwargs={'year': person_tax_year.year, 'person_id': person_tax_year.person.id})

    def get_context_data(self, **kwargs):
        return super().get_context_data(**{
            'back_url': self.back_url,
            **kwargs,
        })


class Prisme10QBatchListView(IsStaffMixin, ListView):
    model = Prisme10QBatch
    template_name = 'prisme/batch_list.html'
    context_object_name = 'batches'
    paginate_by = 10


class Prisme10QBatchView(LoginRequiredMixin, SingleObjectMixin, ListView):
    template_name = 'prisme/batch_detail.html'
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Prisme10QBatch.objects.all())
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['batch'] = self.object
        context['batch_class'] = Prisme10QBatch
        context['jobs'] = Job.objects.filter(arguments__pk=self.object.pk).exclude(status='finished')
        return context

    def get_queryset(self):
        return self.object.active_transactions_qs


class Prisme10QBatchDownloadView(LoginRequiredMixin, View):

    def get(self, *args, **kwargs):
        batch = get_object_or_404(Prisme10QBatch, pk=kwargs['pk'])
        response = HttpResponse(batch.get_content(), content_type='text/plain')
        filename = 'KAS_10Q__%s__%s.txt' % (
            batch.pk,
            dateformat.format(batch.created, 'y-m-d_H_i_s')
        )
        response['Content-Disposition'] = "attachment; filename=%s" % filename
        return response


class Prisme10QBatchSendView(IsStaffMixin, FormView):

    form_class = BatchSendForm
    template_name = 'prisme/batch_send.html'

    def get_object(self):
        return get_object_or_404(Prisme10QBatch, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        kwargs['batch'] = self.get_object()
        kwargs['batch_class'] = Prisme10QBatch
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        # Start job
        batch = self.get_object()
        job_kwargs = {**form.cleaned_data, 'pk': batch.pk}
        # Set status now, so even if it takes some time for the job to start, the user can see that something has happened
        batch.status = Prisme10QBatch.STATUS_DELIVERING
        batch.delivered_by = None
        batch.delivered = None
        batch.delivery_error = ''
        batch.save(update_fields=['status', 'delivered_by', 'delivered', 'delivery_error'])
        Job.schedule_job(
            function=resolve_job_function('prisme.jobs.send_batch'),
            job_type='SendBatch',
            created_by=self.request.user,
            job_kwargs=job_kwargs
        )
        return super(Prisme10QBatchSendView, self).form_valid(form)

    def get_success_url(self):
        return reverse('prisme:batch', kwargs={'pk': self.kwargs['pk']})
