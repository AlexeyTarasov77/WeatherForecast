import logging

from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from forecast import api_client
from forecast import repositories as repos
from forecast.search_history import SearchHistory
from forecast.service import ForecastService

logger = logging.getLogger(__name__)
if settings.DEBUG:
    logger.setLevel(logging.DEBUG)


def _get_forecast_service() -> ForecastService:
    repo = repos.CitiesCountRepository()
    client = api_client.OpenMeteoApiClient()
    return ForecastService(repo=repo, logger=logger, api_client=client)


@api_view(["GET"])
def get_forecast_view(request) -> Response:
    service = _get_forecast_service()
    err_response = {"error": "Can't get forecast. Please try again later."}
    city_name = request.GET.get("city_name")
    forecast_days = int(request.GET.get("forecast_days", 7))
    if not city_name:
        return Response({"error": "city_name is required"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        forecast = service.get_forecast(city_name, forecast_days, SearchHistory(request))
    except api_client.CoordinatesNotFoundError:
        return Response(
            {"error": f"city with name {city_name} not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except api_client.GettingCoordinatesError:
        return Response(
            {"error": f"Can't get coordinates for city {city_name}. Please try again later."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except api_client.ForecastApiError:
        return Response(err_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        logger.exception("get_forecast_view: %s", e)
        return Response(err_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(forecast)


@api_view(["GET"])
def history_view(request) -> Response:
    return Response(SearchHistory(request).history)
