import tempfile

from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from categories.models import Category
from core.test_utils import image_upload
from users.models import User


class CategoryApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.staff = User.objects.create_user(
            email="staff@example.com",
            password="StaffPass123!",
            is_staff=True,
        )
        self.category = Category.objects.create(
            title="Entradas",
            image="categories/test.jpg",
        )

    def test_list_is_public(self):
        response = self.client.get(reverse("categories-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Entradas")

    def test_create_requires_authentication(self):
        response = self.client.post(
            reverse("categories-list"),
            {"title": "Postres", "image": image_upload()},
            format="multipart",
        )

        self.assertEqual(response.status_code, 401)

    def test_staff_can_create_category(self):
        self.client.force_authenticate(user=self.staff)
        media = tempfile.TemporaryDirectory()
        self.addCleanup(media.cleanup)

        with override_settings(MEDIA_ROOT=media.name):
            response = self.client.post(
                reverse("categories-list"),
                {"title": "Postres", "image": image_upload("postres.png")},
                format="multipart",
            )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Category.objects.count(), 2)
        self.assertIn("/uploads/categories/", response.data["image"])

    def test_staff_can_update_category(self):
        self.client.force_authenticate(user=self.staff)

        response = self.client.patch(
            reverse("categories-detail", args=[self.category.pk]),
            {"title": "Entradas frías"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.category.refresh_from_db()
        self.assertEqual(self.category.title, "Entradas frías")

    def test_staff_can_delete_category(self):
        self.client.force_authenticate(user=self.staff)

        response = self.client.delete(
            reverse("categories-detail", args=[self.category.pk])
        )

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Category.objects.filter(pk=self.category.pk).exists())

    def test_str_returns_title(self):
        self.assertEqual(str(self.category), "Entradas")
