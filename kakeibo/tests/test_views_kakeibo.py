from django.test import TestCase
from kakeibo.models import Resource, Usage, Kakeibo, Event, SharedKakeibo, Budget, Exchange
from datetime import date
from django.contrib.auth import get_user_model
from dateutil.relativedelta import relativedelta
from django.shortcuts import reverse
# Create your tests here.


class KakeiboViewTest(TestCase):

    def setUp(self) -> None:
        # user
        self.user = get_user_model().objects.create(username="admin", password="test", is_superuser=True, is_staff=True)
        # data
        self.r_wallet = Resource.objects.create(name="wallet", is_investment=False)
        self.r_saving = Resource.objects.create(name="saving", is_investment=False)
        self.r_other = Resource.objects.create(name="other", is_investment=False)
        self.w_transfer = "振替"
        self.w_pay = "支出（現金）"
        self.u_shopping = Usage.objects.create(name="shopping", is_expense=True)
        self.u_transer = Usage.objects.create(name="transfer", is_expense=False)
        # lgoin
        self.client.force_login(self.user)

    # def test_kakeibo_create(self):
    #     pass

    def test_create_event(self):
        # url
        url = reverse("kakeibo:event_create")
        self.assertEqual("/kakeibo/event/create", url)
        # post
        response = self.client.post(url, {
            "date": "2021-04-01",
            "name": "t",
            "memo": "t",
            "detail": "t",
            "sum_plan": 10000,
            "is_closed": False
        })
        # "date", "name", "memo", "detail", 'sum_plan', "is_closed"
        event_created = Event.objects.last()
        self.assertRedirects(response, reverse("kakeibo:event_detail", kwargs={"pk": event_created.pk}))
        self.assertEqual(1, Event.objects.all().count())
        # redirect
        self.assertRedirects(response, reverse("kakeibo:event_detail", kwargs={"pk": event_created.pk}))

