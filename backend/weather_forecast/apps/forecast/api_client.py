import abc
import logging
import typing as t
from datetime import datetime

import requests
import requests_cache
from geopy.geocoders import Nominatim
from retry_requests import retry

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


### EXCEPTIONS ###


class ForecastApiError(Exception):
    pass


class GettingForecastError(ForecastApiError):
    pass


class ParsingForecastError(ForecastApiError):
    pass


class GettingCoordinatesError(ForecastApiError):
    pass


class CoordinatesNotFoundError(GettingCoordinatesError):
    pass


class GeoData(t.NamedTuple):
    latitude: float
    longitude: float
    timezone: str = "UTC"

    def get_location(self):
        geolocator = Nominatim(user_agent="weatherApp")
        location = geolocator.reverse(f"{self.latitude},{self.longitude}", language="en")
        return location.raw["address"]


class AbstractApiClient(abc.ABC):
    def __init__(
        self,
        forecast_url: str,
        geodata_url: str,
        session_expire_after: int = 3600,
        retries: int = 5,
        logger: logging.Logger | None = None,
    ) -> None:
        self.FORECAST_URL = forecast_url
        self.GEODATA_URL = geodata_url
        self.session = requests_cache.CachedSession(".cache", expire_after=session_expire_after)
        self.retry_session = retry(self.session, retries=retries, backoff_factor=0.2)
        if logger is None:
            logger = logging.getLogger(__name__)
        self.logger = logger

    @abc.abstractmethod
    def get_forecast(self, geo_data: GeoData, **kwargs) -> dict[str, dict[str, t.Any]]:
        pass

    @abc.abstractmethod
    def get_geodata_by_city(self, query: str) -> GeoData:
        pass


class OpenMeteoApiClient(AbstractApiClient):
    def __init__(
        self, session_expire_after: int = 3600, retries: int = 5, logger: logging.Logger = None
    ) -> None:
        super().__init__(
            "https://api.open-meteo.com/v1/forecast",
            "https://geocoding-api.open-meteo.com/v1/search",
            session_expire_after,
            retries,
            logger,
        )

    def get_geodata_by_city(self, query: str) -> GeoData:
        # response = openmeteo.weather_api(GEODATA_URL, {"name": query, "count": 1})[0]
        query = query.strip()
        logger.debug("get_geodata_by_city: %s", query)
        try:
            response = self.retry_session.get(
                self.GEODATA_URL, {"format": "json", "name": query, "count": 1}
            )
            try:
                data = response.json()["results"][0]
            except KeyError as e:
                logger.error("get_geodata_by_city - invalid response: %s", response.json())
                raise CoordinatesNotFoundError from e
        except requests.exceptions.RequestException as e:
            logger.exception("get_geodata_by_city Unexpected error: %s", e)
            raise GettingCoordinatesError from e

        logger.debug("get_geodata_by_city, data: %s", data)
        return GeoData(latitude=data["latitude"], longitude=data["longitude"], timezone=data["timezone"])

    def _process_forecast_response(self, resp_data: dict[str, t.Any]) -> dict:
        daily: dict = resp_data["daily"]
        hourly: dict = resp_data["hourly"]
        daily_data = {}

        def compute_value_with_units(val, units: dict, key: str) -> float:
            try:
                if key in units:
                    return {
                        "val": val,
                        "unit": units[key],
                    }
                return val
            except IndexError:
                pass

        for i, date in enumerate(daily["time"]):
            daily_data[date] = {"hourly": {}}
            for key, vals in daily.items():
                daily_data[date][key] = compute_value_with_units(
                    vals[i], resp_data.get("daily_units", {}), key
                )
            hourly_indices_for_date = [
                i
                for i, dt in enumerate(hourly["time"])
                if datetime.fromisoformat(dt).date() == datetime.fromisoformat(date).date()
            ]
            for i in hourly_indices_for_date:
                time_key = hourly["time"][i]
                hourly_data = daily_data[date]["hourly"]
                hourly_data[time_key] = {}
                for key, vals in hourly.items():
                    hourly_data[time_key][key] = compute_value_with_units(
                        vals[i], resp_data.get("hourly_units", {}), key
                    )
        return daily_data

    def _get_forecast_response(self, geo_data: GeoData, **kwargs) -> dict:
        response = self.retry_session.get(
            self.FORECAST_URL,
            {
                **geo_data._asdict(),
                "hourly": ["temperature_2m", "rain"],
                "daily": [
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "rain_sum",
                    "precipitation_probability_max",
                    "apparent_temperature_max",
                    "apparent_temperature_min",
                ],
                **kwargs,
            },
        )
        return response.json()

    def get_forecast(self, geo_data: GeoData, **kwargs) -> dict:
        try:
            resp_data = self._get_forecast_response(geo_data, **kwargs)
        except Exception as e:
            logger.error("get_forecast: %s", e)
            raise GettingForecastError from e
        try:
            data = self._process_forecast_response(resp_data)
        except Exception as e:
            logger.exception("get_forecast Unexpected error: %s", e)
            raise ParsingForecastError from e
        return {"daily": data}
