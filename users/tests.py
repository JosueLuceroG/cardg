from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from users.models import User


class UserApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            email="admin@example.com",
            password="AdminPass123!",
        )
        self.user = User.objects.create_user(
            email="user@example.com",
            password="UserPass123!",
        )

    def authenticate(self, user=None):
        user = user or self.admin
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"email": user.email, "password": "AdminPass123!" if user == self.admin else "UserPass123!"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def test_login_returns_access_and_refresh_tokens(self):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"email": self.user.email, "password": "UserPass123!"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_refresh_returns_new_access_token(self):
        login = self.client.post(
            reverse("token_obtain_pair"),
            {"email": self.user.email, "password": "UserPass123!"},
            format="json",
        )

        response = self.client.post(
            reverse("token_refresh"),
            {"refresh": login.data["refresh"]},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)

    def test_login_rejects_wrong_password(self):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"email": self.user.email, "password": "wrong-password"},
            format="json",
        )

        self.assertEqual(response.status_code, 401)

    def test_me_requires_authentication(self):
        response = self.client.get(reverse("user-me"))

        self.assertEqual(response.status_code, 401)

    def test_me_returns_profile_without_password(self):
        self.authenticate(self.user)

        response = self.client.get(reverse("user-me"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertNotIn("password", response.data)

    def test_non_admin_cannot_list_users(self):
        self.authenticate(self.user)

        response = self.client.get(reverse("users-list"))

        self.assertEqual(response.status_code, 403)

    def test_admin_can_create_user_with_hashed_password(self):
        self.authenticate()

        response = self.client.post(
            reverse("users-list"),
            {
                "email": "nuevo@example.com",
                "first_name": "Nuevo",
                "last_name": "Usuario",
                "password": "NuevoPass123!",
                "is_staff": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertNotIn("password", response.data)
        created = User.objects.get(email="nuevo@example.com")
        self.assertTrue(created.check_password("NuevoPass123!"))
        self.assertTrue(created.is_staff)
        self.assertEqual(created.username, "nuevo")

    def test_admin_cannot_create_user_without_password(self):
        self.authenticate()

        response = self.client.post(
            reverse("users-list"),
            {"email": "sin-clave@example.com"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("password", response.data)

    def test_admin_cannot_create_user_with_weak_password(self):
        self.authenticate()

        response = self.client.post(
            reverse("users-list"),
            {"email": "debil@example.com", "password": "12345678"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("password", response.data)

    def test_admin_cannot_create_duplicate_email(self):
        self.authenticate()

        response = self.client.post(
            reverse("users-list"),
            {"email": self.user.email, "password": "AnotherPass123!"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.data)

    def test_admin_can_update_profile_without_changing_password(self):
        self.authenticate()

        response = self.client.patch(
            reverse("users-detail", args=[self.user.pk]),
            {"first_name": "Actualizado"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Actualizado")
        self.assertTrue(self.user.check_password("UserPass123!"))

    def test_admin_can_change_password(self):
        self.authenticate()

        response = self.client.patch(
            reverse("users-detail", args=[self.user.pk]),
            {"password": "NuevaClave123!"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NuevaClave123!"))
        self.assertFalse(self.user.check_password("UserPass123!"))

    def test_manager_generates_unique_usernames(self):
        first = User.objects.create_user(email="ana@one.test", password="AnaPass123!")
        second = User.objects.create_user(email="ana@two.test", password="AnaPass123!")

        self.assertEqual(first.username, "ana")
        self.assertEqual(second.username, "ana2")

    def test_create_superuser_sets_flags_and_hashes_password(self):
        user = User.objects.create_superuser(
            email="super@example.com",
            password="SuperPass123!",
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password("SuperPass123!"))
        self.assertEqual(str(user), "super@example.com")

    def test_create_user_requires_email(self):
        with self.assertRaisesMessage(ValueError, "correo electrónico"):
            User.objects.create_user(email="", password="SomePass123!")
