from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.models import Sum
from kakeibo.models import SharedKakeibo, Budget, Usage
from kakeibo.functions import calculation_shared
from datetime import date
from dateutil.relativedelta import relativedelta
import math
# Create your tests here.


class CalculationSharedTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Usage.objects.all().delete()
        get_user_model().objects.all().delete()
        # user
        get_user_model().objects.create(
            username="hoko", last_name="朋子", password="test", is_superuser=False, is_staff=False)
        get_user_model().objects.create(
            username="takashi", last_name="敬士", password="test", is_superuser=True, is_staff=True)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        Usage.objects.all().delete()
        get_user_model().objects.all().delete()

    def setUp(self) -> None:
        self.u_t = get_user_model().objects.get(username="takashi")
        self.u_h = get_user_model().objects.get(username="hoko")
        self.u_elec = Usage.objects.create(name="電気", is_expense=True, is_shared=True)
        self.u_food = Usage.objects.create(name="食費", is_expense=True, is_shared=True)
        self.u_gas = Usage.objects.create(name="ガス", is_expense=True, is_shared=True)

    def test_calc_seisan_black(self):
        """
        calc_seisan: black
        """
        # prepare
        today = date.today()
        SharedKakeibo.objects.create(fee=1000, paid_by=self.u_t, usage=self.u_food, date=today)
        SharedKakeibo.objects.create(fee=1000, paid_by=self.u_h, usage=self.u_food, date=today)
        SharedKakeibo.objects.create(fee=6000, paid_by=self.u_t, usage=self.u_elec, date=today)
        SharedKakeibo.objects.create(fee=6000, paid_by=self.u_t, usage=self.u_gas, date=today)
        budget = Budget.objects.create(takashi=10000, hoko=6000, date="1999-01-01")
        payment = calculation_shared.calc_payment(SharedKakeibo.objects.all())['payment']
        diff = SharedKakeibo.objects.all().aggregate(sum=Sum('fee'))['sum'] - budget.total
        # calculation
        seisan = calculation_shared.calc_seisan(budget=budget,diff=diff, payment=payment)
        # assert
        test_scenarios = [
            (seisan['seisan']['takashi'], 0),
            (seisan['seisan']['hoko'], 3000),  
            # (6000:h予算 - 1000:h支払 - 2000:黒字) 
        ]
        for actual, expected in test_scenarios:
            with self.subTest(actual=actual, excepted=expected):
                self.assertEqual(actual, expected)
    
    def test_calc_seisan_red(self):
        """
        calc_seisan: red
        """
        # prepare
        today = date.today()
        SharedKakeibo.objects.create(fee=1000, paid_by=self.u_t, usage=self.u_food, date=today)
        SharedKakeibo.objects.create(fee=1000, paid_by=self.u_h, usage=self.u_food, date=today)
        SharedKakeibo.objects.create(fee=10000, paid_by=self.u_t, usage=self.u_elec, date=today)
        SharedKakeibo.objects.create(fee=6000, paid_by=self.u_t, usage=self.u_gas, date=today)
        budget = Budget.objects.create(takashi=10000, hoko=6000, date="1999-01-01")
        payment = calculation_shared.calc_payment(SharedKakeibo.objects.all())['payment']
        diff = SharedKakeibo.objects.all().aggregate(sum=Sum('fee'))['sum'] - budget.total
        # calculation
        seisan = calculation_shared.calc_seisan(budget=budget,diff=diff, payment=payment)
        # assert
        test_scenarios = [
            (seisan['seisan']['takashi'], 0),
            (seisan['seisan']['hoko'], 6000),  
            # (6000:h予算 - 1000:h支払 + 1000:赤字/2) 
        ]
        for actual, expected in test_scenarios:
            with self.subTest(actual=actual, excepted=expected):
                self.assertEqual(actual, expected)

    def test_calc_p_budget_black(self):
        """
        calc_p_budget: black
        """
        # prepare
        today = date.today()
        SharedKakeibo.objects.create(fee=1000, paid_by=self.u_t, usage=self.u_food, date=today)
        SharedKakeibo.objects.create(fee=1000, paid_by=self.u_h, usage=self.u_food, date=today)
        SharedKakeibo.objects.create(fee=6000, paid_by=self.u_t, usage=self.u_elec, date=today)
        SharedKakeibo.objects.create(fee=6000, paid_by=self.u_t, usage=self.u_gas, date=today)
        budget = Budget.objects.create(takashi=10000, hoko=6000, date="1999-01-01")
        diff = SharedKakeibo.objects.all().aggregate(sum=Sum('fee'))['sum'] - budget.total
        # calculation
        p_budget = calculation_shared.calc_p_budget(budget, diff)
        # assert
        test_scenarios = [
            (p_budget['p_budget']['takashi'], math.floor(10000/16000*100), "takashi"),
            (p_budget['p_budget']['over'], 0, "over"),
            (
                p_budget['p_budget']['hoko'], 
                100-p_budget['p_budget']['over']-p_budget['p_budget']['takashi'], 
                "hoko"
            ),
        ]
        for actual, expected, key in test_scenarios:
            with self.subTest(actual=actual, excepted=expected, key=key):
                self.assertEqual(actual, expected)

    def test_calc_p_budget_red(self):
        """
        calc_p_budget: red
        """
        # prepare
        today = date.today()
        SharedKakeibo.objects.create(fee=1000, paid_by=self.u_t, usage=self.u_food, date=today)
        SharedKakeibo.objects.create(fee=1000, paid_by=self.u_h, usage=self.u_food, date=today)
        SharedKakeibo.objects.create(fee=10000, paid_by=self.u_t, usage=self.u_elec, date=today)
        SharedKakeibo.objects.create(fee=6000, paid_by=self.u_t, usage=self.u_gas, date=today)
        budget = Budget.objects.create(takashi=10000, hoko=6000, date="1999-01-01") 
        diff = SharedKakeibo.objects.all().aggregate(sum=Sum('fee'))['sum'] - budget.total
        # calculation
        p_budget = calculation_shared.calc_p_budget(budget, diff)
        # assert
        test_scenarios = [
            (p_budget['p_budget']['takashi'], math.floor(10000/18000*100), "takashi"),
            (p_budget['p_budget']['over'], math.floor(2000/18000*100), "over"),
            (
                p_budget['p_budget']['hoko'], 
                100-p_budget['p_budget']['over']-p_budget['p_budget']['takashi'], 
                "hoko"
            ),
        ]
        for actual, expected, key in test_scenarios:
            with self.subTest(actual=actual, excepted=expected, key=key):
                self.assertEqual(actual, expected)


    def test_calc_payment(self):
        """
        calc_payment
        """
        # prepare
        today = date.today()
        SharedKakeibo.objects.create(fee=1000, paid_by=self.u_t, usage=self.u_food, date=today)
        SharedKakeibo.objects.create(fee=1000, paid_by=self.u_h, usage=self.u_food, date=today)
        SharedKakeibo.objects.create(fee=10000, paid_by=self.u_t, usage=self.u_elec, date=today)
        SharedKakeibo.objects.create(fee=6000, paid_by=self.u_t, usage=self.u_gas, date=today)
        # calculation
        payment = calculation_shared.calc_payment(SharedKakeibo.objects.all())
        # assert
        test_scenarios = [
            (payment['payment']['takashi'], 17000),
            (payment['payment']['hoko'], 1000),
            (payment['payment']['total'], 18000),
            (payment['p_payment']['takashi'], math.floor(17000/18000*100)),
            (payment['p_payment']['hoko'], 100-math.floor(17000/18000*100)),
        ]
        for actual, expected in test_scenarios:
            with self.subTest(actual=actual, excepted=expected):
                self.assertEqual(actual, expected)