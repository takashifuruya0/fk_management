from django.contrib import admin
from django.db.models import query
from asset.models import Stock, Order, Entry, StockAnalysisData, StockValueData
from asset.models import AssetStatus, AssetTarget, ReasonWinLoss, Ipo, Dividend


# =====================
# TabularInline
# =====================
class OrderInline(admin.TabularInline):
    model = Order
    ordering = ("-datetime", )
    verbose_name = "売買注文"
    verbose_name_plural = "売買注文"
    fields = ("datetime", "is_buy", "val", "num", "commission")
    readonly_fields = ("datetime", "is_buy", "val", "num", "commission")
    can_delete = False 
    show_change_link = True


class EntryInline(admin.TabularInline):
    model = Entry
    ordering = ("is_closed", "stock__code")
    verbose_name = "エントリー"
    verbose_name_plural = "エントリー"
    fields = (
        "pk", "is_closed", "date_open", "date_close", 
        "profit_after_tax", "total_buy", "total_sell")
    readonly_fields = (
        "pk", "is_closed", "date_open", "date_close", 
        "profit_after_tax", "total_buy", "total_sell")
    can_delete = False
    show_change_link = True


class DividendInline(admin.TabularInline):
    model = Dividend
    ordering = ("-date", )
    verbose_name = "配当"
    verbose_name_plural = "配当"
    fields = ("pk", "date", "val", "tax")
    readonly_fields = fields
    can_delete = False


# =====================
# ModelAdmin
# =====================
class StockAdmin(admin.ModelAdmin):
    list_filter = ("industry", "market")
    list_display = ("pk", "code", "name",)
    readonly_fields = ("latest_val", "latest_val_date")
    inlines = [EntryInline, ]


class OrderAdmin(admin.ModelAdmin):
    list_display = ("pk", "datetime", "is_buy", "val", "num", "commission")
    list_filter = ("stock", )
    ordering = ("-datetime",)


class EntryAdmin(admin.ModelAdmin):
    list_filter = ("status", "is_closed")
    list_display = (
        "pk", "stock", "status", "entry_type", "is_closed", "is_nisa", 
        "date_open", "date_close", "profit_after_tax")
    readonly_fields = (
        "val_buy", "num_buy", "total_buy",
        "val_sell", "num_sell", "total_sell",
        "profit_after_tax",)
    inlines = [OrderInline, DividendInline]
    ordering = ("is_closed", "stock__code")


class StockValueDataAdmin(admin.ModelAdmin):
    list_display = (
        "pk", "stock", "date", "val_high", "val_low", "val_open", "val_close", "turnover")
    list_filter = ("stock", "date")
    ordering = ("-date",)


class AssetStatusAdmin(admin.ModelAdmin):
    list_display = ("pk", "date", "total", "gross_profit", "buying_power")
    ordering = ("-date",)


class AssetTargetAdmin(admin.ModelAdmin):
    list_display = ("pk", "date", "val_investment", "val_target",
        "is_achieved_target", "is_achieved_investment")
    readonly_fields = (
        "is_achieved_target",  "actual_target", "diff_target",
        "is_achieved_investment",  "actual_investment", "diff_investment",
    )
    ordering = ("-date",)


class IpoAdmin(admin.ModelAdmin):
    list_display = ("pk", "stock", "status", "rank", "is_applied", "datetime_open", "datetime_close", "datetime_select")
    ordering = ("-datetime_open", "is_applied")


class DividendAdmin(admin.ModelAdmin):
    list_display = ("pk", "entry", "date", "val", "tax")

# =====================
# Register your models here.
# =====================
admin.site.register(Stock, StockAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Entry, EntryAdmin)
admin.site.register(StockValueData, StockValueDataAdmin)
admin.site.register(StockAnalysisData)
admin.site.register(AssetStatus, AssetStatusAdmin)
admin.site.register(AssetTarget, AssetTargetAdmin)
admin.site.register(ReasonWinLoss)
admin.site.register(Ipo, IpoAdmin)
admin.site.register(Dividend, DividendAdmin)