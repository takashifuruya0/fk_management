from django.db import models
from datetime import date
from django.db.models import Sum, Value
from django.contrib.auth import get_user_model
import math
from ..functions import money
from .models_base import BaseModel
from .models_base import CHOICES_KIND_CRON_KAKEIBO, CHOICES_KIND_TARGET, CHOICES_WAY
from .models_base import CHOICES_EXCHANGE_METHOD, CHOICES_CARD, CHOICES_CURRENCY
# Create your models here.


class Resource(BaseModel):
    name = models.CharField("名前", max_length=255)
    memo = models.CharField("備考", max_length=255, null=True, blank=True)
    is_investment = models.BooleanField("投資フラグ")

    def __str__(self) -> str:
        return self.name

    @property
    def total(self):
        sum_from = Kakeibo.objects.select_related('resource_from').filter(
            resource_from=self, is_active=True).aggregate(sum=Sum('fee'))['sum']
        sum_to = Kakeibo.objects.select_related('resource_to').filter(
            resource_to=self, is_active=True).aggregate(sum=Sum('fee'))['sum']
        if sum_from and sum_to:
            val = sum_to - sum_from
        else:
            val = sum_to if sum_to else 0
        return val

    @property
    def total_calculated(self):
        sum_from = Kakeibo.objects.select_related('resource_from') \
            .filter(resource_from=self, is_active=True) \
            .values("currency").annotate(sum=Sum('fee'), pm=Value(-1, models.IntegerField()))
        sum_to = Kakeibo.objects.select_related('resource_to') \
            .filter(resource_to=self, is_active=True) \
            .values("currency").annotate(sum=Sum('fee'), pm=Value(1, models.IntegerField()))
        rate = {"JPY": 1}
        total = 0
        data = sum_from.union(sum_to)
        for d in data:
            if rate.get(d['currency'], None) is None:
                rate[d['currency']] = money.get_rate(d['currency'])
            r = rate.get(d['currency'])
            total += (float(d["sum"]) * r * d["pm"])
        return int(total)
    
    @property
    def total_converted(self):
        sum_from = Kakeibo.objects.select_related('resource_from').filter(
            resource_from=self, is_active=True).aggregate(sum=Sum('fee_converted'))['sum']
        sum_to = Kakeibo.objects.select_related('resource_to').filter(
            resource_to=self, is_active=True).aggregate(sum=Sum('fee_converted'))['sum']
        if sum_from and sum_to:
            val = sum_to - sum_from
        else:
            val = sum_to if sum_to else 0
        return val

    @property
    def diff_this_month(self):
        today = date.today()
        sum_from = Kakeibo.objects.select_related('resource_from').filter(
            currency=self.currency, resource_from=self, date__month=today.month, date__year=today.year, is_active=True
        ) .aggregate(sum=Sum('fee'))['sum']
        sum_to = Kakeibo.objects.select_related('resource_to').filter(
            currency=self.currency, resource_to=self, date__month=today.month, date__year=today.year, is_active=True
        ).aggregate(sum=Sum('fee'))['sum']
        if sum_from and sum_to:
            val = sum_to - sum_from
        elif sum_from and sum_from > 0 and not sum_to:
            val = - sum_from
        else:
            val = sum_to if sum_to else 0
        return val


class Usage(BaseModel):
    name = models.CharField("名前", max_length=255)
    memo = models.CharField("備考", max_length=255, null=True, blank=True)
    # is_expense = models.BooleanField("支出フラグ", default=True)
    way = models.CharField("種別", choices=CHOICES_WAY, max_length=255)
    is_shared = models.BooleanField("共通フラグ", default=False)

    def __str__(self) -> str:
        return self.name


class Event(BaseModel):
    name = models.CharField("名前", max_length=255)
    memo = models.CharField("備考", max_length=255, null=True, blank=True)
    detail = models.TextField("詳細", blank=True, null=True)
    is_closed = models.BooleanField("終了フラグ", default=False)
    date = models.DateField("日付")
    sum_plan = models.IntegerField("計画総額")

    def __str__(self) -> str:
        return self.name

    @property
    def sum_actual(self):
        return self.kakeibo_set.filter(is_active=True).aggregate(sum=Sum('fee'))['sum']


class Credit(BaseModel):
    fee = models.DecimalField('金額', max_digits=9, decimal_places=2)
    date = models.DateField("日付")
    debit_date = models.DateField("引き落とし日")
    name = models.CharField("名前", max_length=255)
    memo = models.CharField("備考", max_length=255, null=True, blank=True)
    card = models.CharField("カード", max_length=255, choices=CHOICES_CARD)
    currency = models.CharField("通貨", max_length=3, choices=CHOICES_CURRENCY, default="JPY")
    fee_converted = models.IntegerField("金額（JPY）")
    rate = models.FloatField("レート", help_text='JPY for 1 local currency', null=True, blank=True)

    def __str__(self):
        return "({}) {}".format(self.date, self.name)


