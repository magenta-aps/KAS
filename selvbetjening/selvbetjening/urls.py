from django.conf.urls import url
from django.views.generic import RedirectView
from selvbetjening.views import CustomJavaScriptCatalog, SetLanguageView, PolicyFormView, PolicySubmittedView


app_name = 'selvbetjening'

urlpatterns = [
    url(r'^$', RedirectView.as_view(url='/policy/edit/')),
    url(r'^policy/edit/', PolicyFormView.as_view(), name='policy-edit'),
    url(r'^policy/submitted/', PolicySubmittedView.as_view(), name='policy-submitted'),
    url(
        r'^language/(?P<locale>[a-z]{2})',
        CustomJavaScriptCatalog.as_view(domain='django', packages=['selvbetjening']),
        name='javascript-language-catalog'
    ),
    url(r'^language', SetLanguageView.as_view(), name='set-language'),
]
