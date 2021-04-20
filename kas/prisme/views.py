from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView
from django.views.generic.detail import SingleObjectMixin

from kas.models import PersonTaxYear
from prisme.forms import CreateTransActionForm
from prisme.models import Transaction


class TransactionCreateView(LoginRequiredMixin, CreateView, SingleObjectMixin):
    model = Transaction
    form_class = CreateTransActionForm

    def get_object(self, queryset=None):
        return get_object_or_404(PersonTaxYear, pk=self.kwargs['person_tax_year_id'])

    def get_form_kwargs(self):
        kwargs = super(TransactionCreateView, self).get_form_kwargs()
        kwargs.update({
            'instance': Transaction(person_tax_year=self.get_object(), created_by=self.request.user)
        })
        return kwargs

    def get_success_url(self):
        return reverse('kas:person_in_year', kwargs={'year': self.object.person_tax_year.year,
                                                     'person_id': self.object.person_tax_year.person.id})
