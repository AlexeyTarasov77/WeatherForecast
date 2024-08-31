import logging
import typing as t

import pandas as pd

from forecast import api_client as client
from forecast.domain import models as dm
from forecast.search_history import SearchHistory


class RepoInterface(t.Protocol):
    def add_or_update(self, city_name: str) -> None: ...

    def get_all(self) -> list[dm.CitiesCountDTO]: ...


class ApiClientInterface(t.Protocol):
    def get_forecast(self, city_name: str, forecast_days: int) -> pd.DataFrame: ...

    def get_geodata_by_city(self, query: str) -> client.GeoData: ...


class ForecastServiceError(Exception): ...


class NotFoundError(ForecastServiceError): ...


class ForecastService:
    def __init__(
        self, repo: RepoInterface, logger: logging.Logger | None, api_client: ApiClientInterface
    ) -> None:
        self.repo = repo
        if logger is None:
            logger = logging.getLogger(__name__)
        self.logger = logger
        self.client = api_client

    def get_forecast(
        self,
        forecast_days: int,
        history: SearchHistory,
        city_name: str | None = None,
        coords: dict[str, str] | None = None,
    ) -> tuple[pd.DataFrame, str]:
        if not city_name and not coords:
            raise Exception("Either city_name or coords must be provided")
        try:
            try:
                if coords is not None:
                    geo_data = client.GeoData(**coords)
                    city_name = city_name or geo_data.get_location()["city"]
                else:
                    geo_data = self.client.get_geodata_by_city(city_name)
            except client.CoordinatesNotFoundError:
                self.logger.warning("get_forecast_view.CoordinatesNotFound")
                raise
            except client.GettingCoordinatesError as e:
                self.logger.exception("get_forecast_view.GettingCoordinatesError: %s", e)
                raise
            forecast = self.client.get_forecast(geo_data, forecast_days=forecast_days)
        except client.ForecastApiError as e:
            self.logger.exception("get_forecast_view.ForecastError: %s", e)
            raise
        history.add(city_name)
        self.repo.add_or_update(city_name)
        return forecast, city_name

    def get_cities_count(self):
        return self.repo.get_all()

    def get_last_viewed_city(self, history: SearchHistory) -> str:
        try:
            res = history[-1]
        except IndexError as e:
            self.logger.info("Attempt to get last viewed city, but history is empty")
            raise NotFoundError from e
        return res
