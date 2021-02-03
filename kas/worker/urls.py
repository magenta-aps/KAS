from django.urls import path

from worker.views import IndexTemplateView, JobControlView, JobDetailView

urlpatterns = [
    path('', IndexTemplateView.as_view(), name='index'),
    path('jobcontrol', JobControlView.as_view(), name='control_job'),
    path('jobdetail/<uuid:uuid>/', JobDetailView.as_view(), name='job_detail')
]
app_name = 'worker'
