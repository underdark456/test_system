from src.drivers.abstract_http_driver import CHROME
from src.options_providers.options_provider import CHROME_CONNECT, CONNECTION

system = {
    CHROME_CONNECT: {
        'type': CHROME,
        'no_gui': False,
        'maximize_window': True,
        # 'window_size': (1920, 1080),
    },
    CONNECTION: CHROME_CONNECT,
}

options = {

}
