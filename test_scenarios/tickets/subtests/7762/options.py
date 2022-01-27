from src.drivers.abstract_http_driver import CHROME
from src.options_providers.options_provider import CHROME_CONNECT, CONNECTION

system = {
    CONNECTION: CHROME_CONNECT,
    CHROME_CONNECT: {
        'type': CHROME,
    }
}

options = {
    'tdma_modcodes': [
        'BPSK 1/2',
        'BPSK 2/3',
        'BPSK 3/4',
        'BPSK 5/6',
        'QPSK 1/2',
        'QPSK 2/3',
        'QPSK 3/4',
        'QPSK 5/6',
        '8PSK 1/2',
        '8PSK 2/3',
        '8PSK 3/4',
        '8PSK 5/6',
        '16APSK 1/2',
        '16APSK 2/3',
        '16APSK 3/4',
        '16APSK 5/6',
    ]

}
