from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet

from payments.api.serializers import PaymentSerializer
from payments.models import Payment


class PaymentApiViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = PaymentSerializer
    queryset = Payment.objects.select_related("table").order_by("-created_at")
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["table", "statusPayment"]
    ordering_fields = "__all__"
