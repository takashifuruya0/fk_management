from django.db import models
from django.conf import settings
from datetime import date, datetime, timezone
from django.db.models import Sum, Avg
from django.contrib.auth import get_user_model
from django.conf import settings
from django_currentuser.db.models import CurrentUserField
import math
import logging
logger = logging.getLogger('django')


#! ===============================================
#! BaseModel
#! ===============================================
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


#! ===============================================
#! Models
#! ===============================================
class ReasonWinLoss(BaseModel):
    is_win = models.BooleanField("勝ちフラグ")
    name = models.CharField("名前", max_length=255)
    memo = models.CharField("メモ", max_length=255, blank=True, null=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "理由"
        verbose_name_plural = "理由"


class Stock(BaseModel):
    code = models.CharField("銘柄コード", max_length=10, unique=True)
    name = models.CharField("銘柄名", max_length=255)
    is_trust = models.BooleanField("投資信託フラグ", default=False)
    market = models.CharField("市場", max_length=255, null=True, blank=True)
    industry = models.CharField("産業", max_length=255, null=True, blank=True)
    feature = models.CharField("特色", max_length=100, blank=True, null=True)
    consolidated_business = models.CharField("連結事業", max_length=100, blank=True, null=True)
    settlement_date = models.CharField("決算月", max_length=10, blank=True, null=True)
    unit = models.CharField("単元株数", max_length=10, blank=True, null=True)
    is_listed = models.BooleanField("上場済みフラグ", default=True)

    def __str__(self) -> str:
        return f"({self.code}) {self.name}"

    @property
    def latest_val(self):
        """直近の株価"""
        svd = StockValueData.objects.filter(stock=self)
        return svd.latest('date').val_close if svd.exists() else None

    @property
    def latest_val_date(self):
        """直近の株価の日付"""
        svd = StockValueData.objects.filter(stock=self)
        return svd.latest('date').date if svd.exists() else None
    
    class Meta:
        verbose_name = "銘柄"
        verbose_name_plural = "銘柄"


class StockValueData(BaseModel):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, verbose_name="銘柄")
    date = models.DateField("日付", default=date.today)
    val_high = models.FloatField("高値")
    val_low = models.FloatField("低値")
    val_open = models.FloatField("始値")
    val_close = models.FloatField("終値")
    turnover = models.FloatField("出来高")

    def __str__(self):
        return "{}_{}".format(self.date, self.stock)

    class Meta:
        verbose_name = "銘柄日次情報"
        verbose_name_plural = "銘柄日次情報"


