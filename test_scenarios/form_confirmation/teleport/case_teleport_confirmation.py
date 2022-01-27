import re
import time

from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes, LatitudeModesStr, LongitudeModesStr, TdmaSearchModesStr
from src.exceptions import NmsControlledModeException
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.nms import Nms
from src.nms_entities.basic_entities.teleport import Teleport
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.form_confirmation.teleport'
backup_name = 'default_config.txt'
_sleep = 1.5


# TODO: make the rest test methods when range is finally set
class TeleportConfirmationCase(CustomTestCase):
    """Confirm that UHP gets correct settings from NMS teleport form"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.27'
    __execution_time__ = 160  # approximate case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls) -> None:
        controller = OptionsProvider.get_uhp_by_model('UHP200', 'UHP200X', number=1)[0]
        cls.mf_hub_uhp = controller.get('web_driver')

        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.teleport_options = OptionsProvider.get_options(options_path).get('teleport')
        cls.nms = Nms(cls.driver, 0, 0)

        Network.create(cls.driver, 0, {'name': 'test_net', 'dev_password': 'tp_conf'})
        cls.tp = Teleport.create(cls.driver, 0, cls.teleport_options)
        cls.mf_hub = Controller.create(cls.driver, 0, {
            'name': 'mf_hub',
            'mode': ControllerModes.MF_HUB,
            'teleport': f'teleport:{cls.tp.get_id()}',
            'device_ip': controller.get('device_ip'),
            'device_vlan': controller.get('device_vlan'),
            'device_gateway': controller.get('device_gateway'),
            'uhp_model': controller.get('model')
        })
        cls.mf_hub_uhp.set_nms_permission(vlan=controller.get('device_vlan'), password='tp_conf')

        if not cls.mf_hub.wait_not_states(['Unknown', 'Unreachable', ]):
            raise NmsControlledModeException('Controller is not under NMS control')

        cls.nms.wait_next_tick()

    def test_teleport_all_at_once(self):
        """Test all predetermined teleport values getting by UHP"""
        uhp_values = self.mf_hub_uhp.get_teleport_values()
        # Teleport name, satellite name are not used in UHP, removing them.
        self.teleport_options.pop('name')
        self.teleport_options.pop('sat_name')

        for key, value in self.teleport_options.items():
            with self.subTest(key, field_name=key, value=value):
                self.assertEqual(value, uhp_values.get(key, None))

    def test_teleport_sat_lon(self):
        for sat_lon_deg, sat_lon_min in ([-179, 0], [-1, 1], [0, 30], [1, 58], [179, 59]):
            self.tp.send_params({'sat_lon_deg': sat_lon_deg, 'sat_lon_min': sat_lon_min})
            self.nms.wait_next_tick()
            time.sleep(_sleep)
            uhp_values = self.mf_hub_uhp.get_timing_values()
            self.assertEqual(uhp_values.get('sat_lon_deg'), str(sat_lon_deg), msg=f'sat_lon_deg differs')
            self.assertEqual(uhp_values.get('sat_lon_min'), str(sat_lon_min), msg=f'sat_lon_min differs')

    def test_teleport_lat(self):
        south, north = LatitudeModesStr.SOUTH, LatitudeModesStr.NORTH
        for lat_deg, lat_min, lat_south in ([0, 0, south], [1, 1, north], [88, 58, north], [89, 59, south]):
            self.tp.send_params({'lat_deg': lat_deg, 'lat_min': lat_min, 'lat_south': lat_south})
            self.nms.wait_next_tick()
            time.sleep(_sleep)
            uhp_values = self.mf_hub_uhp.get_teleport_values()
            self.assertEqual(uhp_values.get('lat_deg'), str(lat_deg), msg=f'lat_deg differs')
            self.assertEqual(uhp_values.get('lat_min'), str(lat_min), msg=f'lat_min differs')
            self.assertEqual(uhp_values.get('lat_south'), str(lat_south), msg=f'lat_south differs')

    def test_teleport_lon(self):
        east, west = LongitudeModesStr.EAST, LongitudeModesStr.WEST
        for lon_deg, lon_min, lon_west in ([0, 0, east], [1, 1, west], [178, 58, west], [179, 59, east]):
            self.tp.send_params({'lon_deg': lon_deg, 'lon_min': lon_min, 'lon_west': lon_west})
            self.nms.wait_next_tick()
            time.sleep(_sleep)
            uhp_values = self.mf_hub_uhp.get_teleport_values()
            self.assertEqual(uhp_values.get('lon_deg'), str(lon_deg), msg=f'lon_deg differs')
            self.assertEqual(uhp_values.get('lon_min'), str(lon_min), msg=f'lon_min differs')
            self.assertEqual(uhp_values.get('lon_west'), str(lon_west), msg=f'lon_west differs')

    def test_teleport_timezone(self):
        for time_zone in range(-12, 13, 4):
            self.tp.send_param('time_zone', time_zone)
            self.nms.wait_next_tick()
            time.sleep(_sleep)
            uhp_time_zone = self.mf_hub_uhp.get_support_info_value(regex=re.compile(r'timezone:\s[-]*[0-9]+'))
            if uhp_time_zone is not None:
                self.assertEqual(uhp_time_zone, str(time_zone), msg=f'time_zone differs')
            else:
                self.fail(f'Cannot obtain UHP timezone value')

    def test_teleport_rx_search_bw(self):
        for dvb_search, tdma_search in (
                [0, TdmaSearchModesStr.BW6],
                [1, TdmaSearchModesStr.BW12],
                [9999, TdmaSearchModesStr.BW24],
                [10000, TdmaSearchModesStr.BW40]
        ):
            self.tp.send_params({'dvb_search': dvb_search, 'tdma_search': tdma_search})
            self.nms.wait_next_tick()
            time.sleep(_sleep)
            uhp_values = self.mf_hub_uhp.get_teleport_values()
            self.assertEqual(uhp_values.get('dvb_search'), str(dvb_search), msg=f'dvb_search differs')
            self.assertEqual(uhp_values.get('tdma_search'), str(tdma_search), msg=f'tdma_search differs')


