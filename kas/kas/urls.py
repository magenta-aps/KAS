from django.urls import path
from kas.views import FrontpageView, PersonTaxYearListView, PersonTaxYearDetailView, PolicyTaxYearDetailView


app_name = 'kas'

urlpatterns = [
    path('', FrontpageView.as_view(), name='frontpage'),
    path(r'tax_year/<int:year>/persons/', PersonTaxYearListView.as_view(), name='persons_in_year'),
    path(r'tax_year/<int:year>/persons/<int:person_id>/', PersonTaxYearDetailView.as_view(), name='person_in_year'),
    path(r'policy/<int:pk>/', PolicyTaxYearDetailView.as_view(), name='policy_detail'),
]