class Entry(BaseModel):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, verbose_name="銘柄")
    entry_type = models.CharField("種別", choices=settings.CHOICES_ENTRY_TYPE, max_length=255, default="中期")
    status = models.CharField("ステータス", choices=settings.CHOICES_ENTRY_STATUS, max_length=255, default="01.BeforeEntry")
    memo = models.TextField("メモ", blank=True, null=True)
    is_closed = models.BooleanField("終了フラグ", default=False, help_text="終了したEntryかどうか")
    is_nisa = models.BooleanField("NISAフラグ", default=False, help_text="NISA口座かどうか")
    # plan
    is_plan = models.BooleanField("計画フラグ", default=False, help_text="EntryPlanかどうか")
    border_loss_cut = models.FloatField("損切株価", blank=True, null=True)
    border_profit_determination = models.FloatField("利確株価", blank=True, null=True)
    num_plan = models.IntegerField("予定口数", blank=True, null=True)
    val_plan = models.FloatField("予定Entry株価", blank=True, null=True)
    # close
    reason_win_loss = models.ForeignKey(ReasonWinLoss, on_delete=models.CASCADE, blank=True, null=True, verbose_name="理由")

    def __str__(self):
        if self.is_plan:
            head = 'I' if self.is_closed else 'P'
        else:
            head = 'C' if self.is_closed else 'O'
        return "{}{:0>3}_{}".format(head, self.pk, self.stock)

    def get_val_order(self, is_buy):
        """取引株価"""
        orders = self.order_set.filter(is_buy=is_buy)
        val = 0
        if orders.exists():
            for o in orders:
                val += (o.val * o.num)
            val = val/self.num_order(is_buy)
        return val

    def get_num_order(self, is_buy):
        """取引口数"""
        orders = self.order_set.filter(is_buy=is_buy)
        num = 0
        if orders.exists():
            num = orders.aggregate(num=Sum('num'))['num']
        return num

    @property
    def num_buy(self):
        """買付口数"""
        return self.get_num_order(is_buy=True)

    @property
    def num_sell(self):
        """売付口数"""
        return self.get_num_order(is_buy=False)

    @property
    def val_buy(self):
        """買付株価"""
        return self.get_val_order(is_buy=True)

    @property
    def val_sell(self):
        """売付株価"""
        return self.get_val_order(is_buy=False)

    @property
    def total_buy(self):
        """買付合計"""
        return self.val_buy * self.num_buy

    @property
    def total_sell(self):
        """売付合計"""
        return self.val_sell * self.num_sell if self.num_sell > 0 else None

    @property
    def total_plan(self):
        """Plan合計"""
        return self.val_plan * self.num_plan if self.val_plan else None

    @property
    def total_now(self):
        """現在合計"""
        return self.remaining * self.stock.latest_val

    @property
    def remaining(self):
        """残口数"""
        return self.num_buy - self.num_sell

    @property
    def profit(self):
        """利益（配当含む）"""
        profit = 0
        for o in self.order_set.all():
            if o.is_buy:
                profit -= (o.num * o.val + o.commission)
            else:
                profit += (o.num * o.val - o.commission)
        if not self.is_closed:
            profit += self.stock.latest_val * self.remaining
        # 配当
        if self.dividend_set.exists():
            profit += self.dividend_set.all().aggregate(sum=Sum('val'))['sum']
        return profit

    @property
    def profit_after_tax(self):
        """税引利益"""
        profit = self.profit
        return round(profit * 0.8) if profit > 0 and not self.is_nisa else profit

    @property
    def profit_pct(self):
        """利益率"""
        return self.profit / self.val_buy / self.num_buy if self.order_set.exists() else 0

    @property
    def profit_profit_determination(self):
        """利確後の利益額"""
        if self.border_profit_determination and self.is_plan:
            return (self.border_profit_determination - self.stock.latest_val) * self.num_plan
        elif self.border_profit_determination and not self.is_plan:
            return (self.border_profit_determination - self.val_buy) * self.num_buy
        else:
            return None

    @property
    def profit_loss_cut(self):
        """損切後の損失額"""
        if self.border_loss_cut:
            num = self.num_plan if self.is_plan else self.num_buy
            val = self.stock.latest_val if self.is_plan else self.val_buy
            return (self.border_loss_cut - val) * num
        else:
            return None

    @property
    def date_open(self):
        """EntryをOpenした日付"""
        os = self.order_set.filter(is_buy=True)
        return min([o.datetime for o in os]) if os.exists() else None

    @property
    def date_close(self):
        """EntryをCloseした日付"""
        os = self.order_set.filter(is_buy=False)
        return max([o.datetime for o in os]) if os.exists() else None

    @property
    def border_loss_cut_percent(self):
        """損切り損失率"""
        current_val = self.stock.latest_val
        if self.border_loss_cut and current_val:
            val = current_val if self.is_plan else self.val_buy
            return round(self.border_loss_cut / val * 100 - 100, 2)
        else:
            return None

    @property
    def border_profit_determination_percent(self):
        """利確利益率"""
        current_val = self.stock.latest_val
        if self.border_profit_determination and current_val:
            val = current_val if self.is_plan else self.val_buy
            return round(self.border_profit_determination / val * 100 - 100, 2)
        else:
            return None

    @property
    def holding_period(self):
        """保有期間。Planの場合はNoneを返す"""
        if self.is_plan:
            return None
        else:
            days = ((self.date_close if self.is_closed else datetime.now(timezone.utc)) - self.date_open).days
            return days + 1

    @property
    def profit_per_days(self):
        """利益/保有期間"""
        return self.profit / self.holding_period

    def save(self, *args, **kwargs):
        if self.order_set.exists():
            # check closed if remaining = 0
            self.is_plan = False
            self.is_closed = True if self.remaining == 0 else False
            # same stocks should be linked
            for o in self.order_set.all():
                if not o.stock == self.stock:
                    raise Exception('Different stocks are linked')
            # remaining should be over 0
            if self.remaining < 0:
                raise Exception('remaining should be more than equal 0')
            # date_open should be earlier than date_close
            if self.is_closed and self.date_open > self.date_close:
                raise Exception('date_open should be earlier than date_close')
        else:
            self.is_plan = True
            # self.is_closed = False
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "エントリー"
        verbose_name_plural = "エントリー"


