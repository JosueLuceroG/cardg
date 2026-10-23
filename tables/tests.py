from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from tables.models import Table
from users.models import User


class TableApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.staff = User.objects.create_user(
            email="staff@example.com",
            password="StaffPass123!",
            is_staff=True,
        )
        self.table_two = Table.objects.create(number=2)
        self.table_one = Table.objects.create(number=1)

    def test_list_is_public_and_ordered_by_number(self):
        response = self.client.get(reverse("tables-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["number"] for item in response.data], [1, 2])

    def test_filter_by_number(self):
        response = self.client.get(reverse("tables-list"), {"number": 2})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["number"], 2)

    def test_create_requires_authentication(self):
        response = self.client.post(
            reverse("tables-list"),
            {"number": 3},
            format="json",
        )

        self.assertEqual(response.status_code, 401)

    def test_staff_can_create_table(self):
        self.client.force_authenticate(user=self.staff)

        response = self.client.post(
            reverse("tables-list"),
            {"number": 3},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(Table.objects.filter(number=3).exists())

    def test_duplicate_number_is_rejected(self):
        self.client.force_authenticate(user=self.staff)

        response = self.client.post(
            reverse("tables-list"),
            {"number": 1},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("number", response.data)

    def test_str_returns_number(self):
        self.assertEqual(str(self.table_one), "1")
