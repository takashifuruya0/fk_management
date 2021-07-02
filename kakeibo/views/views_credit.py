# coding: UTF-8
from django.shortcuts import render
from django.views.generic import FormView, TemplateView, View
from django.contrib import messages
from django.shortcuts import redirect, reverse
from django.db.models import Q, Sum
from django.db import transaction
from django.contrib import messages
from kakeibo.models import Kakeibo, Usage, Credit, Way
from kakeibo.forms import CreditImportForm
from kakeibo.views.views_kakeibo import MyUserPasssesTestMixin
from datetime import datetime
from dateutil.relativedelta import relativedelta
from io import TextIOWrapper
import csv
import logging
logger = logging.getLogger('django')


class CreditImport(MyUserPasssesTestMixin, View):
    """
    CSVを取り込んで一覧化するView
    """
    def get(self, request):
        messages.warning(request, "アクセスが許可されていません")
        return redirect("kakeibo:kakeibo_top")

    def post(self, request, *args, **kwargs):
        form = CreditImportForm(request.POST, request.FILES)
        if form.is_valid():
            # CSVの読み込み
            data = form.cleaned_data['file']
            try:
                form_data = TextIOWrapper(data, encoding='shift-jis')
                csv_file = csv.reader(form_data)
            except Exception as e:
                # Error時はKakeiboTopへView
                messages.error(self.request, "失敗 {}".format(e))
                logger.error(e)
                return redirect('kakeibo:kakeibo_top')
            # 読み込み成功後
            card = form.cleaned_data['card']
            credit_list = []
            for line in csv_file:
                logger.warning("line: {}".format(line))
                if len(line) < 6:
                    if form.cleaned_data['card'] == "SFC":
                        if line[0] == '古屋\u3000朋子\u3000様':
                            card = "SFC（家族）"
                        else:
                            card = "SFC"
                    logger.warning("SKIP (len<6): {}".format(line))
                elif line[5] == "":
                    logger.warning("SKIP (line[5] == ''): {}".format(line))
                elif line[0] == "" and line[1] == "":
                    # 合計
                    total = int(line[5])
                else:
                    date_card = datetime.strptime(line[0], "%Y/%m/%d").date()
                    fee = int(line[5])
                    name = line[1]
                    memo = line[6]
                    credit = Credit(
                        date=date_card, fee=fee, debit_date=form.cleaned_data['date_debit'],
                        name=name, memo=memo, card=card,
                    )
                    credit_list.append(credit)
            # Credit一括作成
            Credit.objects.bulk_create(credit_list)
            messages.success(self.request, "{}件のCredit取込に成功しました-->{:,}円".format(len(credit_list), total))
            # redirect
            res = redirect('kakeibo:credit_link')
            res['location'] += "?debit_date={}".format(form.cleaned_data['date_debit'])
            return res
        else:
            # Invalid時はKakeiboTopへView
            messages.error(self.request, "失敗 {}".format(form.errors))
            logger.error(form.errors)
            return redirect('kakeibo:kakeibo_top')


