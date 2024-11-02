from dataclasses import asdict
from datetime import datetime

from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from forecast import api_client
from forecast import dependecies as deps
from forecast import serializers as s
from forecast.domain import service as sv
from forecast.models import CitiesCount
from forecast.search_history import SearchHistory

logger = deps.get_logger(__name__)


@api_view()
def daily_forecast_view(request: Request) -> Response:
    service = deps.get_forecast_service()
    location = request.query_params.get("location")
    lat, lon = request.query_params.get("lat"), request.query_params.get("lon")
    coords = sv.Coords(lat, lon) if lat and lon else None
    duration_days = int(request.query_params.get("duration_days", 7))
    if not location and not coords:
        return Response(
            {"error": "Either city_name or coords must be provided"}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        forecast, city = service.get_daily_forecast(
            duration_days, SearchHistory(request), location, coords
        )
    except api_client.CoordinatesNotFoundError:
        return Response(
            {"error": f"Unknown city with name {location}. Can't found coordinates."},
            status=status.HTTP_404_NOT_FOUND,
        )
    except api_client.GettingCoordinatesError:
        return Response(
            {"error": f"Can't get coordinates for city {location}. Please try again later."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except sv.ForecastServiceError as e:
        logger.exception("get_forecast_view: %s", e)
        msg = e.args[0] if len(e.args) > 0 else "Can't get forecast. Please try again later."
        return Response({"error": msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response({"forecast": forecast, "location": city})


@api_view()
def hourly_forecast_view(request: Request, date: str) -> Response:
    service = deps.get_forecast_service()
    location = request.query_params.get("location")
    lat, lon = request.query_params.get("lat"), request.query_params.get("lon")
    raw_date = date
    try:
        date = datetime.fromisoformat(date)
    except ValueError:
        logger.error("Incorrect date format: %s", raw_date)
        return Response(
            {"error": "Incorrect date format. Expected format: YYYY-MM-DDTHH:MM"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    coords = sv.Coords(lat, lon) if lat and lon else None
    if not location and not coords:
        return Response(
            {"error": "Either city_name or coords must be provided"}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        forecast, city = service.get_hourly_forecast_for_date(date, location, coords)
    except api_client.CoordinatesNotFoundError:
        return Response(
            {"error": f"Unknown city with name {location}. Can't found coordinates."},
            status=status.HTTP_404_NOT_FOUND,
        )
    except api_client.GettingCoordinatesError:
        return Response(
            {"error": f"Can't get coordinates for city {location}. Please try again later."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except sv.ForecastServiceError as e:
        logger.exception("get_forecast_view: %s", e)
        msg = e.args[0] if len(e.args) > 0 else "Can't get forecast. Please try again later."
        return Response({"error": msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response({"forecast": forecast, "location": city, "date": raw_date})


class CitiesCountView(generics.ListAPIView):
    serializer_class = s.CitiesCountSerializer
    service = deps.get_forecast_service()

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


@api_view()
def last_viewed_city_view(request) -> Response:
    service = deps.get_forecast_service()
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
