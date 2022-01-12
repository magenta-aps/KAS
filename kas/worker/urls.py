from django.urls import path

from worker.views import JobListTemplateView, JobTypeSelectFormView, \
    StartJobView, JobDetailView, JobListHtmxView

urlpatterns = [
    path('jobs/', JobListTemplateView.as_view(), name='job_list'),
    path('job/<uuid:uuid>/', JobDetailView.as_view(), name='job_detail'),
    #htmx views
    path('joblist/', JobListHtmxView.as_view(), name='joblist_htmx'),
    path('joblist/<uuid:last_uuid>/', JobListHtmxView.as_view(), name='joblist_htmx'),

    path('jobtypeselect/', JobTypeSelectFormView.as_view(), name='job_type_select'),
    path('jobstart/<str:job_type>/', StartJobView.as_view(), name='job_start'),
]
app_name = 'worker'
