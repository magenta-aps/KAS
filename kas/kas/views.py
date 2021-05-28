import csv
import mimetypes
import os
import uuid
from io import StringIO

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.db.models import Count, F, Q, Min
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.generic import TemplateView, ListView, View, UpdateView, CreateView, FormView
from django.views.generic.detail import DetailView
from django.views.generic.detail import SingleObjectMixin, BaseDetailView
from ipware import get_client_ip

from eskat.models import ImportedKasMandtal, ImportedR75PrivatePension, MockModels
from kas.forms import PersonListFilterForm, SelfReportedAmountForm, \
    EditAmountsUpdateForm, PensionCompanySummaryFileForm, CreatePolicyTaxYearForm, \
    PolicyTaxYearActivationForm
from kas.forms import PolicyNotesAndAttachmentForm, PersonNotesAndAttachmentForm, \
    PolicyListFilterForm
from kas.models import PensionCompanySummaryFile, PensionCompanySummaryFileDownload, Note
from kas.models import TaxYear, PersonTaxYear, PolicyTaxYear, TaxSlipGenerated, PolicyDocument, FinalSettlement
from kas.view_mixins import CreateOrUpdateViewWithNotesAndDocumentsForPolicyTaxYear
from prisme.models import Transaction


class StatisticsView(LoginRequiredMixin, TemplateView):
    template_name = 'kas/statistics.html'

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)

        result['years'] = [x.year for x in TaxYear.objects.order_by('year')]

        by_year_data = {
            'imported_mandtal': {},
            'imported_r75': {},
            'persons': {},
            'policies': {},
        }

        for x in ImportedKasMandtal.objects.values("skatteaar").annotate(number_per_year=Count('skatteaar')):
            by_year_data['imported_mandtal'][x['skatteaar']] = x['number_per_year']

        for x in ImportedR75PrivatePension.objects.values("tax_year").annotate(number_per_year=Count('tax_year')):
            by_year_data['imported_r75'][x['tax_year']] = x['number_per_year']

        for x in PersonTaxYear.objects.values("tax_year__year").order_by("tax_year__year").annotate(number_per_year=Count('pk')):
            by_year_data['persons'][x['tax_year__year']] = x['number_per_year']

        for x in PolicyTaxYear.objects.values(
            "person_tax_year__tax_year__year"
        ).annotate(number_per_year=Count('person_tax_year__tax_year__year')):
            by_year_data['policies'][x['person_tax_year__tax_year__year']] = x['number_per_year']

        if settings.ENVIRONMENT != "production":
            result["show_mockup"] = True

            by_year_data['mockup_mandtal'] = {}
            by_year_data['mockup_r75'] = {}

            for x in MockModels.MockKasMandtal.objects.values("skatteaar").annotate(number_per_year=Count('skatteaar')):
                by_year_data['mockup_mandtal'][x['skatteaar']] = x['number_per_year']

            for x in MockModels.MockR75Idx4500230.objects.values("tax_year").annotate(number_per_year=Count('tax_year')):
                by_year_data['mockup_r75'][x['tax_year']] = x['number_per_year']

        for k, v in by_year_data.items():
            result[k] = [v.get(year, 0) for year in result['years']]

        return result


