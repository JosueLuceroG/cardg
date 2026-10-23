from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from categories.api.router import router_category
from icard.views import api_index, health, home
from orders.api.router import router_orders
from payments.api.router import router_payments
from products.api.router import router_product
from tables.api.router import router_table
from users.api.router import router_user

urlpatterns = [
    path("", home, name="home"),
    path("api/", api_index, name="api-index"),
    path("api/health/", health, name="health"),
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    path("api/", include("users.api.router")),
    path("api/", include(router_user.urls)),
    path("api/", include(router_category.urls)),
    path("api/", include(router_product.urls)),
    path("api/", include(router_table.urls)),
    path("api/", include(router_orders.urls)),
    path("api/", include(router_payments.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
