from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, pagination

from .models import Spot
from .serializer import SpotSerializer


class SpotSetPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class SpotViewSet(viewsets.ModelViewSet):
    queryset = Spot.objects.all()
    serializer_class = SpotSerializer
    pagination_class = SpotSetPagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('city',)
    ordering_fields = ('count',)
    ordering = ('-count',)
