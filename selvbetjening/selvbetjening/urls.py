from django.conf.urls import url
from selvbetjening.views import CustomJavaScriptCatalog, SetLanguageView, PolicyFormView, PolicyDetailView


app_name = 'selvbetjening'

urlpatterns = [
    url(r'^policy/edit/', PolicyFormView.as_view(), name='policyedit'),
    url(r'^policy/(?P<year>[0-9]{4})?/?$', PolicyDetailView.as_view(), name='policyview'),
    url(
        r'^language/(?P<locale>[a-z]{2})',
        CustomJavaScriptCatalog.as_view(domain='django', packages=['selvbetjening']),
        name='javascript-language-catalog'
    ),
    url(r'^language', SetLanguageView.as_view(), name='set-language'),
]
