from django.views.generic import TemplateView, CreateView, UpdateView, ListView, DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.list import MultipleObjectMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from django.db.models import Sum
from django.contrib import messages
import math
from kakeibo.models import Resource, SharedKakeibo, Budget, Usage, SharedResource, SharedTransaction
from kakeibo.forms import SharedForm, SharedSearchForm, SharedResourceForm, SharedTransactionForm
from kakeibo.functions import calculation_shared
# Create your views here.


class SharedTop(LoginRequiredMixin, TemplateView):
    template_name = "shared_top.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # year, month
        if self.request.GET.get("target_ym", None):
            target_ym = datetime.strptime(self.request.GET["target_ym"], "%Y-%m").date()
        else:
            target_ym = date.today()
        initial_val = "{}-{}".format(target_ym.year, str(target_ym.month).zfill(2))
        records_this_month = SharedKakeibo.objects.filter(
            is_active=True, date__year=target_ym.year, date__month=target_ym.month
        )
        # last month
        last_ym = target_ym - relativedelta(months=1)
        # budget
        budget = Budget.objects.filter(date__lte=target_ym).latest('date')
        # payment
        context.update(calculation_shared.calc_payment(records_this_month))
        # Black/Red
        diff = context['payment']['total'] - budget.total
        is_black = diff < 0
        # seisan
        context.update(calculation_shared.calc_seisan(budget, diff, context['payment']))
        # p_budget
        context.update(calculation_shared.calc_p_budget(budget, diff))
        # usage
        usages_shared = Usage.objects.filter(
            is_active=True, is_shared=True).prefetch_related('sharedkakeibo_set')
        usages = dict()
        for us in usages_shared.order_by('pk'):
            tm_sum = us.sharedkakeibo_set.filter(
                is_active=True, date__year=target_ym.year, date__month=target_ym.month
            ).aggregate(sum=Sum('fee'))['sum']
            lm_sum = us.sharedkakeibo_set.filter(
                is_active=True, date__year=last_ym.year, date__month=last_ym.month
            ).aggregate(sum=Sum('fee'))['sum']
            usages[us.name] = {
                "tm": tm_sum if tm_sum else 0,
                "lm": lm_sum if lm_sum else 0,
            }
        # SharedResource
        shared_resources = SharedResource.objects.filter(
            date_close=None, is_active=True).order_by('-pk')
        shared_resourcce_form = SharedResourceForm(initial={"date": date.today()})
        shared_transaction_form = SharedTransactionForm(
            initial={"date": date.today(), "paid_by": self.request.user})
        # return
        context.update({
            "budget": budget,
            "diff": diff,
            "is_black": is_black,
            "target_ym": target_ym,
            "last_ym": last_ym,
            "form": SharedForm(initial={"paid_by": self.request.user, "date": date.today()}),
            "initial_val": initial_val,
            "usages": usages,
            "shared_resources": shared_resources,
            "shared_resource_form": shared_resourcce_form,
            "shared_transaction_form": shared_transaction_form,
        })
        return context

#!====================================
#! SharedKakeibo
#!====================================
class SharedList(LoginRequiredMixin, ListView):
    template_name = "shared_list.html"
    model = SharedKakeibo
    paginate_by = 20

    def get_queryset(self):
        q = SharedKakeibo.objects.filter(is_active=True)
        # date
        if self.request.GET.get('date_from', None) and self.request.GET.get('date_to', None):
            q = q.filter(date__range=(self.request.GET['date_from'], self.request.GET['date_to']))
        elif self.request.GET.get('date_from', None):
            q = q.filter(date__gte=self.request.GET['date_from'])
        elif self.request.GET.get('date_to', None):
            q = q.filter(date__lte=self.request.GET['date_to'])
        # usage
        if self.request.GET.getlist('usages', None):
            q = q.filter(usage__in=self.request.GET.getlist('usages'))
        # memo
        if self.request.GET.get("memo", None):
            q = q.filter(memo__icontains=self.request.GET.get("memo"))
        return q.select_related('paid_by', 'usage').order_by('-date')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        params = ""
        for k, vs in dict(self.request.GET).items():
            if not k == "page":
                for v in vs:
                    params = params + "&{}={}".format(k, v)
        if params:
            messages.info(self.request, "検索結果を表示します。{}".format(params))
        context.update({
            'form': SharedForm(initial={"paid_by": self.request.user, "date": date.today()}),
            "search_form": SharedSearchForm(self.request.GET),
            "params": params,
        })
        return context


class SharedDetail(LoginRequiredMixin, DetailView):
    template_name = "shared_detail.html"
    model = SharedKakeibo


class SharedCreate(LoginRequiredMixin, CreateView):
    template_name = "shared_create.html"
    model = SharedKakeibo
    form_class = SharedForm

    def get_success_url(self):
        messages.success(self.request, f"{self.object}を作成しました")
        if self.request.POST.get('source_path', None):
            return self.request.POST['source_path']
        else:
            return reverse("kakeibo:shared_detail", kwargs={"pk": self.object.pk})


class SharedUpdate(LoginRequiredMixin, UpdateView):
    template_name = "shared_update.html"
    model = SharedKakeibo
    form_class = SharedForm

    def get_success_url(self):
        messages.success(self.request, f"{self.object}を更新しました")
        if self.request.POST.get('source_path', None):
            return self.request.POST['source_path']
        else:
            return reverse("kakeibo:shared_detail", kwargs={"pk": self.object.pk})


