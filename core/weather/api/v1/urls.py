from django.urls import path
from weather.api.v1.views import get_weather

app_name = "weather-api-v1"

urlpatterns = [
    path("", get_weather, name="get-weather"),
]