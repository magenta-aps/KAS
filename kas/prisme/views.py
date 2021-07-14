from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import dateformat
from django.views.generic import CreateView, UpdateView, ListView, View

from kas.view_mixins import CreateOrUpdateViewWithNotesAndDocuments

from prisme.forms import TransActionForm
from prisme.models import Transaction, Prisme10QBatch


class TransactionCreateView(CreateOrUpdateViewWithNotesAndDocuments, CreateView):
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


class TransactionUpdateView(CreateOrUpdateViewWithNotesAndDocuments, UpdateView):
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


class Prisme10QBatchView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'prisme/batch_detail.html'
    context_object_name = 'transactions'
    paginate_by = 10

    def get_object(self):

        return get_object_or_404(Prisme10QBatch, pk=self.kwargs['pk'])

    def get_queryset(self):

        return self.get_object().active_transactions_qs

    def get_context_data(self, **kwargs):

        kwargs['batch'] = self.get_object()
        kwargs['batch_class'] = Prisme10QBatch

        return super().get_context_data(**kwargs)

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
