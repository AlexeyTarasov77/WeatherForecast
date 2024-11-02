import logging
import typing as t
from dataclasses import asdict
from datetime import datetime

from forecast import api_client as client
from forecast.domain import models as dm
from forecast.search_history import SearchHistory


class CitiesCountRepoI(t.Protocol):
    def create_or_incr(self, city_name: str) -> None: ...

    def get_all(self) -> list[dm.CitiesCountDTO]: ...


class ForecastServiceError(Exception): ...


class NotFoundError(ForecastServiceError): ...


class Coords(t.NamedTuple):
    lat: str
    lon: str


class ForecastServiceI(t.Protocol):
    def get_daily_forecast(
        self,
        duration_days: int,
        history: SearchHistory,
        city_name: str | None = None,
        coords: Coords | None = None,
    ) -> tuple[dict[str, dm.WeatherDataPerDay], str]: ...

    def get_hourly_forecast_for_date(
        self,
        date: datetime,
        history: SearchHistory,
        city_name: str | None = None,
        coords: Coords | None = None,
    ) -> tuple[dict[str, dm.WeatherDataPerHour], str]: ...

    def get_cities_count(self) -> list[dm.CitiesCountDTO]: ...

    def get_last_viewed_city(self, history: SearchHistory) -> str: ...


class HistoryList(t.Protocol):
    def push(self, city_name: str) -> None: ...

    def __getitem__(self, index: int | slice) -> str: ...


class ForecastService:
    def __init__(
        self, repo: CitiesCountRepoI, logger: logging.Logger | None, api_client: client.AbstractApiClient
    ) -> None:
        self.repo = repo
        if logger is None:
            logger = logging.getLogger(__name__)
        self.logger = logger
        self.client = api_client

    def _get_geodata_by_coords_or_city(
        self, city_name: str | None = None, coords: Coords | None = None
    ) -> tuple[client.GeoData, str]:
        if not city_name and not coords:
            raise ForecastServiceError("Either city_name or coords must be provided")
        try:
            if coords is not None:
                geo_data = client.GeoData(**coords)
                city_name = geo_data.get_location()[
                    "city"
                ]  # WARNING: removed "city_name or", might cause an issue
            else:
                geo_data = self.client.get_geodata_by_city(city_name)
        except client.CoordinatesNotFoundError:
            self.logger.warning("get_forecast_view.CoordinatesNotFound")
            raise
        except client.GettingCoordinatesError as e:
            self.logger.exception("get_forecast_view.GettingCoordinatesError: %s", e)
            raise
        return geo_data, city_name

    def _try_get_daily_forecast(self, geo_data: client.GeoData, duration_days: int):
        try:
            forecast = self.client.get_daily_forecast(geo_data, forecast_days=duration_days)
        except client.ForecastApiError as e:
            self.logger.exception("error getting daily forecast: %s", e)
            raise
        return forecast

    def _try_get_hourly_forecast_for_date(
        self, geo_data: client.GeoData, date: datetime
    ) -> dict[str, dict[str, dm.WeatherDataPerHour] | dm.amount]:
        try:
            forecast = self.client.get_hourly_forecast_for_date(geo_data, date)
        except client.ForecastApiError as e:
            self.logger.exception("error getting hourly forecast for date %s: %s", date, e)
            raise
        return forecast

    def get_daily_forecast(
        self,
        duration_days: int,
        history: HistoryList,
        city_name: str | None = None,
        coords: Coords | None = None,
    ) -> tuple[dict[str, dm.WeatherDataPerDay], str]:
        geo_data, city_name = self._get_geodata_by_coords_or_city(city_name, coords)
        forecast = self._try_get_daily_forecast(geo_data, duration_days)
        for day in forecast:
            forecast[day] = asdict(forecast[day])
        history.push(city_name)
        self.repo.create_or_incr(city_name)
        return forecast, city_name

    def get_hourly_forecast_for_date(
        self,
        date: datetime,
        city_name: str | None = None,
        coords: Coords | None = None,
    ) -> tuple[dict[str, dm.WeatherDataPerHour], str]:
        geo_data, city_name = self._get_geodata_by_coords_or_city(city_name, coords)
        forecast = self._try_get_hourly_forecast_for_date(geo_data, date)
        forecast["temp_min"] = asdict(forecast["temp_min"])
        forecast["temp_max"] = asdict(forecast["temp_max"])
        for hour in forecast["hourly"]:
            forecast["hourly"][hour] = asdict(forecast["hourly"][hour])
        # history.push(city_name)
        # self.repo.create_or_incr(city_name)
        return forecast, city_name

    def get_cities_count(self) -> list[dm.CitiesCountDTO]:
        return self.repo.get_all()

    def get_last_viewed_city(self, history: HistoryList) -> str:
        try:
            res = history[-1]
        except IndexError as e:
            self.logger.info("Attempt to get last viewed city, but history is empty")
            raise NotFoundError from e
        return res
