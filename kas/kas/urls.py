from django.urls import path
from kas.views import FrontpageView


app_name = 'kas'

urlpatterns = [
    path('', FrontpageView.as_view(), name='frontpage'),
]