class Order(BaseModel):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, verbose_name="銘柄")
    datetime = models.DateTimeField("日時")
    is_nisa = models.BooleanField("NISAフラグ", default=False)
    is_buy = models.BooleanField("買注文フラグ")
    num = models.IntegerField("口数")
    val = models.FloatField("株価",  help_text="投資信託は一口当たり単価")
    commission = models.IntegerField("手数料")
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, null=True, blank=True, verbose_name="エントリー")
    chart = models.ImageField("チャート", upload_to='images/', null=True, blank=True)

    def __str__(self):
        bs = "B" if self.is_buy else "S"
        return "{}_{}_{}".format(bs, self.datetime, self.stock)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.entry:
            try:
                self.entry.save()
                logger.info("{} is updated with updates of {}".format(self.entry, self))
            except Exception as e:
                # unlink Entry and save both order and entry
                logger.error(e)
                entry = self.entry
                self.entry = None
                super().save(*args, **kwargs)
                entry.save()

    class Meta:
        verbose_name = "売買注文"
        verbose_name_plural = "売買注文"


class AssetStatus(BaseModel):
    date = models.DateField("日付", unique=True)
    buying_power = models.IntegerField("買付余力")
    investment = models.IntegerField("投資元本")
    nisa_power = models.IntegerField("NISA余力")
    sum_stock = models.IntegerField("株合計")
    sum_trust = models.IntegerField("投資信託合計")
    sum_other = models.IntegerField("その他合計")

    def __str__(self):
        return f"AssetStatus_{self.date}"

    @property
    def total(self):
        """合計の算出"""
        return self.sum_other + self.sum_stock + self.sum_trust + self.buying_power

    @property
    def gross_profit(self):
        """粗利の算出"""
        return self.total - self.investment

    @property
    def gross_profit_percent(self):
        """粗利(%)の算出"""
        return round((self.total - self.investment)/self.investment * 100, 2)

    def update_status(self):
        """Entryに従って、sum_stock, sum_trustの更新"""
        es = Entry.objects.filter(is_closed=False, is_plan=False)
        try:
            self.sum_stock = 0
            self.sum_trust = 0
            for e in es:
                val = e.stock.latest_val
                num = e.remaining
                total = val * num
                if e.stock.is_trust:
                    self.sum_trust += total
                else:
                    self.sum_stock += total
            self.save()
            logger.info("{}.update_status() was completed successfully".format(self))
            return True
        except Exception as err:
            logger.error(err)
            return False

    class Meta:
        verbose_name = "投資状況"
        verbose_name_plural = "投資状況"


