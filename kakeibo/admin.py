from django.contrib import admin
from kakeibo.models import *
from import_export import resources
from import_export.admin import ImportExportModelAdmin
# Register your models here.


# Resources
class ResourceResource(resources.ModelResource):
    class Meta:
        model = Resource


# ModelAdmin
class ResourceAdmin(ImportExportModelAdmin):
    resource_class = ResourceResource


admin.site.register(Resource, ResourceAdmin)
admin.site.register(Way)
admin.site.register(Credit)
admin.site.register(Usage)
admin.site.register(Event)
admin.site.register(SharedKakeibo)
admin.site.register(CronKakeibo)
admin.site.register(Kakeibo)
admin.site.register(Target)
