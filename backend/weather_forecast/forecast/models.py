from django.db import models


# Create your models here.
class CitiesCount(models.Model):
    name = models.CharField(max_length=255, unique=True)
    count = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name}: {self.count}"
