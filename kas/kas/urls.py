from django.urls import path
from kas.views import StatisticsView, PersonTaxYearListView, PersonTaxYearDetailView, \
    PolicyTaxYearDetailView, PdfDownloadView, PolicyDocumentDownloadView, SelfReportedAmountUpdateView, \
    FinalSettlementDownloadView, \
    PersonNotesAndAttachmentsView, PolicyNotesAndAttachmentsView, \
    EditAmountsUpdateView, PensionCompanySummaryFileView, PensionCompanySummaryFileDownloadView, \
    PolicyTaxYearCreateView, ActivatePolicyTaxYearView, PersonTaxYearHistoryListView, PersonTaxYearHistoryDetailView, \
    PolicyTaxYearHistoryDetailView, PolicyTaxYearHistoryListView, PersonTaxYearUnfinishedListView, \
    PersonTaxYearFailSendListView, PolicyTaxYearUnfinishedListView

app_name = 'kas'

urlpatterns = [
    path('', PersonTaxYearListView.as_view(), name='person_search'),
    path('person/unfinished', PersonTaxYearUnfinishedListView.as_view(), name='person_search_unfinished'),
    path('person/failsend', PersonTaxYearFailSendListView.as_view(), name='person_search_failsend'),
    path('statistics', StatisticsView.as_view(), name='statistics'),
    path('tax_year/<int:year>/persons/<int:person_id>/', PersonTaxYearDetailView.as_view(), name='person_in_year'),
    path('tax_year/<int:year>/persons/<int:person_id>/pdf/', PdfDownloadView.as_view(), name='get_pdf'),
    path('tax_year/<int:year>/persons/<int:person_id>/policy/', PolicyTaxYearCreateView.as_view(), name='policy_create'),
    path('policy/<int:pk>/', PolicyTaxYearDetailView.as_view(), name='policy_detail'),
    path('policy/<int:pk>/activate/', ActivatePolicyTaxYearView.as_view(), name='policy_activate'),
    path('policy/unfinished', PolicyTaxYearUnfinishedListView.as_view(), name='policy_search_unfinished'),
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
    path(r'tax_year/<int:year>/company-summary/', PensionCompanySummaryFileView.as_view(), name='policy_summary_list'),
    path(r'tax_year/<int:year>/company-summary/<int:pk>', PensionCompanySummaryFileDownloadView.as_view(), name='policy_summary'),
    path('persontaxyear/<int:pk>/history/', PersonTaxYearHistoryListView.as_view(),
         name='person_history_list'),
    path('persontaxyear/history/<int:pk>', PersonTaxYearHistoryDetailView.as_view(),
         name='person_history_detail'),
    path('policytaxyear/<int:pk>/history/', PolicyTaxYearHistoryListView.as_view(),
         name='policy_history_list'),
    path('policytaxyear/history/<int:pk>', PolicyTaxYearHistoryDetailView.as_view(),
         name='policy_history_detail')


]
