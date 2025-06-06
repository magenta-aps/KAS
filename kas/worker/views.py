from itertools import islice

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.forms import FileField
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import FormView
from project.view_mixins import administrator_required
from worker.forms import JobTypeSelectForm
from worker.job_registry import get_job_types, resolve_job_function
from worker.models import Job

from kas.view_mixins import KasMixin


class JobListHtmxView(KasMixin, PermissionRequiredMixin, ListView):
    permission_denied_message = administrator_required
    template_name = "worker/htmx/jobs.html"
    permission_required = "worker.view_job"

    def get_queryset(self):
        chunk_size = 10
        last_uuid = self.kwargs.get("last_uuid")
        qs = Job.objects.filter(parent__isnull=True)
        if last_uuid:
            # if you provide a nonexisting uuid you get a 404
            last_object = get_object_or_404(Job, uuid=last_uuid)

            # For some reason this doesn't work completely,
            # it outputs Jobs that are later than last_object,
            # when objects are less than one second apart
            qs = qs.filter(created_at__lt=last_object.created_at).order_by(
                "-created_at"
            )

            # Do further filtering
            return islice(
                filter(
                    lambda job: job.created_at < last_object.created_at, qs.iterator()
                ),
                chunk_size,
            )

        return qs.order_by("-created_at")[:chunk_size]

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **{**kwargs, "csp_nonce": self.request.GET.get("csp_nonce")}
        )


class JobListTemplateView(KasMixin, PermissionRequiredMixin, TemplateView):
    permission_denied_message = administrator_required
    template_name = "worker/job_list.html"
    permission_required = "worker.view_job"


class JobDetailView(KasMixin, PermissionRequiredMixin, DetailView):
    permission_denied_message = administrator_required
    slug_field = "uuid"
    slug_url_kwarg = "uuid"
    model = Job
    permission_required = "worker.view_job"


class JobTypeSelectFormView(KasMixin, PermissionRequiredMixin, FormView):
    permission_denied_message = administrator_required
    template_name = "worker/job_type_select.html"
    form_class = JobTypeSelectForm
    permission_required = "worker.add_job"

    def form_valid(self, form):
        return HttpResponseRedirect(
            reverse(
                "worker:job_start", kwargs={"job_type": form.cleaned_data["job_type"]}
            )
        )


class StartJobView(KasMixin, PermissionRequiredMixin, FormView):
    permission_denied_message = administrator_required
    template_name = "worker/job_create_form.html"
    permission_required = "worker.add_job"

    def job_data(self):
        return get_job_types()[self.kwargs["job_type"]]

    def get_context_data(self, **kwargs):
        ctx = super(StartJobView, self).get_context_data(**kwargs)
        ctx.update(
            {"job_data": self.job_data(), "pretty_job_title": self.job_data()["label"]}
        )
        return ctx

    def get_form_class(self):
        try:
            return self.job_data()["form_class"]
        except IndexError:
            raise Http404("No such job type")

    def form_valid(self, form):
        # Todo: Raise a validation error if something goes wrong here?
        function_string = self.job_data().get("function", None)
        function = resolve_job_function(function_string)

        if function:
            job_kwargs = form.cleaned_data
            if FileField in [field.__class__ for field in form.fields.values()]:
                # we need to store the upload file in the file field
                # since we can't json-serialize it
                instance = form.save(commit=False)
                instance.uploaded_by = self.request.user
                instance.save()
                # Remove InMemoryUploadedFile instances from job_kwargs;
                # they have been saved to `instance`, which we refer by pk
                job_kwargs = dict(
                    filter(
                        lambda kvp: not isinstance(kvp[1], InMemoryUploadedFile),
                        job_kwargs.items(),
                    )
                )
                job_kwargs["pk"] = str(instance.pk)
            for key, value in form.cleaned_data.items():
                if isinstance(value, models.Model):
                    job_kwargs[key] = value.pk

            Job.schedule_job(
                function=function,
                job_type=self.kwargs["job_type"],
                created_by=self.request.user,
                job_kwargs=job_kwargs,
            )
        return super(StartJobView, self).form_valid(form)

    def get_success_url(self):
        return reverse("worker:job_list")
