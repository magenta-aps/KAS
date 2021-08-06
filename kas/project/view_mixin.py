from django.contrib.auth.mixins import AccessMixin
from django.utils.translation import gettext as _


class IsStaffMixin(AccessMixin):
    permission_denied_message = _('Du skal være administrator for at benytte denne funktion')
    raise_exception = False  # redirect user if not logged in or not staff
    # like accessing the url directly and not by a link on the site

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:
            return super(IsStaffMixin, self).dispatch(request, *args, **kwargs)
        return self.handle_no_permission()
