from django.test import TestCase
from django.db.utils import IntegrityError
from django.db import transaction
from django.contrib.auth import get_user_model
from asset.models import AssetTarget, AssetStatus
from datetime import date


class AssetStatusTest(TestCase):
    """
    !Test for AssetStatus
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

    def test_order(self):
        """
        Order, Normal
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
        # test
        test_scenarios = [
            (AssetStatus.objects.all().count(), 1, "count"),
            (str(astatus), f"AssetStatus_{d1['date']}", "__str__")
        ]
        for result, expectation, name in test_scenarios:
            with self.subTest(result=result, expectation=expectation, name=name):
                self.assertEqual(result, expectation)

    
class AssetTargetTest(TestCase):
    """
    !Test for AssetTarget
    """
    pass
