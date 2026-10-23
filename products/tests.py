import tempfile

from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from categories.models import Category
from core.test_utils import image_upload
from products.models import Product
from users.models import User


class ProductApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.staff = User.objects.create_user(
            email="staff@example.com",
            password="StaffPass123!",
            is_staff=True,
        )
        self.entradas = Category.objects.create(
            title="Entradas",
            image="categories/entradas.jpg",
        )
        self.postres = Category.objects.create(
            title="Postres",
            image="categories/postres.jpg",
        )
        self.active_product = Product.objects.create(
            title="Gajos de papa",
            image="products/gajos.jpg",
            price="89.00",
            active=True,
            category=self.entradas,
        )
        self.inactive_product = Product.objects.create(
            title="Brownie",
            image="products/brownie.jpg",
            price="49.00",
            active=False,
            category=self.postres,
        )

    def test_list_is_public(self):
        response = self.client.get(reverse("products-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_filter_by_active(self):
        response = self.client.get(reverse("products-list"), {"active": "true"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Gajos de papa")

    def test_filter_by_category(self):
        response = self.client.get(
            reverse("products-list"),
            {"category": self.postres.pk},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Brownie")

    def test_create_requires_authentication(self):
        response = self.client.post(
            reverse("products-list"),
            {
                "title": "Limonada",
                "image": image_upload(),
                "price": "39.00",
                "active": True,
                "category": self.entradas.pk,
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, 401)

    def test_staff_can_create_product(self):
        self.client.force_authenticate(user=self.staff)
        media = tempfile.TemporaryDirectory()
        self.addCleanup(media.cleanup)

        with override_settings(MEDIA_ROOT=media.name):
            response = self.client.post(
                reverse("products-list"),
                {
                    "title": "Limonada",
                    "image": image_upload("limonada.png"),
                    "price": "39.00",
                    "active": True,
                    "category": self.entradas.pk,
                },
                format="multipart",
            )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Product.objects.count(), 3)
        self.assertEqual(response.data["category"], self.entradas.pk)
        self.assertIn("/uploads/products/", response.data["image"])

    def test_staff_can_update_product(self):
        self.client.force_authenticate(user=self.staff)

        response = self.client.patch(
            reverse("products-detail", args=[self.active_product.pk]),
            {"price": "99.00"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.active_product.refresh_from_db()
        self.assertEqual(str(self.active_product.price), "99.00")

    def test_str_returns_title(self):
        self.assertEqual(str(self.active_product), "Gajos de papa")
