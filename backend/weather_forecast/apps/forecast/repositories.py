from django.db import transaction

from forecast import models


class CitiesCountRepository:
    def add_or_update(self, city_name: str) -> None:
        with transaction.atomic():
            try:
                city = models.CitiesCount.objects.select_for_update().get(name=city_name)
            except models.CitiesCount.DoesNotExist:
                city = models.CitiesCount(name=city_name)
                city.count = 0
            city.count += 1
            city.save()

    def get_all(self) -> list[models.CitiesCount]:
        return models.CitiesCount.objects.all()
