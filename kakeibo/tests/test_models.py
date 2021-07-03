from django.test import TestCase
from kakeibo.models import Resource, Way, Usage, Kakeibo, Event, SharedKakeibo
from datetime import date
from dateutil.relativedelta import relativedelta
# Create your tests here.


class KakeiboModelTest(TestCase):

    def setUp(self) -> None:
        self.r_wallet = Resource.objects.create(name="wallet", is_investment=False)
        self.r_saving = Resource.objects.create(name="saving", is_investment=False)
        self.w_transfer = Way.objects.create(
            name="r1-->r2", resource_from=self.r_wallet, resource_to=self.r_saving, is_expense=False, is_transfer=True)
        self.w_pay = Way.objects.create(
            name="pay by cash", resource_from=self.r_wallet, is_expense=True, is_transfer=False)
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
            "event": event
        }
        k1 = Kakeibo.objects.create(**d_k)
        k2 = Kakeibo.objects.create(**d_k)
        self.assertEqual(d_k['fee']*2, event.sum_actual)

    def test_resouce(self):
        # 準備
        d_k1 = {
            "date": date.today(),
            "fee": 100,
            "memo": "test",
            "way": self.w_transfer,
            "usage": self.u_transer,
        }
        d_k2 = {
            "date": date.today()-relativedelta(months=1),
            "fee": 200,
            "memo": "test",
            "way": self.w_transfer,
            "usage": self.u_transer,
        }
        k1 = Kakeibo.objects.create(**d_k1)
        k2 = Kakeibo.objects.create(**d_k2)
        # total
        self.assertEqual(d_k1['fee']+d_k2['fee'], self.w_transfer.resource_to.total)
        # diff_this_month
        self.assertEqual(d_k1['fee'], self.w_transfer.resource_to.diff_this_month)
