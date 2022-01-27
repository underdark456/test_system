from abc import ABC, abstractmethod
from typing import Optional

API = 1
CHROME = 2
FIREFOX = 3

DRIVER_NAMES = {
    API: 'API',
    CHROME: 'CHROME',
    FIREFOX: 'FIREFOX',
}


class AbstractHttpDriver(ABC):
    def __init__(self):
        self._username = None
        self._password = None

    @abstractmethod
    def get_type(self):
        pass

    @abstractmethod
    def load_data(self, address: str = None):
        pass

    @abstractmethod
    def get_value(self, element_id: str):
        pass

    @abstractmethod
    def set_value(self, element_id: str, element_value: any):
        pass

    @abstractmethod
    def send_value(self, element_id: str, element_value: any, sender_selector: str = None):
        pass

    @abstractmethod
    def create_object(self, sender_selector: str = None) -> Optional[int]:
        pass

    @abstractmethod
    def delete_object(self, sender_selector: str = None) -> Optional[int]:
        pass

    @abstractmethod
    def send_data(self, sender_selector: str = None):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def set_path(self, path: str):
        pass

    @abstractmethod
    def has_param_error(self, element_id: str):
        pass

    @abstractmethod  # TODO  реализовать драйверо-незавмсимость
    def search_id_by_name(self, search: dict):
        pass

    @abstractmethod
    def get_current_path(self):
        pass

    @abstractmethod
    def login(self, user, password):
        pass

    @abstractmethod
    def logout(self):
        pass

    @abstractmethod
    def get_driver_name(self):
        pass

    def relogin(self, user, password):
        self.logout()
        self.login(user, password)

    def get_realtime(self, command):
        pass

    def custom_get(self, param):
        pass

    def get_nms_version(self):
        pass

    def add_device(self):
        pass

    def sync_add(self):
        pass
