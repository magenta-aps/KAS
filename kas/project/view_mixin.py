from django.contrib.auth.mixins import AccessMixin
from django.utils.translation import gettext as _


class IsStaffMixin(AccessMixin):
    permission_denied_message = _('Du skal være administrator for at benytte denne funktion')
    raise_exception = True  # do not redirect to login since the user is doing something nasty
    # like accessing the url directly and not by a link on the site

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff is True:
            return super(IsStaffMixin, self).dispatch(request, *args, **kwargs)
        return self.handle_no_permission()
