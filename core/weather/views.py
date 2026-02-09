from django.shortcuts import render
from weather.services import WeatherService



def weather_widget(request):
    """
    View to display weather widget
    """
    context = {}
    
    # Get default city from query parameter or use Tehran as default
    city = request.GET.get('city', 'Tehran')
    weather_data = WeatherService.get_weather(city)
    
    context['weather_data'] = weather_data
    context['current_city'] = city
    
    return render(request, 'weather/weather_widget.html', context)