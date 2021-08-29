from django.test import TestCase
from django.db.utils import IntegrityError
from django.db import transaction
from django.contrib.auth import get_user_model
from asset.models import Stock, Order, Entry, ReasonWinLoss, Ipo, Dividend
from datetime import datetime, timezone


class OrderTest(TestCase):
    """
    !Test for Order
    """
    @classmethod
    def setUpTestData(cls):
        get_user_model().objects.all().delete()
        get_user_model().objects.create(
            username="takashi", password="test", is_superuser=True, is_staff=True)
        Stock.objects.create(code="0000", name="ABC Company")
        Stock.objects.create(code="0001", name="DEF Company")
        Stock.objects.create(code="ABC0000EFG", name="newe trust", is_trust=True)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        get_user_model().objects.all().delete()

    def setUp(self) -> None:
        self.user = get_user_model().objects.first()
        self.client.login()
        self.s0 = Stock.objects.get(code="0000")
        self.s1 = Stock.objects.get(code="0001")
        self.st = Stock.objects.get(is_trust=True)

    def tearDown(self) -> None:
        self.client.logout()
        return super().tearDown()

    def test_order(self):
        """
        Order, Normal
        """
        # prepare
        d1 = {
            "stock": self.s0,
            "datetime": datetime.now(timezone.utc),
            "is_buy": True,
            "val": 1000.1,
            "num": 100,
            "commission": 525,
        }
        o = Order.objects.create(**d1)
        # test
        test_scenarios = [
            (Order.objects.all().count(), 1, "count"),
            (str(o), f"B_{d1['datetime']}_{d1['stock']}", "__str__")
        ]
        for result, expectation, name in test_scenarios:
            with self.subTest(result=result, expectation=expectation, name=name):
                self.assertEqual(result, expectation)

    
class ReasonWinLossTest(TestCase):
    """
    !Test for ReasonWinLoss
    """
    pass


class EntryTest(TestCase):
    """
    !Test for Entry
    """
    pass


class IpoTest(TestCase):
    """
    !Test for Ipo
    """
    pass


class DividendTest(TestCase):
    """
    !Test for Dividend
    """
    pass