from django.contrib import admin
from accounts.models import *
from accounts.forms import *
# Register your models here.


class CustomUserAdmin(admin.ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ("username", "email", "is_staff", "is_superuser")
    readonly_fields = ("last_login", "date_joined", "id")

    def get_form(self, request, obj=None, **kwargs):
        """
        Use special form during foo creation
        """
        defaults = {}
        if obj is None:
            defaults['form'] = self.add_form
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)


admin.site.register(CustomUser, CustomUserAdmin)
