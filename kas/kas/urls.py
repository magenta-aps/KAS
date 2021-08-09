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
    DispatchFinalSettlement, PersonTaxYearGeneralAndForeignNotesListView

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
    path('final_settlement/<int:year>/<int:cpr>/', CurrentFinalSettlementDownloadView.as_view(),
         name='current-final-settlement'),



]
