from typing import Literal

import requests


class WeatherAPI:
    """
    Класс представляет собой обертку над API сервиса Open Weather Map
    """

    def __init__(self, appid: str):
        self.appid = appid
        self.session = requests.session()

    def __make_request(self, path: str, data: dict):
        """
        Базовый метод для всех API вызовов

        :param path: название API метода
        :param data: словарь с параметрами запроса
        :return: JSON с ответом метода или генерирует исключение HTTPError
        """
        base_url = f'https://api.openweathermap.org/data/2.5/'

        # удаляем потенциально ненужное и вставляем потенциально необходимое
        if 'appid' not in data:
            data['appid'] = self.appid
        if 'self' in data:
            del data['self']

        with self.session as session:
            # все методы OWM API вроде как используют GET, так что нет смысла пилить универсальный реквестер
            response = session.get(base_url + path, params=data)
        if response.status_code == 200:
            return response.json()
        return response.raise_for_status()

    def get_weather(self, q: str, units: Literal["standard", "metric", "imperial"] = 'metric') -> float:
        """
        Метод для получения текущей температуры в заданном городе

        :param q: название города
        :param units: единицы измерения. standard - в Кельвинах, metric - в Цельсиях, imperial - в Фаренгейтах. По умолчанию metric
        :return: float c температурой в заданном городе
        """
        response = self.__make_request('weather', data=locals())
        return response['main']['temp']

    def check_city(self, city: str) -> bool:
        """
        Проверяет наличие города в базе
        :param city: название города
        :return: bool с результатом проверки
        """
        try:
            self.get_weather(city)
            return True
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                return False
            raise e
