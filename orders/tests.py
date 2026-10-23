from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from categories.models import Category
from orders.models import Order
from payments.models import Payment
from products.models import Product
from tables.models import Table
from users.models import User


class OrderApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.staff = User.objects.create_user(
            email="staff@example.com",
            password="StaffPass123!",
            is_staff=True,
        )
        self.category = Category.objects.create(
            title="Sushi",
            image="categories/sushi.jpg",
        )
        self.product = Product.objects.create(
            title="Roll clásico",
            image="products/roll_clasico.jpg",
            price="129.00",
            active=True,
            category=self.category,
        )
        self.table = Table.objects.create(number=1)
        self.payment = Payment.objects.create(
            table=self.table,
            totalPayment="129.00",
            paymentType="CASH",
            statusPayment="PENDING",
        )
        self.order = Order.objects.create(
            table=self.table,
            product=self.product,
            payment=self.payment,
            status="PENDING",
            close=False,
        )

    def test_list_is_public(self):
        response = self.client.get(reverse("orders-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["status"], "PENDING")

    def test_filter_by_status(self):
        response = self.client.get(reverse("orders-list"), {"status": "PENDING"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_filter_by_close(self):
        response = self.client.get(reverse("orders-list"), {"close": "false"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_filter_by_table(self):
        response = self.client.get(
            reverse("orders-list"),
            {"table": self.table.pk},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_create_requires_authentication(self):
        response = self.client.post(
            reverse("orders-list"),
            {
                "status": "DELIVERED",
                "table": self.table.pk,
                "product": self.product.pk,
                "payment": self.payment.pk,
                "close": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 401)

    def test_authenticated_user_can_create_order(self):
        self.client.force_authenticate(user=self.staff)

        response = self.client.post(
            reverse("orders-list"),
            {
                "status": "DELIVERED",
                "table": self.table.pk,
                "product": self.product.pk,
                "payment": self.payment.pk,
                "close": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Order.objects.count(), 2)
        self.assertEqual(response.data["product_data"]["title"], "Roll clásico")
        self.assertEqual(response.data["table_data"]["number"], 1)

    def test_authenticated_user_can_update_order(self):
        self.client.force_authenticate(user=self.staff)

        response = self.client.patch(
            reverse("orders-detail", args=[self.order.pk]),
            {"close": True},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertTrue(self.order.close)

    def test_authenticated_user_can_delete_order(self):
        self.client.force_authenticate(user=self.staff)

        response = self.client.delete(
            reverse("orders-detail", args=[self.order.pk])
        )

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Order.objects.filter(pk=self.order.pk).exists())

    def test_str_returns_table_number(self):
        self.assertEqual(str(self.order), "1")
