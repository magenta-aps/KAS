from django.urls import path

from worker.views import JobListTemplateView, JobListAPIView, \
    JobTypeSelectFormView, StartJobView, JobDetailView

urlpatterns = [
    path('jobs/', JobListTemplateView.as_view(), name='job_list'),
    path('job/<uuid:uuid>/', JobDetailView.as_view(), name='job_detail'),
    path('jobsjax/', JobListAPIView.as_view(), name='job_ajax'),
    path('jobtypeselect/', JobTypeSelectFormView.as_view(), name='job_type_select'),
    path('jobstart/<str:job_type>/', StartJobView.as_view(), name='job_start'),
]
app_name = 'worker'
