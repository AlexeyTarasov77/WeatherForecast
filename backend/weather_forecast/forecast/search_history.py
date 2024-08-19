from django.conf import settings
from django.http import HttpRequest


class History:
    def __init__(self, request: HttpRequest) -> None:
        self.session = request.session
        history: list | None = self.session.get(settings.FORECAST_HISTORY_SESSION_KEY)

        if history is None:
            history = self.session[settings.FORECAST_HISTORY_SESSION_KEY] = []
        self.history = history

    def add(self, city_name: str) -> None:
        if city_name not in self.history:
            self.history.append(city_name)
            self.save()

    def save(self):
        self.session.modified = True

    def __iter__(self):
        return iter(self.history)
