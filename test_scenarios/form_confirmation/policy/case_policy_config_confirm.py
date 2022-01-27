import re

from src.backup_manager.backup_manager import BackupManager
from src.constants import NO_ERROR
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import RouteTypes
from src.exceptions import NmsControlledModeException
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.nms import Nms
from src.nms_entities.basic_entities.policy_rule import PolicyRule
from src.nms_entities.basic_entities.service import Service
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.station_route import StationRoute
from src.options_providers.options_provider import OptionsProvider, API_CONNECT

options_path = 'test_scenarios.form_confirmation.policy'
backup_name = 'case_policy_config_confirm.txt'


class PolicyConfigConfirmationCase(CustomTestCase):
    """Confirm that a simple policy containing every rule type is applied to a UHP controller and a station"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.20'
    __execution_time__ = 65  # approximate test case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        controllers, stations = OptionsProvider.get_uhp_controllers_stations(1, ['UHP200', 'UHP200X'], 1, ['ANY'])

        cls.uhp1_ip = controllers[0].get('device_ip')
        cls.uhp2_ip = stations[0].get('device_ip')
        cls.hl_mas_uhp = controllers[0].get('web_driver')
        cls.hl_stn_uhp = stations[0].get('web_driver')

        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(options_path, API_CONNECT)
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)

        cls.options = OptionsProvider.get_options(options_path)
        cls.system_options = OptionsProvider.get_system_options(options_path)

        cls.nms = Nms(cls.driver, 0, 0)
        cls.net = Network(cls.driver, 0, 0)
        cls.net.send_param('dev_password', 'none')

        cls.hl_mas = Controller(cls.driver, 0, 0)
        cls.hl_mas.send_params({
            'device_ip': cls.uhp1_ip,
            'device_vlan': controllers[0].get('device_vlan'),
            'device_gateway': controllers[0].get('device_gateway'),
            'tx_level': cls.options.get('tx_level'),
        }
        )

        cls.stn = Station(cls.driver, 0, 0)
        cls.stn.send_param('serial', stations[0].get('serial'))

        cls.service2 = Service.create(
            cls.driver,
            cls.net.get_id(),
            {'name': 'uhp2_service', 'stn_vlan': stations[0].get('device_vlan')}
        )
        StationRoute.create(cls.driver, cls.stn.get_id(), {
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:{cls.service2.get_id()}',
            'ip': cls.uhp2_ip,
            'mask': '/24',
        })
        StationRoute.create(cls.driver, cls.stn.get_id(), {
            'type': RouteTypes.STATIC_ROUTE,
            'service': f'service:{cls.service2.get_id()}',
            'ip': '0.0.0.0',
            'mask': '/0',
            'gateway': stations[0].get('device_gateway')
        })
        cls.hl_stn_uhp.hubless_station(
            params={
                'frame_length': 64,
                'slot_length': 8,
                'stn_number': 10,
                'mf1_rx': 1000000,
                'mf1_tx': 1000000,
                'tdma_sr': 1000,
                'tdma_mc': 4,
                'timeout': 250,
                'tx_level': cls.options.get('tx_level')
            }
        )
        cls.hl_mas_uhp.set_nms_permission(password='none', vlan=controllers[0].get('device_vlan'))

        if not cls.hl_mas.wait_up():
            raise NmsControlledModeException(f'Controller {cls.uhp1_ip} is not in UP state')

        if not cls.stn.wait_up():
            raise NmsControlledModeException(f'Station {cls.uhp2_ip} is not in UP state')

        cls.nms.wait_ticks(2)

    def test_controller_policy_config_confirm(self):
        """Policy get by UHP controller confirmation"""
        rules_id = PolicyRule.policy_rules_list(self.driver, 0)
        self.assertEqual(31, len(rules_id))
        for rule_id in rules_id:
            path = f'api/object/get/polrule={rule_id}'
            reply, error, error_code = self.driver.custom_get(path)
            self.assertEqual(NO_ERROR, error_code)
            # Removing not tested keys
            reply.pop('%row')
            reply.pop('next')
            reply.pop('uprow')
            reply.pop('sequence')
            uhp_res = self.hl_mas_uhp.get_policy_rule(polrule=rule_id)
            for key, value in reply.items():
                # Special formatting for Set_TS_ch
                if key == 'shaper':
                    val_reg = re.search(r'shaper:[0-9]+', value)
                    if val_reg is not None:
                        value = str(int(val_reg.group().split(':')[-1]) + 1)
                # UHP stores policies as policy number, therefore, policy ID should be `2`
                elif key == 'policy':
                    value = '2'
                with self.subTest(f'NMS polrule={rule_id} key={key} value={value}'):
                    # Special check for queue, as it stores differently in NMS and UHP
                    self.assertIn(key, uhp_res.keys())
                    if key == 'queue':
                        self.assertTrue(uhp_res.get(key).find(str(value)))
                    else:
                        self.assertEqual(str(value).rstrip(), str(uhp_res.get(key)))

    def test_station_policy_config_confirm(self):
        """Policy get by UHP station confirmation"""
        rules_id = PolicyRule.policy_rules_list(self.driver, 0)
        self.assertEqual(31, len(rules_id))
        for rule_id in rules_id:
            path = f'api/object/get/polrule={rule_id}'
            reply, error, error_code = self.driver.custom_get(path)
            self.assertEqual(NO_ERROR, error_code)
            # Removing not tested keys
            reply.pop('%row')
            reply.pop('next')
            reply.pop('uprow')
            reply.pop('sequence')
            uhp_res = self.hl_stn_uhp.get_policy_rule(polrule=rule_id)
            for key, value in reply.items():
                # Special formatting for Set_TS_ch
                if key == 'shaper':
                    val_reg = re.search(r'shaper:[0-9]+', value)
                    if val_reg is not None:
                        value = str(int(val_reg.group().split(':')[-1]) + 1)
                # UHP stores policies as policy number, therefore, policy ID should be `2`
                elif key == 'policy':
                    value = '2'
                with self.subTest(f'NMS polrule={rule_id} key={key} value={value}'):
                    # Special check for queue, as it stores differently in NMS and UHP
                    self.assertIn(key, uhp_res.keys())
                    if key == 'queue':
                        self.assertTrue(uhp_res.get(key).find(str(value)))
                    else:
                        self.assertEqual(str(value).rstrip(), str(uhp_res.get(key)))
