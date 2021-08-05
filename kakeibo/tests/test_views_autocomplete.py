from django.test import TestCase
from kakeibo.models import Resource, Usage, Kakeibo, Event, SharedKakeibo, Budget, Exchange
from kakeibo.forms import KakeiboUSDForm, KakeiboForm
from django.contrib.auth import get_user_model
from django.shortcuts import reverse
import json
# Create your tests here.


class AutocompleteViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # user
        get_user_model().objects.create(username="user_a", password="test", is_superuser=False, is_staff=False)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        Usage.objects.all().delete()
        Resource.objects.all().delete()
        get_user_model().objects.all().delete()

    def setUp(self) -> None:
        # lgoin
        self.client.force_login(get_user_model().objects.last())
        # data
        self.r_wallet = Resource.objects.create(name="wallet_a", is_investment=False)
        self.r_saving = Resource.objects.create(name="saving_a", is_investment=False)
        self.r_other = Resource.objects.create(name="other_a", is_investment=False)
        self.w_transfer = "振替"
        self.w_pay = "支出（現金）"
        self.u_shopping = Usage.objects.create(name="shopping_a", is_expense=True)
        self.u_transer = Usage.objects.create(name="transfer_a", is_expense=False)

    def tearDown(self) -> None:
        Usage.objects.all().delete()
        Resource.objects.all().delete()
        self.client.logout()

    def test_autocomplete_usage(self):
        url = reverse("kakeibo:autocomplete_usage")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        # q
        res = self.client.get(url, data={"q": "test"})
        self.assertEqual(res.status_code, 200)
        # logout
        self.client.logout()
        res = self.client.get(url)
        jsondata = json.loads(res.content)
        self.assertEqual(
            jsondata, {"results": [], "pagination": {"more": False}}
        )
        self.assertEqual(res.status_code, 200)

    def test_autocomplete_resource(self):
        url = reverse("kakeibo:autocomplete_resource")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        # q
        res = self.client.get(url, data={"q": "test"})
        self.assertEqual(res.status_code, 200)
        # logout
        self.client.logout()
        res = self.client.get(url)
        jsondata = json.loads(res.content)
        self.assertEqual(
            jsondata, {"results": [], "pagination": {"more": False}}
        )
        self.assertEqual(res.status_code, 200)