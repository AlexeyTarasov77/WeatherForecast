import logging

from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from forecast import client_errors as errors

from .client import get_forecast, get_geodata_by_city
from .search_history import History

logger = logging.getLogger(__name__)
if settings.DEBUG:
    logger.setLevel(logging.DEBUG)


@api_view(["GET"])
def get_forecast_view(request) -> Response:
    err_response = {"error": "Can't get forecast. Please try again later."}
    city_name = request.GET.get("city_name")
    forecast_days = int(request.GET.get("forecast_days", 7))
    if not city_name:
        return Response({"error": "city_name is required"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        try:
            geo_data = get_geodata_by_city(city_name)
        except errors.CoordinatesNotFoundError:
            logger.warning("get_forecast_view.CoordinatesNotFound")
            return Response(
                {"error": f"city with name {city_name} not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except errors.GettingCoordinatesError as e:
            logger.exception("get_forecast_view.GettingCoordinatesError: %s", e)
            return Response(
                {"error": f"Can't get coordinates for city {city_name}. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        forecast = get_forecast(geo_data, forecast_days=forecast_days)
    except errors.ForecastError as e:
        logger.exception("get_forecast_view.ForecastError: %s", e)
        return Response(err_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    History(request).add(city_name)
    return Response(forecast)


@api_view(["GET"])
def history_view(request) -> Response:
    return Response(History(request).history)
