from django.contrib import admin
from kakeibo.models import *
from import_export import resources
from import_export.admin import ImportExportModelAdmin
# Register your models here.


# ===========================
# Inline
# ===========================
class KakeiboInline(admin.TabularInline):
    model = Kakeibo
    verbose_name = "関連家計簿"
    verbose_name_plural = "関連家計簿"
    fields = ("date", "usage", "fee", "way", "memo")
    readonly_fields = ("date", "usage", "fee", "way", "memo")
    can_delete = False


# ===========================
# Resources
# ===========================
class ResourceResource(resources.ModelResource):
    class Meta:
        model = Resource
        exclude = ["created_by", "created_at", "last_updated_by", "last_updated_at"]


class UsageResource(resources.ModelResource):
    class Meta:
        model = Usage
        exclude = ["created_by", "created_at", "last_updated_by", "last_updated_at"]


class KakeiboResource(resources.ModelResource):
    class Meta:
        model = Kakeibo
        exclude = ["created_by", "created_at", "last_updated_by", "last_updated_at"]


# ModelAdmin
class ResourceAdmin(ImportExportModelAdmin):
    resource_class = ResourceResource
    list_display = [
        "pk", "name", "is_investment", "currency",
        "created_by", "created_at", "last_updated_by", "last_updated_at",
    ]
    search_fields = ("name", )


class UsageAdmin(ImportExportModelAdmin):
    resource_class = UsageResource
    list_display = [
        "pk", "name", "is_expense", "is_shared",
        "created_by", "created_at", "last_updated_by", "last_updated_at",
    ]
    readonly_fields = ["_count_kakeibo", "_count_shared"]
    search_fields = ("name", )

    def _count_kakeibo(self, obj):
        return obj.kakeibo_set.count()
    _count_kakeibo.short_description = 'レコード数（家計簿）'

    def _count_shared(self, obj):
        return obj.shared_kakeibo_set.count()
    _count_shared.short_description = 'レコード数（共通家計簿）'


class BudgetAdmin(admin.ModelAdmin):
    list_display = ["pk", "date", "takashi", "hoko"]


class KakeiboAdmin(ImportExportModelAdmin):
    resource_class = KakeiboResource
    list_display = [
        "pk", "date", "usage", "way", "fee", "memo"
    ]
    autocomplete_fields = ("usage",)
    list_filter = ("way", "usage", "date", )


class CronKakeiboAdmin(admin.ModelAdmin):
    list_display = [
        "pk", "usage", "way", "fee", "memo", "is_coping_to_shared", "kind"
    ]
    autocomplete_fields = ("usage", )


class CreditAdmin(admin.ModelAdmin):
    list_display = [
        "pk", "_debit_month", "date", "name", "fee", "card"
    ]
    list_filter = ("card", )
    search_fields = ("name", "memo")
    inlines = [KakeiboInline, ]

    def _debit_month(self, obj):
        return "{}年{}月".format(obj.debit_date.year, obj.debit_date.month)
    _debit_month.short_description = "請求年月"


class EventAdmin(admin.ModelAdmin):
    list_display = ["pk", "date", "name", "is_closed", "sum_plan"]
    readonly_fields = ("_sum_actual",)
    list_filter = ("is_closed", )
    inlines = [KakeiboInline, ]

    def _sum_actual(self, obj):
        return obj.sum_actual
    _sum_actual.short_description = "sum_actual"


class ExchangeAdmin(admin.ModelAdmin):
    list_display = [
        "pk", "date", "method",
        "_kakeibo_from__resource", "_kakeibo_from__fee",
        "_kakeibo_to__resource", "_kakeibo_to__fee",
    ]

    def _kakeibo_from__resource(self, obj):
        return obj.kakeibo_from.resource_from

    def _kakeibo_to__resource(self, obj):
        return obj.kakeibo_to.resource_to

    def _kakeibo_from__fee(self, obj):
        return obj.kakeibo_from.fee

    def _kakeibo_to__fee(self, obj):
        return obj.kakeibo_to.fee


admin.site.register(Resource, ResourceAdmin)
admin.site.register(Credit, CreditAdmin)
admin.site.register(Usage, UsageAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(SharedKakeibo)
admin.site.register(CronKakeibo, CronKakeiboAdmin)
admin.site.register(Kakeibo, KakeiboAdmin)
admin.site.register(Target)
admin.site.register(Budget, BudgetAdmin)
admin.site.register(Exchange, ExchangeAdmin)