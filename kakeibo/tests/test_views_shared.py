from django.test import TestCase
from kakeibo.models import Resource, Usage, SharedKakeibo, Budget
from kakeibo.forms import SharedForm
from datetime import date
from django.contrib.auth import get_user_model
from dateutil.relativedelta import relativedelta
from django.shortcuts import reverse
# Create your tests here.


class SharedViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Usage.objects.all().delete()
        Resource.objects.all().delete()
        get_user_model().objects.all().delete()
        # user
        get_user_model().objects.create(username="hoko", password="test", is_superuser=False, is_staff=False)
        get_user_model().objects.create(username="takashi", password="test", is_superuser=True, is_staff=True)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        Usage.objects.all().delete()
        Resource.objects.all().delete()
        get_user_model().objects.all().delete()

    def setUp(self) -> None:
        # lgoin
        self.user_takashi = get_user_model().objects.get(username="takashi")
        self.user_hoko = get_user_model().objects.get(username="hoko")
        self.client.force_login(self.user_takashi)
        # data
        self.r_wallet = Resource.objects.create(name="wallet", is_investment=False)
        self.r_saving = Resource.objects.create(name="saving", is_investment=False)
        self.r_other = Resource.objects.create(name="other", is_investment=False)
        self.w_transfer = "振替"
        self.w_pay = "支出（現金）"
        self.u_shopping = Usage.objects.create(name="shopping", is_expense=True, is_shared=True)
        self.u_lunch = Usage.objects.create(name="lunch", is_expense=True, is_shared=True)
        self.u_transer = Usage.objects.create(name="transfer", is_expense=False)
        # Budget
        self.budget = Budget.objects.create(takashi=100000, hoko=60000, date="2000-01-01")
        self.budget2 = Budget.objects.create(takashi=100000, hoko=60000, date=date.today())

    def tearDown(self) -> None:
        Usage.objects.all().delete()
        Resource.objects.all().delete()
        Budget.objects.all().delete()
        self.client.logout()

    # ========================================
    # SharedKakeibo
    # ========================================
    def test_shared_create(self):
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:shared_create")
        self.assertEqual("/kakeibo/shared/create", url)
        # ~~~~~~~~~~~~~~~~ post ~~~~~~~~~~~~~~~~
        data = {
            "date": "2021-04-01",
            "fee": 100,
            "memo": "t",
            "usage": self.u_shopping.pk,
            "paid_by": self.user_takashi.pk,
        }
        response = self.client.post(url, data)
        shared_created = SharedKakeibo.objects.last()
        # assert
        self.assertRedirects(response, reverse("kakeibo:shared_detail", kwargs={"pk": shared_created.pk}))
        self.assertEqual(data['fee'], shared_created.fee)
        self.assertEqual(1, SharedKakeibo.objects.all().count())

    def test_shared_top(self):
        # data
        k1 = SharedKakeibo.objects.create(
            date="2021-05-01", fee=100, usage=self.u_shopping,
            memo="test", paid_by=self.user_takashi
        )
        k2 = SharedKakeibo.objects.create(
            date="2021-06-01", fee=100, usage=self.u_lunch,
            memo="test2", paid_by=self.user_hoko
        )
        k3 = SharedKakeibo.objects.create(
            date="2021-06-02", fee=1000, usage=self.u_lunch,
            memo="test3", paid_by=self.user_takashi
        )
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:shared_top")
        self.assertEqual("/kakeibo/shared", url)
        # ~~~~~~~~~~~~~~~~ access ~~~~~~~~~~~~~~~~
        self.client.get(url)
        self.assertTemplateUsed("shared_top.html")
        # ~~~~~~~~~~~~~~~~ access with target_ym ~~~~~~~~~~~~~~~~
        self.client.get(f"{url}?target_ym=2021-06")
        self.assertTemplateUsed("shared_top.html")

    def test_shared_list(self):
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:shared_list")
        self.assertEqual("/kakeibo/shared/list", url)
        # ~~~~~~~~~~~~~~~~ access ~~~~~~~~~~~~~~~~
        self.client.get(url)
        self.assertTemplateUsed("shared_list.html")
        # ~~~~~~~~~~~~~~~~ search ~~~~~~~~~~~~~~~~
        k1 = SharedKakeibo.objects.create(
            date="2021-06-01", fee=100, usage=self.u_shopping,
            memo="test", paid_by=self.user_takashi
        )
        k2 = SharedKakeibo.objects.create(
            date="2023-06-01", fee=100, usage=self.u_lunch,
            memo="test2", paid_by=self.user_hoko
        )
        res = self.client.get("{}?date_from=2020-06-01".format(url))
        self.assertEqual(res.context['object_list'].count(), 2)
        res = self.client.get("{}?date_to=2022-06-01".format(url))
        self.assertEqual(res.context['object_list'].count(), 1)
        res = self.client.get("{}?date_from=2021-06-02&date_to=2022-06-01".format(url))
        self.assertEqual(res.context['object_list'].count(), 0)
        res = self.client.get("{}?usages={}".format(url, self.u_shopping.pk))
        self.assertEqual(res.context['object_list'].count(), 1)
        res = self.client.get("{}?memo={}".format(url, "test"))
        self.assertEqual(res.context['object_list'].count(), 2)

    def test_shared_detail(self):
        # ~~~~~~~~~~~~~~~~ prepare ~~~~~~~~~~~~~~~~
        data = {
            "date": "2021-06-01",
            "fee": 100,
            "usage": self.u_shopping,
            "memo": "test",
            "paid_by": self.user_takashi
        }
        shared = SharedKakeibo.objects.create(**data)
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:shared_detail", kwargs={"pk": shared.pk})
        self.assertEqual("/kakeibo/shared/{}".format(shared.pk), url)
        # ~~~~~~~~~~~~~~~~ access ~~~~~~~~~~~~~~~~
        self.client.get(url)
        self.assertTemplateUsed("shared_detail.html")

    def test_shared_update(self):
        data = {
            "date": "2021-06-01",
            "fee": 100,
            "usage": self.u_shopping,
            "paid_by": self.user_takashi,
            "memo": "test",
        }
        shared = SharedKakeibo.objects.create(**data)
        # url
        url = reverse("kakeibo:shared_update", kwargs={"pk": shared.pk})
        self.assertEqual("/kakeibo/shared/{}/edit".format(shared.pk), url)
        # access
        res = self.client.get(url)
        self.assertEqual(type(res.context['form']), SharedForm)
        self.assertTemplateUsed("shared_update.html")
        # ~~~~~~~~~~POST~~~~~~~~~~~~~~
        data2 = {
            "date": "2021-06-01",
            "fee": 200,
            "usage": self.u_shopping.pk,
            "paid_by": self.user_hoko.pk,
            "memo": "test",
        }
        res = self.client.post(url, data2)
        shared_updated = SharedKakeibo.objects.get(pk=shared.pk)
        self.assertEqual(data2['fee'], shared_updated.fee)
        self.assertRedirects(res, reverse("kakeibo:shared_detail", kwargs={"pk": shared_updated.pk}))

    def test_shared_delete(self):
        # ~~~~~~~~~~~~~~~~ prepare ~~~~~~~~~~~~~~~~
        data = {
            "date": "2021-06-01",
            "fee": 100,
            "usage": self.u_shopping,
            "memo": "test",
            "paid_by": self.user_takashi
        }
        shared = SharedKakeibo.objects.create(**data)
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:shared_delete", kwargs={"pk": shared.pk})
        self.assertEqual(f"/kakeibo/shared/{shared.pk}/delete", url)
        # ~~~~~~~~~~~~~~~~ get ~~~~~~~~~~~~~~~~
        self.client.get(url)
        self.assertTemplateUsed("shared_delete.html")
        # ~~~~~~~~~~~~~~~~ post ~~~~~~~~~~~~~~~~
        res = self.client.post(url)
        self.assertRedirects(res, reverse("kakeibo:shared_list"))
        self.assertEqual(SharedKakeibo.objects.all_active().count(), 0)