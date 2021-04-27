from django.urls import path
from kas.views import FrontpageView, PersonTaxYearListView, PersonTaxYearDetailView, \
    PolicyTaxYearDetailView, PdfDownloadView, PolicyDocumentDownloadView, SelfReportedAmountUpdateView, \
    EditAmountsUpdateView


app_name = 'kas'

urlpatterns = [
    path('', FrontpageView.as_view(), name='frontpage'),
    path(r'tax_year/<int:year>/persons/', PersonTaxYearListView.as_view(), name='persons_in_year'),
    path(r'tax_year/<int:year>/persons/<int:person_id>/', PersonTaxYearDetailView.as_view(), name='person_in_year'),
    path(r'tax_year/<int:year>/persons/<int:person_id>/pdf/', PdfDownloadView.as_view(), name='get_pdf'),
    path(r'policy/<int:pk>/', PolicyTaxYearDetailView.as_view(), name='policy_detail'),
    path('policy_document/<int:pk>/', PolicyDocumentDownloadView.as_view(), name='policy_document_download'),
    path('change/selfreportedamount/<int:pk>/', SelfReportedAmountUpdateView.as_view(),
         name='change-self-reported-amount'),
    path('change/editamounts/<int:pk>/', EditAmountsUpdateView.as_view(),
         name='change-edit-amounts')
]
