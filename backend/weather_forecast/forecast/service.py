import logging
import typing as t

import pandas as pd

from forecast import api_client as client
from forecast import models
from forecast.search_history import SearchHistory


class RepoInterface(t.Protocol):
    def add_or_update(self, city_name: str) -> None: ...

    def get_all(self) -> list[models.CitiesCount]: ...


class ApiClientInterface(t.Protocol):
    def get_forecast(self, city_name: str, forecast_days: int) -> pd.DataFrame: ...

    def get_geodata_by_city(self, query: str) -> client.GeoData: ...


class ForecastServiceError: ...


class ForecastService:
    def __init__(
        self, repo: RepoInterface, logger: logging.Logger | None, api_client: ApiClientInterface
    ) -> None:
        self.repo = repo
        if logger is None:
            logger = logging.getLogger(__name__)
        self.logger = logger
        self.client = api_client

    def get_forecast(self, city_name: str, forecast_days: int, history: SearchHistory) -> pd.DataFrame:
        try:
            try:
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
        return forecast

    def get_cities_count(self):
        return self.repo.get_all()
