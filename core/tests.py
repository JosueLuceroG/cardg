import tempfile
from io import StringIO
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from categories.models import Category
from orders.models import Order
from payments.models import Payment
from products.models import Product
from tables.models import Table
from users.models import User


class PublicViewsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(
            title="Entradas",
            image="categories/entradas.jpg",
        )
        self.product = Product.objects.create(
            title="Gajos de papa",
            image="products/gajos.jpg",
            price="89.00",
            active=True,
            category=self.category,
        )
        self.table = Table.objects.create(number=1)
        self.payment = Payment.objects.create(
            table=self.table,
            totalPayment="89.00",
            paymentType="CASH",
            statusPayment="PAID",
        )
        Order.objects.create(
            table=self.table,
            product=self.product,
            payment=self.payment,
            status="DELIVERED",
            close=True,
        )

    def test_home_renders_demo_summary(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "CardG API")
        self.assertContains(response, "Demo pública")

    def test_health_reports_database_status(self):
        response = self.client.get(reverse("health"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
        self.assertEqual(response.json()["database"], "ok")

    def test_api_index_lists_main_endpoints(self):
        response = self.client.get(reverse("api-index"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["service"], "cardg-api")
        self.assertIn("categories", response.json()["endpoints"])
        self.assertIn("refresh", response.json()["endpoints"])

    def test_openapi_schema_is_available(self):
        response = self.client.get(reverse("schema"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("CardG API", response.content.decode())

    def test_swagger_ui_is_available(self):
        response = self.client.get(reverse("swagger-ui"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("swagger", response.content.decode().lower())


class SeedDemoCommandTests(TestCase):
    def setUp(self):
        self.media = tempfile.TemporaryDirectory()
        self.addCleanup(self.media.cleanup)
        self.override = override_settings(MEDIA_ROOT=self.media.name)
        self.override.enable()
        self.addCleanup(self.override.disable)
        self.output = StringIO()

    def seed(self):
        call_command("seed_demo", "--reset", stdout=self.output, verbosity=0)

    def test_seed_creates_fictitious_demo_data(self):
        self.seed()

        self.assertEqual(Category.objects.count(), 6)
        self.assertEqual(Product.objects.count(), 10)
        self.assertEqual(Table.objects.count(), 8)
        self.assertEqual(Order.objects.count(), 6)
        self.assertEqual(Payment.objects.count(), 4)
        self.assertEqual(User.objects.count(), 3)
        self.assertTrue(
            all(user.email.endswith("@cardg.demo") for user in User.objects.all())
        )
        self.assertEqual(Product.objects.filter(active=False).count(), 1)
        self.assertTrue(
            (Path(settings.MEDIA_ROOT) / "categories" / "sushi.jpg").exists()
        )
        self.assertTrue(
            (Path(settings.MEDIA_ROOT) / "products" / "roll_clasico.jpg").exists()
        )

    def test_seed_is_idempotent_with_reset(self):
        self.seed()
        first_counts = (
            Category.objects.count(),
            Product.objects.count(),
            Table.objects.count(),
            Order.objects.count(),
            Payment.objects.count(),
            User.objects.count(),
        )

        self.seed()
        second_counts = (
            Category.objects.count(),
            Product.objects.count(),
            Table.objects.count(),
            Order.objects.count(),
            Payment.objects.count(),
            User.objects.count(),
        )

        self.assertEqual(first_counts, second_counts)

    def test_demo_admin_can_login(self):
        self.seed()
        client = APIClient()

        response = client.post(
            reverse("token_obtain_pair"),
            {"email": "admin@cardg.demo", "password": "Admin12345!"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)

    def test_seed_refuses_to_overwrite_non_demo_data_without_reset(self):
        self.seed()

        with self.assertRaises(CommandError):
            call_command("seed_demo", stdout=self.output, verbosity=0)
