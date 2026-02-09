from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from weather.services import WeatherService


@api_view(["GET"])
@permission_classes([AllowAny])
def get_weather(request):
    """
    API endpoint to get weather data for a city
    Query parameter: city (required)
    Example: /api/weather/v1/?city=Tehran
    """
    city = request.query_params.get("city")

    if not city:
        return Response(
            {"error": "City parameter is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    weather_data = WeatherService.get_weather(city)

    if "error" in weather_data:
        return Response(weather_data, status=status.HTTP_400_BAD_REQUEST)

    return Response(weather_data, status=status.HTTP_200_OK)
