from rest_framework import serializers

from forecast import models


class CitiesCountSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CitiesCount
        fields = ("name", "count")


class HistorySerializer(serializers.Serializer):
    city_name = serializers.CharField()
