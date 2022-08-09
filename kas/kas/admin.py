from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from project.admin import kasadmin  # used by the administrator group

from kas.models import FinalSettlement, TaxYear, Person, PersonTaxYear, PolicyTaxYear, PolicyDocument, TaxSlipGenerated


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


class LogEntryAdmin(admin.ModelAdmin):
    # to have a date-based drilldown navigation in the admin page
    date_hierarchy = 'action_time'
    # to filter the resultes by users, content types and action flags
    list_filter = [
        'user',
        'action_flag'
    ]

    # when searching the user will be able to search in both object_repr and change_message
    search_fields = [
        'object_repr',
        'change_message'
    ]

    list_display = [
        'action_time',
        'get_user',
        'action_flag',
        'get_changed_object'
    ]

    def has_module_permission(self, request):
        """
        If you can view the user you can view the logs
        """
        return request.user.has_perm('auth.view_user')

    def has_delete_permission(self, request, obj=None):
        # never allow deletion
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_user(self, obj):
        return obj.user
    get_user.short_description = _('Ændring fortaget af')

    def get_changed_object(self, obj):
        return obj.get_edited_object()
    get_changed_object.short_description = _('Ændret bruger')

    def has_view_permission(self, request, obj=None):
        """
        if wou can view the users you can also view the audit log
        """
        return request.user.has_perm('auth.view_user')

    def get_queryset(self, request):
        """
        only show audit log for user changes
        """
        return LogEntry.objects.filter(content_type__app_label='auth', content_type__model='user')


kasadmin.register(LogEntry, LogEntryAdmin)


class TaxYearAdmin(admin.ModelAdmin):
    list_display = ('year', 'year_part')

    def has_delete_permission(self, request, obj=None):
        # never allow deletion
        return False

    def has_change_permission(self, request, obj=None):
        return True

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
    raw_id_fields = ('person_tax_year',)


admin.site.register(PolicyTaxYear, PolicyTaxYearAdmin)


class PolicyDocumentAdmin(admin.ModelAdmin):
    raw_id_fields = ('person_tax_year', 'policy_tax_year',)


admin.site.register(PolicyDocument, PolicyDocumentAdmin)


class TaxSlipGeneratedAdmin(admin.ModelAdmin):
    list_display = ('persontaxyear', 'status')
    list_filter = ('persontaxyear__tax_year', 'status')


admin.site.register(TaxSlipGenerated, TaxSlipGeneratedAdmin)


class FinalSettlementAdmin(admin.ModelAdmin):
    raw_id_fields = ('person_tax_year',)


admin.site.register(FinalSettlement, FinalSettlementAdmin)
