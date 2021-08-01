from django.test import TestCase
from kakeibo.models import Resource, Usage, Kakeibo, Event, SharedKakeibo, Budget, Exchange
from kakeibo.forms import KakeiboUSDForm, KakeiboForm
from datetime import date
from django.contrib.auth import get_user_model
from dateutil.relativedelta import relativedelta
from django.shortcuts import reverse
# Create your tests here.


class KakeiboViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Usage.objects.all().delete()
        Resource.objects.all().delete()
        get_user_model().objects.all().delete()
        # user
        get_user_model().objects.create(username="user", password="test", is_superuser=False, is_staff=False)
        get_user_model().objects.create(username="admin", password="test", is_superuser=True, is_staff=True)

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
        self.r_wallet = Resource.objects.create(name="wallet", is_investment=False)
        self.r_saving = Resource.objects.create(name="saving", is_investment=False)
        self.r_other = Resource.objects.create(name="other", is_investment=False)
        self.w_transfer = "振替"
        self.w_pay = "支出（現金）"
        self.u_shopping = Usage.objects.create(name="shopping", is_expense=True, is_shared=True)
        self.u_lunch = Usage.objects.create(name="lunch", is_expense=True, is_shared=True)
        self.u_transer = Usage.objects.create(name="transfer", is_expense=False)

    def tearDown(self) -> None:
        Usage.objects.all().delete()
        Resource.objects.all().delete()
        self.client.logout()

    # ========================================
    # Kakeibo
    # ========================================
    def test_kakeibo_create(self):
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:kakeibo_create")
        self.assertEqual("/kakeibo/mine/create", url)
        # ~~~~~~~~~~~~~~~~ post ~~~~~~~~~~~~~~~~
        data = {
            "date": "2021-04-01",
            "fee": 100,
            "memo": "t",
            "way": self.w_pay,
            "usage": self.u_shopping.pk,
            "resource_from": self.r_wallet.pk,
            "currency": "JPY",
            "is_shared": False,
        }
        response = self.client.post(url, data)
        kakeibo_created = Kakeibo.objects.last()
        # assert
        self.assertRedirects(response, reverse("kakeibo:kakeibo_detail", kwargs={"pk": kakeibo_created.pk}))
        self.assertEqual(data['way'], kakeibo_created.way)
        self.assertEqual(1, Kakeibo.objects.all().count())
        # sharedkakeiboは作成されない
        self.assertEqual(0, SharedKakeibo.objects.all().count())
        # ~~~~~~~~~~~~~~~~ post (is_shared=TRUE, source_path) ~~~~~~~~~~~~~~~~
        data = {
            "date": "2021-04-01",
            "fee": 100,
            "memo": "t",
            "way": self.w_pay,
            "usage": self.u_shopping.pk,
            "resource_from": self.r_wallet.pk,
            "currency": "USD",
            "is_shared": True,
            "source_path": "/kakeibo/mine"
        }
        response = self.client.post(url, data)
        kakeibo_created = Kakeibo.objects.last()
        # assert
        self.assertRedirects(response, data['source_path'])
        self.assertEqual(data['way'], kakeibo_created.way)
        self.assertEqual(2, Kakeibo.objects.all().count())
        # sharedkakeiboも作成される
        self.assertEqual(1, SharedKakeibo.objects.all().count())

    def test_kakeibo_top(self):
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:kakeibo_top")
        self.assertEqual("/kakeibo/mine", url)
        # ~~~~~~~~~~~~~~~~ access ~~~~~~~~~~~~~~~~
        self.client.get(url)
        self.assertTemplateUsed("kakeibo_top.html")

    def test_kakeibo_list(self):
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:kakeibo_list")
        self.assertEqual("/kakeibo/mine/list", url)
        # ~~~~~~~~~~~~~~~~ access ~~~~~~~~~~~~~~~~
        self.client.get(url)
        self.assertTemplateUsed("kakeibo_list.html")
        # ~~~~~~~~~~~~~~~~ search ~~~~~~~~~~~~~~~~
        k1 = Kakeibo.objects.create(
            date="2021-06-01", fee=100, currency="JPY", usage=self.u_shopping,
            resource_from=self.r_wallet, resource_to=None, way=self.w_pay,
            memo="test"
        )
        k2 = Kakeibo.objects.create(
            date="2023-06-01", fee=100, currency="USD", usage=self.u_transer,
            resource_from=self.r_wallet, resource_to=self.r_saving, way=self.w_transfer,
            memo="test2"
        )
        res = self.client.get("{}?date_from=2020-06-01".format(url))
        self.assertEqual(res.context['object_list'].count(), 2)
        res = self.client.get("{}?date_to=2022-06-01".format(url))
        self.assertEqual(res.context['object_list'].count(), 1)
        res = self.client.get("{}?date_from=2021-06-02&date_to=2022-06-01".format(url))
        self.assertEqual(res.context['object_list'].count(), 0)
        res = self.client.get("{}?usages={}&ways={}".format(url, self.u_shopping.pk, self.w_pay))
        self.assertEqual(res.context['object_list'].count(), 1)
        res = self.client.get("{}?resources_from={}&resources_to={}".format(url, self.r_wallet.pk, self.r_saving.pk))
        self.assertEqual(res.context['object_list'].count(), 1)
        res = self.client.get("{}?currency={}".format(url, "USD"))
        self.assertEqual(res.context['object_list'].count(), 1)
        res = self.client.get("{}?memo={}".format(url, "test"))
        self.assertEqual(res.context['object_list'].count(), 2)

    def test_kakeibo_detail(self):
        # ~~~~~~~~~~~~~~~~ prepare ~~~~~~~~~~~~~~~~
        data = {
            "date": "2021-06-01",
            "fee": 100,
            "usage": self.u_shopping,
            "resource_from": self.r_wallet,
            "way": self.w_pay,
            "memo": "test",
        }
        kakeibo = Kakeibo.objects.create(**data)
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:kakeibo_detail", kwargs={"pk": kakeibo.pk})
        self.assertEqual("/kakeibo/mine/{}".format(kakeibo.pk), url)
        # ~~~~~~~~~~~~~~~~ access ~~~~~~~~~~~~~~~~
        self.client.get(url)
        self.assertTemplateUsed("kakeibo_detail.html")

    def test_kakeibo_update(self):
        # ~~~~~~~~~~JPY~~~~~~~~~~~~~~
        data = {
            "date": "2021-06-01",
            "fee": 100,
            "usage": self.u_shopping,
            "resource_from": self.r_wallet,
            "way": self.w_pay,
            "memo": "test",
        }
        kakeibo = Kakeibo.objects.create(**data)
        # url
        url = reverse("kakeibo:kakeibo_update", kwargs={"pk": kakeibo.pk})
        self.assertEqual("/kakeibo/mine/{}/edit".format(kakeibo.pk), url)
        # access
        res = self.client.get(url)
        self.assertEqual(type(res.context['form']), KakeiboForm)
        self.assertTemplateUsed("kakeibo_update.html")
        # ~~~~~~~~~~POST~~~~~~~~~~~~~~
        data2 = {
            "date": "2021-06-01",
            "fee": 200,
            "usage": self.u_shopping.pk,
            "resource_from": self.r_wallet.pk,
            "way": self.w_pay,
            "memo": "test",
            "currency": kakeibo.currency,
            "is_shared": False,
        }
        res = self.client.post(url, data2)
        kakeibo_updated = Kakeibo.objects.get(pk=kakeibo.pk)
        self.assertEqual(data2['fee'], kakeibo_updated.fee)
        self.assertRedirects(res, reverse("kakeibo:kakeibo_detail", kwargs={"pk": kakeibo_updated.pk}))
        # ~~~~~~~~~~USD~~~~~~~~~~~~~~
        data_usd = {
            "date": "2021-06-01",
            "fee": 100,
            "usage": self.u_shopping,
            "resource_from": self.r_wallet,
            "way": self.w_pay,
            "memo": "test",
            "currency": "USD",
        }
        kakeibo_usd = Kakeibo.objects.create(**data_usd)
        # url
        url = reverse("kakeibo:kakeibo_update", kwargs={"pk": kakeibo_usd.pk})
        self.assertEqual("/kakeibo/mine/{}/edit".format(kakeibo_usd.pk), url)
        # access
        res = self.client.get(url)
        self.assertEqual(type(res.context['form']), KakeiboUSDForm)
        self.assertTemplateUsed("kakeibo_update.html")

    # ========================================
    # Event
    # ========================================
    def test_event_create(self):
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:event_create")
        self.assertEqual("/kakeibo/event/create", url)
        # ~~~~~~~~~~~~~~~~ post ~~~~~~~~~~~~~~~~
        data = {
            "date": "2021-04-01",
            "name": "t",
            "memo": "t",
            "detail": "t",
            "sum_plan": 10000,
            "is_closed": False
        }
        response = self.client.post(url, data)
        event_created = Event.objects.last()
        # ~~~~~~~~~~~~~~~~ assert ~~~~~~~~~~~~~~~~
        self.assertEqual(data['sum_plan'], event_created.sum_plan)
        self.assertRedirects(response, reverse("kakeibo:event_detail", kwargs={"pk": event_created.pk}))
        self.assertEqual(1, Event.objects.all().count())

    def test_event_update(self):
        # prepare
        data = {
            "date": "2021-04-01",
            "name": "t",
            "memo": "t",
            "detail": "t",
            "sum_plan": 10000,
            "is_closed": False
        }
        event = Event.objects.create(**data)
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:event_update", kwargs={"pk": event.pk})
        self.assertEqual("/kakeibo/event/{}/edit".format(event.pk), url)
        # ~~~~~~~~~~~~~~~~ get ~~~~~~~~~~~~~~~~
        res = self.client.get(url)
        self.assertTemplateUsed(res, "event_update.html")
        # ~~~~~~~~~~~~~~~~ post ~~~~~~~~~~~~~~~~
        data2 = {
            "date": "2021-04-01",
            "name": "t",
            "memo": "t",
            "detail": "t",
            "sum_plan": 20000,
            "is_closed": False
        }
        response = self.client.post(url, data2)
        event_updated = Event.objects.get(pk=event.pk)
        # ~~~~~~~~~~~~~~~~ assert ~~~~~~~~~~~~~~~~
        self.assertEqual(data2['sum_plan'], event_updated.sum_plan)
        self.assertRedirects(response, reverse("kakeibo:event_detail", kwargs={"pk": event_updated.pk}))
        self.assertEqual(1, Event.objects.all().count())

    # ========================================
    # Exchange
    # ========================================
    def test_exchange_form(self):
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:exchange_create")
        self.assertEqual("/kakeibo/exchange/create", url)
        # ~~~~~~~~~~~~~~~~ post ~~~~~~~~~~~~~~~~
        r_jpy = Resource.objects.create(name="rJPY", currency="JPY", is_investment=False)
        r_usd = Resource.objects.create(name="rUSD", currency="USD", is_investment=False)
        u_from = Usage.objects.create(name="Exchange (From)", is_expense=True)
        u_to = Usage.objects.create(name="Exchange (To)", is_expense=False)
        data = {
            "date": "2021-06-01",
            "method": "Wire",
            "resource_from": r_jpy.pk,
            "fee_from": 10000,
            "resource_to": r_usd.pk,
            "fee_to": 90,
            "rate": 110,
            "commission": 100,
            "currency": "JPY",
            "source_path": "/kakeibo/mine",
        }
        res = self.client.post(url, data)
        # ~~~~~~~~~~~~~~~~ assert ~~~~~~~~~~~~~~~~
        self.assertRedirects(res, data['source_path'])
        self.assertEqual(u_from.kakeibo_set.all().count(), 1)
        self.assertEqual(u_to.kakeibo_set.all().count(), 1)
        self.assertEqual(Exchange.objects.all().count(), 1)
        self.assertEqual(Kakeibo.objects.all().count(), 2)
        # ~~~~~~~~~~~~~~~~ get:NG ~~~~~~~~~~~~~~~~
        res = self.client.get(url)
        self.assertRedirects(res, reverse("kakeibo:kakeibo_top"))