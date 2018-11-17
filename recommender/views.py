from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as dfr_filters
from rest_framework import viewsets, filters, pagination

from .models import Spot
from .serializer import SpotSerializer


class SpotSetPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class SpotSearchFilter(dfr_filters.FilterSet):
    title = dfr_filters.CharFilter(name="title", lookup_expr='contains')

    class Meta:
        model = Spot
        fields = ['title']


class SpotViewSet(viewsets.ModelViewSet):
    queryset = Spot.objects.filter(count__gte=15)
    serializer_class = SpotSerializer
    # pagination_class = SpotSetPagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter)
    filter_fields = ('city', 'id', 'title')
    filterset_fields = {
        'city': ('exact', 'in'),
        'id': ('exact',),
        'title': ('icontains',),
    }
    ordering_fields = ('count',)
    ordering = ('-count',)
