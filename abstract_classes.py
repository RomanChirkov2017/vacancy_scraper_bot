from abc import ABC, abstractmethod


class ApiJobSites(ABC):
    """Абстрактный класс для работы с API сайтов вакансий."""

    @abstractmethod
    def get_request(self):
        pass

    @abstractmethod
    def get_vacancies(self):
        pass

    @abstractmethod
    def get_formatted_vacancies(self):
        pass


class FileSaver(ABC):
    """Абстрактный класс для работы с полученными данными."""

    @abstractmethod
    def save_data(self, json_file):
        pass

    @abstractmethod
    def add_vacancy(self):
        pass

    @abstractmethod
    def del_vacancy(self):
        pass
