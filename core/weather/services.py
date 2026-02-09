import requests
from django.core.cache import cache
from django.conf import settings
import json


class WeatherService:
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
    CACHE_TIMEOUT = 1200

    @classmethod
    def get_weather(cls, city_name):
        """
        Get weather data for a city with caching
        """
        cache_key = f"weather_{city_name.lower()}"

        # Try to get from cache first
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data

        # If not in cache, fetch from API
        api_key = settings.OPENWEATHER_API_KEY
        if not api_key:
            return {"error": "OpenWeather API key is not configured"}

        try:
            params = {
                "q": city_name,
                "appid": api_key,
                "units": "metric",
            }

            response = requests.get(cls.BASE_URL, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Format the response
            weather_data = {
                "city": data.get("name"),
                "country": data.get("sys", {}).get("country"),
                "temperature": round(data.get("main", {}).get("temp", 0)),
                "feels_like": round(data.get("main", {}).get("feels_like", 0)),
                "description": data.get("weather", [{}])[0].get("description", ""),
                "icon": data.get("weather", [{}])[0].get("icon", ""),
                "humidity": data.get("main", {}).get("humidity", 0),
                "wind_speed": data.get("wind", {}).get("speed", 0),
                "pressure": data.get("main", {}).get("pressure", 0),
            }

            # Cache the result
            cache.set(cache_key, weather_data, cls.CACHE_TIMEOUT)

            return weather_data

        except requests.exceptions.RequestException as e:
            return {"error": f"Error fetching weather data: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
