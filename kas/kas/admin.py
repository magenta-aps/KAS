from django.contrib import admin

from kas.models import PensionCompany, TaxYear, Person, PersonTaxYear, PolicyTaxYear, PolicyDocument


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
