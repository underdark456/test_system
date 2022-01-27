import time

from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.drivers.uhp.uhp_requests_driver import UhpRequestsDriver
from src.enum_types_constants import ControllerModes, Checkbox, TtsModes, StationModes, RouteTypes, RouteIds
from src.exceptions import UhpResponseException
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.controller_route import ControllerRoute
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.service import Service
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.station_route import StationRoute
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.composite_scenarios.network_up'
backup_name = 'default_config.txt'


class NetworkMfHubUpCase(CustomTestCase):
    """1 controller 3 stations up case"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.26'
    __execution_time__ = 95  # approximate test case execution time in seconds

    @classmethod
    def set_up_class(cls):
        controllers, stations = OptionsProvider.get_uhp_controllers_stations(1, ['UHP200', 'UHP200X'], 3, ['ANY', ])

        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)

        cls.system_options = OptionsProvider.get_system_options(options_path)
        cls.options = OptionsProvider.get_options(options_path)

        cls.uhp1_driver = UhpRequestsDriver(controllers[0].get('device_ip'))
        cls.uhp2_driver = UhpRequestsDriver(stations[0].get('device_ip'))
        cls.uhp3_driver = UhpRequestsDriver(stations[1].get('device_ip'))
        cls.uhp4_driver = UhpRequestsDriver(stations[2].get('device_ip'))

        cls.net = Network.create(cls.driver, 0, {'name': 'test_network'})
        cls.tp = Teleport.create(
            cls.driver,
            cls.net.get_id(),
            {'name': 'test_tp', 'tx_lo': 0, 'rx1_lo': 0, 'rx2_lo': 0}
        )

        cls.mf_hub = Controller.create(cls.driver, cls.net.get_id(), {
            'name': 'test_ctrl',
            'mode': ControllerModes.MF_HUB,
            'teleport': f'teleport:{cls.tp.get_id()}',
            'device_ip': controllers[0].get('device_ip'),
            'device_vlan': controllers[0].get('device_vlan'),
            'device_gateway': controllers[0].get('device_gateway'),
            'uhp_model': controllers[0].get('model'),
            'tx_on': Checkbox.ON,
            'tx_level': cls.options.get('tx_level'),
            'hub_tts_mode': TtsModes.VALUE
        })
        cls.vno = Vno.create(cls.driver, cls.net.get_id(), {'name': 'test_vno'})

        cls.ser_stn1 = Service.create(cls.driver, cls.net.get_id(), {
            'name': 'ser_stn1',
            'hub_vlan': controllers[0].get('device_vlan'),
            'stn_vlan': stations[0].get('device_vlan'),
            'ctr_normal': Checkbox.OFF,
            'ctr_gateway': Checkbox.OFF,
            'ctr_mesh': Checkbox.OFF,
            'stn_normal': Checkbox.OFF,
            'stn_gateway': Checkbox.OFF,
            'stn_mesh': Checkbox.OFF,
        })

        cls.ser_stn2 = Service.create(cls.driver, cls.net.get_id(), {
            'name': 'ser_stn2',
            'hub_vlan': controllers[0].get('device_vlan'),
            'stn_vlan': stations[1].get('device_vlan'),
            'ctr_normal': Checkbox.OFF,
            'ctr_gateway': Checkbox.OFF,
            'ctr_mesh': Checkbox.OFF,
            'stn_normal': Checkbox.OFF,
            'stn_gateway': Checkbox.OFF,
            'stn_mesh': Checkbox.OFF,
        })

        cls.ser_stn3 = Service.create(cls.driver, cls.net.get_id(), {
            'name': 'ser_stn3',
            'hub_vlan': controllers[0].get('device_vlan'),
            'stn_vlan': stations[2].get('device_vlan'),
            'ctr_normal': Checkbox.OFF,
            'ctr_gateway': Checkbox.OFF,
            'ctr_mesh': Checkbox.OFF,
            'stn_normal': Checkbox.OFF,
            'stn_gateway': Checkbox.OFF,
            'stn_mesh': Checkbox.OFF,
        })
        cls.ser_ping = Service.create(cls.driver, cls.net.get_id(), {
            'name': 'ping_service',
            'hub_vlan': 206,
            'stn_vlan': 306,
            'stn_normal': Checkbox.ON,
        })

        cls.stn1 = Station.create(cls.driver, cls.vno.get_id(), {
            'name': 'test_stn1',
            'enable': Checkbox.ON,
            'serial': stations[0].get('serial'),
            'mode': StationModes.STAR,
            'rx_controller': f'controller:{cls.mf_hub.get_id()}',
        })

        cls.stn2 = Station.create(cls.driver, cls.vno.get_id(), {
            'name': 'test_stn2',
            'enable': Checkbox.ON,
            'serial': stations[1].get('serial'),
            'mode': StationModes.STAR,
            'rx_controller': f'controller:{cls.mf_hub.get_id()}',
        })

        cls.stn3 = Station.create(cls.driver, cls.vno.get_id(), {
            'name': 'test_stn3',
            'enable': Checkbox.ON,
            'serial': stations[2].get('serial'),
            'mode': StationModes.STAR,
            'rx_controller': f'controller:{cls.mf_hub.get_id()}',
        })
        ControllerRoute.create(cls.driver, cls.mf_hub.get_id(), {
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:{cls.ser_ping.get_id()}',
            'ip': '192.168.0.1',
        })
        ControllerRoute.create(cls.driver, cls.mf_hub.get_id(), {
            'type': RouteTypes.NETWORK_RX,
            'service': f'service:{cls.ser_ping.get_id()}',
        })

        StationRoute.create(cls.driver, cls.stn1.get_id(), {
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:{cls.ser_stn1.get_id()}',
            'ip': stations[0].get('device_ip'),
            'id': RouteIds.PRIVATE,
        })
        StationRoute.create(cls.driver, cls.stn1.get_id(), {
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:{cls.ser_ping.get_id()}',
            'ip': '192.168.1.1',
            'id': RouteIds.PRIVATE,
        })
        StationRoute.create(cls.driver, cls.stn2.get_id(), {
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:{cls.ser_stn2.get_id()}',
            'ip': stations[1].get('device_ip'),
            'id': RouteIds.PRIVATE,
        })
        StationRoute.create(cls.driver, cls.stn2.get_id(), {
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:{cls.ser_ping.get_id()}',
            'ip': '192.168.2.1',
            'id': RouteIds.PRIVATE,
        })
        StationRoute.create(cls.driver, cls.stn3.get_id(), {
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:{cls.ser_stn3.get_id()}',
            'ip': stations[2].get('device_ip'),
            'id': RouteIds.PRIVATE,
        })
        StationRoute.create(cls.driver, cls.stn3.get_id(), {
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:{cls.ser_ping.get_id()}',
            'ip': '192.168.3.1',
            'id': RouteIds.PRIVATE,
        })
        StationRoute.create(cls.driver, cls.stn1.get_id(), {
            'type': RouteTypes.STATIC_ROUTE,
            'service': f'service:{cls.ser_stn1.get_id()}',
            'ip': '0.0.0.0',
            'mask': '/0',
            'gateway': stations[0].get('device_gateway'),
            'id': RouteIds.PRIVATE,
        })
        StationRoute.create(cls.driver, cls.stn2.get_id(), {
            'type': RouteTypes.STATIC_ROUTE,
            'service': f'service:{cls.ser_stn2.get_id()}',
            'ip': '0.0.0.0',
            'mask': '/0',
            'gateway': stations[1].get('device_gateway'),
            'id': RouteIds.PRIVATE,
        })
        StationRoute.create(cls.driver, cls.stn3.get_id(), {
            'type': RouteTypes.STATIC_ROUTE,
            'service': f'service:{cls.ser_stn3.get_id()}',
            'ip': '0.0.0.0',
            'mask': '/0',
            'gateway': stations[2].get('device_gateway'),
            'id': RouteIds.PRIVATE,
        })

        cls.uhp1_driver.set_nms_permission(vlan=controllers[0].get('device_vlan'), password='')
        cls.uhp2_driver.star_station(params={
            'rx1_frq': cls.mf_hub.get_param('rx1_frq'),
            'rx1_sr': cls.mf_hub.get_param('rx1_sr'),
            'tx_level': cls.options.get('tx_level'),
        })
        cls.uhp3_driver.star_station(params={
            'rx1_frq': cls.mf_hub.get_param('rx1_frq'),
            'rx1_sr': cls.mf_hub.get_param('rx1_sr'),
            'tx_level': cls.options.get('tx_level'),
        })
        cls.uhp4_driver.star_station(params={
            'rx1_frq': cls.mf_hub.get_param('rx1_frq'),
            'rx1_sr': cls.mf_hub.get_param('rx1_sr'),
            'tx_level': cls.options.get('tx_level'),
        })

        if not cls.mf_hub.wait_up(timeout=60):
            raise UhpResponseException('Controller is not UP')

        if not cls.stn1.wait_up():
            raise UhpResponseException('Station 1 is not UP')

        if not cls.stn2.wait_up():
            raise UhpResponseException('Station 2 is not UP')

        if not cls.stn3.wait_up():
            raise UhpResponseException('Station 3 is not UP')

    def test_network_up(self):
        st_time = time.perf_counter()
        while time.perf_counter() - st_time < 10:
            self.assertEqual(
                'operation',
                self.uhp1_driver.get_state(),
                msg=f'Controller UHP state is not operation ({self.uhp1_driver.get_state()}) '
                    f'after {time.perf_counter() - st_time} seconds'
            )

            self.assertEqual(
                'operation',
                self.uhp2_driver.get_state(),
                msg=f'Station 1 UHP state is not operation ({self.uhp2_driver.get_state()}) '
                    f'after {time.perf_counter() - st_time} seconds'
            )

            self.assertEqual(
                'operation',
                self.uhp3_driver.get_state(),
                msg=f'Station 2 UHP state is not operation ({self.uhp3_driver.get_state()}) '
                    f'after {time.perf_counter() - st_time} seconds'
            )

            self.assertEqual(
                'operation',
                self.uhp3_driver.get_state(),
                msg=f'Station 3 UHP state is not operation ({self.uhp4_driver.get_state()}) '
                    f'after {time.perf_counter() - st_time} seconds'
            )

            self.assertEqual(
                'Up',
                self.mf_hub.get_param('state'),
                msg=f'Controller is not Up after {time.perf_counter() - st_time} seconds')

            self.assertEqual(
                'Up',
                self.stn1.get_param('state'),
                msg=f'Station 1 is not Up after {time.perf_counter() - st_time} seconds')

            self.assertEqual(
                'Up',
                self.stn2.get_param('state'),
                msg=f'Station 2 is not Up after {time.perf_counter() - st_time} seconds')

            self.assertEqual(
                'Up',
                self.stn3.get_param('state'),
                msg=f'Station 3 is not Up after {time.perf_counter() - st_time} seconds')

            self.assertEqual(
                3,
                self.mf_hub.get_param('tx_up_stations'),
                msg=f'Controller TX UP stations is not 3 after {time.perf_counter() - st_time} seconds'
            )

            self.assertEqual(
                3,
                self.mf_hub.get_param('rx_up_stations'),
                msg=f'Controller RX UP stations is not 3 after {time.perf_counter() - st_time} seconds'
            )

            self.assertEqual(
                0,
                self.mf_hub.get_param('tx_down_stations'),
                msg=f'Controller TX Down stations is not 0 after {time.perf_counter() - st_time} seconds'
            )

            self.assertEqual(
                0,
                self.mf_hub.get_param('rx_down_stations'),
                msg=f'Controller RX DOWN stations is not 0 after {time.perf_counter() - st_time} seconds'
            )

            self.assertEqual(
                0,
                self.mf_hub.get_param('tx_off_stations'),
                msg=f'Controller TX OFF stations is not 0 after {time.perf_counter() - st_time} seconds'
            )

            self.assertEqual(
                0,
                self.mf_hub.get_param('rx_off_stations'),
                msg=f'Controller RX OFF stations is not 0 after {time.perf_counter() - st_time} seconds'
            )

            self.assertEqual(
                0,
                self.mf_hub.get_param('tx_fault_stations'),
                msg=f'Controller TX FAULT stations is not 0 after {time.perf_counter() - st_time} seconds'
            )

            self.assertEqual(
                0,
                self.mf_hub.get_param('rx_fault_stations'),
                msg=f'Controller RX FAULT stations is not 0 after {time.perf_counter() - st_time} seconds'
            )
            time.sleep(10)
