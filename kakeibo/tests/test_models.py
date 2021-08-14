from django.test import TestCase
from django.contrib.auth import get_user_model
from kakeibo.models import Resource, Usage, Kakeibo, Event, SharedKakeibo, Budget, Exchange
from kakeibo.models import Target, Credit, SharedResource, SharedTransaction
from datetime import date
from dateutil.relativedelta import relativedelta
import math
# Create your tests here.


class KakeiboModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        get_user_model().objects.all().delete()
        get_user_model().objects.create(username="hoko", password="test", is_superuser=False, is_staff=False)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        get_user_model().objects.all().delete()

    def setUp(self) -> None:
        self.user = get_user_model().objects.first()
        self.r_wallet = Resource.objects.create(name="wallet", is_investment=False)
        self.r_usd = Resource.objects.create(name="wallet", is_investment=False, currency="USD")
        self.r_saving = Resource.objects.create(name="saving", is_investment=False)
        self.r_other = Resource.objects.create(name="other", is_investment=False)
        self.w_transfer = "振替"
        self.w_pay = "支出（現金）"
        self.w_income = "収入"
        self.u_shopping = Usage.objects.create(name="shopping", is_expense=True)
        self.u_transer = Usage.objects.create(name="transfer", is_expense=False)
        self.u_income = Usage.objects.create(name="income", is_expense=False)

    def test_kakeibo(self):
        # ========== JPY ==========
        self.assertEqual(0, Kakeibo.objects.all().count())
        d = {
            "date": date.today(),
            "fee": 100,
            "memo": "test",
            "way": self.w_pay,
            "usage": self.u_shopping,
            "resource_from": self.r_wallet,
        }
        k = Kakeibo.objects.create(**d)
        self.assertEqual(1, Kakeibo.objects.all().count())
        self.assertEqual(d['fee'], k.fee)
        self.assertEqual(d['memo'], k.memo)
        self.assertEqual(d['way'], k.way)
        self.assertEqual(d['usage'], k.usage)
        # ========== USD向け ==========
        d2 = {
            "date": date.today(),
            "fee": 100,
            "memo": "USD",
            "way": self.w_pay,
            "usage": self.u_shopping,
            "resource_from": self.r_usd,
            "currency": "USD",
        }
        # 最初は換算なし
        k2 = Kakeibo.objects.create(**d2)
        self.assertEqual(k2.fee_converted, None)
        # 換算実行後の確認
        k2.rate = 110.15
        k2.save()
        self.assertEqual(k2.fee_converted, math.floor(k2.fee*k2.rate))

    def test_event(self):
        self.assertEqual(0, Event.objects.all().count())
        d = {
            "date": date.today(),
            "sum_plan": 100000,
            "name": "Christmas",
            "memo": "2021 Happy Christmas"
        }
        event = Event.objects.create(**d)
        self.assertEqual(1, Event.objects.all().count())
        self.assertEqual(d['date'], event.date)
        self.assertEqual(d['sum_plan'], event.sum_plan)
        self.assertEqual(d['name'], event.name)
        self.assertEqual(d['memo'], event.memo)
        self.assertEqual(str(event), event.name)
        self.assertFalse(event.is_closed)
        # 紐付け
        d_k = {
            "date": date.today(),
            "fee": 100,
            "memo": "test",
            "way": self.w_pay,
            "usage": self.u_shopping,
            "event": event,
            "resource_from": self.r_wallet,
        }
        k1 = Kakeibo.objects.create(**d_k)
        k2 = Kakeibo.objects.create(**d_k)
        self.assertEqual(d_k['fee']*2, event.sum_actual)

    def test_resource(self):
        # 準備
        d_k1 = {
            "date": date.today(),
            "fee": 100,
            "memo": "test",
            "way": self.w_transfer,
            "usage": self.u_transer,
            "resource_from": self.r_wallet,
            "resource_to": self.r_saving,
        }
        d_k2 = {
            "date": date.today()-relativedelta(months=1),
            "fee": 200,
            "memo": "test",
            "way": self.w_transfer,
            "usage": self.u_transer,
            "resource_from": self.r_wallet,
            "resource_to": self.r_saving,
        }
        d_k3 = {
            "date": date.today(),
            "fee": 200,
            "memo": "test",
            "way": self.w_transfer,
            "usage": self.u_transer,
            "resource_from": None,
            "resource_to": self.r_wallet,
        }
        d_k4 = {
            "date": date.today(),
            "fee": 200,
            "memo": "test",
            "way": self.w_pay,
            "usage": self.u_shopping,
            "resource_from": self.r_other,
            "resource_to": None,
        }
        d_k5 = {
            "date": date.today()-relativedelta(months=1),
            "fee": 2000,
            "memo": "income",
            "way": self.w_income,
            "usage": self.u_income,
            "resource_from": None,
            "resource_to": self.r_wallet,
        }
        k1 = Kakeibo.objects.create(**d_k1)
        k2 = Kakeibo.objects.create(**d_k2)
        k3 = Kakeibo.objects.create(**d_k3)
        k4 = Kakeibo.objects.create(**d_k4)
        k5 = Kakeibo.objects.create(**d_k5)
        # total
        self.assertEqual(d_k1['fee']+d_k2['fee'], self.r_saving.total)
        # total (sum_to & sum_from)
        self.assertEqual(d_k3['fee']+d_k5['fee']-d_k1['fee']-d_k2['fee'], self.r_wallet.total)
        # diff_this_month (sum_to)
        self.assertEqual(d_k1['fee'], self.r_saving.diff_this_month)
        # diff_this_month (sum_to & sum_from)
        self.assertEqual(d_k3['fee']-d_k1['fee'], self.r_wallet.diff_this_month)
        # diff_this_month (sum_from)
        self.assertEqual(-d_k4['fee'], self.r_other.diff_this_month)

    def test_budget(self):
        self.assertEqual(0, Budget.objects.count())
        data = {
            "date": date.today(),
            "takashi": 100000,
            "hoko": 60000,
            "memo": "test",
        }
        b = Budget.objects.create(**data)
        self.assertEqual(1, Budget.objects.count())
        self.assertEqual(data['date'], b.date)
        self.assertEqual(data['takashi'], b.takashi)
        self.assertEqual(data['hoko'], b.hoko)
        self.assertEqual(data['memo'], b.memo)
        self.assertEqual(f"予算_{data['date']}", str(b))
        # total
        self.assertEqual(b.total, data['hoko']+data['takashi'])

    def test_deactivate(self):
        data = {
            "date": date.today(),
            "takashi": 100000,
            "hoko": 60000,
            "memo": "test",
        }
        b = Budget.objects.create(**data)
        b.delete()
        # delete時はis_active=False
        self.assertFalse(b.is_active)
        self.assertEqual(0, Budget.objects.all_active().count())

    def test_target(self):
        self.assertEqual(Target.objects.all().count(), 0)
        d = {
            "val": 1000000,
            "date": date.today(),
            "kind": "総資産",
            "memo": "test",
        }
        t = Target.objects.create(**d)
        self.assertEqual(Target.objects.all().count(), 1)
        self.assertEqual(f"Target_{t.date}", str(t))

    def test_credit(self):
        self.assertEqual(Credit.objects.all().count(), 0)
        d = {
            "fee": 1000,
            "date": date.today(),
            "debit_date": date.today(),
            "name": "UBER EATS",
            "memo": "test",
            "card": "SFC",
            "currency": "JPY",
        }
        c = Credit.objects.create(**d)
        self.assertEqual(f"({d['date']}) {d['name']}", str(c))
        self.assertEqual(Credit.objects.all().count(), 1)

    def test_shared_resource(self):
        """SharedResource
        - without SharedTransaction associated
        - with SharedTransaction associated
        """
        self.assertEqual(SharedResource.objects.all().count(), 0)
        dsr = {
            "val_goal": 10000,
            "date_open": date.today(),
            "name": "借金返済",
            "kind": "返済",
            "detail": "詳細",
        }
        sr = SharedResource.objects.create(**dsr)
        # test scenario
        test_scenarios = [
            (sr.val_goal, dsr['val_goal'], "check_val_goal"),
            (str(sr), f"【{sr.kind}】{sr.name}:{sr.val_goal:,}円", "check_str"),
            (sr.val_actual, 0, "before:check_val_actual"),
            (sr.progress_100, 0, "before:check_progress_100"),
            (SharedResource.objects.all().count(), 1, "before:check_num"),
        ]
        # SharedTransactionを紐付け
        dst = {
            "val": 1000,
            "date": date.today(),
            "paid_by": self.user,
            "shared_resource": sr,
            "memo": "test"
        }
        st1 = SharedTransaction.objects.create(**dst)
        st2 = SharedTransaction.objects.create(**dst)
        # add test scenarios
        test_scenarios += [
            (sr.val_actual, dst['val']*2, "after:check_val_actual"),
            (sr.progress_100, math.floor(100*dst['val']*2/sr.val_goal), "after:check_progress_100"),
            (SharedTransaction.objects.all().count(), 2, "after:check_num"),
        ]
        # execute tests
        for actual, expected, name in test_scenarios:
            with self.subTest(actual=actual, expected=expected, name=name):
                self.assertEqual(actual, expected)


    