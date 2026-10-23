from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet

from tables.api.serializers import TableSerializer
from tables.models import Table


class TableApiViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = TableSerializer
    queryset = Table.objects.order_by("number")
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["number"]
