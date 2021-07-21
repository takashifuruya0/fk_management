from django.test import TestCase
from kakeibo.models import Resource, Usage, Kakeibo, Event, SharedKakeibo, Budget, Exchange
from datetime import date
from dateutil.relativedelta import relativedelta
# Create your tests here.


class KakeiboModelTest(TestCase):

    def setUp(self) -> None:
        self.r_wallet = Resource.objects.create(name="wallet", is_investment=False)
        self.r_saving = Resource.objects.create(name="saving", is_investment=False)
        self.r_other = Resource.objects.create(name="other", is_investment=False)
        self.w_transfer = "振替"
        self.w_pay = "支出（現金）"
        self.u_shopping = Usage.objects.create(name="shopping", is_expense=True)
        self.u_transer = Usage.objects.create(name="transfer", is_expense=False)

    def test_kakeibo(self):
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
        k1 = Kakeibo.objects.create(**d_k1)
        k2 = Kakeibo.objects.create(**d_k2)
        k3 = Kakeibo.objects.create(**d_k3)
        k4 = Kakeibo.objects.create(**d_k4)
        # total
        self.assertEqual(d_k1['fee']+d_k2['fee'], self.r_saving.total)
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
