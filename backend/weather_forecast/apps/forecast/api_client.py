import abc
import logging
import typing as t
from datetime import datetime
from dataclasses import asdict

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

    def get_location(self):
        geolocator = Nominatim(user_agent="weatherApp")
        location = geolocator.reverse(f"{self.latitude},{self.longitude}", language="en")
        return location.raw["address"]


class AbstractApiClient(abc.ABC):
    type ForecastDailyData = dict[str, dict[str, t.Any]]

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
    def get_forecast(self, geo_data: GeoData, **kwargs) -> ForecastDailyData:
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

    def _make_geodata_req(self, city_name: str) -> GeoData:
        response = self.retry_session.get(
            self.GEODATA_URL, {"format": "json", "name": city_name, "count": 1}
        ).json()
        try:
            data = response["results"][0]
        except (KeyError, IndexError) as e:
            logger.error("get_geodata_by_city - invalid response: %s", response)
            raise CoordinatesNotFoundError from e
        return data

    def get_geodata_by_city(self, city: str) -> GeoData:
        city = city.strip()
        logger.debug("get_geodata_by_city: %s", city)
        try:
            data = self._make_geodata_req(city)
        except requests.exceptions.RequestException as e:
            logger.exception("get_geodata_by_city Unexpected error: %s", e)
            raise GettingCoordinatesError from e

        logger.debug("get_geodata_by_city, data: %s", data)
        return GeoData(latitude=data["latitude"], longitude=data["longitude"], timezone=data["timezone"])

    def _process_forecast_response(self, resp_data: dict[str, t.Any]):
        try:
            daily: dict = resp_data["daily"]
            hourly: dict = resp_data["hourly"]
        except KeyError as e:
            raise ParsingForecastError from e
        daily_data = {}

        hourly_fields_matching = {
            "temp": "temperature_2m",
            "rain": "rain_sum",
            "precipitation_probability": "precipitation_probability",
            "temp_feels_like": "apparent_temperature",
        }

        daily_fields_matching = {
            "temp_min": "temperature_2m_min",
            "temp_max": "temperature_2m_max",
            "rain_sum": "rain_sum",
            "precipitation_probability": "precipitation_probability",
            "hourly": "hourly",
        }

        def compute_amount[T](
            value: T, units: dict[str, str], unit_key: str
        ) -> dict[str, t.Any] | t.Any:
            try:
                if unit_key in units:
                    return dm.amount(value, units[unit_key])
                return dm.amount(value)
            except IndexError:
                pass

        try:
            for i, date in enumerate(daily["time"]):
                daily_data[date] = {"hourly": {}}
                for field_name, field in dm.WeatherDataPerDay.__dataclass_fields__.items():
                    if (
                        field_name == "hourly"
                    ):  # hourly shouldn't be processed here, because it will be processed later
                        continue
                    assert (
                        field_name in daily_fields_matching
                    ), f"{field_name} must be presented in {daily_fields_matching}"
                    matched_field = daily_fields_matching[field_name]
                    try:
                        field_value = daily[matched_field][i]
                    except KeyError:
                        field_value = None
                    if field.type == dm.amount and field_value is not None:
                        field_value = compute_amount(
                            field_value, resp_data.get("daily_units", {}), matched_field
                        )
                    daily_data[date][field_name] = field_value
                hourly_data_values_indices_per_date = [
                    i
                    for i, dt in enumerate(hourly["time"])
                    if datetime.fromisoformat(dt).date() == datetime.fromisoformat(date).date()
                ]
                hourly_data_per_date = daily_data[date]["hourly"]
                for i in hourly_data_values_indices_per_date:
                    key = hourly["time"][i]
                    hourly_data_per_date[key] = {}
                    for field_name, field in dm.WeatherDataPerHour.__dataclass_fields__.items():
                        assert (
                            field_name in hourly_fields_matching
                        ), f"{field_name} must be presented in {hourly_fields_matching}"
                        matched_field = hourly_fields_matching[field_name]
                        try:
                            field_value = hourly[matched_field][i]
                        except KeyError:
                            field_value = None
                        if field.type == dm.amount and field_value is not None:
                            field_value = compute_amount(
                                field_value,
                                resp_data.get("hourly_units", {}),
                                matched_field,
                            )
                        hourly_data_per_date[key][field_name] = field_value
                    hourly_data_per_date[key] = asdict(dm.WeatherDataPerHour(**hourly_data_per_date[key]))
                    # compute_amount_with_units = partial(
                    #     compute_amount, units=resp_data.get("hourly_units", {})
                    # )
                    # hourly_data[time_key] = dm.WeatherDataPerHour(
                    #     temp=compute_amount_with_units(
                    #         value=hourly["temperature_2m"][i], unit_key="temperature_2m"
                    #     ),
                    #     rain=compute_amount_with_units(value=hourly["rain_sum"][i], unit_key="rain_sum"),
                    #     temp_feels_like=compute_amount_with_units(
                    #         value=hourly["apparent_temperature"][i], unit_key="apparent_temperature"
                    #     ),
                    #     precipitation_probability=compute_amount_with_units(
                    #         value=hourly["precipitation_probability"][i],
                    #         unit_key="precipitation_probability",
                    #     ),
                    # )
                    # for key, vals in hourly.items():
                    #     if key in dm.WeatherDataPerHour.__dataclass_fields__:
                    #         hourly_data[time_key][key] = compute_amount(
                    #             vals[i], resp_data.get("hourly_units", {}), key
                    #         )
                    # hourly_data[time_key] = dm.WeatherDataPerHour(**hourly_data[time_key])
        except Exception as e:
            logger.exception("get_forecast Unexpected error: %s", e)
            raise ParsingForecastError from e
        daily_data = {date: asdict(dm.WeatherDataPerDay(**data)) for date, data in daily_data.items()}
        return daily_data

    def _get_forecast_response(self, geo_data: GeoData, **kwargs) -> dict:
        try:
            response = self.retry_session.get(
                self.FORECAST_URL,
                {
                    **geo_data._asdict(),
                    "hourly": [
                        "temperature_2m",
                        "rain",
                        "precipitation_probability",
                        "apparent_temperature",
                    ],
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
        except Exception as e:
            logger.error("_get_forecast_response: %s", e)
            raise GettingForecastError from e
        return response.json()

    def get_forecast(self, geo_data: GeoData, **kwargs) -> dict:
        resp_data = self._get_forecast_response(geo_data, **kwargs)
        return self._process_forecast_response(resp_data)
