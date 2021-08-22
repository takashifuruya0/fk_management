from django.test import TestCase
from kakeibo.models import Resource, Usage, SharedKakeibo, Budget, SharedResource, SharedTransaction
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

    #! ========================================
    #! SharedKakeibo
    #! ========================================
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

    def test_shared_create_source_path(self):
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
            "source_path": "/kakeibo/shared"
        }
        response = self.client.post(url, data)
        shared_created = SharedKakeibo.objects.last()
        # assert
        self.assertRedirects(response, data["source_path"])
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

    #! ========================================
    #! SharedResource
    #! ========================================
    def test_shared_resource_create_post(self):
        """
        SharedResouceCreate: Normal POST
        """
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:shared_resource_create")
        self.assertEqual("/kakeibo/shared/resource/create", url)
        # ~~~~~~~~~~~~~~~~ post ~~~~~~~~~~~~~~~~
        data = {
            "date_open": "2021-04-01",
            "val_goal": 100000,
            "detail": "t",
            "name": "貯金したい！！",
            "kind": "貯金",
        }
        response = self.client.post(url, data)
        shared_resource_created = SharedResource.objects.last()
        # assert
        self.assertRedirects(
            response, reverse("kakeibo:shared_resource_detail", kwargs={"pk": shared_resource_created.pk})
        )
        self.assertEqual(shared_resource_created.val_goal, data['val_goal'])
        self.assertEqual(SharedResource.objects.all().count(), 1)

    def test_shared_resource_create_post_source_path(self):
        """
        SharedResouceCreate: Normal POST, SourcePath
        """
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:shared_resource_create")
        self.assertEqual("/kakeibo/shared/resource/create", url)
        # ~~~~~~~~~~~~~~~~ post ~~~~~~~~~~~~~~~~
        data = {
            "date_open": "2021-04-01",
            "val_goal": 100000,
            "detail": "t",
            "name": "貯金したい！！",
            "kind": "貯金",
            "source_path": "/kakeibo/shared"
        }
        response = self.client.post(url, data)
        shared_resource_created = SharedResource.objects.last()
        # assert
        self.assertRedirects(response, data['source_path'])
        self.assertEqual(shared_resource_created.val_goal, data['val_goal'])
        self.assertEqual(SharedResource.objects.all().count(), 1)

    def test_shared_resource_create_post_exception(self):
        """
        SharedResouceCreate: Exception, POST, lack of necessary fields
        """
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:shared_resource_create")
        # ~~~~~~~~~~~~~~~~ post ~~~~~~~~~~~~~~~~
        data = {
            "date_open": "2021-04-01",
            "detail": "t",
            "kind": "貯金",
        }
        response = self.client.post(url, data)
        
        # assert
        self.assertEqual(SharedKakeibo.objects.all().count(), 0)

    def test_shared_resource_list_get(self):
        """
        SharedResouceList: Normal GET
        """
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:shared_resource_list")
        self.assertEqual("/kakeibo/shared/resource", url)
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        

    def test_shared_resource_update_post(self):
        """
        SharedResouceCreate: Normal POST
        """
        data = {
            "date_open": "2021-04-01",
            "val_goal": 100000,
            "detail": "t",
            "name": "貯金したい！！",
            "kind": "貯金",
        }
        sr = SharedResource.objects.create(**data)
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:shared_resource_update", kwargs={"pk": sr.pk})
        self.assertEqual(f"/kakeibo/shared/resource/{sr.pk}/edit", url)
        # ~~~~~~~~~~~~~~~~ post ~~~~~~~~~~~~~~~~
        data = {
            "date_open": "2021-04-01",
            "val_goal": 200000,
            "detail": "t",
            "name": "貯金したい",
            "kind": "貯金",
        }
        response = self.client.post(url, data)
        sr_updated = SharedResource.objects.get(pk=sr.pk)
        self.assertEqual(sr_updated.val_goal, data['val_goal'])
        self.assertRedirects(
            response, reverse('kakeibo:shared_resource_detail', kwargs={"pk": sr_updated.pk})
        )

    def test_shared_resource_update_post_exception(self):
        """
        SharedResouceCreate: Normal POST
        """
        data = {
            "date_open": "2021-04-01",
            "val_goal": 100000,
            "detail": "t",
            "name": "貯金",
            "kind": "貯金したい！！",
        }
        sr = SharedResource.objects.create(**data)
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:shared_resource_update", kwargs={"pk": sr.pk})
        self.assertEqual(f"/kakeibo/shared/resource/{sr.pk}/edit", url)
        # ~~~~~~~~~~~~~~~~ post ~~~~~~~~~~~~~~~~
        data = {
            "val_goal": 200000,
        }
        self.client.post(url, data)
        sr_updated = SharedResource.objects.get(pk=sr.pk)
        self.assertNotEqual(sr_updated.val_goal, data['val_goal'])

    def test_shared_resource_detail(self):
        """
        SharedResourceDetail: Normal GET
        """
        data = {
            "date_open": "2021-04-01",
            "val_goal": 100000,
            "detail": "t",
            "name": "貯金",
            "kind": "貯金したい！！",
        }
        sr = SharedResource.objects.create(**data)
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:shared_resource_detail", kwargs={"pk": sr.pk})
        self.assertEqual(f"/kakeibo/shared/resource/{sr.pk}", url)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "shared_resource_detail.html")

    def test_shared_resource_delete_get(self):
        """
        SharedResourceDelte: Normal GET
        """
        # ~~~~~~~~~~~~~~~~ prepare ~~~~~~~~~~~~~~~~
        d = {
            "date_open": "2021-04-01",
            "val_goal": 100000,
            "detail": "t",
            "name": "貯金",
            "kind": "貯金したい！！",
        }
        sr = SharedResource.objects.create(**d)
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:shared_resource_delete", kwargs={"pk": sr.pk})
        self.assertEqual(f"/kakeibo/shared/resource/{sr.pk}/delete", url)
        # ~~~~~~~~~~~~~~~~ get ~~~~~~~~~~~~~~~~
        res = self.client.get(url)
        self.assertTemplateUsed(res, "shared_resource_delete.html")

    def test_shared_resource_delete_get_exception(self):
        """
        SharedResourceDelte: Exception GET, Inactive
        """
        # ~~~~~~~~~~~~~~~~ prepare ~~~~~~~~~~~~~~~~
        d = {
            "date_open": "2021-04-01",
            "val_goal": 100000,
            "detail": "t",
            "name": "貯金",
            "kind": "貯金したい！！",
            "is_active": False,
        }
        sr = SharedResource.objects.create(**d)
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:shared_resource_delete", kwargs={"pk": sr.pk})
        # ~~~~~~~~~~~~~~~~ get ~~~~~~~~~~~~~~~~
        res = self.client.get(url)
        self.assertEqual(SharedResource.objects.all_active().count(), 0)
        self.assertRedirects(res, reverse("kakeibo:shared_top"))

    def test_shared_resource_delete_post(self):
        """
        SharedResourceDelte: Normal POST
        """
        # ~~~~~~~~~~~~~~~~ prepare ~~~~~~~~~~~~~~~~
        d = {
            "date_open": "2021-04-01",
            "val_goal": 100000,
            "detail": "t",
            "name": "貯金",
            "kind": "貯金したい！！",
        }
        sr = SharedResource.objects.create(**d)
        data = {
            "date": "2021-06-01",
            "val": 100,
            "memo": "test",
            "paid_by": self.user_takashi,
            "shared_resource": sr,
        }
        st = SharedTransaction.objects.create(**data)
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:shared_resource_delete", kwargs={"pk": sr.pk})
        # ~~~~~~~~~~~~~~~~ post ~~~~~~~~~~~~~~~~
        res = self.client.post(url)
        self.assertEqual(SharedTransaction.objects.all_active().count(), 0)
        self.assertEqual(SharedResource.objects.all_active().count(), 0)
        self.assertRedirects(res, reverse("kakeibo:shared_resource_list"))

    #! ========================================
    #! SharedTransaction
    #! ========================================
    def test_shared_transaction_detail(self):
        """
        SharedTransactionDetail: Normal GET
        """
        data = {
            "date_open": "2021-04-01",
            "val_goal": 100000,
            "detail": "t",
            "name": "貯金",
            "kind": "貯金したい！！",
        }
        sr = SharedResource.objects.create(**data)
        st = SharedTransaction.objects.create(
            shared_resource=sr, val=1000, date=date.today(), memo="", paid_by=self.user_hoko
        )
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:shared_transaction_detail", kwargs={"pk": sr.pk})
        self.assertEqual(f"/kakeibo/shared/transaction/{sr.pk}", url)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "shared_transaction_detail.html")

    def test_shared_transaction_update_get(self):
        """
        SharedTransactionUpdate: Normal GET
        """
        data = {
            "date_open": "2021-04-01",
            "val_goal": 100000,
            "detail": "t",
            "name": "貯金",
            "kind": "貯金したい！！",
        }
        sr = SharedResource.objects.create(**data)
        st = SharedTransaction.objects.create(
            shared_resource=sr, val=1000, date=date.today(), memo="", paid_by=self.user_hoko
        )
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:shared_transaction_update", kwargs={"pk": sr.pk})
        self.assertEqual(f"/kakeibo/shared/transaction/{sr.pk}/edit", url)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "shared_transaction_update.html")

    def test_shared_transaction_update_post(self):
        """
        SharedTransactionUpdate: Normal POST
        """
        data = {
            "date_open": "2021-04-01",
            "val_goal": 100000,
            "detail": "t",
            "name": "貯金",
            "kind": "貯金したい！！",
        }
        sr = SharedResource.objects.create(**data)
        st = SharedTransaction.objects.create(
            shared_resource=sr, val=1000, date=date.today(), memo="", paid_by=self.user_hoko
        )
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:shared_transaction_update", kwargs={"pk": st.pk})
        self.assertEqual(f"/kakeibo/shared/transaction/{st.pk}/edit", url)
        d = {
            "shared_resource": sr.pk, 
            "val": 2000, 
            "date": date.today(), 
            "memo": "", 
            "paid_by": self.user_hoko.pk,
        }
        response = self.client.post(url, data=d)
        self.assertRedirects(
            response, reverse("kakeibo:shared_resource_detail", kwargs={"pk": sr.pk}))
        st_updated = SharedTransaction.objects.get(pk=st.pk)
        self.assertEqual(st_updated.val, d['val'])


    def test_shared_transaction_update_post_exception(self):
        """
        SharedTransactionUpdate: Exception POST
        """
        data = {
            "date_open": "2021-04-01",
            "val_goal": 100000,
            "detail": "t",
            "name": "貯金",
            "kind": "貯金したい！！",
        }
        sr = SharedResource.objects.create(**data)
        st = SharedTransaction.objects.create(
            shared_resource=sr, val=1000, date=date.today(), memo="", paid_by=self.user_hoko
        )
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:shared_transaction_update", kwargs={"pk": st.pk})
        self.assertEqual(f"/kakeibo/shared/transaction/{st.pk}/edit", url)
        d = {
            "shared_resource": sr.pk, 
            "val": 2000, 
            "memo": "", 
            "paid_by": self.user_hoko.pk
        }
        response = self.client.post(url, data=d)
        st_updated = SharedTransaction.objects.get(pk=st.pk)
        self.assertNotEqual(st_updated.val, d['val'])


    def test_shared_transaction_create_get(self):
        """
        SharedTransactionCreate: Normal GET
        """
        data = {
            "date_open": "2021-04-01",
            "val_goal": 100000,
            "detail": "t",
            "name": "貯金",
            "kind": "貯金したい！！",
        }
        sr = SharedResource.objects.create(**data)
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:shared_transaction_create")
        self.assertEqual(f"/kakeibo/shared/transaction/create", url)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "shared_transaction_create.html")

    def test_shared_transaction_create_post(self):
        """
        SharedTransactionCreate: Normal POST
        """
        data = {
            "date_open": "2021-04-01",
            "val_goal": 100000,
            "detail": "t",
            "name": "貯金",
            "kind": "貯金したい！！",
        }
        sr = SharedResource.objects.create(**data)
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:shared_transaction_create")
        d = {
            "shared_resource": sr.pk, 
            "val": 2000, 
            "date": date.today(), 
            "memo": "", 
            "paid_by": self.user_hoko.pk,
        }
        response = self.client.post(url, data=d)
        st = SharedTransaction.objects.last()
        self.assertRedirects(
            response, 
            reverse("kakeibo:shared_resource_detail", kwargs={"pk": st.shared_resource.pk})
        )
        self.assertEqual(st.val, d['val'])


    def test_shared_transaction_create_post_exception(self):
        """
        SharedTransactionCreate: Exception POST
        """
        data = {
            "date_open": "2021-04-01",
            "val_goal": 100000,
            "detail": "t",
            "name": "貯金",
            "kind": "貯金したい！！",
        }
        sr = SharedResource.objects.create(**data)
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:shared_transaction_create")
        d = {
            "shared_resource": sr.pk, 
            "val": 2000, 
            "memo": "", 
            "paid_by": self.user_hoko.pk
        }
        response = self.client.post(url, data=d)
        self.assertEqual(SharedTransaction.objects.all().count(), 0)

    def test_shared_transaction_delete_get(self):
        """
        SharedTransactionDelte: Normal GET
        """
        # ~~~~~~~~~~~~~~~~ prepare ~~~~~~~~~~~~~~~~
        d = {
            "date_open": "2021-04-01",
            "val_goal": 100000,
            "detail": "t",
            "name": "貯金",
            "kind": "貯金したい！！",
        }
        sr = SharedResource.objects.create(**d)
        data = {
            "date": "2021-06-01",
            "val": 100,
            "memo": "test",
            "paid_by": self.user_takashi,
            "shared_resource": sr,
        }
        st = SharedTransaction.objects.create(**data)
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:shared_transaction_delete", kwargs={"pk": st.pk})
        self.assertEqual(f"/kakeibo/shared/transaction/{st.pk}/delete", url)
        # ~~~~~~~~~~~~~~~~ get ~~~~~~~~~~~~~~~~
        res = self.client.get(url)
        self.assertTemplateUsed(res, "shared_transaction_delete.html")

    def test_shared_transaction_delete_get_exception(self):
        """
        SharedTransactionDelte: Exception GET, Inactive
        """
        # ~~~~~~~~~~~~~~~~ prepare ~~~~~~~~~~~~~~~~
        d = {
            "date_open": "2021-04-01",
            "val_goal": 100000,
            "detail": "t",
            "name": "貯金",
            "kind": "貯金したい！！",
        }
        sr = SharedResource.objects.create(**d)
        data = {
            "date": "2021-06-01",
            "val": 100,
            "memo": "test",
            "paid_by": self.user_takashi,
            "shared_resource": sr,
            "is_active": False,
        }
        st = SharedTransaction.objects.create(**data)
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:shared_transaction_delete", kwargs={"pk": st.pk})
        # ~~~~~~~~~~~~~~~~ get ~~~~~~~~~~~~~~~~
        res = self.client.get(url)
        self.assertEqual(SharedResource.objects.all_active().count(), 1)
        self.assertRedirects(res, reverse("kakeibo:shared_top"))


    def test_shared_transaction_delete_post(self):
        """
        SharedTransactionDelte: Normal POST
        """
        # ~~~~~~~~~~~~~~~~ prepare ~~~~~~~~~~~~~~~~
        d = {
            "date_open": "2021-04-01",
            "val_goal": 100000,
            "detail": "t",
            "name": "貯金",
            "kind": "貯金したい！！",
        }
        sr = SharedResource.objects.create(**d)
        data = {
            "date": "2021-06-01",
            "val": 100,
            "memo": "test",
            "paid_by": self.user_takashi,
            "shared_resource": sr,
        }
        st = SharedTransaction.objects.create(**data)
        # ~~~~~~~~~~~~~~~~ url ~~~~~~~~~~~~~~~~
        url = reverse("kakeibo:shared_transaction_delete", kwargs={"pk": st.pk})
        # ~~~~~~~~~~~~~~~~ post ~~~~~~~~~~~~~~~~
        res = self.client.post(url)
        self.assertEqual(SharedTransaction.objects.all_active().count(), 0)
        self.assertEqual(SharedResource.objects.all_active().count(), 1)
        self.assertRedirects(res, reverse("kakeibo:shared_resource_detail", kwargs={"pk": sr.pk}))