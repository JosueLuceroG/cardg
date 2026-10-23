from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet

from orders.api.serializers import OrderSerializer
from orders.models import Order


class OrderApiViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = OrderSerializer
    queryset = Order.objects.select_related("table", "product", "payment").order_by(
        "-created_at"
    )
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["table", "status", "payment", "close"]
    ordering_fields = "__all__"
