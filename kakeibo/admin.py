from django.contrib import admin
from kakeibo.models import *
# Register your models here.


# class TestmodelAdmin(admin.ModelAdmin):
#     list_display = [
#         "memo", "created_by", "created_at", "last_updated_by", "last_updated_at"
#     ]
#
#
# admin.site.register(Testmodel, TestmodelAdmin)
admin.site.register(Resource)
admin.site.register(Way)
admin.site.register(Credit)
admin.site.register(Usage)
admin.site.register(Event)
admin.site.register(SharedKakeibo)
admin.site.register(CronKakeibo)
admin.site.register(Kakeibo)
admin.site.register(Target)
