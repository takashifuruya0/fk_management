from django.test import TestCase
from django.db.utils import IntegrityError
from django.db import transaction
from django.contrib.auth import get_user_model
from asset.models import Stock, Order, Entry, ReasonWinLoss, Ipo, Dividend, StockValueData
from datetime import date, datetime, timezone, tzinfo


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

    def test_entry_exception_different_stocks(self):
        """
        Entry, Exception
        Orders for different stocks are not linked with the same entry
        """
        # prepare
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
        d1 = {
            "stock": self.s0, 
            "datetime": datetime.now(timezone.utc),
            "is_buy": True,
            "val": 1000,
            "num": 100,
            "commission": 525,
            "entry": e2
        }
        # with self.assertRaises(Exception, msg='Different stocks are linked'):
        o1 = Order(**d1)
        o1.save()
        self.assertEqual(o1.entry, None)

    def test_entry_exception_order_datetime(self):
        """
        Entry, Exception
        Buy Orders should be earlier than Sell Orders
        """
        # prepare
        e2 =Entry.objects.create(stock=self.s1)
        d2 = {
            "stock": self.s1,
            "datetime": datetime(2021, 3, 13, 11, 0, tzinfo=timezone.utc),
            "is_buy": True,
            "val": 1000.1,
            "num": 100,
            "commission": 525,
            "entry": e2
        }
        o2 = Order.objects.create(**d2)
        d1 = {
            "stock": self.s1,
            "datetime": datetime(2021, 3, 12, 10, 0, tzinfo=timezone.utc),
            "is_buy": False,
            "val": 1200,
            "num": 100,
            "commission": 525,
            "entry": e2
        }
        # with self.assertRaises(Exception, msg='Different stocks are linked'):
        o1 = Order(**d1)
        o1.save()
        self.assertEqual(o1.entry, None)
        self.assertEqual(e2.remaining, 100)

    def test_entry_exception_remaining(self):
        """
        Entry, Exception
        Remaining should be greater than or equal to 0
        """
        # prepare
        e2 =Entry.objects.create(stock=self.s1)
        d2 = {
            "stock": self.s1,
            "datetime": datetime(2021, 3, 13, 11, 0, tzinfo=timezone.utc),
            "is_buy": True,
            "val": 1000.1,
            "num": 100,
            "commission": 525,
            "entry": e2
        }
        o2 = Order.objects.create(**d2)
        d1 = {
            "stock": self.s1,
            "datetime": datetime(2021, 3, 14, 10, 0, tzinfo=timezone.utc),
            "is_buy": False,
            "val": 1200,
            "num": 120,
            "commission": 525,
            "entry": e2
        }
        # with self.assertRaises(Exception, msg='Different stocks are linked'):
        o1 = Order(**d1)
        o1.save()
        self.assertEqual(o1.entry, None)
        self.assertEqual(e2.remaining, 100)


