from src.drivers.abstract_http_driver import CHROME, FIREFOX, API
from src.drivers.http.api_driver import ApiDriver
from src.drivers.http.web_driver import WebDriver
from src.exceptions import DriverInitException


class DriversProvider(object):
    _drivers = {}

    @classmethod
    def get_driver_instance(cls, driver_options, driver_id='default', store_driver=True):
        """
        Class method for driver creation

        :param dict driver_options: driver options that are used to create a new driver
        :param str driver_id: the ID of the driver, that can be used to get the existing driver instance
        :param bool store_driver: if True driver_id is stored for future usage to get initialized driver by its ID
        :raises DriverInitException: if there is any error associated with creation of the driver
        :returns AbstractHttpDriver driver: an instance of the driver
        """
        _type = driver_options.get('type')
        _address = driver_options.get('address')
        _username = driver_options.get('username')
        _password = driver_options.get('password')
        for drv_id, driver in DriversProvider._drivers.items():
            if drv_id == driver_id and \
                    driver.get_type() == _type and \
                    driver.address == _address and \
                    driver._username == _username and \
                    driver._password == _password and \
                    driver.get_type() == API and \
                    driver._cookies is not None:
                return driver
        # If by some reason there are not all the required options to init a new driver
        # TODO: probably check WEB driver related options as well
        if _type is None or _address is None or _username is None or _password is None:
            raise DriverInitException('Driver type, NMS address, username, and password must be in options')

        driver = None

        if CHROME == driver_options.get("type") or FIREFOX == driver_options.get("type"):
            driver = WebDriver.create_driver(driver_options)
        elif API == driver_options.get("type"):
            driver = ApiDriver.create_driver(driver_options)

        if driver is not None and store_driver:
            DriversProvider._drivers[driver_id] = driver
        return driver
