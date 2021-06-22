from dal import autocomplete
from kakeibo.models import Kakeibo, Usage, Resource, Way
# Create your views here.


# =============================
# Autocomplete
# =============================
class UsageAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Usage.objects.none()
        qs = Usage.objects.filter(is_active=True)
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs.order_by("is_expense")


class SharedUsageAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Usage.objects.none()
        qs = Usage.objects.filter(is_active=True, is_shared=True)
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs.order_by("is_expense")


class WayAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Way.objects.none()
        qs = Way.objects.filter(is_active=True)
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs.order_by("is_expense", "is_transfer")