class PersonTaxYearListView(LoginRequiredMixin, ListView):
    template_name = 'kas/persontaxyear_list.html'
    context_object_name = 'personstaxyears'
    paginate_by = 20

    model = PersonTaxYear
    form_class = PersonListFilterForm

    def get_form(self):
        years = [tax_year.year for tax_year in TaxYear.objects.order_by('year')]
        current_year = timezone.now().year
        if current_year not in years:
            current_year = max([y for y in years if y < current_year])
        kwargs = {'initial': {'year': current_year}}
        if self.request.GET:
            kwargs['data'] = self.request.GET
        return PersonListFilterForm(**kwargs)

    def should_search(self, form):
        return form.is_valid() and form.has_changed()

    def get_queryset(self):
        form = self.get_form()
        qs = super().get_queryset()
        qs = qs.annotate(next_processing_date=Min('policytaxyear__next_processing_date'))

        try:
            self.year = form.cleaned_data['year']
        except (AttributeError, KeyError):
            self.year = form.initial['year']
        qs = qs.filter(tax_year__year=self.year)

        if self.should_search(form):
            if hasattr(form, 'cleaned_data'):
                # Check whether there are any fields filled out apart from 'year'
                if len([
                    v for k, v in form.cleaned_data.items()
                    if v not in ('', None) and k not in ['year']
                ]):
                    if form.cleaned_data['cpr']:
                        qs = qs.filter(person__cpr__icontains=form.cleaned_data['cpr'])
                    if form.cleaned_data['name']:
                        qs = qs.filter(person__name__icontains=form.cleaned_data['name'])
                    if form.cleaned_data['municipality_code']:
                        qs = qs.filter(person__municipality_code=form.cleaned_data['municipality_code'])
                    if form.cleaned_data['municipality_name']:
                        qs = qs.filter(person__municipality_name__icontains=form.cleaned_data['municipality_name'])
                    if form.cleaned_data['address']:
                        qs = qs.filter(person__full_address__icontains=form.cleaned_data['address'])
                    if form.cleaned_data['tax_liability'] is not None:  # False is a valid value
                        qs = qs.filter(fully_tax_liable=form.cleaned_data['tax_liability'])
                    if form.cleaned_data['foreign_pension_notes'] is not None:
                        empty = Q(foreign_pension_notes='') | Q(foreign_pension_notes__isnull=True)
                        if form.cleaned_data['foreign_pension_notes'] is True:
                            qs = qs.exclude(empty)
                        else:
                            qs = qs.filter(empty)
        else:
            # Don't find anything if form is invalid or empty
            qs = self.model.objects.none()
        self.form = form
        return qs


class PersonTaxYearSpecialListView(PersonTaxYearListView):

    default_order_by = 'person__cpr'

    def should_search(self, form):
        # Allow searching with an unbound form (just the default year)
        return not form.errors

    def get_queryset(self):

        order_by = self.request.GET.get('order_by', self.default_order_by)

        # Handle fields that should always have null last when sorting
        if order_by.endswith("_nulllast"):
            order_by = order_by[:-9]
            if order_by.startswith("-"):
                order_by = F(order_by[1:]).desc(nulls_last=True)
            else:
                order_by = F(order_by).asc(nulls_last=True)

        return self.filter_queryset(
            super().get_queryset()
        ).order_by(order_by, 'person__name')

    def filter_queryset(self, qs):
        return qs


class PersonTaxYearUnfinishedListView(PersonTaxYearSpecialListView):

    template_name = 'kas/persontaxyear_unfinished_list.html'
    default_order_by = '-efterbehandling_count'

    def filter_queryset(self, qs):
        return qs.annotate(
            policy_count=Count('policytaxyear')
        ).annotate(
            efterbehandling_count=Count(
                'policytaxyear',
                filter=Q(policytaxyear__efterbehandling=True)
            )
        ).filter(efterbehandling_count__gt=0)


class PersonTaxYearFailSendListView(PersonTaxYearSpecialListView):

    template_name = 'kas/persontaxyear_failsend_list.html'
    default_order_by = 'person__name'

    def filter_queryset(self, qs):
        return qs.annotate(
            policy_count=Count('policytaxyear')
        ).filter(tax_slip__status='failed')


class PersonTaxYearDetailView(LoginRequiredMixin, DetailView):
    template_name = 'kas/persontaxyear_detail.html'
    model = PersonTaxYear
    context_object_name = 'person_tax_year'

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        self.year = self.kwargs.get("year", None)

        if not self.year:
            raise Http404("No year specified")

        self.person_id = self.kwargs.get("person_id", None)

        if not self.person_id:
            raise Http404("No person specified")

        try:
            obj = queryset.get(
                tax_year__year=self.year,
                person=self.person_id
            )
        except queryset.model.DoesNotExist:
            raise Http404("Persontaxyear not found")
        self.object = obj
        return obj

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        context['joined_address'] = "\n".join([x or "" for x in (
            self.object.person.address_line_1,
            self.object.person.address_line_2,
            self.object.person.address_line_3,
            self.object.person.address_line_4,
            self.object.person.address_line_5,
        )])
        context['transactions'] = Transaction.objects.filter(
            person_tax_year=self.object).select_related('transferred_by')
        context['person_tax_years'] = PersonTaxYear.objects.filter(person=self.object.person)
        return context


