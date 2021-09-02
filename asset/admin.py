from django.contrib import admin
from asset.models import Stock, Order, Entry, StockAnalysisData, StockValueData
from asset.models import AssetStatus, AssetTarget, ReasonWinLoss, Ipo, Dividend

# Register your models here.
admin.site.register(Stock)
admin.site.register(Order)
admin.site.register(Entry)
admin.site.register(StockValueData)
admin.site.register(StockAnalysisData)
admin.site.register(AssetStatus)
admin.site.register(AssetTarget)
admin.site.register(ReasonWinLoss)
admin.site.register(Ipo)
admin.site.register(Dividend)