from django.forms import formset_factory
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import formats
from django.utils.translation import to_locale, get_language

from kas.forms import NoteForm, PolicyDocumentForm
from kas.models import PersonTaxYear


class BootstrapTableMixin:

    def get_context_data(self, **kwargs):
        ctx = super(BootstrapTableMixin, self).get_context_data(**kwargs)
        lang = get_language()
        ctx['table_locale'] = to_locale(lang).replace('_', '-')  # da-DK
        ctx['lang_locale'] = ctx['table_locale'].split('-')[0]  # da, de etc
        ctx['date_format'] = formats.get_format('SHORT_DATE_FORMAT', lang=lang)
        return ctx


class CreateOrUpdateViewWithNotesAndDocuments:
    """
    Should work in combination with a Create or Update View.
    Expects the pk of a PersonTaxYear located in the url.
    can be used with 'includes/notes_and_documents_form.html'
    """

    def __init__(self, **kwargs):
        super(CreateOrUpdateViewWithNotesAndDocuments, self).__init__(**kwargs)
        self.NoteFormSet = formset_factory(NoteForm)
        self.UploadFormSet = formset_factory(PolicyDocumentForm)

    def get_person_tax_year(self):
        """
        Should always return a PersonTaxYear.
        By default we look for the url param pk.
        Could be used to lookup related instances if the PK passed in related to another model.
        Override as needed.
        """
        if not hasattr(self, 'person_tax_year'):
            self.person_tax_year = get_object_or_404(PersonTaxYear, id=self.kwargs['pk'])
        return self.person_tax_year

    def get_context_data(self, **kwargs):
        context = super(CreateOrUpdateViewWithNotesAndDocuments, self).get_context_data(**kwargs)
        context.update({
            'notes_formset': self.NoteFormSet(prefix='notes'),
            'upload_formset': self.UploadFormSet(prefix='uploads'),
            'person_tax_year': self.get_person_tax_year()
        })
        return context

    def form_valid(self, form):
        note_form_set = self.NoteFormSet(self.request.POST, prefix='notes')
        for note_form in note_form_set:
            if note_form.has_changed():
                note = note_form.save(commit=False)
                note.person_tax_year = self.get_person_tax_year()
                note.author = self.request.user
                note.save()
        upload_form_set = self.UploadFormSet(self.request.POST, self.request.FILES, prefix='uploads')
        for upload_form in upload_form_set:
            if upload_form.has_changed():  # no file no upload
                document = upload_form.save(commit=False)
                document.person_tax_year = self.get_person_tax_year()
                document.created_by = self.request.user
                document.name = document.file.name
                document.save()
        return super(CreateOrUpdateViewWithNotesAndDocuments, self).form_valid(form)

    def get_success_url(self):
        return reverse('kas:person_in_year', kwargs={'year': self.get_person_tax_year().year,
                                                     'person_id': self.get_person_tax_year().person_id})
