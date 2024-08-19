from django.urls import path

from . import views

app_name = "forecast"

urlpatterns = [
    path("", views.get_forecast_view, name="get-forecast"),
    path("history/", views.history_view, name="history"),
]