# class StockFinancialData(BaseModel):
#     stock = models.ForeignKey(Stock, on_delete=models.CASCADE, verbose_name="銘柄")
#     date = models.DateField("日付")
#     """ stock_settlement_info """
#     interest_bearing_debt = models.FloatField(blank=True, null=True, verbose_name="有利子負債")
#     roa = models.FloatField(blank=True, null=True, verbose_name="ROA")
#     roe = models.FloatField(blank=True, null=True, verbose_name="ROE")
#     sales = models.FloatField(blank=True, null=True, verbose_name="売上高")
#     assets = models.FloatField(blank=True, null=True, verbose_name="総資産")
#     eps = models.FloatField(blank=True, null=True, verbose_name="EPS")
#     net_income = models.FloatField(blank=True, null=True, verbose_name="当期利益")
#     bps = models.FloatField(blank=True, null=True, verbose_name="BPS")
#     roa_2 = models.FloatField(blank=True, null=True, verbose_name="総資産経常利益率")
#     operating_income = models.FloatField(blank=True, null=True, verbose_name="営業利益")
#     equity_ratio = models.FloatField(blank=True, null=True, verbose_name="自己資本比率")
#     capital = models.FloatField(blank=True, null=True, verbose_name="資本金")
#     recurring_profit = models.FloatField(blank=True, null=True, verbose_name="経常利益")
#     equity = models.FloatField(blank=True, null=True, verbose_name="自己資本")
#     """ stock_finance_info() """
#     pbr_f = models.FloatField(blank=True, null=True, verbose_name="PBR（実績）")
#     eps_f = models.FloatField(blank=True, null=True, verbose_name="EPS（会社予想）")
#     market_value = models.FloatField(blank=True, null=True, verbose_name="時価総額")
#     per_f = models.FloatField(blank=True, null=True, verbose_name="PER（会社予想）")
#     dividend_yield = models.FloatField(blank=True, null=True, verbose_name="配当利回り（会社予想）")
#     bps_f = models.FloatField(blank=True, null=True, verbose_name="BPS実績")

#     def __str__(self):
#         return "{}_{}".format(self.date, self.stock)
    
#     class Meta:
#         verbose_name = "銘柄決算情報"
#         verbose_name_plural = "銘柄決算情報"


