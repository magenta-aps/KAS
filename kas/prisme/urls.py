from django.urls import path

from prisme.views import TransactionCreateView, TransactionUpdateView, \
    Prisme10QBatchView, Prisme10QBatchDownloadView

app_name = 'prisme'

urlpatterns = [
    path('transaction/create/<int:pk>/', TransactionCreateView.as_view(), name='create-transaction'),
    path('transaction/update/<uuid:pk>/', TransactionUpdateView.as_view(), name='update-transaction'),
    path('batch/<int:pk>/', Prisme10QBatchView.as_view(), name='prisme-batch'),
    path('batch/<int:pk>/download', Prisme10QBatchDownloadView.as_view(), name='prisme-batch-download'),
]
