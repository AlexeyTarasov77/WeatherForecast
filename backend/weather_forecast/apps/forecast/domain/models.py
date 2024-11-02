from dataclasses import dataclass


@dataclass
class CitiesCountDTO:
    name: str
    count: int


@dataclass
class amount:  # noqa: N801
    value: int
    unit: str | None = None


@dataclass
class WeatherDataPerHour:
    temp: amount
    temp_feels_like: amount
    rain: float
    precipitation_probability: amount


@dataclass
class WeatherDataPerDay:
    temp_min: amount
    temp_max: amount
    rain_sum: amount
    precipitation_probability: amount
