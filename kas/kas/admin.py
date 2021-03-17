from django.contrib import admin

from kas.models import PensionCompany, TaxYear, Person, PersonTaxYear, PolicyTaxYear, PolicyDocument, TaxSlipGenerated


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
    list_filter = ('persontaxyear__tax_year', )

    def delivery_method(self, obj):
        return obj.delivery_method


admin.site.register(TaxSlipGenerated, TaxSlipGeneratedAdmin)
