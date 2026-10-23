from django.contrib.auth.models import UserManager as DjangoUserManager


class UserManager(DjangoUserManager):
    """Create users with email as the login field and an auto-generated username."""

    def _create_user(self, username, email, password, **extra_fields):
        if not email:
            raise ValueError("El correo electrónico es obligatorio.")

        email = self.normalize_email(email)
        username = username or email.split("@", 1)[0]
        base_username = username
        counter = 1
        while self.model.objects.filter(username=username).exists():
            counter += 1
            username = f"{base_username}{counter}"

        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        username = extra_fields.pop("username", None)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Un superusuario debe tener is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Un superusuario debe tener is_superuser=True.")

        username = extra_fields.pop("username", None)
        return self._create_user(username, email, password, **extra_fields)
