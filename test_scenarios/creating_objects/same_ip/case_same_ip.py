import ipaddress

from src.backup_manager.backup_manager import BackupManager
from src.constants import NEW_OBJECT_ID
from src.custom_test_case import CustomTestCase
from src.drivers.abstract_http_driver import API
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes, CheckboxStr, DeviceModes, ControlModes, DeviceModesStr, \
    RouteTypes, StationModes
from src.exceptions import ObjectNotCreatedException
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.controller_route import ControllerRoute
from src.nms_entities.basic_entities.device import Device
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.service import Service
from src.nms_entities.basic_entities.sr_controller import SrController
from src.nms_entities.basic_entities.sr_teleport import SrTeleport
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.station_route import StationRoute
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider, CHROME_CONNECT

options_path = 'test_scenarios.creating_objects.same_ip'
backup_name = 'default_config.txt'


class SameIpCase(CustomTestCase):
    """Create objects with same IP addresses"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.21'
    __execution_time__ = 90  # approximate test case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        driver_options = OptionsProvider.get_connection()
        cls.driver = DriversProvider.get_driver_instance(
            driver_options
        )
        cls.web_driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(options_path, CHROME_CONNECT)
        )
        cls.backup = BackupManager()

    def test_controller(self):
        """Create two controllers (control=full) with same device_ip via WEB and API"""
        for driver in (self.driver, self.web_driver):
            self.backup.apply_backup(backup_name)
            net = Network.create(driver, 0, {'name': 'test_net'})
            tp = Teleport.create(driver, net.get_id(), {'name': 'test_tp', 'tx_lo': 0, 'rx1_lo': 0, 'rx2_lo': 0})
            Controller.create(driver, net.get_id(), {
                'name': 'test_ctrl',
                'mode': ControllerModes.HUBLESS_MASTER,
                'teleport': f'teleport:{tp.get_id()}',
                'device_ip': '127.0.0.2',
                'device_gateway': '127.0.0.1',
                'tx_on': CheckboxStr.ON
            })
            for i in range(2, 4):
                ctrl = Controller.create(driver, net.get_id(), {
                    'name': f'test_ctrl{i}',
                    'mode': ControllerModes.MF_HUB,
                    'teleport': f'teleport:{tp.get_id()}',
                    'device_ip': '127.0.0.2',
                    'device_gateway': '127.0.0.1',
                    'tx_on': CheckboxStr.ON,
                    'control': ControlModes.NO_ACCESS
                })
                with self.subTest(f'driver={driver.get_driver_name()}'):
                    ctrl.send_param('control', ControlModes.FULL)
                    if driver.get_type() == API:
                        self.assertTrue(ctrl.has_param_error('control'))
                    # Cannot get error by param name as `Bad Value: IP address already in use` error appear
                    else:
                        self.assertEqual(str(ControlModes.NO_ACCESS), ctrl.get_param('control'))

    def test_device(self):
        """Create three devices (control=full): first with unique IP, the rest with the same via WEB and API"""
        for driver in (self.driver, self.web_driver):
            self.backup.apply_backup(backup_name)
            net = Network.create(driver, 0, {'name': 'test_net'})
            tp = Teleport.create(driver, net.get_id(), {'name': 'test_tp', 'tx_lo': 0, 'rx1_lo': 0, 'rx2_lo': 0})
            sr_ctrl = SrController.create(self.driver, net.get_id(), {
                'name': 'test_sr_ctrl',
                'enable': CheckboxStr.ON
            })
            sr_tp = SrTeleport.create(self.driver, sr_ctrl.get_id(), {
                'name': 'test_sr_tp',
                'teleport': f'teleport:{tp.get_id()}'
            })
            Device.create(self.driver, sr_tp.get_id(), {
                'name': 'test_dev1',
                'mode': DeviceModes.USED,
                'mask': '/24',
                'ip': '127.0.0.2',
            })
            Device.create(self.driver, sr_tp.get_id(), {
                'name': f'test_dev2',
                'mode': DeviceModes.USED,
                'mask': '/24',
                'ip': '127.0.0.3',
            })
            for i in range(3, 5):
                dev = Device.create(self.driver, sr_tp.get_id(), {
                    'name': f'test_dev{i}',
                    'mode': DeviceModes.NO_ACCESS,
                    'mask': '/24',
                    'ip': '127.0.0.3',
                })
                with self.subTest(f'driver={driver.get_driver_name()}'):
                    dev.send_param('mode', DeviceModes.USED)
                    if driver.get_type() == API:
                        self.assertTrue(dev.has_param_error('mode'))
                    # Cannot get error by param name as `Bad Value: IP address already in use` error appear
                    else:
                        self.assertEqual(str(DeviceModesStr.NO_ACCESS), dev.get_param('mode'))

    def test_ctrl_and_device(self):
        """Create a controller and a device with the same IPv4 address"""
        for driver in (self.driver, self.web_driver):
            self.backup.apply_backup(backup_name)
            net = Network.create(self.driver, 0, {'name': 'test_net'})
            tp = Teleport.create(self.driver, net.get_id(), {'name': 'test_tp', 'tx_lo': 0, 'rx1_lo': 0, 'rx2_lo': 0})
            sr_ctrl = SrController.create(self.driver, net.get_id(), {'name': 'test_sr_ctrl', 'enable': CheckboxStr.ON})
            sr_tp = SrTeleport.create(self.driver, sr_ctrl.get_id(),
                                      {'name': 'test_sr_tp', 'teleport': f'teleport:{tp.get_id()}'})
            Controller.create(self.driver, net.get_id(), {
                'name': 'test_ctrl',
                'mode': ControllerModes.MF_HUB,
                'teleport': f'teleport:{tp.get_id()}',
                'device_ip': '127.0.0.1',
                'sr_controller': f'sr_controller:{sr_ctrl.get_id()}'
            })
            dev1 = Device.create(self.driver, sr_tp.get_id(), {
                'name': 'dev1',
                'mode': DeviceModes.NO_ACCESS,
                'ip': '127.0.0.1',
                'mask': '/24',
            })
            with self.subTest(f'driver={driver.get_driver_name()}'):
                dev1.send_param('mode', DeviceModes.USED)
                if driver.get_type() == API:
                    self.assertTrue(dev1.has_param_error('mode'))
                # Cannot get error by param name as `Bad Value: IP address already in use` error appear
                else:
                    self.assertEqual(str(DeviceModesStr.NO_ACCESS), dev1.get_param('mode'))

    def test_ip_address(self):
        """Create IPv4 addresses with the same values"""
        for driver in (self.driver, self.web_driver):
            self.backup.apply_backup(backup_name)
            net = Network.create(self.driver, 0, {'name': 'test_net'})
            tp = Teleport.create(self.driver, net.get_id(), {'name': 'test_tp', 'tx_lo': 0, 'rx1_lo': 0, 'rx2_lo': 0})
            ser = Service.create(self.driver, net.get_id(), {'name': 'test_service'})
            ctrl = Controller.create(self.driver, net.get_id(), {
                'name': 'test_ctrl',
                'mode': ControllerModes.MF_HUB,
                'teleport': f'teleport:{tp.get_id()}',
            })
            ControllerRoute.create(self.driver, ctrl.get_id(), {
                'type': RouteTypes.IP_ADDRESS,
                'service': f'service:{ser.get_id()}',
                'ip': '127.0.0.1'
            })
            with self.subTest(f'driver={driver.get_driver_name()}'):
                route2 = ControllerRoute(self.driver, ctrl.get_id(), NEW_OBJECT_ID, {
                    'type': RouteTypes.IP_ADDRESS,
                    'service': f'service:{ser.get_id()}',
                    'ip': '127.0.0.1'
                })
                self.assertRaises(ObjectNotCreatedException, route2.save)

    def test_same_ip_different_stations(self):
        """Create IPv4 addresses with the same values in different stations"""
        for driver in (self.driver, self.web_driver):
            self.backup.apply_backup(backup_name)
            net = Network.create(self.driver, 0, {'name': 'test_net'})
            tp = Teleport.create(self.driver, net.get_id(), {'name': 'test_tp', 'tx_lo': 0, 'rx1_lo': 0, 'rx2_lo': 0})
            ser = Service.create(self.driver, net.get_id(), {'name': 'test_service'})
            ctrl = Controller.create(self.driver, net.get_id(), {
                'name': 'test_ctrl',
                'mode': ControllerModes.MF_HUB,
                'teleport': f'teleport:{tp.get_id()}',
            })
            vno = Vno.create(self.driver, net.get_id(), {'name': 'test_vno'})
            _ip = ipaddress.IPv4Address('172.16.78.33')
            for i in range(10):
                Station.create(self.driver, vno.get_id(), {
                    'name': f'stn{i}',
                    'enable': True,
                    'serial': 12345 + i,
                    'mode': StationModes.STAR,
                    'rx_controller': f'controller:{ctrl.get_id()}'
                })
            StationRoute.create(self.driver, 0, {
                'type': RouteTypes.IP_ADDRESS,
                'service': f'service:{ser.get_id()}',
                'ip': str(_ip),
                'mask': '/24',
            })

            for i in range(1, 10):
                with self.subTest(f'driver={driver.get_driver_name()}'):
                    stn = StationRoute(driver, i, NEW_OBJECT_ID, {
                        'type': RouteTypes.IP_ADDRESS,
                        'service': f'service:{ser.get_id()}',
                        'ip': str(_ip + i),
                        'mask': '/24',
                    })
                    self.assertRaises(ObjectNotCreatedException, stn.save)
