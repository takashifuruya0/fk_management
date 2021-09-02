from django.test import TestCase
from django.db.utils import IntegrityError
from django.db import transaction
from django.contrib.auth import get_user_model
from asset.models import AssetTarget, AssetStatus, Stock, Order, Entry, StockValueData
from datetime import date, datetime, timezone


class AssetStatusTest(TestCase):
    """
    !Test for AssetStatus
    """
    @classmethod
    def setUpTestData(cls):
        get_user_model().objects.all().delete()
        get_user_model().objects.create(
            username="takashi", password="test", is_superuser=True, is_staff=True)
        Stock.objects.create(name="stock", code="0000")
        Stock.objects.create(name="trust", code="0000ABCDEF", is_trust=True)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        get_user_model().objects.all().delete()

    def setUp(self) -> None:
        self.user = get_user_model().objects.first()
        self.stock = Stock.objects.get(is_trust=False)
        self.trust = Stock.objects.get(is_trust=True)
        self.svd_stock = StockValueData.objects.create(
            stock=self.stock, val_high=110, val_low=80, val_open=90, val_close=100, turnover=20000)
        self.svd_trust = StockValueData.objects.create(
            stock=self.trust, val_high=1.1, val_low=1.1, val_open=1.1, val_close=1.1, turnover=20000)
        self.client.login()

    def tearDown(self) -> None:
        self.client.logout()
        return super().tearDown()

    def test_asset_status(self):
        """
        Asset Status, Normal
        """
        # prepare
        d1 = {
            "date": date.today(),
            "investment": 1000000,
            "buying_power": 1000000,
            "nisa_power": 1000000,
            "sum_stock": 100000,
            "sum_trust": 100000,
            "sum_other": 100000,
        }
        astatus = AssetStatus.objects.create(**d1)
        total = d1["buying_power"]+d1["sum_stock"]+d1["sum_trust"]+d1["sum_other"]
        gross_profit = total - d1["investment"]
        gross_profit_percent = round(gross_profit / d1["investment"] * 100, 2)
        # test
        test_scenarios = [
            (AssetStatus.objects.all().count(), 1, "count"),
            (str(astatus), f"AssetStatus_{d1['date']}", "__str__"),
            (astatus.total, total, "total"),
            (astatus.gross_profit, gross_profit, "gross_profit"),
            (astatus.gross_profit_percent, gross_profit_percent, "gross_profit_percent"),
        ]
        for result, expectation, name in test_scenarios:
            with self.subTest(result=result, expectation=expectation, name=name):
                self.assertEqual(result, expectation)

    def test_update_status(self):
        """
        Asset Status, update_status()
        """
        # prepare
        now = datetime.now(timezone.utc)
        e1 = Entry.objects.create(stock=self.stock)
        e2 = Entry.objects.create(stock=self.trust, is_nisa=True)
        o1 = Order.objects.create(datetime=now,
            stock=self.stock, entry=e1, is_buy=True, num=100, val=90, commission=500)
        o2 = Order.objects.create(datetime=now,
            stock=self.trust, entry=e2, is_buy=True, is_nisa=True, num=10000, val=1.05, commission=0)
        d1 = {
            "date": date.today(),
            "investment": 1000000,
            "buying_power": 1000000,
            "nisa_power": 1000000,
            "sum_stock": 100000,
            "sum_trust": 100000,
            "sum_other": 100000,
        }
        astatus = AssetStatus.objects.create(**d1)
        res = astatus.update_status()
        astatus_updated = AssetStatus.objects.get(pk=astatus.pk)
        # test
        test_scenarios = [
            (res, True, "result of update_status()"),
            (astatus_updated.sum_stock, o1.num*o1.stock.latest_val, "sum_stock"),
            (astatus_updated.sum_trust, o2.num*o2.stock.latest_val, "sum_trust"),
        ]
        for result, expectation, name in test_scenarios:
            with self.subTest(result=result, expectation=expectation, name=name):
                self.assertEqual(result, expectation)
        
    
class AssetTargetTest(TestCase):
    """
    !Test for AssetTarget
    """
    @classmethod
    def setUpTestData(cls):
        get_user_model().objects.all().delete()
        get_user_model().objects.create(
            username="takashi", password="test", is_superuser=True, is_staff=True)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        get_user_model().objects.all().delete()

    def setUp(self) -> None:
        self.user = get_user_model().objects.first()
        self.client.login()

    def tearDown(self) -> None:
        self.client.logout()
        return super().tearDown()
    
    def test_asset_target(self):
        """
        AssetTarget, Normal
        """
        d1 = {
            "date": date.today(),
            "val_investment": 1000000,
            "val_target": 1500000,
        }
        d2 = {
            "date": date(2020,1,1),
            "val_investment": 1000000,
            "val_target": 1500000,
        }
        d3 = {
            "date": date.today(),
            "investment": 1000000,
            "buying_power": 1000000,
            "nisa_power": 1000000,
            "sum_stock": 100000,
            "sum_trust": 100000,
            "sum_other": 100000,
        }
        d4 = {
            "date": date(2020,1,1),
            "investment": 900000,
            "buying_power": 100000,
            "nisa_power": 1000000,
            "sum_stock": 10000,
            "sum_trust": 10000,
            "sum_other": 10000,
        }
        atarget1 = AssetTarget.objects.create(**d1)
        atarget2 = AssetTarget.objects.create(**d2)
        astatus1 = AssetStatus.objects.create(**d3)
        astatus2 = AssetStatus.objects.create(**d4)
        # test
        test_scenarios = [
            (AssetTarget.objects.all().count(), 2, "count"),
            (str(atarget1), f"AssetTarget_{d1['date']}", "__str__"),
            (atarget1.is_achieved_target, atarget1.val_target<=astatus1.total, "is_achieved_target: True"),
            (atarget2.is_achieved_target, atarget2.val_target<=astatus2.total, "is_achieved_target: False"),
            (atarget1.is_achieved_investment, atarget1.val_investment<=astatus1.investment, "is_achieved_investment: True"),
            (atarget2.is_achieved_investment, atarget2.val_investment<=astatus2.investment, "is_achieved_investment: False"),
            (atarget1.actual_target, astatus1.total, "actual_target"),
            (atarget1.actual_investment, astatus1.investment, "actual_investment"),
            (atarget1.actual_date, astatus1.date,  "actual_date"),
            (atarget1.diff_target, astatus1.total-atarget1.val_target, "diff_target"),
            (atarget1.diff_investment, astatus1.investment-atarget1.val_investment, "diff_investment"),
        ]
        for result, expectation, name in test_scenarios:
            with self.subTest(result=result, expectation=expectation, name=name):
                self.assertEqual(result, expectation)
