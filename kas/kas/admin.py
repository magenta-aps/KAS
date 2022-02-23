from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.translation import gettext as _

from kas.models import FinalSettlement, TaxYear, Person, PersonTaxYear, PolicyTaxYear, PolicyDocument, TaxSlipGenerated
from project.admin import kasadmin  # used by is_staff users


class KasUserAdmin(UserAdmin):
    # Specialized admin
    def has_delete_permission(self, request, obj=None):
        # never allow deletion
        return False

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        if not request.user.is_superuser:
            # Staff users (not superadmins) don't need to change users' groups, permissions, superuser status etc.
            return (
                (None, {'fields': ('username', 'password')}),
                (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
                (_('Permissions'), {'fields': ('is_active', 'groups')}),
            )
        return super().get_fieldsets(request, obj)

    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active']
    list_filter = ('is_staff', 'is_active')
    save_as_continue = False


kasadmin.register(User, KasUserAdmin)


class TaxYearAdmin(admin.ModelAdmin):
    list_display = ('year', 'year_part')

    def has_delete_permission(self, request, obj=None):
        # never allow deletion
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return [(None, {'fields': ('year', )})]
        return super(TaxYearAdmin, self).get_fieldsets(request, obj)


kasadmin.register(TaxYear, TaxYearAdmin)

# ------------------/django-admin/-------------------------------#

admin.site.register(TaxYear)


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
