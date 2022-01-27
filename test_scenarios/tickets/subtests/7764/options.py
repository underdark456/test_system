from src.drivers.abstract_http_driver import CHROME
from src.options_providers.options_provider import CONNECTION, CHROME_CONNECT

system = {
    CHROME_CONNECT: {
        'type': CHROME,
        'no_gui': False
    },
    CONNECTION: CHROME_CONNECT
}

options = {

}
