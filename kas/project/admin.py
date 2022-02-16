from django.contrib.admin import AdminSite
from django.contrib.auth.forms import AuthenticationForm


class KASAdminSite(AdminSite):
    site_header = 'KAS administration'
    login_template = 'kas/login.html'
    login_form = AuthenticationForm

    def has_permission(self, request):
        """
        allow access to the simple admin if the user can view users or add tax_years.
        (Being a member of the administrator group).
        """
        if request.user.is_active:
            if request.user.is_superuser or \
                    request.user.has_perm('auth.view_user') or \
                    request.user.has_perm('kas.add_taxyear'):
                return True
        return False


kasadmin = KASAdminSite(name='kasadmin')
