import time

from src.drivers.drivers_provider import DriversProvider
from src.options_providers.options_provider import OptionsProvider, FIREFOX_CONNECT, CHROME_CONNECT


def clear_firefox():
    nms_web_driver = DriversProvider.get_driver_instance(
        OptionsProvider.get_connection('global_options', FIREFOX_CONNECT),
        driver_id='clear_local_storage',
        store_driver=False
    )
    nms_web_driver.driver.execute_script('window.localStorage.clear();')


def clear_chrome():
    nms_web_driver = DriversProvider.get_driver_instance(
        OptionsProvider.get_connection('global_options', CHROME_CONNECT),
        driver_id='clear_local_storage',
        store_driver=False
    )
    nms_web_driver.driver.execute_script('window.localStorage.clear();')
    time.sleep(30)


if __name__ == '__main__':
    clear_chrome()
