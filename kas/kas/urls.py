from django.conf import settings
from django.urls import path

from kas.views import StatisticsView, PersonTaxYearListView, PersonTaxYearDetailView, \
    PolicyTaxYearDetailView, PdfDownloadView, PolicyDocumentDownloadView, SelfReportedAmountUpdateView, \
    FinalSettlementDownloadView, \
    PersonNotesAndAttachmentsView, PolicyNotesAndAttachmentsView, \
    EditAmountsUpdateView, PensionCompanySummaryFileView, PensionCompanySummaryFileDownloadView, \
    PolicyTaxYearCreateView, ActivatePolicyTaxYearView, PersonTaxYearHistoryListView, PersonTaxYearHistoryDetailView, \
    PolicyTaxYearHistoryDetailView, PolicyTaxYearHistoryListView, PersonTaxYearUnfinishedListView, \
    PersonTaxYearFailSendListView, PolicyTaxYearUnfinishedListView, PersonTaxYearDocumentsAndNotesUpdateView, \
    PolicyPaymentOverrideView, \
    PersonTaxYearUnhandledDocumentsAndNotes, FinalSettlementGenerateView, MarkFinalSettlementAsInvalid, \
    DispatchFinalSettlement, PersonTaxYearGeneralAndForeignNotesListView, UpdateSingleMandtal, WaitForSingleMandtal, \
    PolicyTaxYearCompanyUpdateView, \
    PensionCompanyFormView, PensionCompanyHtmxView, PensionCompanyUpdateView, AgreementDownloadView, \
    FeatureFlagView
from kas.viewsets import CurrentFinalSettlementDownloadView

app_name = 'kas'

urlpatterns = [
    path('', PersonTaxYearListView.as_view(), name='person_search'),
    path('person/unfinished', PersonTaxYearUnfinishedListView.as_view(), name='person_search_unfinished'),
    path('person/failsend', PersonTaxYearFailSendListView.as_view(), name='person_search_failsend'),
    path('person/unhandled/', PersonTaxYearUnhandledDocumentsAndNotes.as_view(), name='person_search_unhandled'),
    path('person/foreign/', PersonTaxYearGeneralAndForeignNotesListView.as_view(), name='person_search_foreign'),


    path('statistics', StatisticsView.as_view(), name='statistics'),
    path('tax_year/<int:year>/persons/<int:person_id>/', PersonTaxYearDetailView.as_view(), name='person_in_year'),
    path('tax_year/<int:year>/persons/<int:person_id>/pdf/', PdfDownloadView.as_view(), name='get_pdf'),
    path('tax_year/<int:year>/persons/<int:person_id>/policy/', PolicyTaxYearCreateView.as_view(), name='policy_create'),
    path('person_tax_year/<int:pk>/handled/', PersonTaxYearDocumentsAndNotesUpdateView.as_view(), name='person_in_year_handled'),
    path('policy/<int:pk>/', PolicyTaxYearDetailView.as_view(), name='policy_detail'),
    path('policy/<int:pk>/activate/', ActivatePolicyTaxYearView.as_view(), name='policy_activate'),
    path('policy/<int:pk>/company/', PolicyTaxYearCompanyUpdateView.as_view(), name='policy_company'),
    path('policy/unfinished', PolicyTaxYearUnfinishedListView.as_view(), name='policy_search_unfinished'),
    path('policy/<int:pk>/paymentoverride/', PolicyPaymentOverrideView.as_view(), name='policy_payment_override'),
    path('policy_document/<int:pk>/', PolicyDocumentDownloadView.as_view(), name='policy_document_download'),
    path('finalsettlement/<uuid:uuid>/', FinalSettlementDownloadView.as_view(), name='final_settlement_download'),
    path('change/selfreportedamount/<int:pk>/', SelfReportedAmountUpdateView.as_view(),
         name='change-self-reported-amount'),
    path('change/editamounts/<int:pk>/', EditAmountsUpdateView.as_view(),
         name='change-edit-amounts'),
    path('person/<int:pk>/add/notes-attachments/', PersonNotesAndAttachmentsView.as_view(),
         name='person_add_notes_or_attachement'),
    path('policy/<int:pk>/add/notes-attachments/', PolicyNotesAndAttachmentsView.as_view(),
         name='policy_add_notes_or_attachement'),
    path(r'tax_year/latest/company-summary/', PensionCompanySummaryFileView.as_view(), name='policy_summary_list_latest'),
    path(r'tax_year/<int:year>/company-summary/', PensionCompanySummaryFileView.as_view(), name='policy_summary_list'),
    path(r'tax_year/<int:year>/company-summary/<int:pk>', PensionCompanySummaryFileDownloadView.as_view(), name='policy_summary'),
    path('persontaxyear/<int:pk>/history/', PersonTaxYearHistoryListView.as_view(),
         name='person_history_list'),
    path('persontaxyear/history/<int:pk>', PersonTaxYearHistoryDetailView.as_view(),
         name='person_history_detail'),
    path('policytaxyear/<int:pk>/history/', PolicyTaxYearHistoryListView.as_view(),
         name='policy_history_list'),
    path('policytaxyear/history/<int:pk>', PolicyTaxYearHistoryDetailView.as_view(),
         name='policy_history_detail'),
    path('final_settlement/generate/<int:pk>/', FinalSettlementGenerateView.as_view(), name='generate-final-settlement'),
    path('final_settlement/invalid/<uuid:pk>/', MarkFinalSettlementAsInvalid.as_view(), name='invalid-final-settlement'),
    path('final_settlement/dispatch/<uuid:pk>/', DispatchFinalSettlement.as_view(), name='dispatch-final-settlement'),
    path('final_settlement/<int:year>/<str:cpr>/', CurrentFinalSettlementDownloadView.as_view(),
         name='current-final-settlement'),
    path('persontaxyear/<int:pk>//update_mandtal/', UpdateSingleMandtal.as_view(), name='update_persontaxyear_mandtal'),
    path('wait_for_mandtal_update/<uuid:pk>/', WaitForSingleMandtal.as_view(), name='wait_for_mandtal_update'),

    path('pensioncompany/', PensionCompanyFormView.as_view(), name='pensioncompany-listview'),
    path('pensioncompanyhtmx/', PensionCompanyHtmxView.as_view(), name='pensioncompany-htmxview'),
    path('pensioncompanyhtmx/<int:last_id>/', PensionCompanyHtmxView.as_view(), name='pensioncompany-htmxview'),
    path('pensioncompany/<int:pk>/edit/', PensionCompanyUpdateView.as_view(), name='pensioncompany-updateview'),
    path('pensioncompany/<int:pk>/agreement/', AgreementDownloadView.as_view(), name='pensioncompany-agreementdownload'),
]

if settings.FEATURE_FLAGS.get('enable_feature_flag_list'):
    urlpatterns.append(
        path('feature_flags/', FeatureFlagView.as_view(), name='feature_flags')
    )
