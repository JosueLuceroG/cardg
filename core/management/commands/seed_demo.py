import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from categories.models import Category
from orders.models import Order
from payments.models import Payment
from products.models import Product
from tables.models import Table
from users.models import User

DEMO_USERS = [
    {
        "email": "admin@cardg.demo",
        "password": "Admin12345!",
        "username": "admin",
        "first_name": "Admin",
        "last_name": "CardG",
        "is_staff": True,
        "is_superuser": True,
    },
    {
        "email": "mesero@cardg.demo",
        "password": "Mesero12345!",
        "username": "mesero",
        "first_name": "Mesa",
        "last_name": "Demo",
        "is_staff": True,
        "is_superuser": False,
    },
    {
        "email": "cliente@cardg.demo",
        "password": "Cliente12345!",
        "username": "cliente",
        "first_name": "Cliente",
        "last_name": "Demo",
        "is_staff": False,
        "is_superuser": False,
    },
]

DEMO_CATEGORIES = [
    ("Entradas", "categories/entradas.jpg"),
    ("Sushi", "categories/sushi.jpg"),
    ("Bowls", "categories/bowls.jpg"),
    ("Hamburguesas", "categories/hamburguesas.jpg"),
    ("Bebidas", "categories/bebidas.jpg"),
    ("Postres", "categories/postres.jpg"),
]

DEMO_PRODUCTS = [
    ("Gajos de papa", "products/gajos.jpg", "89.00", True, "Entradas"),
    ("Roll clásico", "products/roll_clasico.jpg", "129.00", True, "Sushi"),
    ("Roll jumbo", "products/roll_jumbo.jpg", "159.00", True, "Sushi"),
    ("Bowl de salmón", "products/bowl_salmon.jpg", "149.00", True, "Bowls"),
    (
        "Hamburguesa clásica",
        "products/hamburguesa_clasica.jpg",
        "139.00",
        True,
        "Hamburguesas",
    ),
    (
        "Hamburguesa BBQ",
        "products/hamburguesa_clasica.jpg",
        "149.00",
        True,
        "Hamburguesas",
    ),
    ("Malteada de chocolate", "products/malteada.jpg", "59.00", True, "Bebidas"),
    ("Limonada de la casa", "products/limonada.jpg", "39.00", True, "Bebidas"),
    ("Brownie con helado", "products/brownie.jpg", "49.00", True, "Postres"),
    ("Roll de temporada", "products/roll_clasico.jpg", "139.00", False, "Sushi"),
]

DEMO_PAYMENTS = [
    {
        "key": "mesa_1",
        "table": 1,
        "totalPayment": "129.00",
        "paymentType": "CASH",
        "statusPayment": "PENDING",
    },
    {
        "key": "mesa_2",
        "table": 2,
        "totalPayment": "139.00",
        "paymentType": "CARD",
        "statusPayment": "PAID",
    },
    {
        "key": "mesa_4",
        "table": 4,
        "totalPayment": "89.00",
        "paymentType": "CASH",
        "statusPayment": "PAID",
    },
    {
        "key": "mesa_6",
        "table": 6,
        "totalPayment": "49.00",
        "paymentType": "CARD",
        "statusPayment": "PAID",
    },
]

DEMO_ORDERS = [
    {
        "table": 1,
        "product": "Roll clásico",
        "payment": "mesa_1",
        "status": "PENDING",
        "close": False,
    },
    {
        "table": 2,
        "product": "Hamburguesa clásica",
        "payment": "mesa_2",
        "status": "DELIVERED",
        "close": True,
    },
    {
        "table": 3,
        "product": "Bowl de salmón",
        "payment": None,
        "status": "PENDING",
        "close": False,
    },
    {
        "table": 4,
        "product": "Gajos de papa",
        "payment": "mesa_4",
        "status": "DELIVERED",
        "close": True,
    },
    {
        "table": 5,
        "product": "Malteada de chocolate",
        "payment": None,
        "status": "PENDING",
        "close": False,
    },
    {
        "table": 6,
        "product": "Brownie con helado",
        "payment": "mesa_6",
        "status": "DELIVERED",
        "close": True,
    },
]


class Command(BaseCommand):
    help = "Crea usuarios, carta, mesas, pedidos y pagos ficticios para la demo."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Elimina los datos de las apps antes de sembrar la demo.",
        )

    def handle(self, *args, **options):
        reset = options["reset"]
        if not reset and Category.objects.exists():
            raise CommandError(
                "La base ya contiene datos. Ejecuta seed_demo --reset en una base de demostración."
            )

        with transaction.atomic():
            if reset:
                self._reset_data()
            self._create_users()
            categories = self._create_categories()
            products = self._create_products(categories)
            tables = self._create_tables()
            payments = self._create_payments(tables)
            self._create_orders(tables, products, payments)

        self.stdout.write(self.style.SUCCESS("Demo de CardG creada correctamente."))
        self.stdout.write("")
        self.stdout.write("Credenciales de demostración:")
        for user in DEMO_USERS:
            self.stdout.write(f"  {user['email']} / {user['password']}")

    def _reset_data(self):
        Order.objects.all().delete()
        Payment.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        Table.objects.all().delete()
        User.objects.filter(email__in=[user["email"] for user in DEMO_USERS]).delete()

    def _create_users(self):
        for data in DEMO_USERS:
            password = data["password"]
            user = User.objects.filter(email=data["email"]).first()
            if user is None:
                user = User(email=data["email"])
            user.username = data["username"]
            user.first_name = data["first_name"]
            user.last_name = data["last_name"]
            user.is_staff = data["is_staff"]
            user.is_superuser = data["is_superuser"]
            user.is_active = True
            user.set_password(password)
            user.save()

    def _copy_asset(self, relative_path):
        source = Path(settings.BASE_DIR) / "demo_assets" / relative_path
        destination = Path(settings.MEDIA_ROOT) / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        return relative_path

    def _create_categories(self):
        categories = {}
        for title, image in DEMO_CATEGORIES:
            category, _ = Category.objects.update_or_create(
                title=title,
                defaults={"image": self._copy_asset(image)},
            )
            categories[title] = category
        return categories

    def _create_products(self, categories):
        products = {}
        for title, image, price, active, category_title in DEMO_PRODUCTS:
            product, _ = Product.objects.update_or_create(
                title=title,
                defaults={
                    "image": self._copy_asset(image),
                    "price": price,
                    "active": active,
                    "category": categories[category_title],
                },
            )
            products[title] = product
        return products

    def _create_tables(self):
        tables = {}
        for number in range(1, 9):
            table, _ = Table.objects.get_or_create(number=number)
            tables[number] = table
        return tables

    def _create_payments(self, tables):
        payments = {}
        for data in DEMO_PAYMENTS:
            payment, _ = Payment.objects.update_or_create(
                table=tables[data["table"]],
                statusPayment=data["statusPayment"],
                defaults={
                    "totalPayment": data["totalPayment"],
                    "paymentType": data["paymentType"],
                },
            )
            payments[data["key"]] = payment
        return payments

    def _create_orders(self, tables, products, payments):
        for data in DEMO_ORDERS:
            Order.objects.update_or_create(
                table=tables[data["table"]],
                product=products[data["product"]],
                defaults={
                    "payment": payments.get(data["payment"]),
                    "status": data["status"],
                    "close": data["close"],
                },
            )
