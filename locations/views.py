from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, pagination

from .models import Prefecture, City
from .serializer import PrefectureSerializer, CitySerializer


class PrefectureViewSet(viewsets.ModelViewSet):
    queryset = Prefecture.objects.all()
    serializer_class = PrefectureSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    ordering_fields = ('id',)
    ordering = ('id',)
