from django.test import TestCase
from django.db.utils import IntegrityError
from django.db import transaction
from django.contrib.auth import get_user_model
from asset.models import Stock, StockAnalysisData, StockValueData
from datetime import date, datetime


class StockTest(TestCase):
    """
    !Test for Stock
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

    def test_stock(self):
        """
        Stock, Normal
        """
        # prepare
        d1 = {
            "code": "1234",
            "name": "test stock",
        }
        s = Stock.objects.create(**d1)
        # test
        test_scenarios = [
            (Stock.objects.all().count(), 1, "count"),
            (str(s), f"({d1['code']}) {d1['name']}", "__str__")
        ]
        for result, expectation, name in test_scenarios:
            with self.subTest(result=result, expectation=expectation, name=name):
                self.assertEqual(result, expectation)

    def test_stock_unique(self):
        """
        Stock, Exception: Code is unique 
        """
        # prepare
        d1 = {
            "code": "1234",
            "name": "test stock",
        }
        s1 = Stock.objects.create(**d1)
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                s2 = Stock.objects.create(**d1)

    def test_latest_val(self):
        """
        Stock, Normal: latet_val
        """
        # prepare
        d1 = {
            "code": "1234",
            "name": "test stock",
        }
        d2 = {
            "code": "1235",
            "name": "test stock",
        }
        s1 = Stock.objects.create(**d1)
        s2 = Stock.objects.create(**d2)
        d3 = {
            "stock": s1,
            "date": date.today(),
            "val_high": 120,
            "val_low": 90,
            "val_open": 105,
            "val_close": 100,
            "turnover": 100000,
        }
        svd1 = StockValueData.objects.create(**d3)
        # test
        test_scenarios = [
            (s1.latest_val, d3["val_close"], "with svd"),
            (s2.latest_val, None, "without svd")
        ]
        for result, expectation, name in test_scenarios:
            with self.subTest(result=result, expectation=expectation, name=name):
                self.assertEqual(result, expectation)
        

    def test_latest_val_date(self):
        """
        Stock, Normal: latet_val_date
        """
        # prepare
        # prepare
        d1 = {
            "code": "1234",
            "name": "test stock",
        }
        d2 = {
            "code": "1235",
            "name": "test stock",
        }
        s1 = Stock.objects.create(**d1)
        s2 = Stock.objects.create(**d2)
        d3 = {
            "stock": s1,
            "date": date.today(),
            "val_high": 120,
            "val_low": 90,
            "val_open": 105,
            "val_close": 100,
            "turnover": 100000,
        }
        svd1 = StockValueData.objects.create(**d3)
        # test
        test_scenarios = [
            (s1.latest_val_date, d3["date"], "with svd"),
            (s2.latest_val_date, None, "without svd")
        ]
        for result, expectation, name in test_scenarios:
            with self.subTest(result=result, expectation=expectation, name=name):
                self.assertEqual(result, expectation)


class StockValueDataTest(TestCase):
    """
    !Test for StockValueData
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

    def test_stock_value_data(self):
        """
        Stock, Normal
        """
        # prepare
        d1 = {
            "code": "1234",
            "name": "test stock",
        }
        s1 = Stock.objects.create(**d1)
        d2 = {
            "stock": s1,
            "date": date.today(),
            "val_high": 120,
            "val_low": 90,
            "val_open": 105,
            "val_close": 100,
            "turnover": 100000,
        }
        svd = StockValueData.objects.create(**d2)
        # test
        test_scenarios = [
            (StockValueData.objects.all().count(), 1, "count"),
            (str(svd), f"SVD_{d2['date']}_{d2['stock']}", "__str__")
        ]
        for result, expectation, name in test_scenarios:
            with self.subTest(result=result, expectation=expectation, name=name):
                self.assertEqual(result, expectation)

class StockAnalysisDataTest(TestCase):
    """
    !Test for StockAnalysisData
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

    def test_stock_analysis_data(self):
        """
        Stock, Normal
        """
        # prepare
        d1 = {
            "code": "1234",
            "name": "test stock",
        }
        s1 = Stock.objects.create(**d1)
        d2 = {
            "stock": s1,
            "date": date.today(),
            "val_high": 120,
            "val_low": 90,
            "val_open": 105,
            "val_close": 100,
            "turnover": 100000,
        }
        svd = StockValueData.objects.create(**d2)
        d3 = {
            "stock": s1,
            "date": date(2021,3,1),
            # prepare
            'val_close_dy': 1.01,
            'val_close_dy_pct': 1.01,
            'turnover_dy': 1.01,
            'turnover_dy_pct': 1.01,
            'val_line': 1.01,
            'val_line_pct': 1.01,
            'is_positive': False,
            'lower_mustache': 1.01,
            'upper_mustache': 1.01,
            'ma05': 1.01,
            'ma25': 1.01,
            'ma75': 1.01,
            'ma05_diff': 1.01,
            'ma25_diff': 1.01,
            'ma75_diff': 1.01,
            'ma05_diff_pct': 1.01,
            'ma25_diff_pct': 1.01,
            'ma75_diff_pct': 1.01,
            'sigma25': 1.01,
            'ma25_p2sigma': 1.01,
            'ma25_m2sigma': 1.01,
            'is_upper05': True,
            'is_upper25': False,
            'is_upper75': True,
            # check
            'is_takuri': True,
            'is_tsutsumi': False,
            'is_harami': True,
            'is_age_sanpo': False,
            'is_sage_sanpo': True,
            'is_sanku_tatakikomi': False,
            'is_sante_daiinsen': True,
            'svd': svd,
        }
        svd = StockAnalysisData.objects.create(**d3)
        # test
        test_scenarios = [
            (StockAnalysisData.objects.all().count(), 1, "count"),
            (str(svd), f"SAD_{d3['date']}_{d3['stock']}", "__str__")
        ]
        for result, expectation, name in test_scenarios:
            with self.subTest(result=result, expectation=expectation, name=name):
                self.assertEqual(result, expectation)