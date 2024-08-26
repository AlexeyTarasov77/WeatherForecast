import typing as t

from django.conf import settings
from django.http import HttpRequest


class SearchHistory:
    def __init__(self, request: HttpRequest) -> None:
        self.session = request.session
        history: list | None = self.session.get(settings.FORECAST_HISTORY_SESSION_KEY)

        if history is None:
            history = self.session[settings.FORECAST_HISTORY_SESSION_KEY] = []
        self._history = history

    def add(self, city_name: str) -> None:
        if city_name not in self._history:
            self._history.append(city_name)
            self.save()

    def __getitem__(self, index: int | slice) -> str:
        return self._history[index]

    def save(self):
        self.session.modified = True

    def __iter__(self) -> t.Iterator:
        return iter(self._history)
