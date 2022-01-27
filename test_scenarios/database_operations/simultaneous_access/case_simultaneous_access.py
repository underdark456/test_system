from multiprocessing import Process, Manager

import requests

from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.abstract_http_driver import API
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes, StationModes
from src.exceptions import ObjectNotCreatedException, ObjectNotDeletedException
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.user import User
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.database_operations.simultaneous_access'
backup_name = 'default_config.txt'


class ApiSimultaneousAccessCase(CustomTestCase):
    """8 users database operations in parallel"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.20'
    __execution_time__ = 80
    __express__ = False

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)
        cls.net = Network.create(cls.driver, 0, {'name': 'test_net'})
        cls.tp = Teleport.create(cls.driver, 0, {'name': 'test_tp'})
        for i in range(1, 9):
            Controller.create(cls.driver, cls.net.get_id(), {
                'name': f'ctrl-{i}',
                'mode': ControllerModes.MF_HUB,
                'teleport': f'teleport:{cls.tp.get_id()}',
            })
        cls.vno = Vno.create(cls.driver, cls.net.get_id(), {'name': 'test_vno'})
        cls.stn = Station.create(cls.driver, cls.vno.get_id(), {
            'name': 'stn-1',
            'enable': True,
            'serial': 1,
            'mode': StationModes.STAR,
            'rx_controller': f'controller:0',
        })
        nms_ip_port = OptionsProvider.get_connection(options_path).get('address')
        driver_options = {
            'type': API,
            'address': nms_ip_port,
            'username': None,
            'password': None,
            'auto_login': True,
        }
        cls.drivers = []
        for i in range(1, 9):
            username = f'user_{i}'
            password = '12345'
            User.create(cls.driver, 0, params={'name': username, 'password': password})
            driver_options['username'] = username
            driver_options['password'] = password
            driver = DriversProvider.get_driver_instance(driver_options, f'simultaneous_access{i}', store_driver=False)
            cls.drivers.append(driver)

    def test_simultaneous_controller_change(self):
        """8 users change station's rx_controller in parallel"""
        def change_controller(_driver, process_num, _return_dict):
            number_of_iterations = 2000
            for j in range(number_of_iterations):
                try:
                    self.stn.send_param('rx_controller', f'controller:{process_num}')
                except requests.exceptions.ReadTimeout:
                    _return_dict[process_num] = f'no_response_at_iteration_{j}'
                    break
            else:
                _return_dict[process_num] = 'ok'
        processes = []
        manager = Manager()
        return_dict = manager.dict()
        for i in range(len(self.drivers)):
            process = Process(target=change_controller, args=(self.drivers[i], i, return_dict))
            processes.append(process)
        for process in processes:
            process.start()
        for process in processes:
            process.join()
        for proc, result in return_dict.items():
            if result != 'ok':
                self.fail(f'Process {proc} result: {result}')
            else:
                self.ok(f'Process {proc} result: {result}')

    def test_simultaneous_create_delete(self):
        """8 users create and delete networks in parallel"""
        def create_delete(_driver, process_num, _return_dict):
            number_of_iterations = 2000
            for j in range(number_of_iterations):
                try:
                    net = Network.create(_driver, 0, {'name': f'net-{process_num * number_of_iterations + j}'})
                except requests.exceptions.ReadTimeout:
                    _return_dict[process_num] = f'no_response_at_create_iteration_{j}'
                    break
                except ObjectNotCreatedException:
                    continue
                try:
                    net.delete()
                except requests.exceptions.ReadTimeout:
                    _return_dict[process_num] = f'no_response_at_delete_iteration_{j}'
                    break
                except ObjectNotDeletedException:
                    _return_dict[process_num] = f'no_delete_at_iteration_{j}'
            else:
                _return_dict[process_num] = 'ok'
        processes = []
        manager = Manager()
        return_dict = manager.dict()
        for i in range(len(self.drivers)):
            process = Process(target=create_delete, args=(self.drivers[i], i, return_dict))
            processes.append(process)
        for process in processes:
            process.start()
        for process in processes:
            process.join()
        for proc, result in return_dict.items():
            if result != 'ok':
                self.fail(f'Process {proc} result: {result}')
            else:
                self.ok(f'Process {proc} result: {result}')

    def test_network_name_simultaneous_edit(self):
        """8 users edit network name in parallel"""
        def network_name_edit(_driver, process_num, _return_dict):
            number_of_iterations = 2000
            for j in range(number_of_iterations):
                try:
                    self.net.send_param('name', f'net-{process_num * number_of_iterations + j}')
                except requests.exceptions.ReadTimeout:
                    _return_dict[process_num] = f'no_response_at_iteration_{j}'
                    break
            else:
                _return_dict[process_num] = 'ok'

        processes = []
        manager = Manager()
        return_dict = manager.dict()
        for i in range(len(self.drivers)):
            process = Process(target=network_name_edit, args=(self.drivers[i], i, return_dict, ))
            processes.append(process)
        for process in processes:
            process.start()
        for process in processes:
            process.join()
        for proc, result in return_dict.items():
            if result != 'ok':
                self.fail(f'Process {proc} result: {result}')
            else:
                self.ok(f'Process {proc} result: {result}')