class PersonNotesAndAttachmentsView(LoginRequiredMixin, UpdateView):
    form_class = PersonNotesAndAttachmentForm
    model = PersonTaxYear
    template_name = 'kas/person/add_notes_and_attachment_form.html'

    def get_form_kwargs(self):
        kwargs = super(PersonNotesAndAttachmentsView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_success_url(self):
        return reverse('kas:person_in_year', kwargs={'year': self.object.year, 'person_id': self.object.person.id})

    def get_context_data(self, **kwargs):
        ctx = super(PersonNotesAndAttachmentsView, self).get_context_data(**kwargs)
        ctx.update({
            'person_tax_year': self.object
        })
        return ctx


class PolicyTaxYearListView(LoginRequiredMixin, ListView):
    # template_name = 'kas/persontaxyear_list.html'
    context_object_name = 'policytaxyears'
    paginate_by = 20

    model = PolicyTaxYear
    form_class = PolicyListFilterForm

    def get_form(self):
        years = [tax_year.year for tax_year in TaxYear.objects.order_by('year')]
        current_year = timezone.now().year
        if current_year not in years:
            current_year = max([y for y in years if y < current_year])
        kwargs = {'initial': {'year': current_year}}
        if self.request.GET:
            kwargs['data'] = self.request.GET
        return PolicyListFilterForm(**kwargs)

    def should_search(self, form):
        return form.is_valid() and form.has_changed()

    def get_queryset(self):
        form = self.get_form()

        qs = super().get_queryset()
        try:
            self.year = form.cleaned_data['year']
        except (AttributeError, KeyError):
            self.year = form.initial['year']
        qs = qs.filter(person_tax_year__tax_year__year=self.year)

        if self.should_search(form):
            if hasattr(form, 'cleaned_data'):
                # Check whether there are any fields filled out apart from 'year'
                if len([
                    v for k, v in form.cleaned_data.items()
                    if v not in ('', None) and k not in ['year']
                ]):
                    if form.cleaned_data['pension_company']:
                        qs = qs.filter(pension_company__name__icontains=form.cleaned_data['pension_company'])
                    if form.cleaned_data['policy_number']:
                        qs = qs.filter(policy_number__icontains=form.cleaned_data['policy_number'])
        else:
            # Don't find anything if form is invalid or empty
            qs = self.model.objects.none()
        self.form = form
        return qs


class PolicyTaxYearSpecialListView(PolicyTaxYearListView):

    default_order_by = 'policy_number'

    def should_search(self, form):
        # Allow searching with an unbound form (just the default year)
        return not form.errors

    def get_queryset(self):

        order_by = self.request.GET.get('order_by', self.default_order_by)

        # Handle fields that should always have null last when sorting
        if order_by.endswith("_nulllast"):
            order_by = order_by[:-9]
            if order_by.startswith("-"):
                order_by = F(order_by[1:]).desc(nulls_last=True)
            else:
                order_by = F(order_by).asc(nulls_last=True)

        return self.filter_queryset(
            super().get_queryset()
        ).order_by(order_by, 'person_tax_year__person__name', 'policy_number')

    def filter_queryset(self, qs):
        return qs


class PolicyTaxYearUnfinishedListView(PolicyTaxYearSpecialListView):

    template_name = 'kas/policytaxyear_unfinished_list.html'
    default_order_by = 'difference_pct_nulllast'

    def filter_queryset(self, qs):
        return qs.filter(efterbehandling=True).annotate(
            difference=F('self_reported_amount') - F('prefilled_amount')
        ).annotate(
            difference_pct=F('difference') * 100 / F('prefilled_amount')
        )


class PolicyTaxYearDetailView(LoginRequiredMixin, DetailView):
    template_name = 'kas/policytaxyear_detail.html'
    model = PolicyTaxYear
    context_object_name = 'policy'

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)

        result['calculation'] = self.object.get_calculation()

        amount_choices_by_value = {x[0]: x[1] for x in PolicyTaxYear.active_amount_options}

        result['pension_company_amount_label'] = amount_choices_by_value[PolicyTaxYear.ACTIVE_AMOUNT_PREFILLED]
        result['self_reported_amount_label'] = amount_choices_by_value[PolicyTaxYear.ACTIVE_AMOUNT_SELF_REPORTED]

        result['used_negativ_table'] = self.object.previous_year_deduction_table_data

        result['used_from'] = self.object.payouts_used.order_by('used_from__person_tax_year__tax_year__year')
        return result


