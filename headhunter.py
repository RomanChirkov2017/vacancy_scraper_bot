import time

import requests

from abstract_classes import ApiJobSites


class HeadHunterAPI(ApiJobSites):
    """Класс для работы с API HeadHunter."""

    url = "https://api.hh.ru/vacancies"

    def __init__(self, keyword: str) -> None:
        """Инициализатор класса HeadHunterAPI."""
        self.headers ={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
        }
        self.params = {"per_page": 10, "page": None, "text": keyword, "archive": False, "only_with_salary": True}
        self.keyword = keyword
        self.vacancies = []

    def get_request(self) -> list[dict]:
        """Отправляет запрос к HH API и возвращает список словарей с информацией о вакансиях."""
        response = requests.get(self.url, headers=self.headers, params=self.params)
        if response.status_code == 200:
            return response.json()['items']
        else:
            print(f"Ошибка запроса! Статус-код: {response.status_code}")

    def get_vacancies(self, page_count=5) -> None:
        """Получение вакансий через HH API."""
        self.vacancies = []
        for page in range(page_count):
            time.sleep(1)
            page_vacancies = []
            self.params['page'] = page
            print(f"{self.__class__.__name__} загрузка страницы {page + 1} HH -", end=" ")
            try:
                page_vacancies = self.get_request()
            except Exception as error:
                print(error)
            else:
                self.vacancies.extend(page_vacancies)
                print(f"Загружено вакансий: {len(page_vacancies)}.")
            if len(page_vacancies) == 0:
                print(f"Не удалось загрузить страницу {page + 1}.")
                break

    def get_formatted_vacancies(self) -> list[dict]:
        """Возвращает отформатированные данные о вакансиях."""
        formatted_vacancies = []
        for vacancy in self.vacancies:
            formatted_vacancy = {
                "name": vacancy["name"].lower(),
                "url": vacancy["alternate_url"],
                "salary_from": vacancy["salary"]["from"] if vacancy["salary"]["from"] is not None else 0,
                "salary_to": vacancy["salary"]["to"] if vacancy["salary"]["to"] is not None else vacancy["salary"]["from"],
                "currency": vacancy["salary"]["currency"] if vacancy["salary"] else "",
                "description": vacancy["snippet"]["requirement"].replace('<highlighttext>', '').replace('</highlighttext>', '')
                if vacancy["snippet"]["requirement"] is not None else "",
            }
            formatted_vacancies.append(formatted_vacancy)
        return formatted_vacancies
