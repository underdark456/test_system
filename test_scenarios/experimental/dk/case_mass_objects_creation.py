import ipaddress
import random
import time
from multiprocessing import Process
from unittest import skip

import requests

from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes, StationModes, RouteTypes, LatitudeModes, LongitudeModes, \
    CheckboxStr, RuleTypes, CheckTypes, ActionTypes
from src.exceptions import ObjectNotCreatedException
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.controller_route import ControllerRoute
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.policy import Policy
from src.nms_entities.basic_entities.policy_rule import PolicyRule
from src.nms_entities.basic_entities.service import Service
from src.nms_entities.basic_entities.shaper import Shaper
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.user import User
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider

option_path = 'test_scenarios.creating_objects'
backup = 'default_config.txt'


class MassObjectsCreationCase(CustomTestCase):
    """Create maximum number of objects in tables"""

    __author__ = 'dkudryashov'
    __version__ = '0.1'
    __execution_time__ = 18520  # approximate test case execution time in seconds

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(option_path)
        )
        cls.backup = BackupManager()

    def set_up(self):
        self.backup.apply_backup(backup)

    @skip('Not needed as a bigger test exists')
    def test_512_vnos_creating(self):
        """512 VNOs creation test"""
        options = OptionsProvider.get_options(option_path)
        net = Network.create(self.driver, 0, params={'name': 'net'})

        for i in range(1, 513):
            options['vno']['values']['name'] = 'VNO-' + str(i)
            vno = Vno.create(
                self.driver,
                net.get_id(),
                params={'name': f'vno-{i}'}
            )
            self.assertIsNotNone(vno.get_id())
        # Check that VNO table is cleared upon calling default config (ticket 7722)
        self.backup.apply_backup(backup)
        net = Network.create(self.driver, 0, params={'name': 'net'})
        for i in range(1, 513):
            options['vno']['values']['name'] = 'VNO-' + str(i)
            vno = Vno.create(
                self.driver,
                net.get_id(),
                params={'name': f'vno-{i}'}
            )
            self.assertIsNotNone(vno.get_id())

    @skip('Not needed as a bigger test exists')
    def test_65000_routes_creation_deletion(self):
        """Create maximum number of routes (65000) and delete them one by one"""
        Network.create(self.driver, 0, params={'name': 'net1'})
        Teleport.create(self.driver, 0, params={'name': 'tp1'})
        Controller.create(
            self.driver,
            0,
            params={'name': 'ctrl1', 'mode': ControllerModes.HUBLESS_MASTER, 'teleport': f'teleport:0'}
        )
        Service.create(self.driver, 0, {'name': 'test_service'})
        ip_addresses_pool = ipaddress.IPv4Network('172.16.0.0/16').hosts()
        st_time = time.perf_counter()
        for i in range(1, 65001):
            next_ip = str(next(ip_addresses_pool))
            ControllerRoute.create(self.driver, 0, {
                'type': RouteTypes.IP_ADDRESS,
                'service': 'service:0',
                'ip': next_ip,
                'mask': '/32',
            })

        self.info(f'65000 routes creation time is {time.perf_counter() - st_time} seconds')
        # Getting a list of routes in controller 0 (cannot get them all at once due to 8 Mbytes response limit)
        routes1 = ControllerRoute.controller_route_list(self.driver, 0, vars_=['ip'], max_=30000)
        routes2 = ControllerRoute.controller_route_list(self.driver, 0, vars_=['ip'], skip=30000)
        self.assertEqual(65000, len(routes1) + len(routes2), msg='65000 routes created in one controller')

        del_time = time.perf_counter()
        for i in range(65000):
            ControllerRoute(self.driver, 0, i).delete()
        routes_after = ControllerRoute.controller_route_list(self.driver, 0, vars_=['ip'])
        self.info(f'65000 routes deletion time is {time.perf_counter() - del_time} seconds')
        self.info(f'65000 routes creation/deletion time is {time.perf_counter() - st_time} seconds')
        self.assertEqual(0, len(routes_after), msg='all the routes have been deleted')

    @skip('Has to be fixed - do no change username and password in options')
    def test_station_create_delete_multiprocessing(self):
        """Create and delete maximum number of stations using 8 processes (1 iteration)"""
        # Each process creates 4096 stations and deletes them afterwards.
        # The create-delete cycle has 10 iterations.

        def create_delete_cycle(_driver, number, process_num):
            # TODO: change the value
            for iteration in range(1):
                stations = []
                for j in range(number, number + 4096):
                    try:
                        stn = Station.create(_driver, 0, params={
                            'name': f'stn-{j}',
                            'enable': 'ON',
                            'serial': j + 1,
                            'mode': StationModes.MESH,
                            'rx_controller': 'controller:0'
                        })
                    except ObjectNotCreatedException as exc:
                        self.critical(f'Process {process_num} create iteration {iteration + 1} station {j} not created')
                        raise exc
                    except requests.exceptions.ReadTimeout as exc:
                        self.critical(f'Process {process_num} create iteration {iteration + 1} station {j} no response')
                        raise exc
                    stations.append(stn)
                for j in range(len(stations)):
                    try:
                        stations[j].delete()
                    except requests.exceptions.ReadTimeout as exc:
                        self.critical(f'Process {process_num} delete iteration '
                                      f'{iteration + 1} station {j} unsuccessful')
                        raise exc

        Network.create(self.driver, 0, params={'name': 'net1'})
        Vno.create(self.driver, 0, params={'name': 'vno1'})
        Teleport.create(self.driver, 0, params={'name': 'tp1'})
        Controller.create(self.driver, 0,
                          params={'name': 'ctrl1', 'mode': ControllerModes.HUBLESS_MASTER, 'teleport': f'teleport:0'})
        # Create 8 users in UserGroup ID 0 (Admins) - the group has full access
        driver_options = OptionsProvider.get_connection(option_path)
        drivers = []
        processes = []
        for i in range(1, 8):
            username = f'admin{i}'
            password = '12345'
            User.create(self.driver, 0, params={'name': username, 'password': password})
            driver_options['username'] = username
            driver_options['password'] = password
            driver = DriversProvider.get_driver_instance(driver_options, f'admin{i}')
            drivers.append(driver)
        for i in range(len(drivers)):
            process = Process(target=create_delete_cycle, args=(drivers[i], int(32768 / 8) * i, i))
            processes.append(process)
        for process in processes:
            process.start()
        for process in processes:
            process.join()

    @skip('Not needed as a bigger test exists')
    def test_all_shapers_in_one_net(self):
        """Create maximum number of shapers in one net"""
        Network.create(self.driver, 0, {'name': 'test_net'})
        for i in range(2048):
            Shaper.create(self.driver, 0, {
                'name': f'shaper-{i}',
                'template': random.choice([*CheckboxStr()]),
                'max_enable': random.choice([*CheckboxStr()]),
                'min_enable': random.choice([*CheckboxStr()]),
                'wfq_enable': random.choice([*CheckboxStr()]),
                'night_enable': random.choice([*CheckboxStr()]),
            })

    @skip('Not needed as a bigger test exists')
    def test_all_polrules(self):
        """Maximum number of pol_rule creation test"""
        Network.create(self.driver, 0, {'name': 'test_net'})
        number_of_polrules = 0
        for i in range(512):
            pol = Policy.create(self.driver, 0, {'name': f'biggest_policy-{i}'})
            if number_of_polrules > 9999:
                break
            sequence = 1
            for j in range(random.randint(17, 25)):
                if random.random() > 0.5:
                    check = random.choice([*CheckTypes()])
                    PolicyRule.create(self.driver, pol.get_id(), {
                        'sequence': sequence,
                        'type': RuleTypes.CHECK,
                        'check_type': check
                    })

                else:
                    action = [*ActionTypes()]
                    action.remove(str(ActionTypes.CALL_POLICY))
                    action.remove(str(ActionTypes.GOTO_POLICY))
                    PolicyRule.create(self.driver, pol.get_id(), {
                        'sequence': sequence,
                        'type': RuleTypes.ACTION,
                        'action_type': random.choice(action)
                    })
                sequence += 1
                number_of_polrules += 1
                if number_of_polrules == 10000:
                    break
