from django.conf.urls import url
from django.views.generic import RedirectView, TemplateView
from selvbetjening.views import CustomJavaScriptCatalog, SetLanguageView, PolicyFormView


app_name = 'selvbetjening'

urlpatterns = [
    url(r'^$', RedirectView.as_view(url='/policy/edit/')),
    url(r'^policy/edit/', PolicyFormView.as_view(), name='policy-edit'),
    url(r'^policy/submitted/', TemplateView.as_view(template_name='submitted.html'), name='policy-submitted'),
    url(r'^policy/no_person_data/', TemplateView.as_view(template_name='not_found.html'), name='policy-not-found'),
    url(
        r'^language/(?P<locale>[a-z]{2})',
        CustomJavaScriptCatalog.as_view(domain='django', packages=['selvbetjening']),
        name='javascript-language-catalog'
    ),
    url(r'^language', SetLanguageView.as_view(), name='set-language'),
]
