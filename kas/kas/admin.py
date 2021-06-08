from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.translation import gettext as _

from kas.models import FinalSettlement
from kas.models import PensionCompany, TaxYear, Person, PersonTaxYear, PolicyTaxYear, PolicyDocument, TaxSlipGenerated
from project.admin import kasadmin  # used by is_staff users


class IsStaffPermission(admin.ModelAdmin):

    def has_delete_permission(self, request, obj=None):
        # never allow deletion
        return False

    def has_add_permission(self, request):
        if request.user.is_authenticated:
            if request.user.is_staff or request.user.is_superuser:
                return True
        return False

    def has_change_permission(self, request, obj=None):
        if request.user.is_authenticated:
            if request.user.is_staff or request.user.is_superuser:
                return True
        return False

    def has_view_or_change_permission(self, request, obj=None):
        if request.user.is_authenticated:
            if request.user.is_staff or request.user.is_superuser:
                return True
        return False

    def has_module_permission(self, request):
        if request.user.is_authenticated:
            if request.user.is_staff or request.user.is_superuser:
                return True
        return False


class KasUserAdmin(UserAdmin, IsStaffPermission):
    # Specialized admin

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        if not request.user.is_superuser:
            # Staff users (not superadmins) don't need to change users' groups, permissions, superuser status etc.
            return (
                (None, {'fields': ('username', 'password')}),
                (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
                (_('Permissions'), {'fields': ('is_active', 'is_staff')}),
            )
        return super().get_fieldsets(request, obj)

    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active']
    list_filter = ('is_staff', 'is_active')
    save_as_continue = False


kasadmin.register(User, KasUserAdmin)


class PensionCompanyAdmin(IsStaffPermission, admin.ModelAdmin):
    list_display = ('name', 'res', 'email', 'phone', 'agreement_present')
    list_filter = ('agreement_present', )
    search_fields = ('name', 'res', 'email')


kasadmin.register(PensionCompany, PensionCompanyAdmin)


class TaxYearAdmin(IsStaffPermission, admin.ModelAdmin):
    list_display = ('year', 'year_part')

    def has_change_permission(self, request, obj=None):
        return False

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return [(None, {'fields': ('year', )})]
        return super(TaxYearAdmin, self).get_fieldsets(request, obj)


kasadmin.register(TaxYear, TaxYearAdmin)

# ------------------/django-admin/-------------------------------#


class PersonAdmin(admin.ModelAdmin):
    pass


admin.site.register(Person, PersonAdmin)


class PersonTaxYearAdmin(admin.ModelAdmin):
    pass


admin.site.register(PersonTaxYear, PersonTaxYearAdmin)


class PolicyTaxYearAdmin(admin.ModelAdmin):
    pass


admin.site.register(PolicyTaxYear, PolicyTaxYearAdmin)


class PolicyDocumentAdmin(admin.ModelAdmin):
    pass


admin.site.register(PolicyDocument, PolicyDocumentAdmin)


class TaxSlipGeneratedAdmin(admin.ModelAdmin):
    list_display = ('persontaxyear', 'status', 'delivery_method')
    list_filter = ('persontaxyear__tax_year', 'status')

    def delivery_method(self, obj):
        return obj.delivery_method


admin.site.register(TaxSlipGenerated, TaxSlipGeneratedAdmin)


admin.site.register(FinalSettlement)
