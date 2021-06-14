from django.contrib import admin
from kakeibo.models import *
from import_export import resources, fields, widgets
from import_export.admin import ImportExportModelAdmin
# Register your models here.


# Resources
class ResourceResource(resources.ModelResource):
    class Meta:
        model = Resource
        exclude = ["created_by", "created_at", "last_updated_by", "last_updated_at"]


class WayResource(resources.ModelResource):
    resource_from = fields.Field(
        column_name='resource_from',
        attribute='resource_from',
        widget=widgets.ForeignKeyWidget(Resource, 'name')
    )
    resource_to = fields.Field(
        column_name='resource_to',
        attribute='resource_to',
        widget=widgets.ForeignKeyWidget(Resource, 'name')
    )

    class Meta:
        model = Way
        exclude = ["created_by", "created_at", "last_updated_by", "last_updated_at"]
        export_order = [
            "id", "name", "resource_from", "resource_to", "memo", "is_expense", "is_active",
        ]


class UsageResource(resources.ModelResource):
    class Meta:
        model = Usage
        exclude = ["created_by", "created_at", "last_updated_by", "last_updated_at"]


# ModelAdmin
class ResourceAdmin(ImportExportModelAdmin):
    resource_class = ResourceResource
    list_display = [
        "pk", "name", "is_investment",
        "created_by", "created_at", "last_updated_by", "last_updated_at",
    ]


class WayAdmin(ImportExportModelAdmin):
    resource_class = WayResource
    # readonly_fields = ["resource_from", "resource_to"]
    list_display = [
        "pk", "name", "is_expense", "is_transfer", "resource_from", "resource_to",
        "created_by", "created_at", "last_updated_by", "last_updated_at",
    ]
    list_filter = ["is_expense", "is_transfer"]
    # list_editable = ["name", "is_expense", "is_transfer", "resource_from", "resource_to",]


class UsageAdmin(ImportExportModelAdmin):
    resource_class = UsageResource
    list_display = [
        "pk", "name", "is_expense", "is_shared",
        "created_by", "created_at", "last_updated_by", "last_updated_at",
    ]


class BudgetAdmin(admin.ModelAdmin):
    list_display = ["pk", "date", "takashi", "hoko"]


admin.site.register(Resource, ResourceAdmin)
admin.site.register(Way, WayAdmin)
admin.site.register(Credit)
admin.site.register(Usage, UsageAdmin)
admin.site.register(Event)
admin.site.register(SharedKakeibo)
admin.site.register(CronKakeibo)
admin.site.register(Kakeibo)
admin.site.register(Target)
admin.site.register(Budget, BudgetAdmin)
