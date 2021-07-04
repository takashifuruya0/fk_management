from dal import autocomplete
from django.db.models import Q
from kakeibo.models import Usage, Resource
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


class ResourceAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Resource.objects.none()
        qs = Resource.objects.filter(is_active=True)
        if self.q:
            qs = qs.filter(Q(name__icontains=self.q) | Q(currency__icontains=self.q))
        return qs.order_by("name")


class SharedUsageAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Usage.objects.none()
        qs = Usage.objects.filter(is_active=True, is_shared=True)
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs.order_by("is_expense")
