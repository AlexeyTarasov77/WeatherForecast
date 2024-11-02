from core.redis import conn as redis_conn
from django.db import transaction

from forecast import models
from forecast.domain import models as dm


class CitiesCountRepositorySQL:
    def create_or_incr(self, city_name: str) -> None:
        with transaction.atomic():
            try:
                city = models.CitiesCount.objects.select_for_update().get(name=city_name)
            except models.CitiesCount.DoesNotExist:
                city = models.CitiesCount(name=city_name)
                city.count = 0
            city.count += 1
            city.save()

    def get_all(self) -> list[dm.CitiesCountDTO]:
        data = models.CitiesCount.objects.all().values_list("name", "count", flat=True)
        return [dm.CitiesCountDTO(name, count) for name, count in data]


class CitiesCountRepositoryRedis:
    def __init__(self) -> None:
        self.db = redis_conn

    def create_or_incr(self, city_name: str) -> None:
        self.db.hincrby("cities_count", city_name, 1)

    def get_all(self) -> list[dm.CitiesCountDTO]:
        return [
            dm.CitiesCountDTO(name, count) for name, count in self.db.hgetall("cities_count").items()
        ]