class EntryMethodTest(TestCase):
    """
    ! Tests for methods of Entry 
    """
    @classmethod
    def setUpTestData(cls):
        get_user_model().objects.all().delete()
        get_user_model().objects.create(
            username="takashi", password="test", is_superuser=True, is_staff=True)
        # Stock
        s0= Stock.objects.create(code="0000", name="ABC Company")
        s1= Stock.objects.create(code="0001", name="DEF Company")
        st= Stock.objects.create(code="ABC0000EFG", name="newe trust", is_trust=True)
        # StockValueData
        svd0 = StockValueData.objects.create(
            stock=s0, val_high=2020, val_low=2020, val_open=2020, val_close=2020, 
            turnover=10000, date=date(2021,4,5))
        svd1 = StockValueData.objects.create(
            stock=s1, val_high=1980, val_low=1980, val_open=1980, val_close=1980, 
            turnover=10000, date=date(2021,4,5))
        svdt = StockValueData.objects.create(
            stock=st, val_high=2.2020, val_low=2.2020, val_open=2.2020, val_close=2.2020, 
            turnover=10000, date=date(2021,4,5))
        # Open Entry of Stock
        e0 = Entry.objects.create(stock=s0, memo="without dividend", 
            border_loss_cut=1900, border_profit_determination=2100)
        o0b = Order.objects.create(
            datetime=datetime(2021,4,1,9, 0, tzinfo=timezone.utc), 
            val=2000, num=100, commission=525, is_nisa=False, is_buy=True,
            stock=s0, entry=e0)
        # Open Entry of Stock with dividend
        e0d = Entry.objects.create(stock=s0, memo="with dividend")
        o0db = Order.objects.create(
            datetime=datetime(2021,4,2,9, 0, tzinfo=timezone.utc), 
            val=2000, num=1000, commission=525, is_nisa=False, is_buy=True,
            stock=s0, entry=e0d)
        div = Dividend.objects.create(
            entry=e0d, val_unit=10, unit=1000, val=10000, tax=2000, date=date(2021,4,8))
        # Open Entry of Trust
        et = Entry.objects.create(stock=st)
        otb = Order.objects.create(
            datetime=datetime(2021,4,1,9, 0, tzinfo=timezone.utc), 
            val=2.1010, num=10000, commission=0, is_nisa=True, is_buy=True,
            stock=st, entry=et)
        # Open Entry with multiple orders
        e1 = Entry.objects.create(stock=s1)
        o1b1 = Order.objects.create(
            datetime=datetime(2021,4,1,9, 0, tzinfo=timezone.utc), 
            val=2000, num=100, commission=525, is_nisa=False, is_buy=True,
            stock=s1, entry=e1)
        o1b2 = Order.objects.create(
            datetime=datetime(2021,4,3,9, 0, tzinfo=timezone.utc), 
            val=2100, num=200, commission=525, is_nisa=False, is_buy=True,
            stock=s1, entry=e1)
        # Closed Entry
        e11 = Entry.objects.create(stock=s1)
        o11b = Order.objects.create(
            datetime=datetime(2021,4,1,9, 0, tzinfo=timezone.utc), 
            val=2000, num=100, commission=525, is_nisa=False, is_buy=True,
            stock=s1, entry=e11)
        o11s = Order.objects.create(
            datetime=datetime(2021,4,3,9, 0, tzinfo=timezone.utc), 
            val=2100, num=100, commission=525, is_nisa=False, is_buy=False,
            stock=s1, entry=e11)
        

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        get_user_model().objects.all().delete()

    def setUp(self) -> None:
        self.user = get_user_model().objects.first()
        self.client.login()
        # Stock
        self.s0 = Stock.objects.get(code="0000")
        self.s1 = Stock.objects.get(code="0001")
        self.st = Stock.objects.get(is_trust=True)
        # StockValueData
        self.svd0 = StockValueData.objects.get(stock=self.s0)
        self.svd1 = StockValueData.objects.get(stock=self.s1)
        self.svdt = StockValueData.objects.get(stock=self.st)
        # Open Entry of Stock
        self.e0 = Entry.objects.get(stock=self.s0, memo="without dividend")
        self.o0b = Order.objects.get(stock=self.s0, is_buy=True, entry=self.e0)
        # Open Entry of Stock with Dividend
        self.e0d = Entry.objects.get(stock=self.s0, memo="with dividend")
        self.o0db = Order.objects.get(stock=self.s0, is_buy=True, entry=self.e0d)
        self.div0 = Dividend.objects.get(entry=self.e0d)
        # Open Entry with multiple orders
        self.e1 = Entry.objects.get(stock=self.s1, is_closed=False)
        self.o1b1 = Order.objects.get(stock=self.s1, is_buy=True, num=100, entry=self.e1)
        self.o1b2 = Order.objects.get(stock=self.s1, is_buy=True, num=200, entry=self.e1)
        # Open Entry of Trust
        self.et = Entry.objects.get(stock=self.st)
        self.otb = Order.objects.get(stock=self.st, is_buy=True)
        # Closed Entry
        self.e11 = Entry.objects.get(stock=self.s1, is_closed=True)
        self.o11b = Order.objects.get(stock=self.s1, is_buy=True, entry=self.e11)
        self.o11s = Order.objects.get(stock=self.s1, is_buy=False, entry=self.e11)

    def tearDown(self) -> None:
        self.client.logout()
        return super().tearDown()

    def test_total_now(self):
        """
        total_now, Normal
        """
        # test
        test_scenarios = [
            (self.e0.total_now, self.svd0.val_close*self.o0b.num, "Stock with one order"),
            (self.e1.total_now, self.svd1.val_close*(self.o1b1.num+self.o1b2.num), "Stock with multiple orders"),
        ]
        for result, expectation, name in test_scenarios:
            with self.subTest(result=result, expectation=expectation, name=name):
                self.assertEqual(result, expectation)

    def test_profit_profit_determination(self):
        """
        profit_profit_determination, Normal
        """
        # prepare
        profit_profit_determination = self.o0b.num * (self.e0.border_profit_determination - self.o0b.val)
        # test
        test_scenarios = [
            (self.e0.profit_profit_determination, profit_profit_determination, "Stock with border_profit_determination"),
            (self.e1.profit_profit_determination, None, "Stock without border_profit_determination"),
        ]
        for result, expectation, name in test_scenarios:
            with self.subTest(result=result, expectation=expectation, name=name):
                self.assertEqual(result, expectation)

    def test_border_profit_determination_percent(self):
        """
        border_profit_determination_percent, Normal
        """
        # prepare
        border_profit_determination_percent = self.o0b.num * (self.e0.border_profit_determination - self.o0b.val) / self.o0b.val 
        # test
        test_scenarios = [
            (self.e0.border_profit_determination_percent, border_profit_determination_percent, "Stock with border_profit_determination"),
            (self.e1.border_profit_determination_percent, None, "Stock without border_profit_determination"),
        ]
        for result, expectation, name in test_scenarios:
            with self.subTest(result=result, expectation=expectation, name=name):
                self.assertEqual(result, expectation)
    
    def test_profit_loss_cut(self):
        """
        profit_loss_cut, Normal
        """
        # prepare
        profit_loss_cut = self.o0b.num * (self.e0.border_loss_cut - self.o0b.val)
        # test
        test_scenarios = [
            (self.e0.profit_loss_cut, profit_loss_cut, "Stock with border_loss_cut"),
            (self.e1.profit_loss_cut, None, "Stock without border_loss_cut"),
        ]
        for result, expectation, name in test_scenarios:
            with self.subTest(result=result, expectation=expectation, name=name):
                self.assertEqual(result, expectation)

    def test_border_loss_cut_percent(self):
        """
        border_loss_cut_percent, Normal
        """
        # prepare
        border_loss_cut_percent = self.o0b.num * (self.e0.border_loss_cut - self.o0b.val) / self.o0b.val
        # test
        test_scenarios = [
            (self.e0.border_loss_cut_percent, border_loss_cut_percent, "Stock with border_loss_cut"),
            (self.e1.border_loss_cut_percent, None, "Stock without border_loss_cut"),
        ]
        for result, expectation, name in test_scenarios:
            with self.subTest(result=result, expectation=expectation, name=name):
                self.assertEqual(result, expectation)

    def test_num_buy(self):
        """
        num_buy, Normal
        """
        # test
        test_scenarios = [
            (self.e0.num_buy, self.o0b.num, "Stock with one order"),
            (self.et.num_buy, self.otb.num, "Trust with one order"),
            (self.e1.num_buy, self.o1b1.num+self.o1b2.num, "Stock with multiple orders"),
        ]
        for result, expectation, name in test_scenarios:
            with self.subTest(result=result, expectation=expectation, name=name):
                self.assertEqual(result, expectation)

    def test_val_buy(self):
        """
        val_buy, Normal
        """
        # prepare
        e1_val_buy = (self.o1b1.val*self.o1b1.num+self.o1b2.val*self.o1b2.num)/(self.o1b1.num+self.o1b2.num)
        # test
        test_scenarios = [
            (self.e0.val_buy, self.o0b.val, "Stock with one order"),
            (self.et.val_buy, self.otb.val, "Trust with one order"),
            (self.e1.val_buy, e1_val_buy, "Stock with multiple orders"),
        ]
        for result, expectation, name in test_scenarios:
            with self.subTest(result=result, expectation=expectation, name=name):
                self.assertEqual(result, expectation)

    def test_total_buy(self):
        """
        total_buy, Normal
        """
        # prepare
        e1_total_buy = self.o1b1.val*self.o1b1.num+self.o1b2.val*self.o1b2.num
        # test
        test_scenarios = [
            (self.e0.total_buy, self.o0b.val*self.o0b.num, "Stock with one order"),
            (self.et.total_buy, self.otb.val*self.otb.num, "Trust with one order"),
            (self.e1.total_buy, e1_total_buy, "Stock with multiple orders"),
        ]
        for result, expectation, name in test_scenarios:
            with self.subTest(result=result, expectation=expectation, name=name):
                self.assertEqual(result, expectation)

    def test_num_sell(self):
        """
        num_sell, Normal
        """
        # test
        test_scenarios = [
            (self.e11.num_sell, self.o11s.num, "Stock with one order"),
        ]
        for result, expectation, name in test_scenarios:
            with self.subTest(result=result, expectation=expectation, name=name):
                self.assertEqual(result, expectation)

    def test_val_sell(self):
        """
        num_val, Normal
        """
        # test
        test_scenarios = [
            (self.e11.val_sell, self.o11s.val, "Stock with one order"),
        ]
        for result, expectation, name in test_scenarios:
            with self.subTest(result=result, expectation=expectation, name=name):
                self.assertEqual(result, expectation)

    def test_total_sell(self):
        """
        toal_sell, Normal
        """
        # test
        test_scenarios = [
            (self.e11.total_sell, self.o11s.num*self.o11s.val, "Stock with one order"),
        ]
        for result, expectation, name in test_scenarios:
            with self.subTest(result=result, expectation=expectation, name=name):
                self.assertEqual(result, expectation)

    def test_holding_period(self):
        """
        holding_period, Normal
        """
        # prepare
        holding_period11 = (self.o11s.datetime.date()  - self.o11b.datetime.date()).days + 1
        holding_period0 = (date.today()  - self.o0b.datetime.date()).days + 1
        # test
        test_scenarios = [
            (self.e11.holding_period, holding_period11, "Closed Entry"),
            (self.e0.holding_period, holding_period0, "Open Entry"),
        ]
        for result, expectation, name in test_scenarios:
            with self.subTest(result=result, expectation=expectation, name=name):
                self.assertEqual(result, expectation)

    def test_profit_per_days(self):
        """
        profit_per_days, Normal
        """
        # prepare
        profit_per_days11 = (
            self.o11s.num * self.o11s.val - self.o11b.num * self.o11b.val - self.o11b.commission - self.o11s.commission
            ) / ((self.o11s.datetime.date() - self.o11b.datetime.date()).days + 1) 
        profit_per_days0 = (
            (self.s0.latest_val - self.o0b.val) * self.o0b.num - self.o0b.commission
            ) / ((date.today() - self.o0b.datetime.date()).days + 1) 
        profit_per_days0d = (
            (self.s0.latest_val - self.o0db.val) * self.o0db.num - self.o0db.commission + self.div0.val
            ) / ((date.today() - self.o0db.datetime.date()).days + 1) 
        # test
        test_scenarios = [
            (self.e11.profit_per_days, profit_per_days11, "Closed Entry"),
            (self.e0.profit_per_days, profit_per_days0, "Open Entry"),
            (self.e0d.profit_per_days, profit_per_days0d, "Open Entry with dividend"),
        ]
        for result, expectation, name in test_scenarios:
            with self.subTest(result=result, expectation=expectation, name=name):
                self.assertEqual(result, expectation)

    def test_profit(self):
        """
        profit, Normal
        """
        # prepare
        profit11 = self.o11s.num * self.o11s.val - self.o11b.num * self.o11b.val - self.o11b.commission - self.o11s.commission
        profit0 = (self.s0.latest_val - self.o0b.val) * self.o0b.num - self.o0b.commission
        profit0d = (self.s0.latest_val - self.o0db.val) * self.o0db.num - self.o0db.commission + self.div0.val
        # test
        test_scenarios = [
            (self.e11.profit, profit11, "Closed Entry"),
            (self.e0.profit, profit0, "Open Entry"),
            (self.e0d.profit, profit0d, "Entry with Dividend")
        ]
        for result, expectation, name in test_scenarios:
            with self.subTest(result=result, expectation=expectation, name=name):
                self.assertEqual(result, expectation)

    def test_profit_after_tax(self):
        """
        profit_after_tax, Normal
        """
        # prepare
        profit_after_tax11 = self.o11s.num * self.o11s.val - self.o11b.num * self.o11b.val - self.o11b.commission - self.o11s.commission
        profit_after_tax0 = (self.s0.latest_val - self.o0b.val) * self.o0b.num - self.o0b.commission
        profit_after_tax1 = self.s1.latest_val * (self.o1b1.num + self.o1b2.num) \
            - self.o1b1.val * self.o1b1.num - self.o1b1.commission \
            - self.o1b2.val * self.o1b2.num - self.o1b2.commission
        # test
        test_scenarios = [
            (self.e11.profit_after_tax, round(profit_after_tax11*0.8), "Closed Entry Black"),
            (self.e0.profit_after_tax, round(profit_after_tax0*0.8), "Open Entry Black"),
            (self.e1.profit_after_tax, profit_after_tax1, "Open Entry Red"),
        ]
        for result, expectation, name in test_scenarios:
            with self.subTest(result=result, expectation=expectation, name=name):
                self.assertEqual(result, expectation)

    def test_profit_pct(self):
        """
        profit_pct, Normal
        """
        # prepare
        profit_pct = (
            self.o11s.num * self.o11s.val 
            - self.o11b.num * self.o11b.val 
            - self.o11b.commission - self.o11s.commission
            ) / (self.o11b.num * self.o11b.val)
        # test
        test_scenarios = [
            (self.e11.profit_pct, profit_pct, "Stock with one order"),
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