from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.translation import gettext as _

from kas.models import PensionCompany, TaxYear, Person, PersonTaxYear, PolicyTaxYear, PolicyDocument, TaxSlipGenerated


class KasUserAdmin(UserAdmin):
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

    save_as_continue = False

    # Cannot delete users
    def has_delete_permission(self, request, obj=None):
        return False


admin.site.unregister(User)
admin.site.register(User, KasUserAdmin)


class PensionCompanyAdmin(admin.ModelAdmin):
    pass


admin.site.register(PensionCompany, PensionCompanyAdmin)


class TaxYearAdmin(admin.ModelAdmin):
    pass


admin.site.register(TaxYear, TaxYearAdmin)


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
