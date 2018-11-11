from rest_framework import serializers, pagination
from .models import Spot, SpotImage


class SpotImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpotImage
        fields = ('url', 'license', 'height', 'width', 'owner', 'owner_name')


class SpotSerializer(serializers.ModelSerializer):
    # city = Serializer()
    # image = serializers.SerializerMethodField()
    # image = SpotImageSerializer(many=True, read_only=True)

    # def get_image(self, instance):
    #     return SpotImageSerializer(instance.spotimage_set.first()).data
    spotimage_set = SpotImageSerializer(read_only=True, many=True)

    class Meta:
        model = Spot
        # fields = ('id', 'base_id', 'title', 'url', 'city')
        fields = ('id', 'title', 'url', 'spotimage_set')
        ordering_fields = ('count', '-count',)
        ordering = ('-count',)
