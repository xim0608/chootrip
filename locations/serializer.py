from rest_framework import serializers
from .models import Prefecture, City


class PrefectureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prefecture
        fields = ('id', 'name')


class CitySerializer(serializers.ModelSerializer):
    spot_count = serializers.SerializerMethodField()

    class Meta:
        model = City
        fields = ('id', 'name', 'spot_count')

    def get_spot_count(self, obj):
        return obj.spot_set.filter(count__gte=15).count()
