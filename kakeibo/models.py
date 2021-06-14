from django.db import models
from django.conf import settings
from django_currentuser.middleware import get_current_authenticated_user
from django.contrib.auth import get_user_model
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
    is_closed = models.BooleanField("修了フラグ", default=False)
    date = models.DateField("日付")
    sum_plan = models.IntegerField("計画総額")

    def __str__(self) -> str:
        return self.name


class Credit(BaseModel):
    CHOICES_CARD = (
        (k, k) for k in ("SFC", "GoldPoint", "SFC（家族）")
    )
    fee = models.IntegerField("金額")
    date = models.DateField("日付")
    debit_date = models.DateField("引き落とし日")
    name = models.CharField("名前", max_length=255)
    memo = models.CharField("備考", max_length=255, null=True, blank=True)
    card = models.CharField("カード", max_length=255, choices=CHOICES_CARD)


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
    CHOICES_KIND = (
        ("monthly", "月次"),
        ("yearly_01", "年次（1月）"), ("yearly_02", "年次（2月）"), ("yearly_03", "年次（3月）"),
        ("yearly_04", "年次（4月）"), ("yearly_05", "年次（5月）"), ("yearly_06", "年次（6月）"),
        ("yearly_07", "年次（7月）"), ("yearly_08", "年次（8月）"), ("yearly_09", "年次（9月）"),
        ("yearly_10", "年次（10月）"), ("yearly_11", "年次（11月）"), ("yearly_12", "年次（12月）"),
    )
    fee = models.IntegerField("金額")
    memo = models.CharField("備考", max_length=255, null=True, blank=True)
    way = models.ForeignKey(Way, verbose_name="種別", on_delete=models.CASCADE)
    usage = models.ForeignKey(Usage, verbose_name="用途", on_delete=models.CASCADE)
    is_coping_to_shared = models.BooleanField("共通コピーフラグ")
    kind = models.CharField("種類", max_length=255, choices=CHOICES_KIND)


class Target(BaseModel):
    CHOICES_KIND = (
        (k, k) for k in ("総資産", )
    )
    val = models.IntegerField("値")
    date = models.DateField("日付")
    memo = models.CharField("備考", max_length=255, null=True, blank=True)
    kind = models.CharField("種類", max_length=255, choices=CHOICES_KIND)

    def __str__(self) -> str:
        return "Target_{}".format(self.date)


class Budget(BaseModel):
    date = models.DateField("日付")
    takashi = models.IntegerField("敬士予算")
    hoko = models.IntegerField("朋子予算")
    memo = models.CharField("備考", max_length=255, null=True, blank=True)

    def __str__(self):
        return "予算_{}".format(self.date)