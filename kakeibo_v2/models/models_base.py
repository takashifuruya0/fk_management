from django.db import models
from django_currentuser.db.models import CurrentUserField


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
