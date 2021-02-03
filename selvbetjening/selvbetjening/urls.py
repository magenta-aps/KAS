from django.conf.urls import url
from django.views.generic import TemplateView
from selvbetjening.views import CustomJavaScriptCatalog, SetLanguageView

app_name = 'selvbetjening'

urlpatterns = [
    url(r'^test$', TemplateView.as_view(template_name='test.html'), name='test'),
    url(
        r'^language/(?P<locale>[a-z]{2})',
        CustomJavaScriptCatalog.as_view(domain='django', packages=['selvbetjening']),
        name='javascript-language-catalog'
    ),
    url(r'^language', SetLanguageView.as_view(), name='set-language'),
]
