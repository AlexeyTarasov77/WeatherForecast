import logging
from typing import NamedTuple

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


class GeoData(NamedTuple):
    latitude: float
    longitude: float
    timezone: str = "UTC"

    def get_location(self):
        geolocator = Nominatim(user_agent="weatherApp")
        location = geolocator.reverse(f"{self.latitude},{self.longitude}", language="en")
        return location.raw["address"]


class OpenMeteoApiClient:
    def __init__(self, session_expire_after: int = 3600, retries: int = 5) -> None:
        self.FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
        self.GEODATA_URL = "https://geocoding-api.open-meteo.com/v1/search"
        self.session = requests_cache.CachedSession(".cache", expire_after=session_expire_after)
        self.retry_session = retry(self.session, retries=retries, backoff_factor=0.2)

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

    def get_forecast(self, geo_data: GeoData, **kwargs) -> dict:
        try:
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
            resp_data = response.json()
        except Exception as e:
            logger.error("get_forecast: %s", e)
            raise GettingForecastError from e
        try:
            # TODO: add data processing for hourly forecast
            daily: dict = resp_data["daily"]
            hourly: dict = resp_data["hourly"]
            daily_data = {}
            hourly_data = {}
            for i, date in enumerate(daily["time"]):

                daily_data[date] = {}
                for key, val in daily.items():
                    print(i, val[i])
                    try:
                        if key in (units := resp_data.get("daily_units", {})):
                            daily_data[date][key] = {
                                "val": val[i],
                                "unit": units[key],
                            }
                        else:
                            daily_data[date][key] = val[i]
                    except IndexError:
                        pass
            data = {
                "hourly": hourly_data,
                "daily": daily_data,
            }
        except Exception as e:
            logger.exception("get_forecast Unexpected error: %s", e)
            raise ParsingForecastError from e
        return data
