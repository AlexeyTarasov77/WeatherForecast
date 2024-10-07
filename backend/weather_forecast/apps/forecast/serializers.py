from rest_framework import serializers

from forecast import models


class CitiesCountSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CitiesCount
        fields = ("name", "count")


class HistorySerializer(serializers.Serializer):
    city_name = serializers.CharField()


# class AmountSerializer(serializers.Serializer):
#     value = serializers.FloatField()
#     unit = serializers.CharField(allow_blank=True, required=False)


# class ForecastHourlySerializer(serializers.Serializer):
#     temp = AmountSerializer()
#     temp_feels_like = AmountSerializer()
#     rain = serializers.FloatField(required=False, allow_null=True)
#     precipitation_probability = AmountSerializer(required=False, allow_null=True)


# class ForecastDailySerializer(serializers.Serializer):
#     temp_min = AmountSerializer()
#     temp_max = AmountSerializer()
#     rain_sum = AmountSerializer()
#     precipitation_probability = AmountSerializer(required=False, allow_null=True)
#     hourly = serializers.DictField(child=ForecastHourlySerializer())


# class ForecastSerializer(serializers.Serializer):
#     dates = serializers.DictField(child=ForecastDailySerializer())
