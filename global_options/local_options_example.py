# данный файл просто образец переопределения параметров.
# он НИКАК не влияет на систему тестирования
from src.custom_logger import *
from src.options_providers.options_provider import CHROME_CONNECT, API_CONNECT, CONNECTION

_host = "http://some_nms_address/"

system = {
    CHROME_CONNECT: {
        'address': _host,  # переопределяем адрес
        'driver_path': 'path/to/selenium/driver'  # переопределяем путь к бинарнику селениума
    },
    API_CONNECT: {
        'address': _host,  # переопределяем адрес
    },

    # default connection
    CONNECTION: CHROME_CONNECT,  # переопределяем дефолтный драйвер

    LOGGING: DEBUG
}

options = {

}
