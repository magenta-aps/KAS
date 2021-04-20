from django.urls import path

from prisme.views import TransactionCreateView

app_name = 'prisme'

urlpatterns = [
    path('transaction/create/<int:person_tax_year_id>', TransactionCreateView.as_view(), name='create-transaction')
]
