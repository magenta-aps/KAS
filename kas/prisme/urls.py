from django.urls import path

from prisme.views import (
    Prisme10QBatchListView,
    Prisme10QBatchView,
    Prisme10QBatchDownloadView,
    Prisme10QBatchSendView,
)

app_name = "prisme"

urlpatterns = [
    path("batch/", Prisme10QBatchListView.as_view(), name="batch-list"),
    path("batch/<int:pk>/", Prisme10QBatchView.as_view(), name="batch"),
    path(
        "batch/<int:pk>/download",
        Prisme10QBatchDownloadView.as_view(),
        name="batch-download",
    ),
    path("batch/<int:pk>/send", Prisme10QBatchSendView.as_view(), name="batch-send"),
]
