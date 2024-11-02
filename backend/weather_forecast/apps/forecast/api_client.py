import abc
import logging
import typing as t
from datetime import datetime

import requests
import requests_cache
from geopy.geocoders import Nominatim
from retry_requests import retry

from forecast.domain import models as dm

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

### EXCEPTIONS ###  # noqa: E266


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

    def get_location(self) -> str:
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
    def get_daily_forecast(self, geo_data: GeoData, **kwargs) -> dict[str, dm.WeatherDataPerDay]: ...

    @abc.abstractmethod
    def get_hourly_forecast_for_date(
        self, geo_data: GeoData, date: datetime, **kwargs
    ) -> dict[str, dict[str, dm.WeatherDataPerHour] | dm.amount]: ...

    @abc.abstractmethod
    def get_geodata_by_city(self, query: str) -> GeoData: ...


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

    def _try_get_geodata_by_city(self, city_name: str) -> GeoData:
        try:
            response = self.retry_session.get(
                self.GEODATA_URL, {"format": "json", "name": city_name, "count": 1}
            ).json()
            try:
                data = response["results"][0]
            except (KeyError, IndexError) as e:
                logger.error("get_geodata_by_city - invalid response: %s", response)
                raise CoordinatesNotFoundError from e
        except requests.exceptions.RequestException as e:
            logger.exception("get_geodata_by_city Unexpected error: %s", e)
            raise GettingCoordinatesError from e
        return data

    def get_geodata_by_city(self, city_name: str) -> GeoData:
        city_name = city_name.strip()
        logger.debug("get_geodata_by_city: %s", city_name)
        data = self._try_get_geodata_by_city(city_name)
        logger.debug("get_geodata_by_city, received data: %s", data)
        return GeoData(latitude=data["latitude"], longitude=data["longitude"], timezone=data["timezone"])

    def _process_hourly_forecast(
        self, raw_forecast: dict
    ) -> dict[str, dict[str, dm.WeatherDataPerHour] | dm.amount]:
        try:
            hourly = raw_forecast["hourly"]
            units = raw_forecast["hourly_units"]
            processed_forecast: dict[str, dm.WeatherDataPerHour] = {
                "hourly": {},
                "temp_min": dm.amount(
                    raw_forecast["daily"]["temperature_2m_min"],
                    raw_forecast["daily_units"]["temperature_2m_min"],
                ),
                "temp_max": dm.amount(
                    raw_forecast["daily"]["temperature_2m_max"],
                    raw_forecast["daily_units"]["temperature_2m_max"],
                ),
            }
            for i in range(len(hourly["time"])):
                processed_forecast["hourly"][hourly["time"][i]] = dm.WeatherDataPerHour(
                    temp=dm.amount(hourly["temperature_2m"][i], units["temperature_2m"]),
                    rain=dm.amount(hourly["rain"][i], units["rain"]),
                    temp_feels_like=dm.amount(
                        hourly["apparent_temperature"][i],
                        units["apparent_temperature"],
                    ),
                    precipitation_probability=dm.amount(
                        hourly["precipitation_probability"][i],
                        units["precipitation_probability"],
                    ),
                )
            return processed_forecast
        except Exception as e:
            logger.exception("error while processing hourly forecast: %s", e)
            raise ParsingForecastError from e

    def _process_daily_forecast(self, raw_forecast: dict) -> dict[str, dm.WeatherDataPerDay]:
        try:
            daily = raw_forecast["daily"]
            units = raw_forecast["daily_units"]
            processed_forecast: dict[str, dm.WeatherDataPerDay] = {}
            for i in range(len(daily["time"])):
                processed_forecast[daily["time"][i]] = dm.WeatherDataPerDay(
                    temp_max=dm.amount(daily["temperature_2m_max"][i], units["temperature_2m_max"]),
                    temp_min=dm.amount(daily["temperature_2m_min"][i], units["temperature_2m_min"]),
                    rain_sum=dm.amount(daily["rain_sum"][i], units["rain_sum"]),
                    precipitation_probability=dm.amount(
                        daily["precipitation_probability_max"][i],
                        units["precipitation_probability_max"],
                    ),
                )
            return processed_forecast
        except Exception as e:
            logger.exception("error while processing daily forecast: %s", e)
            raise ParsingForecastError from e

    def get_hourly_forecast_for_date(
        self, geo_data: GeoData, date: datetime, **kwargs
    ) -> dict[str, dict[str, dm.WeatherDataPerHour] | dm.amount]:
        response = self.retry_session.get(
            self.FORECAST_URL,
            {
                **geo_data._asdict(),
                "start_date": date.strftime("%Y-%m-%d"),
                "end_date": date.strftime("%Y-%m-%d"),
                "hourly": [
                    "temperature_2m",
                    "rain",
                    "precipitation_probability",
                    "apparent_temperature",
                ],
                "daily": ["temperature_2m_max", "temperature_2m_min"],
                **kwargs,
            },
        )
        resp_data = response.json()
        processed_forecast = self._process_hourly_forecast(resp_data)
        return processed_forecast

    def get_daily_forecast(self, geo_data: GeoData, **kwargs) -> dict[str, dm.WeatherDataPerDay]:
        response = self.retry_session.get(
            self.FORECAST_URL,
            {
                **geo_data._asdict(),
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
        resp_data = response.json()
        processed_forecast = self._process_daily_forecast(resp_data)
        return processed_forecast
