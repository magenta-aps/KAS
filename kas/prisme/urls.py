from django.urls import path

from prisme.views import (  # isort: skip
    Prisme10QBatchDownloadView,
    Prisme10QBatchListView,
    Prisme10QBatchSendView,
    Prisme10QBatchView,
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
