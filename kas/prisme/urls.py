from django.urls import path

from prisme.views import TransactionCreateView, TransactionUpdateView

app_name = 'prisme'

urlpatterns = [
    path('transaction/create/<int:pk>/', TransactionCreateView.as_view(), name='create-transaction'),
    path('transaction/update/<uuid:pk>/', TransactionUpdateView.as_view(), name='update-transaction'),
]
