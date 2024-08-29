from django.urls import path

from . import views

app_name = "forecast"

urlpatterns = [
    path("", views.forecast_view, name="get-forecast"),
    path("search-history/", views.history_view, name="history"),
    path("cities-count/", views.cities_count_view, name="city-count"),
    path("last-viewed-city/", views.last_viewed_city_view, name="last-viewed-city"),
]
