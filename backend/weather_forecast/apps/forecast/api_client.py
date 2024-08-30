import logging
from typing import NamedTuple

import openmeteo_requests
import pandas as pd
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
        self.openmeteo = openmeteo_requests.Client(session=self.retry_session)

    def get_geodata_by_city(self, query: str) -> GeoData:
        # response = openmeteo.weather_api(GEODATA_URL, {"name": query, "count": 1})[0]
        query = query.strip()
        logger.debug("get_geodata_by_city: %s", query)
        try:
            response = requests.get(self.GEODATA_URL, {"format": "json", "name": query, "count": 1})
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

    def get_forecast(self, geo_data: GeoData, **kwargs) -> pd.DataFrame:
        try:
            response = self.openmeteo.weather_api(
                self.FORECAST_URL,
                {
                    **geo_data._asdict(),
                    "hourly": ["temperature_2m", "rain"],
                    "daily": ["temperature_2m_max", "temperature_2m_min", "rain_sum"],
                    **kwargs,
                },
            )[0]
        except Exception as e:
            logger.error("get_forecast: %s", e)
            raise GettingForecastError from e
        try:
            daily = response.Daily()
            hourly = response.Hourly()
            hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()

            hourly_rain = hourly.Variables(1).ValuesAsNumpy()

            daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
            daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
            daily_rain_sum = daily.Variables(2).ValuesAsNumpy()

            hourly_data = {
                "date": pd.date_range(
                    start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                    end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                    freq=pd.Timedelta(seconds=hourly.Interval()),
                    inclusive="left",
                ),
                "temperature_2m": hourly_temperature_2m,
                "rain": hourly_rain,
            }

            daily_data = {
                "date": pd.date_range(
                    start=pd.to_datetime(daily.Time(), unit="s", utc=True),
                    end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
                    freq=pd.Timedelta(seconds=daily.Interval()),
                    inclusive="left",
                ),
                "temperature_2m_max": daily_temperature_2m_max,
                "temperature_2m_min": daily_temperature_2m_min,
                "rain_sum": daily_rain_sum,
            }

            # hourly_dataframe = pd.DataFrame(hourly_data)
            # daily_dataframe = pd.DataFrame(daily_data)
            # data = pd.concat([hourly_dataframe, daily_dataframe], axis=1)

            data = {
                "hourly": hourly_data,
                "daily": daily_data,
            }

            # dataframe = pd.DataFrame(data)
            # print(dataframe)
        except Exception as e:
            logger.exception("get_forecast Unexpected error: %s", e)
            raise ParsingForecastError from e
        # logger.debug("get_forecast - dataframe: %s", dataframe)
        return data