class PolicyTaxYearCreateView(LoginRequiredMixin, CreateOrUpdateViewWithNotesAndDocumentsForPolicyTaxYear, CreateView):
    form_class = CreatePolicyTaxYearForm
    template_name = "kas/policytaxyear_create.html"

    def get_person_tax_year(self):
        self.year = self.kwargs.get("year", None)
        self.person_id = self.kwargs.get("person_id", None)
        try:
            return PersonTaxYear.objects.get(tax_year__year=self.year, person__id=self.person_id)
        except PersonTaxYear.DoesNotExist:
            raise Http404

    def get_policy_tax_year(self):
        return getattr(self, 'object')

    def form_valid(self, form):
        form.instance.person_tax_year = self.get_person_tax_year()
        form.instance.active_amount = PolicyTaxYear.ACTIVE_AMOUNT_SELF_REPORTED
        return super().form_valid(form)


class PolicyNotesAndAttachmentsView(LoginRequiredMixin, UpdateView):
    model = PolicyTaxYear
    form_class = PolicyNotesAndAttachmentForm
    template_name = 'kas/policy/add_notes_and_attachment_form.html'

    def get_success_url(self):
        return reverse('kas:policy_detail', kwargs={'pk': self.object.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class PolicyDocumentDownloadView(LoginRequiredMixin, View):

    def get(self, *args, **kwargs):
        document = get_object_or_404(PolicyDocument, pk=kwargs['pk'])
        mime_type, _ = mimetypes.guess_type(document.file.name)
        response = HttpResponse(document.file.read(), content_type=mime_type)
        response['Content-Disposition'] = "attachment; filename=%s" % document.name
        return response


class PdfDownloadView(LoginRequiredMixin, SingleObjectMixin, View):
    model = TaxSlipGenerated

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        year = self.kwargs.get("year", None)

        if not year:
            raise Http404("No year specified")

        person_id = self.kwargs.get("person_id", None)

        if not person_id:
            raise Http404("No person specified")

        try:
            obj = queryset.get(
                persontaxyear__tax_year__year=year,
                persontaxyear__person=person_id
            )
        except queryset.model.DoesNotExist:
            raise Http404("PDF not found")

        return obj

    def get(self, *args, **kwargs):

        obj = self.get_object()
        filefield = obj.file
        file_obj = filefield.file

        response = HttpResponse(
            file_obj.read(),
            content_type='application/pdf'
        )
        response['Content-Disposition'] = 'inline; filename=' + os.path.basename(obj.file.file.name)

        return response


class SelfReportedAmountUpdateView(LoginRequiredMixin, CreateOrUpdateViewWithNotesAndDocumentsForPolicyTaxYear, UpdateView):
    form_class = SelfReportedAmountForm
    template_name = 'kas/selfreportedamount_form.html'
    allowed_year_parts = ['selvangivelse']

    def get_queryset(self):
        return PolicyTaxYear.objects.filter(person_tax_year__tax_year__year_part='selvangivelse')


class EditAmountsUpdateView(LoginRequiredMixin, CreateOrUpdateViewWithNotesAndDocumentsForPolicyTaxYear, UpdateView):
    form_class = EditAmountsUpdateForm
    template_name = 'kas/edit_amounts_form.html'

    def get_queryset(self):
        return PolicyTaxYear.objects.filter(person_tax_year__tax_year__year_part__in=['ligning', 'genoptagelsesperiode'])

    def get_form_kwargs(self):
        if self.object.assessed_amount is None:
            # if the assessed amount is not set prefill it
            self.object.assessed_amount = self.object.get_assessed_amount()
        if self.object.adjusted_r75_amount is None:
            # Fill out adjusted_r75_amount since we are not allowed to change prefilled_amount.
            self.object.adjusted_r75_amount = self.object.prefilled_amount
        return super(EditAmountsUpdateView, self).get_form_kwargs()


class PensionCompanySummaryFileView(LoginRequiredMixin, SingleObjectMixin, FormView):
    model = TaxYear
    form_class = PensionCompanySummaryFileForm
    template_name = "kas/policycompanysummary_list.html"
    paginate_by = 20
    slug_url_kwarg = 'year'
    slug_field = 'year'

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        return super().get_context_data(**{
            'object_list': PensionCompanySummaryFile.objects.filter(tax_year=self.object).order_by('company', '-created'),
            **kwargs
        })

    def get_success_url(self):
        return reverse('kas:policy_summary_list', kwargs=self.kwargs)

    def form_valid(self, form):
        self.object = self.get_object()
        # Generate a PensionCompanySummaryFile entry and populate a file for it
        pension_company = form.cleaned_data['pension_company']
        qs = PolicyTaxYear.objects.filter(
            pension_company=pension_company,
            person_tax_year__tax_year=self.object
        ).prefetch_related('person_tax_year', 'person_tax_year__person')
        file_entry = PensionCompanySummaryFile(company=pension_company, tax_year=self.object, creator=self.request.user)

        csvfile = StringIO()
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for policy_tax_year in qs.iterator():
            calculation = policy_tax_year.get_calculation()
            line = [
                policy_tax_year.tax_year.year,  # TaxYear (Integer, 4 digits, positive. XXXX eg. 2013)
                pension_company.res,  # Reg_se_nr (Integer, positive)
                policy_tax_year.cpr,  # Cpr: The CPR on the person
                policy_tax_year.policy_number,  # Police_no (Integer, positive)
                calculation['initial_amount'],  # Tax base 1 per police (Return)(Integer)
                calculation['used_negative_return'],  # The previous year's negative return (Integer)
                calculation['taxable_amount'],  # Tax base 2 (Tax base 1 minus the previous year's negative return)(Integer, 10 digits)
                policy_tax_year.preliminary_paid_amount or 0,  # Provisional tax paid (Integer, 10 digits, positive)
                calculation['tax_with_deductions'],  # Wanted cash tax (Integer)
                None,  # Actual settlement pension company (Empty column)
            ]
            writer.writerow(line)

        file_entry.file.save(uuid.uuid4(), csvfile, save=True)
        file_entry.save()
        csvfile.close()

        # Instruct the client to download the file after refreshing the page
        return HttpResponseRedirect(self.get_success_url() + f'?download={file_entry.id}')


class PensionCompanySummaryFileDownloadView(LoginRequiredMixin, BaseDetailView):

    model = PensionCompanySummaryFile

    # Register info about who is downloading, and serve the file
    def render_to_response(self, context):
        client_ip, is_routable = get_client_ip(self.request)
        PensionCompanySummaryFileDownload.objects.create(
            downloaded_by=self.request.user,
            downloaded_to=client_ip,
            file=self.object
        )
        response = HttpResponse(self.object.file, content_type='text/csv')
        response['Content-Length'] = self.object.file.size
        response['Content-Disposition'] = f"attachment; filename={os.path.basename(self.object.file.name)}"
        return response


class ActivatePolicyTaxYearView(LoginRequiredMixin, UpdateView):

    form_class = PolicyTaxYearActivationForm
    model = PolicyTaxYear

    def get_success_url(self):
        return reverse('kas:policy_detail', kwargs=self.kwargs)


class PersonTaxYearHistoryListView(LoginRequiredMixin, DetailView):
    """
    shows all changes related to a person tax year
    """
    model = PersonTaxYear
    template_name = 'kas/persontaxyear_historical_list.html'

    def get_context_data(self, **kwargs):
        ctx = super(PersonTaxYearHistoryListView, self).get_context_data(**kwargs)

        qs = self.object.history.all().annotate(
            klass=models.Value('PersonTaxYear', output_field=models.CharField()),
        ).values('history_id', 'history_date', 'history_user__username', 'history_change_reason', 'history_type', 'klass')

        person_qs = self.object.person.history.all().annotate(
            klass=models.Value('Person', output_field=models.CharField()),
        ).values('history_id', 'history_date', 'history_user__username', 'history_change_reason', 'history_type', 'klass')

        policy_qs = PolicyTaxYear.history.filter(person_tax_year=self.object).annotate(
            klass=models.Value('Policy', output_field=models.CharField()),
        ).values('id', 'history_date', 'history_user__username', 'history_change_reason', 'history_type', 'klass')

        notes_qs = Note.objects.filter(person_tax_year=self.object).annotate(
            history_type=models.Value('+', output_field=models.CharField()),
            klass=models.Value('Note', output_field=models.CharField()),
        ).values('id', 'date', 'author__username', 'content', 'history_type', 'klass')

        documents_qs = PolicyDocument.objects.filter(person_tax_year=self.object).annotate(
            history_type=models.Value('+', output_field=models.CharField()),
            klass=models.Value('PolicyDocument', output_field=models.CharField()),
        ).values('id', 'uploaded_at', 'uploaded_by__username', 'description', 'history_type', 'klass')

        # generated tax slips
        tax_slip_generated_qs = TaxSlipGenerated.objects.filter(persontaxyear=self.object).annotate(
            created_by=models.Value('', output_field=models.CharField()),
            description=models.Value('Generated', output_field=models.CharField()),
            history_type=models.Value('+', output_field=models.CharField()),
            klass=models.Value('TaxSlipGenerated', output_field=models.CharField()),
        ).values('id', 'created_at', 'created_by', 'description', 'history_type', 'klass')

        # send tax slips
        tax_slip_sendt_qs = TaxSlipGenerated.objects.filter(persontaxyear=self.object).exclude(send_at__isnull=True).annotate(
            created_by=models.Value('', output_field=models.CharField()),
            description=models.Value('Send', output_field=models.CharField()),
            history_type=models.Value('~', output_field=models.CharField()),
            klass=models.Value('TaxSlipGenerated', output_field=models.CharField()),
        ).values('id', 'send_at', 'created_by', 'description', 'history_type', 'klass')

        # TODO add final settlements
        ctx['objects'] = qs.union(policy_qs, person_qs, notes_qs, documents_qs,
                                  tax_slip_generated_qs, tax_slip_sendt_qs, all=True).order_by('-history_date')
        return ctx


class PersonTaxYearHistoryDetailView(LoginRequiredMixin, DetailView):
    """
    Shows a specific "version" of a person_tax_year
    """
    model = PersonTaxYear.history.model
    slug_field = 'history_id'
    template_name = 'kas/persontaxyear_detail.html'
    context_object_name = 'person_tax_year'

    def get_context_data(self, **kwargs):
        ctx = super(PersonTaxYearHistoryDetailView, self).get_context_data(**kwargs)
        ctx['historical'] = True
        return ctx


class PolicyTaxYearHistoryListView(LoginRequiredMixin, DetailView):
    model = PolicyTaxYear
    template_name = 'kas/policytaxyear_historical_list.html'

    def get_context_data(self, **kwargs):
        ctx = super(PolicyTaxYearHistoryListView, self).get_context_data(**kwargs)
        qs = self.object.history.all().annotate(
            klass=models.Value('Policy', output_field=models.CharField()),
        ).values('history_date', 'history_user__username', 'history_id', 'history_change_reason', 'history_type', 'klass')
        notes_qs = Note.objects.filter(policy_tax_year=self.object).annotate(
            history_type=models.Value('+', output_field=models.CharField()),
            klass=models.Value('Note', output_field=models.CharField()),
        ).values('date', 'author__username', 'id', 'content', 'history_type', 'klass')
        documents_qs = PolicyDocument.objects.filter(policy_tax_year=self.object).annotate(
            history_type=models.Value('+', output_field=models.CharField()),
            klass=models.Value('PolicyDocument', output_field=models.CharField()),
        ).values('uploaded_at', 'uploaded_by__username', 'id', 'description', 'history_type', 'klass')
        ctx['objects'] = qs.union(notes_qs, documents_qs, all=True).order_by('-history_date')
        return ctx


class PolicyTaxYearHistoryDetailView(LoginRequiredMixin, DetailView):
    model = PolicyTaxYear.history.model
    slug_field = 'history_id'
    template_name = 'kas/policytaxyear_detail.html'
    context_object_name = 'policy'

    def get_context_data(self, **kwargs):
        ctx = super(PolicyTaxYearHistoryDetailView, self).get_context_data(**kwargs)
        ctx['historical'] = True
        return ctx


class FinalSettlementDownloadView(LoginRequiredMixin, SingleObjectMixin, View):
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'
    model = FinalSettlement

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        response = HttpResponse(self.object.pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = "attachment; filename={year}_{cpr}.pdf".format(
            year=self.object.person_tax_year.tax_year.year, cpr=self.object.person_tax_year.person.cpr)
        return response