class CreditUsage(BaseModel):
    name = models.CharField("名前", max_length=255)
    usage = models.ForeignKey(Usage, verbose_name="用途", on_delete=models.CASCADE)
    memo = models.CharField("備考", max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


class SharedKakeibo(BaseModel):
    fee = models.DecimalField('金額', max_digits=9, decimal_places=2)
    date = models.DateField("日付")
    memo = models.CharField("備考", max_length=255, null=True, blank=True)
    paid_by = models.ForeignKey(get_user_model(), verbose_name="支払者", on_delete=models.CASCADE)
    usage = models.ForeignKey(Usage, verbose_name="用途", on_delete=models.CASCADE)


class Kakeibo(BaseModel):
    fee = models.DecimalField('金額', max_digits=9, decimal_places=2)
    date = models.DateField("日付")
    memo = models.CharField("備考", max_length=255, null=True, blank=True)
    usage = models.ForeignKey(Usage, verbose_name="用途", on_delete=models.CASCADE)
    shared = models.ForeignKey(SharedKakeibo, verbose_name="共通家計簿", on_delete=models.CASCADE, null=True, blank=True)
    credit = models.ForeignKey(Credit, verbose_name="クレジット", on_delete=models.CASCADE, null=True, blank=True)
    event = models.ForeignKey(Event, verbose_name="イベント", on_delete=models.CASCADE, null=True, blank=True)
    way = models.CharField("種別", choices=CHOICES_WAY, max_length=255)
    resource_from = models.ForeignKey(
        Resource, related_name="resource_from", null=True, blank=True, verbose_name="From", on_delete=models.CASCADE
    )
    resource_to = models.ForeignKey(
        Resource, related_name="resource_to", null=True, blank=True, verbose_name="To", on_delete=models.CASCADE
    )
    card = models.CharField("カード", max_length=255, choices=CHOICES_CARD, blank=True, null=True)
    currency = models.CharField("通貨", max_length=3, choices=CHOICES_CURRENCY, default="JPY")
    fee_converted = models.IntegerField("金額（JPY）")
    rate = models.FloatField("レート", help_text='JPY for 1 local currency', null=True, blank=True)

    def update_fee_converted(self):
        self.fee_converted = int(float(self.fee) * self.rate)
        self.save()

    def save(self, *args, **kwargs):
        if self.currency == "JPY":
            self.fee_converted = int(self.fee)
        elif self.rate:
            self.fee_converted = int(float(self.fee) * self.rate)
        else:
            self.rate = money.get_rate(self.currency)
            self.fee_converted = int(float(self.fee) * self.rate)
        return super(Kakeibo, self).save(*args, **kwargs)


class CronKakeibo(BaseModel):
    fee = models.DecimalField('金額', max_digits=9, decimal_places=2)
    memo = models.CharField("備考", max_length=255, null=True, blank=True)
    way = models.CharField("種別", choices=CHOICES_WAY, max_length=255)
    resource_from = models.ForeignKey(
        Resource, related_name="cronkakeibo_resource_from", null=True, blank=True, verbose_name="From",
        on_delete=models.CASCADE)
    resource_to = models.ForeignKey(
        Resource, related_name="cronkakeibo_resource_to", null=True, blank=True, verbose_name="To",
        on_delete=models.CASCADE)
    usage = models.ForeignKey(Usage, verbose_name="用途", on_delete=models.CASCADE)
    card = models.CharField("カード", max_length=255, choices=CHOICES_CARD, blank=True, null=True)
    is_coping_to_shared = models.BooleanField("共通コピーフラグ")
    kind = models.CharField("種類", max_length=255, choices=CHOICES_KIND_CRON_KAKEIBO)


class Target(BaseModel):
    val = models.IntegerField("値")
    date = models.DateField("日付")
    memo = models.CharField("備考", max_length=255, null=True, blank=True)
    kind = models.CharField("種類", max_length=255, choices=CHOICES_KIND_TARGET)

    def __str__(self) -> str:
        return "Target_{}".format(self.date)


class Budget(BaseModel):
    date = models.DateField("日付")
    takashi = models.IntegerField("敬士予算")
    hoko = models.IntegerField("朋子予算")
    memo = models.CharField("備考", max_length=255, null=True, blank=True)

    @property
    def total(self):
        return self.takashi + self.hoko

    def __str__(self):
        return "予算_{}".format(self.date)


class Exchange(BaseModel):
    date = models.DateField("Date")
    method = models.CharField("Method", max_length=255, choices=CHOICES_EXCHANGE_METHOD)
    kakeibo_from = models.OneToOneField(
        Kakeibo, related_name="exchange_from", on_delete=models.CASCADE, verbose_name="Kakeibo_From")
    kakeibo_to = models.OneToOneField(
        Kakeibo, related_name="exchange_to", on_delete=models.CASCADE, verbose_name="Kakeibo_To")
    rate = models.FloatField("レート", help_text='JPY for 1 local currency', null=True, blank=True)