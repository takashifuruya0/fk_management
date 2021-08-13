from django.db import models
from django.conf import settings
from datetime import date
from django.db.models import Sum, Avg
from django_currentuser.middleware import get_current_authenticated_user
from django.contrib.auth import get_user_model
from django.conf import settings
from django_currentuser.db.models import CurrentUserField
import math


# Create your models here.

class BaseManager(models.Manager):
    def all_active(self):
        return self.get_queryset().filter(is_active=True)


class BaseModel(models.Model):
    objects = BaseManager()
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    last_updated_at = models.DateTimeField(auto_now=True, verbose_name="最終更新日時")
    created_by = CurrentUserField(
        related_name="%(app_label)s_%(class)s_created_by",
        verbose_name="作成者", editable=False, null=True, blank=True,
    )
    last_updated_by = CurrentUserField(
        related_name="%(app_label)s_%(class)s_last_updated_by",
        verbose_name="最終更新者", editable=False, null=True, blank=True, on_update=True
    )
    is_active = models.BooleanField(default=True, verbose_name="有効")
    legacy_id = models.IntegerField("旧ID", blank=True, null=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        super(BaseModel, self).save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        self.is_active = False
        self.save()


class Resource(BaseModel):
    name = models.CharField("名前", max_length=255)
    memo = models.CharField("備考", max_length=255, null=True, blank=True)
    is_investment = models.BooleanField("投資フラグ")
    currency = models.CharField("通貨", max_length=3, choices=settings.CHOICES_CURRENCY, default="JPY")

    def __str__(self) -> str:
        return "{} ({})".format(self.name, self.currency)

    @property
    def total(self):
        sum_from = Kakeibo.objects.select_related('resource_from').filter(
            currency=self.currency, resource_from=self, is_active=True).aggregate(sum=Sum('fee'))['sum']
        sum_to = Kakeibo.objects.select_related('resource_to').filter(
            currency=self.currency, resource_to=self, is_active=True).aggregate(sum=Sum('fee'))['sum']
        if sum_from and sum_to:
            val = sum_to - sum_from
        else:
            val = sum_to if sum_to else 0
        return val
    
    @property
    def total_converted(self):
        sum_from = Kakeibo.objects.select_related('resource_from').filter(
            currency=self.currency, resource_from=self, is_active=True).aggregate(sum=Sum('fee_converted'))['sum']
        sum_to = Kakeibo.objects.select_related('resource_to').filter(
            currency=self.currency, resource_to=self, is_active=True).aggregate(sum=Sum('fee_converted'))['sum']
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
    is_expense = models.BooleanField("支出フラグ", default=True)
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
    fee = models.IntegerField("金額")
    date = models.DateField("日付")
    debit_date = models.DateField("引き落とし日")
    name = models.CharField("名前", max_length=255)
    memo = models.CharField("備考", max_length=255, null=True, blank=True)
    card = models.CharField("カード", max_length=255, choices=settings.CHOICES_CARD)
    currency = models.CharField("通貨", max_length=3, choices=settings.CHOICES_CURRENCY, default="YEN")
    fee_converted = models.IntegerField("金額（換算後）", null=True, blank=True)
    rate = models.FloatField("レート", null=True, blank=True)

    def __str__(self):
        return "({}) {}".format(self.date, self.name)


class SharedKakeibo(BaseModel):
    fee = models.IntegerField("金額")
    date = models.DateField("日付")
    memo = models.CharField("備考", max_length=255, null=True, blank=True)
    paid_by = models.ForeignKey(get_user_model(), verbose_name="支払者", on_delete=models.CASCADE)
    usage = models.ForeignKey(Usage, verbose_name="用途", on_delete=models.CASCADE)


class Kakeibo(BaseModel):
    fee = models.IntegerField("金額")
    date = models.DateField("日付")
    memo = models.CharField("備考", max_length=255, null=True, blank=True)
    usage = models.ForeignKey(Usage, verbose_name="用途", on_delete=models.CASCADE)
    shared = models.ForeignKey(SharedKakeibo, verbose_name="共通家計簿", on_delete=models.CASCADE, null=True, blank=True)
    credit = models.ForeignKey(Credit, verbose_name="クレジット", on_delete=models.CASCADE, null=True, blank=True)
    event = models.ForeignKey(Event, verbose_name="イベント", on_delete=models.CASCADE, null=True, blank=True)
    #
    way = models.CharField("種別", choices=settings.CHOICES_WAY, max_length=255)
    resource_from = models.ForeignKey(
        Resource, related_name="resource_from", null=True, blank=True, verbose_name="From", on_delete=models.CASCADE
    )
    resource_to = models.ForeignKey(
        Resource, related_name="resource_to", null=True, blank=True, verbose_name="To", on_delete=models.CASCADE
    )
    currency = models.CharField("通貨", max_length=3, choices=settings.CHOICES_CURRENCY, default="JPY")
    fee_converted = models.IntegerField("金額（換算後）", null=True, blank=True)
    rate = models.FloatField("レート", null=True, blank=True)

    def update_fee_converted(self):
        self.fee_converted = math.floor(self.fee * self.rate)
        self.save()

    def save(self, *args, **kwargs):
        if self.currency == "JPY":
            self.fee_converted = self.fee
        elif self.rate:
            self.fee_converted = math.floor(self.fee * self.rate)
        return super(Kakeibo, self).save(*args, **kwargs)


class CronKakeibo(BaseModel):
    fee = models.IntegerField("金額")
    memo = models.CharField("備考", max_length=255, null=True, blank=True)
    way = models.CharField("種別", choices=settings.CHOICES_WAY, max_length=255)
    resource_from = models.ForeignKey(
        Resource, related_name="cronkakeibo_resource_from", null=True, blank=True, verbose_name="From",
        on_delete=models.CASCADE)
    resource_to = models.ForeignKey(
        Resource, related_name="cronkakeibo_resource_to", null=True, blank=True, verbose_name="To",
        on_delete=models.CASCADE)
    usage = models.ForeignKey(Usage, verbose_name="用途", on_delete=models.CASCADE)
    is_coping_to_shared = models.BooleanField("共通コピーフラグ")
    kind = models.CharField("種類", max_length=255, choices=settings.CHOICES_KIND_CRON_KAKEIBO)


class Target(BaseModel):
    val = models.IntegerField("値")
    date = models.DateField("日付")
    memo = models.CharField("備考", max_length=255, null=True, blank=True)
    kind = models.CharField("種類", max_length=255, choices=settings.CHOICES_KIND_TARGET)

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
    method = models.CharField("Method", max_length=255, choices=settings.CHOICES_EXCHANGE_METHOD)
    kakeibo_from = models.OneToOneField(
        Kakeibo, related_name="exchange_from", on_delete=models.CASCADE, verbose_name="Kakeibo_From")
    kakeibo_to = models.OneToOneField(
        Kakeibo, related_name="exchange_to", on_delete=models.CASCADE, verbose_name="Kakeibo_To")
    rate = models.FloatField("Rate (JPY)")
    commission = models.FloatField("Commission")
    currency = models.CharField("Currency of commission", max_length=3, choices=settings.CHOICES_CURRENCY)


class SharedResource(BaseModel):
    name = models.CharField('名前', max_length=255)
    kind = models.CharField('種別', max_length=255, choices=settings.CHOICES_KIND_SHARED_RESOURCE)
    date_open = models.DateField('開始日')
    date_close = models.DateField('終了日', null=True, blank=True)
    detail = models.TextField("詳細", blank=True, null=True)
    val_goal = models.IntegerField("目標金額")

    def __str__(self) -> str:
        return f"【{self.kind}】{self.name}:{self.val_goal:,}円"

    @property
    def val_actual(self):
        val_sum = self.sharedtransaction_set.filter(is_active=True).aggregate(sum=Sum('val'))['sum']
        return val_sum if val_sum else 0
    

class SharedTransaction(BaseModel):
    shared_resource = models.ForeignKey(SharedResource, verbose_name="共通口座", on_delete=models.CASCADE)
    date = models.DateField('日付')
    val = models.IntegerField('金額')
    memo = models.CharField("備考", max_length=255, null=True, blank=True)
    paid_by = models.ForeignKey(get_user_model(), verbose_name="支払者", on_delete=models.CASCADE)
