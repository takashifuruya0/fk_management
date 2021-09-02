from django.test import TestCase
from django.db.utils import IntegrityError
from django.db import transaction
from django.contrib.auth import get_user_model
from asset.models import Stock, Order, Entry, ReasonWinLoss, Ipo, Dividend, StockValueData
from datetime import date, datetime, timezone


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

    def test_reason_win_loss(self):
        """
        ReasonWinLoss, Normal
        """
        # prepare
        d1 = {
            "is_win": True, "name": "Won", "memo": "Won because I'm the only appliciant."
        }
        r = ReasonWinLoss.objects.create(**d1)
        # test
        test_scenarios = [
            (ReasonWinLoss.objects.all().count(), 1, "count"),
            (str(r), d1['name'], "__str__")
        ]
        for result, expectation, name in test_scenarios:
            with self.subTest(result=result, expectation=expectation, name=name):
                self.assertEqual(result, expectation)


class EntryTest(TestCase):
    """
    !Test for Entry
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

    def test_entry(self):
        """
        Entry, Normal
        """
        # prepare
        e1 = Entry.objects.create(stock=self.s0)
        e2 =Entry.objects.create(stock=self.s1)
        d2 = {
            "stock": self.s1,
            "datetime": datetime.now(timezone.utc),
            "is_buy": True,
            "val": 1000.1,
            "num": 100,
            "commission": 525,
            "entry": e2
        }
        o2 = Order.objects.create(**d2)
        # test
        test_scenarios = [
            (Entry.objects.all().count(), 2, "count"),
            (str(e1), f"P{e1.pk:0>3}_{e1.stock}", "__str__ for Plan"),
            (str(e2), f"O{e2.pk:0>3}_{e2.stock}", "__str__ for Open")
        ]
        for result, expectation, name in test_scenarios:
            with self.subTest(result=result, expectation=expectation, name=name):
                self.assertEqual(result, expectation)


class IpoTest(TestCase):
    """
    !Test for Ipo
    """
    @classmethod
    def setUpTestData(cls):
        get_user_model().objects.all().delete()
        get_user_model().objects.create(
            username="takashi", password="test", is_superuser=True, is_staff=True)
        Stock.objects.create(code="0000", name="ABC Company", is_listed=False)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        get_user_model().objects.all().delete()

    def setUp(self) -> None:
        self.user = get_user_model().objects.first()
        self.client.login()
        self.s0 = Stock.objects.get(code="0000")

    def tearDown(self) -> None:
        self.client.logout()
        return super().tearDown()

    def test_ipo(self):
        """
        Ipo, Normal
        """
        # prepare
        d1 = {
            "stock": self.s0,
        }
        ipo = Ipo.objects.create(**d1)
        # test
        test_scenarios = [
            (Ipo.objects.all().count(), 1, "count"),
            (str(ipo), f"IPO_{d1['stock']}", "__str__"),
        ]
        for result, expectation, name in test_scenarios:
            with self.subTest(result=result, expectation=expectation, name=name):
                self.assertEqual(result, expectation)



class DividendTest(TestCase):
    """
    !Test for Dividend
    """
    @classmethod
    def setUpTestData(cls):
        get_user_model().objects.all().delete()
        get_user_model().objects.create(
            username="takashi", password="test", is_superuser=True, is_staff=True)
        Stock.objects.create(code="0000", name="ABC Company")

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        get_user_model().objects.all().delete()

    def setUp(self) -> None:
        self.user = get_user_model().objects.first()
        self.client.login()
        self.s0 = Stock.objects.get(code="0000")

    def tearDown(self) -> None:
        self.client.logout()
        return super().tearDown()

    def test_entry(self):
        """
        Entry, Normal
        """
        # prepare
        e1 = Entry.objects.create(stock=self.s0)
        d2 = {
            "entry": e1,
            "date": date.today(),
            "val_unit": 100,
            "unit": 100,
            "val": 10000,
            "tax": 2000,
        }
        div = Dividend.objects.create(**d2)
        # test
        test_scenarios = [
            (Dividend.objects.all().count(), 1, "count"),
            (str(div), f"Div_{d2['date']}_{d2['entry']}", "__str__"),
        ]
        for result, expectation, name in test_scenarios:
            with self.subTest(result=result, expectation=expectation, name=name):
                self.assertEqual(result, expectation)