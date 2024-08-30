import logging

from django.conf import settings
from rest_framework import generics, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from forecast import api_client
from forecast import repositories as repos
from forecast import serializers as s
from forecast import service as sv
from forecast.models import CitiesCount
from forecast.search_history import SearchHistory

logger = logging.getLogger(__name__)
if settings.DEBUG:
    logger.setLevel(logging.DEBUG)


def _get_forecast_service() -> sv.ForecastService:
    repo = repos.CitiesCountRepository()
    client = api_client.OpenMeteoApiClient()
    return sv.ForecastService(repo=repo, logger=logger, api_client=client)


@api_view(["GET"])
def forecast_view(request) -> Response:
    service = _get_forecast_service()
    err_response = {"error": "Can't get forecast. Please try again later."}
    city_name = request.GET.get("city_name")
    lat, lon = request.GET.get("lat"), request.GET.get("lon")
    coords = {"latitude": lat, "longitude": lon} if lat and lon else None
    forecast_days = int(request.GET.get("forecast_days", 7))
    if not city_name and not coords:
        return Response(
            {"error": "Either city_name or coords must be provided"}, status=status.HTTP_400_BAD_REQUEST
        )
    if coords is None:
        return Response(
            {"error": "Invalid coords, (should be provided both lat and lon)."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        forecast, city = service.get_forecast(forecast_days, SearchHistory(request), city_name, coords)
    except api_client.CoordinatesNotFoundError:
        return Response(
            {"error": f"city with name {city_name} not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except api_client.GettingCoordinatesError:
        return Response(
            {"error": f"Can't get coordinates for city {city_name}. Please try again later."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except (api_client.ForecastApiError, Exception) as e:
        logger.exception("get_forecast_view: %s", e)
        return Response(err_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response({**forecast, "city": city})


class CitiesCountView(generics.ListAPIView):
    serializer_class = s.CitiesCountSerializer
    service = _get_forecast_service()

    def get_queryset(self) -> Response | list[CitiesCount]:
        try:
            res = self.service.get_cities_count()
        except Exception as e:
            logger.exception("cities_count_view: %s", e)
            return Response(
                {"error": "Can't get cities count. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return res


cities_count_view = CitiesCountView.as_view()


class HistoryView(generics.ListAPIView):
    serializer_class = s.HistorySerializer

    def get_queryset(self) -> list[str]:
        return list(SearchHistory(self.request))


history_view = HistoryView.as_view()


@api_view(["GET"])
def last_viewed_city_view(request) -> Response:
    service = _get_forecast_service()
    try:
        res = service.get_last_viewed_city(SearchHistory(request))
    except sv.NotFoundError:
        return Response({"last_viewed_city": ""}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.exception("last_viewed_city: %s", e)
        return Response(
            {"error": "Can't get last viewed city. Please try again later."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    return Response({"last_viewed_city": res})
