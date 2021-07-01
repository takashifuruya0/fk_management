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
            # res = redirect('kakeibo:credit_link')
            # res['location'] += "?debit_date={}".format(form.cleaned_data['date_debit'])
            # return res

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
            import_data = []
            way_card = Way.objects.get(name__icontains="カード")
            credit_list = []
            for line in csv_file:
                logger.warning("line: {}".format(line))
                if len(line) < 6:
                    logger.warning("SKIP (len<6): {}".format(line))
                    continue
                if line[5] == "":
                    logger.warning("SKIP (line[5] == ''): {}".format(line))
                    pass
                elif line[0] == "" and line[1] == "":
                    # 合計
                    total = int(line[5])
                else:
                    date_card = datetime.strptime(line[0], "%Y/%m/%d").date()
                    fee = int(line[5])
                    name = line[1]
                    memo = line[6]
                    # Targets
                    targets = Kakeibo.objects.filter(
                        is_active=True, way=way_card, fee=fee, date=date_card, credit=None,
                    ).select_related('way', 'usage')
                    # Sub Targets
                    date_range = (date_card-relativedelta(days=2), date_card+relativedelta(days=2))
                    targets2 = Kakeibo.objects.filter(
                        is_active=True, way=way_card, fee=fee, date__range=date_range, credit=None,
                    ).exclude(pk__in=[t.pk for t in targets]).select_related('way', 'usage')
                    # credit
                    credit = Credit(
                        date=date_card, fee=fee, debit_date=form.cleaned_data['date_debit'],
                        name=name, memo=memo, card=form.cleaned_data['card'],
                    )
                    credit_list.append(credit)
                    # import_data
                    import_data.append({
                        "pk": 1,
                        "date": date_card,
                        "name": name,
                        "fee": fee,
                        "memo": memo,
                        "targets_count": targets.count(),
                        "subtargets_count": targets2.count(),
                        "targets": targets,
                        "subtarget": targets2,
                    })
            # Credit一括作成
            Credit.objects.bulk_create(credit_list)
            messages.success(self.request, "{}件のCredit取込に成功しました".format(len(credit_list)))
            # return
            context = {
                "object_list": import_data,
                "total": total,
                "debit_date": form.cleaned_data['date_debit'],
                "card": form.cleaned_data['card'],
                "usages": Usage.objects.filter(is_expense=True, is_active=True),
            }
            return render(request, "credit_link.html", context)
        else:
            # Invalid時はKakeiboTopへView
            messages.error(self.request, "失敗 {}".format(form.errors))
            logger.error(form.errors)
            return redirect('kakeibo:kakeibo_top')


class CreditLink(MyUserPasssesTestMixin, TemplateView):
    """
    KakeiboとCreditを追加紐付けをするView
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
        for c in credits_unlinked:
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
                "pk": c.pk,
                "date": c.date,
                "name": c.name,
                "fee": c.fee,
                "memo": c.memo,
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
        for r in request.POST:
            logger.info(r)
            if r[0:3] == "id_":
                logger.info("{}-->{}".format(r, r[3:]))
        messages.success(request, "{}件の紐付け、{}件の作成に成功しました".format(1, 1))
        return redirect("kakeibo:credit_link")
