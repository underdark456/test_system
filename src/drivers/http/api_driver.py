import requests

from src.drivers.abstract_http_driver import API
from src.drivers.http.nms_api_driver import NmsApiDriver
from src.exceptions import DriverInitException


class ApiDriver(object):

    @classmethod
    def create_driver(cls, driver_options=None):
        driver_type = driver_options.get("type")
        if driver_options is not None:
            driver = None
            if API == driver_type:
                driver = ApiDriver._create_api_driver(driver_type, driver_options)
            if driver is None:
                raise DriverInitException
            if driver_options.get('auto_login'):
                driver.login(driver_options.get('username'), driver_options.get('password'))
        else:
            raise DriverInitException('empty options')
        return driver

    @classmethod
    def _create_api_driver(cls, driver_type, driver_options):
        driver = requests
        drv = NmsApiDriver(driver_type, driver)
        drv.address = driver_options.get('address')
        return drv
