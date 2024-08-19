class ForecastError(Exception):
    pass


class GettingForecastError(ForecastError):
    pass


class ParsingForecastError(ForecastError):
    pass


class GettingCoordinatesError(ForecastError):
    pass


class CoordinatesNotFoundError(GettingCoordinatesError):
    pass
