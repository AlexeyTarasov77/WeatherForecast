import logging

from django.conf import settings

from forecast import api_client
from forecast import repositories as repos
from forecast.domain import service


def get_logger(name):
    logger = logging.getLogger(name)
    if settings.DEBUG:
        logger.setLevel(logging.DEBUG)


def get_forecast_service(logger_name: str = "forecast_service") -> service.ForecastService:
    repo = repos.CitiesCountRepositoryRedis()
    client = api_client.OpenMeteoApiClient()
    logger = get_logger(logger_name)
    return service.ForecastService(repo=repo, logger=logger, api_client=client)
