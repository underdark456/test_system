import multiprocessing
import random
from multiprocessing import Process
from time import time
from unittest import skip

import requests

from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.abstract_http_driver import AbstractHttpDriver
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes, StationModes, Checkbox
from src.exceptions import ObjectNotCreatedException
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider

__author__ = 'dkudryashov'
__version__ = '4.0.0.10'
backup_name = 'default_config.txt'
options_path = 'test_scenarios.users'

REPEATS_COUNT = 5000


@skip('No ready')
class UserMultiProcCase(CustomTestCase):
    """Case multiple user processes station creation"""

    @classmethod
    def set_up_class(cls):
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)

        cls.options = OptionsProvider.get_options(options_path)
        cls.system_options = OptionsProvider.get_system_options(options_path)
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.net = Network.create(cls.driver, 0, {'name': 'test_net'})
        cls.vno = Vno.create(cls.driver, cls.net.get_id(), {'name': 'test_vno'})
        cls.tp = Teleport.create(cls.driver, cls.net.get_id(), {'name': 'test_tp'})
        cls.controllers = []
        for i in range(5):
            ctrl = Controller.create(cls.driver, cls.net.get_id(), {
                'name': f'test_ctrl{i}',
                'mode': ControllerModes.MF_HUB,
                'teleport': f'teleport:{cls.tp.get_id()}',
            })
            cls.controllers.append(ctrl)

        cls.queue = multiprocessing.Queue()

    # noinspection PyMethodMayBeStatic
    def test_concurrently_station_create(self):
        """Several users concurrent station creation test"""
        def handler(user_num, driver: AbstractHttpDriver, queue: multiprocessing.Queue, repeats_count: int):
            name = F"user {user_num}"
            print(F"{name} started at {time()}")
            params = {
                'mode': StationModes.STAR,
                'enable': Checkbox.ON,
            }
            for i in range(repeats_count):
                number = user_num * repeats_count + i + 1
                params['name'] = F"{name} {number}"
                params['serial'] = F"{user_num}{number}"
                params['rx_controller'] = f'controller:{self.controllers[random.randint(0, len(self.controllers) - 1)]}'
                s = Station(driver, self.vno.get_id(), -1, params)
                try:
                    s.save()
                except ObjectNotCreatedException as e:
                    queue.put({'name': name, 'error': e})
                except requests.exceptions.ReadTimeout as e:
                    queue.put({'name': name, 'error': e})

            print(F"{user_name} ended at {time()}")

        # ====================================================================================================
        options = OptionsProvider.get_options(options_path)
        num = 0
        processes = []
        for user_name, user_params in options['users'].items():
            driver = DriversProvider.get_driver_instance(OptionsProvider.get_connection(), user_name)
            processes.append(Process(
                target=handler,
                args=(num, driver, self.queue, REPEATS_COUNT)
            ))
            num += 1
        for process in processes:
            process.start()
        for process in processes:
            process.join()
        print('end all')
