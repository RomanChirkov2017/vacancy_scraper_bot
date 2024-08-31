import os
import time

import requests

from abstract_classes import ApiJobSites
from dotenv import load_dotenv

load_dotenv(".env")

API_KEY = os.getenv("SUPERJOB_API_KEY")


class SuperJobAPI(ApiJobSites):
    """Класс для работы с API SuperJob."""

    url = "https://api.superjob.ru/2.0/vacancies"

    def __init__(self, keyword: str) -> None:
        """Инициализатор класса SuperJobApi."""
        self.params = {"count": 10, "page": None, "keyword": keyword, "archive": False, "agreement": False}
        self.secret_key = API_KEY
        self.headers = {"X-Api-App-Id": self.secret_key}
        self.keyword = keyword
        self.vacancies = []

    def get_request(self) -> list[dict]:
        """Отправляет запрос к API SuperJob и возвращает список словарей с информацией о вакансиях."""
        response = requests.get(self.url, headers=self.headers, params=self.params)
        if response.status_code == 200:
            return response.json()["objects"]
        else:
            print(f"Ошибка запроса! Статус-код: {response.status_code}.")

    def get_vacancies(self, page_count=5):
        """Получение вакансий от SuperJob API."""
        self.vacancies = []
        for page in range(page_count):
            time.sleep(1)
            self.params["page"] = page
            print(f"{self.__class__.__name__} загрузка страницы {page + 1} SJ -", end=" ")
            try:
                page_vacancies = self.get_request()
                if len(page_vacancies) == 0:
                    print(f"На странице {page + 1} нет вакансий, удовлетворяющих запросу.")
                    break
            except Exception as error:
                print(error)
            else:
                self.vacancies.extend(page_vacancies)
                print(f"Загружено вакансий: {len(page_vacancies)}.")

    def get_formatted_vacancies(self) -> list[dict]:
        """Возвращает отформатированные данные о вакансиях."""
        formatted_vacancies = []

        for vacancy in self.vacancies:
            formatted_vacancy = {
                "name": vacancy["profession"].lower(),
                "url": vacancy["link"],
                "salary_from": vacancy["payment_from"] if vacancy["payment_from"] is not None else 0,
                "salary_to": vacancy["payment_to"] if vacancy["payment_to"] != 0 else vacancy["payment_from"],
                "currency": vacancy["currency"].upper(),
                "description": vacancy["candidat"].lower(),
            }
            formatted_vacancies.append(formatted_vacancy)
        return formatted_vacancies