class StockAnalysisData(BaseModel):
    date = models.DateField(verbose_name="日付")
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, verbose_name="銘柄")
    # prepare
    val_close_dy = models.FloatField(verbose_name="終値前日比")
    val_close_dy_pct = models.FloatField(verbose_name="終値前日比率")
    turnover_dy = models.FloatField(verbose_name="出来高前日比")
    turnover_dy_pct = models.FloatField(verbose_name="出来高前日比率")
    val_line = models.FloatField(verbose_name="ローソク長")
    val_line_pct = models.FloatField(verbose_name="ローソク長率")
    is_positive = models.BooleanField(verbose_name="陽線")
    lower_mustache = models.FloatField(verbose_name="下ヒゲ")
    upper_mustache = models.FloatField(verbose_name="上ヒゲ")
    ma05 = models.FloatField(verbose_name="移動平均（5日）")
    ma25 = models.FloatField(verbose_name="移動平均（25日）")
    ma75 = models.FloatField(verbose_name="移動平均（75日）")
    ma05_diff = models.FloatField(verbose_name="移動平均乖離（5日）", help_text="終値ー5日移動平均")
    ma25_diff = models.FloatField(verbose_name="移動平均乖離（25日）", help_text="終値ー25日移動平均")
    ma75_diff = models.FloatField(verbose_name="移動平均乖離（75日）", help_text="終値ー75日移動平均")
    ma05_diff_pct = models.FloatField(verbose_name="移動平均乖離率（5日）")
    ma25_diff_pct = models.FloatField(verbose_name="移動平均乖離率（25日）")
    ma75_diff_pct = models.FloatField(verbose_name="移動平均乖離率（75日）")
    sigma25 = models.FloatField(verbose_name="標準偏差（25日）")
    ma25_p2sigma = models.FloatField(verbose_name="ボリンジャーバンド+2σ（25日）")
    ma25_m2sigma = models.FloatField(verbose_name="ボリンジャーバンド-2σ（25日）")
    is_upper05 = models.BooleanField(verbose_name="上昇傾向（5日）", help_text="前日移動平均値より上（5日）")
    is_upper25 = models.BooleanField(verbose_name="上昇傾向（25日）", help_text="前日移動平均値より上（25日）")
    is_upper75 = models.BooleanField(verbose_name="上昇傾向（75日）", help_text="前日移動平均値より上（75日）")
    # check
    is_takuri = models.BooleanField(
        verbose_name="たくり線", help_text="長い下ヒゲ陰線", default=False
    )
    is_tsutsumi = models.BooleanField(
        verbose_name="包線", help_text="前日ローソクを包み込む、大きいローソク", default=False
    )
    is_harami = models.BooleanField(
        verbose_name="はらみ線", help_text="前日ローソクに包まれる、小さいローソク", default=False
    )
    is_age_sanpo = models.BooleanField(
        verbose_name="上げ三法", help_text="大陽線後→3本のローソクが収まる→最初の陽線終値をブレイク", default=False
    )
    is_sage_sanpo = models.BooleanField(
        verbose_name="下げ三法", help_text="大陰線後→3本のローソクが収まる→最初の陰線終値を割り込み", default=False
    )
    is_sanku_tatakikomi = models.BooleanField(
        verbose_name="三空叩き込み", help_text="3日連続の窓開き下落", default=False
    )
    is_sante_daiinsen = models.BooleanField(
        verbose_name="三手大陰線", help_text="3日連続の大陰線", default=False
    )
    svd = models.ForeignKey(StockValueData, verbose_name="SVD", null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return "SAD_{}_{}".format(self.date, self.stock)

    @property
    def is_having_trend(self):
        if (self.val_close_dy_pct >= 0.05 and self.turnover_dy_pct >= 1) \
                or (self.val_close_dy_pct <= 0.05 and self.turnover_dy_pct >= 1) \
                or self.is_takuri \
                or self.is_harami \
                or self.is_tsutsumi \
                or self.is_sanku_tatakikomi \
                or self.is_age_sanpo \
                or self.is_sage_sanpo \
                or self.is_sante_daiinsen:
            return True
        else:
            return False

    class Meta:
        verbose_name = "銘柄分析情報"
        verbose_name_plural = "銘柄分析情報"


class AssetTarget(BaseModel):
    date = models.DateField(verbose_name="日付", unique=True)
    val_investment = models.IntegerField(verbose_name="予定投資元本")
    val_target = models.IntegerField(verbose_name="投資目標")
    memo = models.TextField(blank=True, null=True, verbose_name="メモ")

    def __str__(self):
        return f"AssetTarget_{self.date}"

    @property
    def is_achieved_target(self) -> bool:
        """投資目標を達成しているか"""
        astatus = AssetStatus.objects.filter(date__lte=self.date).latest('date')
        return astatus.total >= self.val_target if date.today() >= self.date else None

    @property
    def is_achieved_investment(self) -> bool:
        """投資元本目標を達成しているか"""
        astatus = AssetStatus.objects.filter(date__lte=self.date).latest('date')
        return astatus.investment >= self.val_investment if date.today() >= self.date else None

    @property
    def actual_target(self) -> int:
        """対応する投資実績"""
        astatus = AssetStatus.objects.filter(date__lte=self.date).latest('date')
        return astatus.total if date.today() >= self.date else None

    @property
    def actual_investment(self) -> bool:
        """対応する投資元本実績"""
        astatus = AssetStatus.objects.filter(date__lte=self.date).latest('date')
        return astatus.investment

    @property
    def actual_date(self) -> date:
        """対応する投資実績日付"""
        astatus = AssetStatus.objects.filter(date__lte=self.date).latest('date')
        return astatus.date if date.today() >= self.date else None

    @property
    def diff_target(self) -> int:
        """投資実績 - 投資目標"""
        astatus = AssetStatus.objects.filter(date__lte=self.date).latest('date')
        return astatus.total - self.val_target if date.today() >= self.date else None

    @property
    def diff_investment(self)-> int:
        """投資元本実績 - 投資元本目標"""
        astatus = AssetStatus.objects.filter(date__lte=self.date).latest('date')
        return astatus.investment - self.val_investment if date.today() >= self.date else None

    class Meta:
        verbose_name = "投資目標"
        verbose_name_plural = "投資目標"


class Ipo(BaseModel):
    # ===================================
    # fields
    # ===================================
    # 事前情報
    stock = models.ForeignKey(Stock, verbose_name="銘柄", on_delete=models.CASCADE)
    datetime_open = models.DateTimeField("ブックビル開始日時", blank=True, null=True)
    datetime_close = models.DateTimeField("ブックビル終了日時", blank=True, null=True)
    status = models.CharField('ステータス', max_length=255, choices=settings.CHOICES_STATUS, default="0.起票")
    val_list = models.FloatField("発行価格", blank=True, null=True)
    date_list = models.DateField("上場日", blank=True, null=True)
    datetime_select = models.DateTimeField("抽選開始日時", blank=True, null=True)
    # 申請情報
    is_applied = models.BooleanField("申込済", default=False)
    date_applied = models.DateField("申込日", blank=True, null=True)
    num_applied = models.IntegerField("申込数", blank=True, null=True)
    point = models.IntegerField("使用ポイント数", default=None, blank=True, null=True)
    result_select = models.CharField("抽選結果", max_length=255, default="抽選待ち", blank=True, null=True)
    # 購入情報
    datetime_purchase_open = models.DateTimeField("購入意思表示開始日時", blank=True, null=True)
    datetime_purchase_close = models.DateTimeField("購入意思表示終了日時", blank=True, null=True)
    num_select = models.IntegerField("当選数", blank=True, null=True)
    # 評判/評価 (https://96ut.com/ipo/yoso.php)
    rank = models.CharField("評価", max_length=1, choices=settings.CHOICES_RANK, blank=True, null=True)
    val_predicted = models.FloatField("予想初値", blank=True, null=True)
    num_comment = models.PositiveIntegerField("コメント数", blank=True, null=True)
    managing_underwriter = models.CharField("主幹証券会社", max_length=255, blank=True, null=True)
    url = models.URLField("評価詳細URL", blank=True, null=True)
    # 上場後
    val_initial = models.FloatField("上場後初値", blank=True, null=True)
    entry = models.ForeignKey(Entry, verbose_name="Entry", on_delete=models.CASCADE, blank=True, null=True)
    # その他
    memo = models.TextField("メモ", blank=True, null=True)

    # ===================================
    # methods and Meta
    # ===================================
    def __str__(self):
        return "IPO_{}".format(self.stock)

    @property
    def profit_expected(self) -> float:
        """見込初値売り利益"""
        if self.val_predicted and self.val_list and self.num_applied:
            return (self.val_predicted - self.val_list) * self.num_applied
        else:
            return None

    @property
    def profit_actual(self) -> float:
        """初値売り利益"""
        if self.val_initial and self.val_list and self.num_applied:
            return (self.val_initial - self.val_list) * self.num_applied
        else:
            return None

    @property
    def profit_pct_expected(self) -> float:
        """見込み初値売り利益率（%）"""
        if self.val_predicted and self.val_list:
            return (self.val_predicted - self.val_list) / self.val_list * 100
        else:
            return None

    @property
    def profit_pct_actual(self) -> float:
        """初値売り利益率（%）"""
        if self.val_initial and self.val_list:
            return (self.val_initial - self.val_list) / self.val_list * 100
        else:
            return None

    @property
    def total_applied(self) -> float:
        """申込み合計金額"""
        if self.num_applied and self.val_list:
            return self.num_applied * self.val_list
        else:
            return None

    class Meta:
        verbose_name = "IPO"
        verbose_name_plural = "IPO"


class Dividend(BaseModel):
    entry = models.ForeignKey(Entry, verbose_name="Entry", on_delete=models.CASCADE)
    date = models.DateField("配当日")
    val_unit = models.IntegerField("配当単価")
    unit = models.IntegerField("配当単位数")
    val = models.IntegerField("配当総額（税引前）")
    tax = models.IntegerField("税額")

    class Meta:
        verbose_name = "配当"
        verbose_name_plural = "配当"

    def __str__(self) -> str:
        return f"Div_{self.date}_{self.entry}"


