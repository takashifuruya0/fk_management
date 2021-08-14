from django.test import TestCase
from django.test.client import MULTIPART_CONTENT
from kakeibo.models import Resource, Usage, Kakeibo, Event, SharedKakeibo
from kakeibo.models import Budget, Exchange, Credit
from kakeibo.forms import KakeiboUSDForm, KakeiboForm
from datetime import date
from django.contrib.auth import get_user_model
from dateutil.relativedelta import relativedelta
from django.shortcuts import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
# Create your tests here.


class KakeiboViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Usage.objects.all().delete()
        Resource.objects.all().delete()
        get_user_model().objects.all().delete()
        # user
        get_user_model().objects.create(username="user", 
            password="test", is_superuser=False, is_staff=False)
        get_user_model().objects.create(username="admin", 
            password="test", is_superuser=True, is_staff=True)

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
        self.w_credit = "支出（カード）"
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
    def test_kakeibo_create_post(self):
        """
        KakeiboCreate: Normal POST
        """
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
        self.assertRedirects(
            response, 
            reverse("kakeibo:kakeibo_detail", kwargs={"pk": kakeibo_created.pk})
        )
        self.assertEqual(data['way'], kakeibo_created.way)
        self.assertEqual(1, Kakeibo.objects.all().count())
        # sharedkakeiboは作成されない
        self.assertEqual(0, SharedKakeibo.objects.all().count())

    def test_kakeibo_create_post_shared(self):
        """
        KakeiboCreate: Normal POST (Shared)
        """
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:kakeibo_create")
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
        self.assertEqual(1, Kakeibo.objects.all().count())
        # sharedkakeiboも作成される
        self.assertEqual(1, SharedKakeibo.objects.all().count())
    
    def test_kakeibo_create_exception_get(self):
        """
        KakeiboCreate: Exception POST
        """
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:kakeibo_create")
        # ~~~~~~~~~~~~~~~~ post failed ~~~~~~~~~~~~~~~~
        data = {
            "date": "2021-04-011",
            "fee": 100,
        }
        response = self.client.post(url, data)
        # 増えない
        self.assertEqual(0, Kakeibo.objects.all().count())

    def test_kakeibo_top(self):
        """
        KakeiboTop: Normal
        """
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:kakeibo_top")
        self.assertEqual("/kakeibo/mine", url)
        # ~~~~~~~~~~~~~~~~ access ~~~~~~~~~~~~~~~~
        self.client.get(url)
        self.assertTemplateUsed("kakeibo_top.html")

    def test_kakeibo_top_exception(self):
        """
        KakeiboTop: Exception
        """
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:kakeibo_top")
        # ~~~~~~~~~~~~~~~~ logout ~~~~~~~~~~~~~~~~
        self.client.logout()
        res = self.client.get(url)
        self.assertTemplateNotUsed("kakeibo_top.html")
        # self.assertRedirects(res, "/auth/login/")
        # ~~~~~~~~~~~~~~~~ user without permission ~~~~~~~~~~~~~~~~
        self.client.force_login(get_user_model().objects.get(username="user"))
        res = self.client.get(url)
        self.assertTemplateNotUsed("kakeibo_top.html")
        # self.assertRedirects(res, "/auth/login/")

    def test_kakeibo_list(self):
        """
        KakeiboList: Normal
        """
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:kakeibo_list")
        self.assertEqual("/kakeibo/mine/list", url)
        # ~~~~~~~~~~~~~~~~ access ~~~~~~~~~~~~~~~~
        self.client.get(url)
        self.assertTemplateUsed("kakeibo_list.html")
    
    def test_kakeibo_list(self):
        """
        KakeiboList: Normal (Search)
        """
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:kakeibo_list")
        # ~~~~~~~~~~~~~~~~ search ~~~~~~~~~~~~~~~~
        k1 = Kakeibo.objects.create(
            date="2021-06-01", fee=100, currency="JPY", usage=self.u_shopping,
            resource_from=self.r_wallet, resource_to=None, way=self.w_pay,
            memo="test"
        )
        k2 = Kakeibo.objects.create(
            date="2023-06-01", fee=100, currency="USD", usage=self.u_transer,
            resource_from=self.r_wallet, resource_to=self.r_saving, 
            way=self.w_transfer, memo="test2"
        )
        # subtest
        test_scenarios = [  # (url, count)
            # date_from
            (f"?date_from=2020-06-01", 2),
            # date_to
            (f"?date_to=2022-06-01", 1),
            # date_from and date_to
            (f"?date_from=2021-06-02&date_to=2022-06-01", 0),
            # usage and ways
            (f"?usages={self.u_shopping.pk}&ways={self.w_pay}", 1),
            # resource_from and resource_to
            (f"?resources_from={self.r_wallet.pk}&resources_to={self.r_saving.pk}", 1),
            # currency
            (f"?currency=USD", 1),
            # memo
            (f"?memo=test", 2),
        ]
        for condition, num in test_scenarios:
            with self.subTest(condition=condition, num=num):
                res = self.client.get(f"{url}{condition}")
                self.assertEqual(res.context['object_list'].count(), num)
                


    def test_kakeibo_detail(self):
        """
        KakeiboDetail: Normal
        """
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

    def test_kakeibo_update_get(self):
        """
        KakeiboUpdate: Normal, GET
        """
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

    def test_kakeibo_update_post(self):
        """
        KakeiboUpdate: Normal, POST
        """
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
        self.assertRedirects(
            res, reverse("kakeibo:kakeibo_detail", kwargs={"pk": kakeibo_updated.pk}))

    def test_kakeibo_update_get_usd(self):
        """
        KakeiboUpdate: Normal, GET, USD
        """
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

    def test_kakeibo_delete_get(self):
        """
        KakeiboDelete: Normal, GET
        """
        k1 = Kakeibo.objects.create(
            date="2021-06-01", fee=100, currency="JPY", usage=self.u_shopping,
            resource_from=self.r_wallet, resource_to=None, way=self.w_pay,
            memo="test"
        )
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:kakeibo_delete", kwargs={"pk": k1.pk})
        self.assertEqual("/kakeibo/mine/{}/delete".format(k1.pk), url)
        # ~~~~~~~~~~~~~~~~ get ~~~~~~~~~~~~~~~~
        res = self.client.get(url)
        self.assertTemplateUsed("kakeibo_delete.html")
        self.assertEqual(res.status_code, 200)

    def test_kakeibo_delete_exception_get(self):
        """
        KakeiboDelete: Exception, GET
        """
        k1 = Kakeibo.objects.create(
            date="2021-06-01", fee=100, currency="JPY", usage=self.u_shopping,
            resource_from=self.r_wallet, resource_to=None, way=self.w_pay,
            memo="test", is_active=False
        )
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:kakeibo_delete", kwargs={"pk": k1.pk})
        self.assertEqual("/kakeibo/mine/{}/delete".format(k1.pk), url)
        # ~~~~~~~~~~~~~~~~ get ~~~~~~~~~~~~~~~~
        res = self.client.get(url)
        self.assertRedirects(res, reverse("kakeibo:kakeibo_list"))


    def test_kakeibo_delete_post(self):
        """
        KakeiboDelete: Normal, POST
        """
        k1 = Kakeibo.objects.create(
            date="2021-06-01", fee=100, currency="JPY", usage=self.u_shopping,
            resource_from=self.r_wallet, resource_to=None, way=self.w_pay,
            memo="test"
        )
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:kakeibo_delete", kwargs={"pk": k1.pk})
        # ~~~~~~~~~~~~~~~~ post ~~~~~~~~~~~~~~~~        
        self.client.post(url)
        k1_deleted = Kakeibo.objects.get(pk=k1.pk)
        self.assertFalse(k1_deleted.is_active)

    # ========================================
    # Event
    # ========================================
    def test_event_create_get(self):
        """
        EventCreate: Normal, GET
        """
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:event_create")
        self.assertEqual("/kakeibo/event/create", url)

    def test_event_create_post(self):
        """
        EventCreate: Normal, POST
        """
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:event_create")
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
        self.assertEqual(1, Event.objects.all().count())
        self.assertRedirects(
            response, reverse("kakeibo:event_detail", kwargs={"pk": event_created.pk}))
        

    def test_event_update_get(self):
        """
        EventUpdate: Normal, GET
        """
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

    def test_event_update_post(self):
        """
        EventUpdate: Normal, POST
        """
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
        self.assertEqual(1, Event.objects.all().count())
        self.assertRedirects(
            response, reverse("kakeibo:event_detail", kwargs={"pk": event_updated.pk}))
        

    def test_event_delete_get(self):
        """
        EventDelte: Normal, GET
        """
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
        url = reverse("kakeibo:event_delete", kwargs={"pk": event.pk})
        self.assertEqual("/kakeibo/event/{}/delete".format(event.pk), url)
        # ~~~~~~~~~~~~~~~~ get ~~~~~~~~~~~~~~~~
        res = self.client.get(url)
        self.assertTemplateUsed("event_delete.html")
        self.assertEqual(res.status_code, 200)

    def test_event_delete_exception_get(self):
        """
        EventDelte: Exception, GET
        """
        data = {
            "date": "2021-04-01",
            "name": "t",
            "memo": "t",
            "detail": "t",
            "sum_plan": 10000,
            "is_closed": False,
            "is_active": False,
        }
        event = Event.objects.create(**data)
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:event_delete", kwargs={"pk": event.pk})
        # ~~~~~~~~~~~~~~~~ get ~~~~~~~~~~~~~~~~
        res = self.client.get(url)
        self.assertRedirects(res, reverse("kakeibo:event_list"))
    
    def test_event_delete_post(self):
        """
        EventDelte: Normal, POST
        """
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
        url = reverse("kakeibo:event_delete", kwargs={"pk": event.pk})
        # ~~~~~~~~~~~~~~~~ post ~~~~~~~~~~~~~~~~        
        self.client.post(url)
        event_deleted = Event.objects.get(pk=event.pk)
        self.assertFalse(event_deleted.is_active)
        

    # ========================================
    # Exchange
    # ========================================
    def test_exchange_form_post(self):
        """
        ExchangeCreate: Normal, POST
        """
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
        test_scenarios = (
            (u_from.kakeibo_set.all().count(), 1),
            (u_to.kakeibo_set.all().count(), 1),
            (Exchange.objects.all().count(), 1),
            (Kakeibo.objects.all().count(), 2)
        )
        for actual, expected in test_scenarios:
            with self.subTest(actual=actual, expected=expected):
                self.assertEqual(actual, expected)

    def test_exchange_form_get(self):
        """
        ExchangeCreate: Exception, GET
        """
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:exchange_create")
        # ~~~~~~~~~~~~~~~~ get:NG ~~~~~~~~~~~~~~~~
        res = self.client.get(url)
        self.assertRedirects(res, reverse("kakeibo:kakeibo_top"))

    def test_exchange_form_post_source_path(self):
        """
        ExchangeCreate: Normal, POST (SourcePath)
        """
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:exchange_create")
        # ~~~~~~~~~~~~~~~~ post without source_path~~~~~~~~~~~~~~~~
        r_jpy = Resource.objects.create(name="rJPY", currency="JPY", is_investment=False)
        r_usd = Resource.objects.create(name="rUSD", currency="USD", is_investment=False)
        u_from = Usage.objects.create(name="Exchange (From)", is_expense=True)
        u_to = Usage.objects.create(name="Exchange (To)", is_expense=False)
        data = {
            "date": "2021-06-02",
            "method": "Wire",
            "resource_from": r_jpy.pk,
            "fee_from": 10000,
            "resource_to": r_usd.pk,
            "fee_to": 90,
            "rate": 110,
            "commission": 100,
            "currency": "JPY",
        }
        res = self.client.post(url, data)
        self.assertRedirects(res, reverse("kakeibo:kakeibo_top"))
        test_scenarios = (
            (u_from.kakeibo_set.all().count(), 1),
            (u_to.kakeibo_set.all().count(), 1),
            (Exchange.objects.all().count(), 1),
            (Kakeibo.objects.all().count(), 2)
        )
        for actual, expected in test_scenarios:
            with self.subTest(actual=actual, expected=expected):
                self.assertEqual(actual, expected)
    
    # ========================================
    # Credit
    # ========================================
    def test_credit_import_get(self):    
        """
        CreditImport: Normal, GET
        """
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:credit_import")
        self.assertEqual("/kakeibo/credit/import", url)
        # ~~~~~~~~~~~~~~~~ get ~~~~~~~~~~~~~~~~
        res = self.client.get(url)
        self.assertRedirects(res, reverse("kakeibo:kakeibo_top"))
    
    def test_credit_import_exception_post(self):    
        """
        CreditImport: Exception, POST
        """
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:credit_import")
        # ~~~~~~~~~~~~~~~~ post ~~~~~~~~~~~~~~~~
        post_data = {
            "file": "It should be CSV file encoded by shit-jis",
            "card": "SFC",
            "date_debit": "2021-08-01",
        }
        res = self.client.post(url, data=post_data)
        self.assertRedirects(res, reverse("kakeibo:kakeibo_top"))


    def data_credit_link(self):
        """
        Data for tests of CreditLink
        """
        # Credit
        d1 = {
            "fee": 1000,
            "date": "2020-07-16",
            "debit_date": "2020-09-01",
            "name": "UBER EATS",
            "memo": "test",
            "card": "SFC",
            "currency": "JPY",
        }
        d2 = {
            "fee": 1000,
            "date": "2020-07-13",
            "debit_date": "2020-08-01",
            "name": "UBER EATS",
            "memo": "test",
            "card": "SFC",
            "currency": "JPY",
        }
        d3 = {
            "fee": 1000,
            "date": "2020-07-13",
            "debit_date": "2020-08-01",
            "name": "Amazon",
            "memo": "test",
            "card": "SFC",
            "currency": "JPY",
        }
        c1 = Credit.objects.create(**d1)
        c2 = Credit.objects.create(**d2)
        c3 = Credit.objects.create(**d3)
        # kakeibo
        d4 = {
            "date": "2020-07-15",
            "fee": 1000,
            "memo": "Amazon",
            "way": self.w_credit,
            "usage": self.u_shopping,
        }
        k4 = Kakeibo.objects.create(**d4)
        return c1, c2, c3, k4


    def test_credit_link_get(self):
        """
        CreditLink: Normal GET
        """
        # ~~~~~~~~~~~~~~~~ prepare ~~~~~~~~~~~~~~~~
        c1, c2, c3, k4 = self.data_credit_link()
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:credit_link")
        self.assertEqual("/kakeibo/credit/link", url)
        # ~~~~~~~~~~~~~~~~ get ~~~~~~~~~~~~~~~~
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "credit_link.html")
        self.assertEqual(res.context['total'], c1.fee+c2.fee+c3.fee)
        # debit_dateを指定
        res = self.client.get(url+"?debit_date=2020-08-01")
        self.assertEqual(res.context['total'], c2.fee+c3.fee)

    def test_credit_link_post(self):
        """
        CreditLink: Normal POST
        """
        # ~~~~~~~~~~~~~~~~ prepare ~~~~~~~~~~~~~~~~
        c1, c2, c3, k4 = self.data_credit_link()
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:credit_link")
        # ~~~~~~~~~~~~~~~~ post ~~~~~~~~~~~~~~~~
        num_before = Credit.objects.filter(is_active=True).count()
        num_before_kakeibo = Kakeibo.objects.filter(is_active=True).count()
        post_data = {
            f"id_{c1.pk}": "new",
            f"usage_{c1.pk}": self.u_lunch.pk,
            f"id_{c2.pk}": "delete",
            f"id_{c3.pk}": k4.pk,
        }
        res = self.client.post(url, data=post_data)
        # 同ページにリダイレクト
        self.assertRedirects(res, reverse("kakeibo:credit_link"))
        # subtest
        num_after = Credit.objects.filter(is_active=True).count()
        num_after_kakeibo = Kakeibo.objects.filter(is_active=True).count()
        k_new = Kakeibo.objects.last()
        test_scenarios = (
            # c1：新規Kakiebo作成
            (num_before_kakeibo, num_after_kakeibo-1),
            (Credit.objects.get(pk=c1.pk), k_new.credit),
            (post_data[f"usage_{c1.pk}"], k_new.usage.pk),
            # c2：delete
            (Credit.objects.get(pk=c2.pk).is_active, False),
            (num_before, num_after+1),
            # c3:link with k4
            (Credit.objects.get(pk=c3.pk), Kakeibo.objects.get(pk=k4.pk).credit)
        )
        for actual, expected in test_scenarios:
            with self.subTest(actual=actual, expected=expected):
                self.assertEqual(actual, expected)

    def data_credit_link_from_kakeibo(self):
        """
        Data for tests of CreditLinkFromKakeibo
        """
        d1 = {
            "date": "2020-07-15",
            "fee": 1000,
            "memo": "test",
            "way": self.w_credit,
            "usage": self.u_shopping,
        }
        d2 = {
            "date": "2020-08-15",
            "fee": 2000,
            "memo": "test",
            "way": self.w_credit,
            "usage": self.u_shopping,
        }
        d3 = {
            "date": "2020-08-15",
            "fee": 2000,
            "memo": "test",
            "way": self.w_pay,
            "usage": self.u_shopping,
        }
        k1 = Kakeibo.objects.create(**d1)
        k2 = Kakeibo.objects.create(**d2)
        k3 = Kakeibo.objects.create(**d3)
        # Credit
        d4 = {
            "fee": 1000,
            "date": "2020-07-15",
            "debit_date": "2020-08-01",
            "name": "UBER EATS",
            "memo": "test",
            "card": "SFC",
            "currency": "JPY",
        }
        c4 = Credit.objects.create(**d4)
        return k1, k2, k3, c4

    def test_credit_link_from_kakeibo_get(self):
        """
        CreditLinkFromKakeibo: Normal GET
        """
        # ~~~~~~~~~~~~~~~~ prepare ~~~~~~~~~~~~~~~~
        k1, k2, k3, c4 = self.data_credit_link_from_kakeibo()
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:credit_link_from_kakeibo")
        self.assertEqual("/kakeibo/credit/link_from_kakeibo", url)
        # ~~~~~~~~~~~~~~~~ get ~~~~~~~~~~~~~~~~
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "credit_link_from_kakeibo.html")
        self.assertEqual(res.context['total'], k1.fee+k2.fee)
        # target_dateを指定
        res = self.client.get(url+"?target_date=2020-08-01")
        self.assertEqual(res.context['total'], k2.fee)

    def test_credit_link_from_kakeibo_post(self):
        """
        CreditLinkFromKakeibo: Normal POST
        """
        # ~~~~~~~~~~~~~~~~ prepare ~~~~~~~~~~~~~~~~
        k1, k2, k3, c4 = self.data_credit_link_from_kakeibo()
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:credit_link_from_kakeibo")
        # ~~~~~~~~~~~~~~~~ post ~~~~~~~~~~~~~~~~
        num_before = Kakeibo.objects.filter(way=self.w_credit, is_active=True).count()
        post_data = {
            f"id_{k1.pk}": "link",
            f"credit_{k1.pk}": c4.pk,
            f"id_{k2.pk}": "delete",
        }
        res = self.client.post(url, data=post_data)
        num_after = Kakeibo.objects.filter(way=self.w_credit, is_active=True).count()
        # 同ページにリダイレクト
        self.assertRedirects(res, reverse("kakeibo:credit_link_from_kakeibo"))
        test_scenarios = (
            # k2がdeleteされる
            (Kakeibo.objects.get(pk=k2.pk).is_active, False),
            (num_before, num_after+1),
            # k1がc4に紐づく
            (Kakeibo.objects.get(pk=k1.pk).credit, c4),
        )
        for actual, expected in test_scenarios:
            with self.subTest(actual=actual, expected=expected):
                self.assertEqual(actual, expected)
