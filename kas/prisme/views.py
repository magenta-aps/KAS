from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import dateformat
from django.views.generic import ListView, View, FormView
from django.views.generic.detail import SingleObjectMixin

from prisme.forms import BatchSendForm
from prisme.models import Prisme10QBatch
from project.view_mixins import (
    PermissionRequiredWithMessage,
    regnskab_or_administrator_required,
)
from worker.job_registry import resolve_job_function
from worker.models import Job
from kas.view_mixins import KasMixin


class Prisme10QBatchListView(KasMixin, PermissionRequiredWithMessage, ListView):
    permission_required = "prisme.view_prisme10qbatch"
    model = Prisme10QBatch
    template_name = "prisme/batch_list.html"
    context_object_name = "batches"
    paginate_by = 10


class Prisme10QBatchView(
    KasMixin, PermissionRequiredWithMessage, SingleObjectMixin, ListView
):
    template_name = "prisme/batch_detail.html"
    permission_required = "prisme.view_prisme10qbatch"
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Prisme10QBatch.objects.all())
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["batch"] = self.object
        context["batch_class"] = Prisme10QBatch
        context["jobs"] = Job.objects.filter(arguments__pk=self.object.pk).exclude(
            status="finished"
        )
        return context

    def get_queryset(self):
        return self.object.active_transactions_qs


class Prisme10QBatchDownloadView(KasMixin, PermissionRequiredWithMessage, View):
    permission_required = "prisme.view_prisme10qbatch"

    def get(self, *args, **kwargs):
        batch = get_object_or_404(Prisme10QBatch, pk=kwargs["pk"])
        response = HttpResponse(batch.get_content(), content_type="text/plain")
        filename = "KAS_10Q__%s__%s.txt" % (
            batch.pk,
            dateformat.format(batch.created, "y-m-d_H_i_s"),
        )
        response["Content-Disposition"] = "attachment; filename=%s" % filename
        return response


class Prisme10QBatchSendView(KasMixin, PermissionRequiredWithMessage, FormView):
    permission_required = "prisme.add_prisme10qbatch"
    permission_denied_message = regnskab_or_administrator_required
    form_class = BatchSendForm
    template_name = "prisme/batch_send.html"

    def get_object(self):
        return get_object_or_404(Prisme10QBatch, pk=self.kwargs["pk"])

    def form_valid(self, form):
        # Start job
        batch = self.get_object()
        job_kwargs = {**form.cleaned_data, "pk": batch.pk}
        # Set status now, so even if it takes some time for the job to start, the user can see that something has happened
        batch.status = Prisme10QBatch.STATUS_DELIVERING
        batch.delivered_by = None
        batch.delivered = None
        batch.delivery_error = ""
        batch.save(
            update_fields=["status", "delivered_by", "delivered", "delivery_error"]
        )
        Job.schedule_job(
            function=resolve_job_function("prisme.jobs.send_batch"),
            job_type="SendBatch",
            created_by=self.request.user,
            job_kwargs=job_kwargs,
        )
        return super(Prisme10QBatchSendView, self).form_valid(form)

    def get_success_url(self):
        return reverse("prisme:batch", kwargs={"pk": self.kwargs["pk"]})
