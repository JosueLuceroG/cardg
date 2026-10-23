from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from payments.models import Payment
from tables.models import Table
from users.models import User


class PaymentApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.staff = User.objects.create_user(
            email="staff@example.com",
            password="StaffPass123!",
            is_staff=True,
        )
        self.table = Table.objects.create(number=1)
        self.payment = Payment.objects.create(
            table=self.table,
            totalPayment="129.00",
            paymentType="CARD",
            statusPayment="PAID",
        )

    def test_list_is_public(self):
        response = self.client.get(reverse("payments-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["statusPayment"], "PAID")

    def test_filter_by_status(self):
        response = self.client.get(
            reverse("payments-list"),
            {"statusPayment": "PAID"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_create_requires_authentication(self):
        response = self.client.post(
            reverse("payments-list"),
            {
                "table": self.table.pk,
                "totalPayment": "89.00",
                "paymentType": "CASH",
                "statusPayment": "PENDING",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 401)

    def test_authenticated_user_can_create_payment(self):
        self.client.force_authenticate(user=self.staff)

        response = self.client.post(
            reverse("payments-list"),
            {
                "table": self.table.pk,
                "totalPayment": "89.00",
                "paymentType": "CASH",
                "statusPayment": "PENDING",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Payment.objects.count(), 2)
        self.assertEqual(response.data["table_data"]["number"], 1)

    def test_payment_can_have_no_table(self):
        self.client.force_authenticate(user=self.staff)

        response = self.client.post(
            reverse("payments-list"),
            {
                "totalPayment": "10.00",
                "paymentType": "CASH",
                "statusPayment": "PENDING",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertIsNone(response.data["table"])

    def test_authenticated_user_can_update_payment(self):
        self.client.force_authenticate(user=self.staff)

        response = self.client.patch(
            reverse("payments-detail", args=[self.payment.pk]),
            {"statusPayment": "PENDING"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.statusPayment, "PENDING")

    def test_authenticated_user_can_delete_payment(self):
        self.client.force_authenticate(user=self.staff)

        response = self.client.delete(
            reverse("payments-detail", args=[self.payment.pk])
        )

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Payment.objects.filter(pk=self.payment.pk).exists())

    def test_str_returns_table_number(self):
        self.assertEqual(str(self.payment), "1")
