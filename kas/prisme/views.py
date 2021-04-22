from django.views.generic import CreateView, UpdateView

from kas.view_mixins import CreateOrUpdateViewWithNotesAndDocuments
from prisme.forms import TransActionForm
from prisme.models import Transaction


class TransactionCreateView(CreateOrUpdateViewWithNotesAndDocuments, CreateView):
    """
    The PK pased in from the urls belongs to the person_tax_year we want to create the transaction for.
    """
    model = Transaction
    form_class = TransActionForm

    def get_form_kwargs(self):
        """
        Set person_tax_year as passed in by the url and set created_by to the current user
        """
        kwargs = super(TransactionCreateView, self).get_form_kwargs()
        kwargs.update({
            'instance': Transaction(person_tax_year=self.get_person_tax_year(),
                                    created_by=self.request.user)
        })
        return kwargs


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