class SharedDelete(LoginRequiredMixin, DeleteView):
    model = SharedKakeibo
    template_name = "shared_delete.html"

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        if not obj.is_active:
            messages.warning(request, "{}は削除済みです".format(obj))
            return redirect('kakeibo:shared_list')
        return super(SharedDelete, self).get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('kakeibo:shared_list')

    def post(self, request, *args, **kwargs):
        ob = self.get_object()
        result = super().delete(request, *args, **kwargs)
        messages.success(self.request, '「{}」を削除しました'.format(ob))
        return result


#!====================================
#! SharedResource
#!====================================
class SharedResourceDetail(LoginRequiredMixin, DetailView, MultipleObjectMixin):
    model = SharedResource
    paginate_by = 5
    template_name = "shared_resource_detail.html"

    def get_context_data(self, **kwargs):
        object_list = SharedTransaction.objects.filter(
            shared_resource=self.get_object(), is_active=True).order_by('-date')
        shared_transaction_form = SharedTransactionForm(
            initial={"date": date.today(), "shared_resource": self.object, "paid_by": self.request.user}
        )
        res = super(SharedResourceDetail, self).get_context_data(
            object_list=object_list, shared_transaction_form=shared_transaction_form,
            **kwargs
        )
        return res


class SharedResourceList(LoginRequiredMixin, ListView):
    model = SharedResource
    paginate_by = 10
    template_name = "shared_resource_list.html"
    queryset = SharedResource.objects.all_active()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = SharedResourceForm(initial={"date_open": date.today()})
        return context


class SharedResourceUpdate(LoginRequiredMixin, UpdateView):
    model = SharedResource
    template_name = "shared_resource_update.html"
    form_class = SharedResourceForm
    
    def get_success_url(self) -> str:
        messages.success(self.request, f"{self.object}を更新しました")
        if self.request.POST.get('source_path', None):
            return self.request.POST['source_path']
        else:
            return reverse('kakeibo:shared_resource_detail', kwargs={"pk": self.object.pk})


class SharedResourceCreate(LoginRequiredMixin, CreateView):
    model = SharedResource
    template_name = "shared_resource_create.html"
    form_class = SharedResourceForm

    def get_success_url(self) -> str:
        messages.success(self.request, f"{self.object}を作成しました")
        if self.request.POST.get('source_path', None):
            return self.request.POST['source_path']
        else:
            return reverse('kakeibo:shared_resource_detail', kwargs={"pk": self.object.pk})


class SharedResourceDelete(LoginRequiredMixin, DeleteView):
    model = SharedResource
    template_name = "shared_resource_delete.html"

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        if not obj.is_active:
            messages.warning(request, "{}は削除済みです".format(obj))
            return redirect("kakeibo:shared_top") 
        return super(SharedResourceDelete, self).get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('kakeibo:shared_resource_list')

    def post(self, request, *args, **kwargs):
        ob = self.get_object()
        result = super().delete(request, *args, **kwargs)
        sts = SharedTransaction.objects.filter(shared_resource=ob)
        num = sts.count()
        sts.update(is_active=False)
        messages.success(self.request, '「{}」と紐づく{}件の明細を削除しました'.format(ob, num))
        return result


#!====================================
#! SharedTransaction
#!====================================
class SharedTransactionDetail(LoginRequiredMixin, DetailView):
    model = SharedTransaction
    template_name = "shared_transaction_detail.html"


class SharedTransactionCreate(LoginRequiredMixin, CreateView):
    model = SharedTransaction
    template_name = "shared_transaction_create.html"
    form_class = SharedTransactionForm

    def get_success_url(self) -> str:
        messages.success(self.request, f"{self.object}を作成しました")
        return reverse('kakeibo:shared_resource_detail', kwargs={"pk": self.object.shared_resource.pk})

    def get_form(self, form_class=form_class):
        form = super().get_form(form_class=form_class)
        form.initial={
            "shared_resource": self.request.GET.get("shared_resource", None),
            "date": date.today(),
            "paid_by": self.request.user,
        }
        return form 

class SharedTransactionUpdate(LoginRequiredMixin, UpdateView):
    model = SharedTransaction
    template_name = "shared_transaction_update.html"
    form_class = SharedTransactionForm

    def get_success_url(self) -> str:
        messages.success(self.request, f"{self.object}を更新しました")
        return reverse('kakeibo:shared_resource_detail', kwargs={"pk": self.object.shared_resource.pk})


class SharedTransactionDelete(LoginRequiredMixin, DeleteView):
    model = SharedTransaction
    template_name = "shared_transaction_delete.html"

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        if not obj.is_active:
            messages.warning(request, "{}は削除済みです".format(obj))
            return redirect("kakeibo:shared_top") 
        return super(SharedTransactionDelete, self).get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('kakeibo:shared_resource_detail', kwargs={"pk": self.object.shared_resource.pk})

    def post(self, request, *args, **kwargs):
        ob = self.get_object()
        result = super().delete(request, *args, **kwargs)
        messages.success(self.request, '「{}」を削除しました'.format(ob))
        return result