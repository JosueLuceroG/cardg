from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render

from categories.models import Category
from orders.models import Order
from payments.models import Payment
from products.models import Product
from tables.models import Table

API_VERSION = "2.0.0"


def home(request):
    context = {
        "version": API_VERSION,
        "category_count": Category.objects.count(),
        "product_count": Product.objects.count(),
        "table_count": Table.objects.count(),
        "order_count": Order.objects.count(),
        "payment_count": Payment.objects.count(),
    }
    return render(request, "icard/home.html", context)


def api_index(request):
    return JsonResponse(
        {
            "service": "cardg-api",
            "version": API_VERSION,
            "docs": request.build_absolute_uri("/docs/"),
            "redoc": request.build_absolute_uri("/redoc/"),
            "schema": request.build_absolute_uri("/api/schema/"),
            "health": request.build_absolute_uri("/api/health/"),
            "endpoints": {
                "login": request.build_absolute_uri("/api/auth/login/"),
                "refresh": request.build_absolute_uri("/api/auth/refresh/"),
                "me": request.build_absolute_uri("/api/auth/me/"),
                "users": request.build_absolute_uri("/api/users/"),
                "categories": request.build_absolute_uri("/api/categories/"),
                "products": request.build_absolute_uri("/api/products/"),
                "tables": request.build_absolute_uri("/api/tables/"),
                "orders": request.build_absolute_uri("/api/orders/"),
                "payments": request.build_absolute_uri("/api/payments/"),
            },
        }
    )


def health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        database_status = "ok"
    except Exception:
        database_status = "error"

    healthy = database_status == "ok"
    return JsonResponse(
        {
            "status": "ok" if healthy else "degraded",
            "database": database_status,
            "service": "cardg-api",
            "version": API_VERSION,
        },
        status=200 if healthy else 503,
    )
