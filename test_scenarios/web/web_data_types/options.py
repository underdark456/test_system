from src.custom_logger import LOGGING, OK
from src.options_providers.options_provider import CONNECTION, CHROME_CONNECT

system = {
    LOGGING: OK,
    CONNECTION: CHROME_CONNECT,
    CHROME_CONNECT: {
        'no_gui': True,
    },
}

options = {

}
