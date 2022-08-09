from django.contrib import admin
from prisme.models import Transaction, Prisme10QBatch


class TransactionAdmin(admin.ModelAdmin):
    raw_id_fields = ("person_tax_year",)
    list_display = ("__str__", "status")


admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Prisme10QBatch)
