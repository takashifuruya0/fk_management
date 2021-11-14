from django.db import models
from datetime import date
from django.db.models import Sum, Avg
from django_currentuser.middleware import get_current_authenticated_user
from django.contrib.auth import get_user_model
from django_currentuser.db.models import CurrentUserField
import math


# Create your models here.
CHOICES_WAY = (
    ("収入", "収入"), 
    ("支出", "支出"), 
    ("振替", "振替"), 
    ("両替", "両替"), 
    ("その他", "その他"),
)
CHOICES_CARD = (
    ("SFC", "SFC"), 
    ("SFC（家族）", "SFC（家族）"), 
    ("GoldPoint", "GoldPoint"),
    ("ANA USA", "ANA USA")
)
CHOICES_KIND_CRON_KAKEIBO = (
    ("monthly", "月次"),
    ("yearly_01", "年次（1月）"), ("yearly_02", "年次（2月）"), ("yearly_03", "年次（3月）"),
    ("yearly_04", "年次（4月）"), ("yearly_05", "年次（5月）"), ("yearly_06", "年次（6月）"),
    ("yearly_07", "年次（7月）"), ("yearly_08", "年次（8月）"), ("yearly_09", "年次（9月）"),
    ("yearly_10", "年次（10月）"), ("yearly_11", "年次（11月）"), ("yearly_12", "年次（12月）"),
)
CHOICES_KIND_TARGET = (
    ("総資産", "総資産"),
    ("流動資産", "流動資産"),
)
CHOICES_CURRENCY = (
    ("JPY", "JPY"), ("USD", "USD"),
)
CHOICES_EXCHANGE_METHOD = (
    ("Wise", "Wise"), ("prestia", "prestia"), ("その他", "その他")
)


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

    def __str__(self) -> str:
        return self.name

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