class CreditLink(MyUserPasssesTestMixin, TemplateView):
    """
    KakeiboとCreditを追加紐付けをするView
    Credit --> Kakeibo
    """
    template_name = "credit_link.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        target_data = []
        way_card = Way.objects.get(name__icontains="カード")
        # credit_unlinked
        if self.request.GET.get('debit_date', None):
            debit_date = datetime.strptime(self.request.GET.get('debit_date', None), "%Y-%m-%d")
            debit_month = debit_date.month
            debit_year = debit_date.year
            credits_unlinked = Credit.objects.prefetch_related('kakeibo_set').filter(
                is_active=True, kakeibo=None, debit_date__year=debit_year, debit_date__month=debit_month)
        else:
            debit_date = None
            credits_unlinked = Credit.objects.prefetch_related('kakeibo_set').filter(is_active=True, kakeibo=None)
        # total
        total = credits_unlinked.aggregate(sum=Sum('fee'))['sum']
        # loop
        for c in credits_unlinked.order_by('-date'):
            # Targets
            targets = Kakeibo.objects.filter(
                is_active=True, way=way_card, fee=c.fee, date=c.date, credit=None,
            ).select_related('way', 'usage')
            # Sub Targets
            date_range = (c.date-relativedelta(days=2), c.date+relativedelta(days=2))
            targets2 = Kakeibo.objects.filter(
                is_active=True, way=way_card, fee=c.fee, date__range=date_range, credit=None,
            ).exclude(pk__in=[t.pk for t in targets]).select_related('way', 'usage')
            # Data
            target_data.append({
                "credit": c,
                "targets_count": targets.count(),
                "subtargets_count": targets2.count(),
                "targets": targets,
                "subtarget": targets2,
            })
        # return
        context.update({
            "object_list": target_data,
            "total": total,
            "debit_date": debit_date,
            "card": None,
            "usages": Usage.objects.filter(is_expense=True, is_active=True),
        })
        return context

    def post(self, request, *args, **kwargs):
        logger.info(request.POST)
        way_card = Way.objects.get(name="カード払い")
        num_add = 0
        num_link = 0
        num_delete = 0
        for r in request.POST:
            # credit.pk をチェック
            if r[0:3] == "id_":
                pk = r[3:]
                credit = Credit.objects.get(pk=pk)
                # 紐付ける家計簿
                target = request.POST.get(r, None)
                if target == "new":
                    # kakeibo作成
                    usage = Usage.objects.get(pk=request.POST.get("usage_{}".format(pk)))
                    kakeibo = Kakeibo(
                        fee=credit.fee, date=credit.date, way=way_card, memo=credit.name, usage=usage, credit=credit
                    )
                    kakeibo.save()
                    num_add += 1
                elif target == "delete":
                    # credit削除
                    credit.delete()
                    num_delete += 1
                elif target:
                    # kakeibo紐付け
                    kakeibo = Kakeibo.objects.get(pk=target)
                    kakeibo.credit = credit
                    kakeibo.save()
                    num_link += 1
                else:
                    raise Exception('Kakeibo was Not found ')
        if num_link > 0 or num_add > 0:
            messages.success(request, "{}件の紐付け、{}件の作成に成功しました".format(num_link, num_add))
        if num_delete > 0:
            messages.info(request, "{}件のCredit削除を実施しました".format(num_delete))
        return redirect("kakeibo:credit_link")


class CreditLinkFromKakeibo(MyUserPasssesTestMixin, TemplateView):
    """
    KakeiboとCreditを追加紐付けをするView
    Kakeibo --> Credit
    """
    template_name = "credit_link_from_kakeibo.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        target_data = []
        way_card = Way.objects.get(name__icontains="カード")
        # kakeibo_unlinked
        if self.request.GET.get('target_date', None):
            target_date = datetime.strptime(self.request.GET.get('target_date', None), "%Y-%m-%d")
            target_month = target_date.month
            target_year = target_date.year
            kakeibos_unlinked = Kakeibo.objects.filter(
                way=way_card, is_active=True, credit=None, date__year=target_year, date__month=target_month, fee__gt=0
            ).select_related('usage').order_by('-date')
        else:
            target_date = None
            kakeibos_unlinked = Kakeibo.objects.filter(
                way=way_card, is_active=True, credit=None, fee__gt=0
            ).select_related('usage').order_by('-date')[0:100]
        for ku in kakeibos_unlinked:
            credit = Credit.objects.prefetch_related('kakeibo_set').filter(
                is_active=True, kakeibo=None, fee=ku.fee)
            target_data.append({
                "kakeibo": ku,
                "credit": credit,
            })
        # total
        total = kakeibos_unlinked.aggregate(sum=Sum('fee'))['sum']
        # credits_unlinked
        credits_unlinked = Credit.objects.prefetch_related('kakeibo_set').filter(is_active=True, kakeibo=None)
        # return
        context.update({
            # "object_list": kakeibos_unlinked,
            "object_list": target_data,
            "total": total,
            "target_date": target_date,
            "card": None,
            "credits": credits_unlinked
        })
        return context

    def post(self, request, *args, **kwargs):
        num_link = 0
        num_delete = 0
        for r in request.POST:
            # kakeibo.pk をチェック
            if r[0:3] == "id_":
                pk = r[3:]
                kakeibo = Kakeibo.objects.get(pk=pk)
                # 紐付ける家計簿
                target = request.POST.get(r, None)
                if target == "link":
                    # credit紐付け
                    kakeibo.credit = Credit.objects.get(pk=request.POST.get("credit_{}".format(pk)))
                    kakeibo.save()
                    num_link += 1
                elif target == "delete":
                    # kakeibo削除
                    kakeibo.delete()
                    num_delete += 1
        if num_link > 0:
            messages.success(request, "{}件のレコードを紐付けました".format(num_link))
        if num_delete > 0:
            messages.warning(request, "{}件のレコード削除しました".format(num_delete))
        return redirect("kakeibo:credit_link_from_kakeibo")
#