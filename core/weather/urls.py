from django.urls import path
from weather.views import weather_widget

app_name = "weather"

urlpatterns = [
    path("", weather_widget, name="weather-widget"),
]