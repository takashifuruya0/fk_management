from django.db import models
from django.conf import settings
from datetime import date
from django.db.models import Sum, Avg
from django_currentuser.middleware import get_current_authenticated_user
from django.contrib.auth import get_user_model
from django.conf import settings
from django_currentuser.db.models import CurrentUserField


# Create your models here.
class BaseModel(models.Model):
    objects = None
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
        sum_from = Kakeibo.objects.select_related('way').filter(
            way__resource_from=self, is_active=True).aggregate(sum=Sum('fee'))['sum']
        sum_to = Kakeibo.objects.select_related('way').filter(
            way__resource_to=self, is_active=True).aggregate(sum=Sum('fee'))['sum']
        if sum_from and sum_to:
            val = sum_to - sum_from
        else:
            val = sum_to if sum_to else 0
        return val

    @property
    def diff_this_month(self):
        today = date.today()
        sum_from = Kakeibo.objects.select_related('way') \
            .filter(way__resource_from=self, date__month=today.month, date__year=today.year, is_active=True) \
            .aggregate(sum=Sum('fee'))['sum']
        sum_to = Kakeibo.objects.select_related('way') \
            .filter(way__resource_to=self, date__month=today.month, date__year=today.year, is_active=True) \
            .aggregate(sum=Sum('fee'))['sum']
        if sum_from and sum_to:
            val = sum_to - sum_from
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


class Way(BaseModel):
    name = models.CharField("名前", max_length=255)
    memo = models.CharField("備考", max_length=255, null=True, blank=True)
    resource_from = models.ForeignKey(
        Resource, related_name="resource_from", null=True, blank=True, verbose_name="From", on_delete=models.CASCADE
    )
    resource_to = models.ForeignKey(
        Resource, related_name="resource_to", null=True, blank=True, verbose_name="To", on_delete=models.CASCADE
    )
    is_expense = models.BooleanField("支出フラグ", default=True)
    is_transfer = models.BooleanField("振替フラグ", default=True)

    def __str__(self) -> str:
        # return self.name
        rf = "" if self.resource_from is None else self.resource_from
        rt = "" if self.resource_to is None else self.resource_to
        return "{} ({}→{})".format(self.name, rf, rt)


class Event(BaseModel):
    name = models.CharField("名前", max_length=255)
    memo = models.CharField("備考", max_length=255, null=True, blank=True)
    is_closed = models.BooleanField("終了フラグ", default=False)
    date = models.DateField("日付")
    sum_plan = models.IntegerField("計画総額")

    def __str__(self) -> str:
        return self.name

    @property
    def sum_actual(self):
        return self.kakeibo_set.filter(is_active=True).aggregate(sum=Sum('fee'))['sum']


class Credit(BaseModel):
    # CHOICES_CARD = (
    #     (k, k) for k in ("SFC", "GoldPoint", "SFC（家族）")
    # )
    fee = models.IntegerField("金額")
    date = models.DateField("日付")
    debit_date = models.DateField("引き落とし日")
    name = models.CharField("名前", max_length=255)
    memo = models.CharField("備考", max_length=255, null=True, blank=True)
    card = models.CharField("カード", max_length=255, choices=settings.CHOICES_CARD)


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
    way = models.ForeignKey(Way, verbose_name="種別", on_delete=models.CASCADE)
    usage = models.ForeignKey(Usage, verbose_name="用途", on_delete=models.CASCADE)
    shared = models.ForeignKey(SharedKakeibo, verbose_name="共通家計簿", on_delete=models.CASCADE, null=True, blank=True)
    credit = models.ForeignKey(Credit, verbose_name="クレジット", on_delete=models.CASCADE, null=True, blank=True)
    event = models.ForeignKey(Event, verbose_name="イベント", on_delete=models.CASCADE, null=True, blank=True)


class CronKakeibo(BaseModel):
    fee = models.IntegerField("金額")
    memo = models.CharField("備考", max_length=255, null=True, blank=True)
    way = models.ForeignKey(Way, verbose_name="種別", on_delete=models.CASCADE)
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