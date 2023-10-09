import os

from .external_requests import WeatherAPI

__all__ = ["weather_api"]

weather_api = WeatherAPI(os.environ['OWM_APPID'])
