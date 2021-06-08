from django.contrib.admin import AdminSite


class KASAdminSite(AdminSite):
    site_header = 'KAS administration'


kasadmin = KASAdminSite(name='kasadmin')
