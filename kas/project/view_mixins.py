from django.contrib.auth.mixins import PermissionRequiredMixin
from django.utils.translation import gettext as _

sagsbehandler_or_administrator_required = _('Du skal være logget ind som '
                                            'enten administrator eller sagsbehandler '
                                            'for at kunne redigere')

sagsbehandler_or_administrator_or_borgerservice_required = _('Du skal være logget ind som enten administrator, '
                                                             'sagsbehandler eller borgerservice '
                                                             'for at kunne tilføje notater og uploade bilag.')

regnskab_or_administrator_required = _('Du skal være logget ind som enten administrator eller regnskabsmedarbejder. '
                                       'For at kunne benytte denne funktion')

administrator_required = _('Du skal være administrator for at benytte følgende funktion.')


class PermissionRequiredWithMessage(PermissionRequiredMixin):
    permission_denied_message = _('Du har ikke rettigheder til at tilgå denne funktion.')
