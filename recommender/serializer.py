from rest_framework import serializers
from .models import Spot, SpotImage


class SpotImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpotImage
        fields = ('url', 'license', 'height', 'width', 'owner', 'owner_name')


class SpotSerializer(serializers.ModelSerializer):
    # spotimage_set = SpotImageSerializer(read_only=True, many=True)

    class Meta:
        model = Spot
        fields = ('id', 'title', 'url')
        ordering_fields = ('count', '-count',)
        ordering = ('-count',)
