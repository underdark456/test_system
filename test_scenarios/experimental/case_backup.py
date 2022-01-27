import json

from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.drivers.uhp.uhp_requests_driver import UhpRequestsDriver
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.experimental'
backup_name = ''

class Case(CustomTestCase):
    """"""

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )


    def set_up(self) -> None:
        pass

    def test(self):
        ctrl_request = UhpRequestsDriver('10.56.27.43')

        temp = ctrl_request.get_teleport_values()
        # print(type(temp))
        # todos = json.loads(temp.text)

        name = temp["name"]
        print(temp)

    def tear_down(self) -> None:
        pass

    @classmethod
    def tear_down_class(cls) -> None:
        pass