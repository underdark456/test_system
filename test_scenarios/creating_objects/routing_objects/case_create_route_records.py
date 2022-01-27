from src.backup_manager.backup_manager import BackupManager
from src.constants import NEW_OBJECT_ID
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes, StationModes
from src.exceptions import ObjectNotCreatedException
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.controller_route import ControllerRoute
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.service import Service
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.station_route import StationRoute
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.creating_objects.routing_objects'
backup = 'default_config.txt'


class CreateRouteRecordsCase(CustomTestCase):
    """Create different types of routes test case"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.26'
    __execution_time__ = 110  # approximate test case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(options_path)
        )
        cls.backup = BackupManager()

    def set_up(self):
        self.backup.apply_backup(backup)
        self.net = Network.create(self.driver, 0, params={'name': 'net-0'})
        self.service = Service.create(self.driver, self.net.get_id(), params={'name': 'ser-0'})
        self.service2 = Service.create(self.driver, self.net.get_id(), params={
            'name': 'ser-1',
            'hub_vlan': 206,
            'stn_vlan': 306
        })
        self.tp = Teleport.create(self.driver, self.net.get_id(), params={'name': 'tp-0'})
        self.controller = Controller.create(self.driver, self.net.get_id(), params={
            'name': 'ctrl-0', 'teleport': f'teleport:{self.tp.get_id()}', 'mode': ControllerModes.MF_HUB
        })
        self.vno = Vno.create(self.driver, self.net.get_id(), params={'name': 'vno-0'})
        self.stn = Station.create(self.driver, self.vno.get_id(), params={
            'name': 'stn-0',
            'mode': StationModes.STAR,
            'serial': 10000,

        })

    def test_create_controller_ip_address(self):
        """Create ip address in controller test"""
        controller_route_options = OptionsProvider.get_options(options_path, 'route_values')
        controller_route = ControllerRoute.create(
            self.driver,
            controller_route_options['controller_id'],
            controller_route_options['IP_address']
        )
        self.assertIsNotNone(controller_route.get_id(), msg=f'IP address in controller is not created')

    def test_create_station_ip_address(self):
        """Create ip address in station test"""
        station_route_options = OptionsProvider.get_options(options_path, 'route_values')
        station_route = StationRoute.create(
            self.driver,
            station_route_options['station_id'],
            station_route_options['IP_address']
        )
        self.assertIsNotNone(station_route.get_id(), msg=f'IP address in station is not created')

    def test_create_controller_static_route(self):
        """Create static route in controller test"""
        controller_route_options = OptionsProvider.get_options(options_path, 'route_values')
        controller_route = ControllerRoute.create(
            self.driver,
            controller_route_options['controller_id'],
            controller_route_options['Static_route']
        )
        self.assertIsNotNone(controller_route.get_id(), msg=f'IPv4 static route in controller is not created')

    def test_create_station_static_route(self):
        """Create static route in station test"""
        station_route_options = OptionsProvider.get_options(options_path, 'route_values')
        station_route = StationRoute.create(
            self.driver,
            station_route_options['station_id'],
            station_route_options['Static_route']
        )
        self.assertIsNotNone(station_route.get_id(), msg=f'IPv4 static route in station is not created')

    def test_create_controller_route_to_hub(self):
        """Create route to hub on controller test. Should trigger deny to create route to hub on controllers"""
        controller_route_options = OptionsProvider.get_options(options_path, 'route_values')
        controller_route = ControllerRoute(
            self.driver,
            controller_route_options['controller_id'],
            NEW_OBJECT_ID,
            controller_route_options['Route_to_hub'],
        )
        self.assertRaises(ObjectNotCreatedException, controller_route.save)
        self.assertIsNone(controller_route.get_id(), msg=f'IPv4 route to hub in controller is created')

    def test_create_station_route_to_hub(self):
        """Create  route to hub on station test"""
        station_route_options = OptionsProvider.get_options(options_path, 'route_values')
        station_route = StationRoute.create(
            self.driver,
            station_route_options['station_id'],
            station_route_options['Route_to_hub']
        )
        self.assertIsNotNone(station_route.get_id(), msg=f'IPv4 route to hub in station is not created')

    def test_create_controller_network_tx(self):
        """Create network tx route on controller test"""
        controller_route_options = OptionsProvider.get_options(options_path, 'route_values')
        controller_route = ControllerRoute.create(
            self.driver,
            controller_route_options['controller_id'],
            controller_route_options['Network_TX']
        )
        self.assertIsNotNone(controller_route.get_id(), msg=f'IPv4 network TX in controller is not created')

    def test_create_station_network_tx(self):
        """Create network tx route on station test"""
        station_route_options = OptionsProvider.get_options(options_path, 'route_values')
        station_route = StationRoute.create(
            self.driver,
            station_route_options['station_id'],
            station_route_options['Network_TX']
        )
        self.assertIsNotNone(station_route.get_id(), msg=f'IPv4 network TX in station is not created')

    def test_create_controller_network_rx(self):
        """Create network tx route on controller test"""
        controller_route_options = OptionsProvider.get_options(options_path, 'route_values')
        controller_route = ControllerRoute.create(
            self.driver,
            controller_route_options['controller_id'],
            controller_route_options['Network_RX']
        )
        self.assertIsNotNone(controller_route.get_id(), msg=f'IPv4 network RX in controller is not created')

    def test_create_station_network_rx(self):
        """Create network tx route on station test"""
        station_route_options = OptionsProvider.get_options(options_path, 'route_values')
        station_route = StationRoute.create(
            self.driver,
            station_route_options['station_id'],
            station_route_options['Network_RX']
        )
        self.assertIsNotNone(station_route.get_id(), msg=f'IPv4 network RX in station is not created')

    def test_create_controller_l2_bridge(self):
        """Create network tx route on controller test"""
        controller_route_options = OptionsProvider.get_options(options_path, 'route_values')
        controller_route = ControllerRoute.create(
            self.driver,
            controller_route_options['controller_id'],
            controller_route_options['L2_bridge']
        )
        self.assertIsNotNone(controller_route.get_id(), msg=f'L2 bridge in controller is not created')

    def test_create_station_l2_bridge(self):
        """Create network tx route on station test"""
        station_route_options = OptionsProvider.get_options(options_path, 'route_values')
        station_route = StationRoute.create(
            self.driver,
            station_route_options['station_id'],
            station_route_options['L2_bridge']
        )
        self.assertIsNotNone(station_route.get_id(), msg=f'L2 bridge in station is not created')

    def test_create_controller_ipv6_address(self):
        """Create ip address on controller test"""
        controller_route_options = OptionsProvider.get_options(options_path, 'route_values')
        controller_route = ControllerRoute.create(
            self.driver,
            controller_route_options['controller_id'],
            controller_route_options['IPv6_address']
        )
        self.assertIsNotNone(controller_route.get_id(), msg=f'IPv6 address in controller is not created')

    def test_create_station_ipv6_address(self):
        """Create ip address on station test"""
        station_route_options = OptionsProvider.get_options(options_path, 'route_values')
        station_route = StationRoute.create(
            self.driver,
            station_route_options['station_id'],
            station_route_options['IPv6_address']
        )
        self.assertIsNotNone(station_route.get_id(), msg=f'IPv6 address in station is not created')

    def test_create_controller_ipv6_route(self):
        """Create static route on controller test"""
        controller_route_options = OptionsProvider.get_options(options_path, 'route_values')
        controller_route = ControllerRoute.create(
            self.driver,
            controller_route_options['controller_id'],
            controller_route_options['IPv6_route']
        )
        self.assertIsNotNone(controller_route.get_id(), msg=f'IPv6 static route in controller is not created')

    def test_create_station_ipv6_route(self):
        """Create static route on station test"""
        station_route_options = OptionsProvider.get_options(options_path, 'route_values')
        station_route = StationRoute.create(
            self.driver,
            station_route_options['station_id'],
            station_route_options['IPv6_route']
        )
        self.assertIsNotNone(station_route.get_id(), msg=f'IPv6 static route in station is not created')

    def test_create_controller_ipv6_to_hub(self):
        """Create IPv6 route to hub in controller test. Should trigger deny to create route to hub on controllers"""
        controller_route_options = OptionsProvider.get_options(options_path, 'route_values')
        controller_route = ControllerRoute(
            self.driver,
            controller_route_options['controller_id'],
            NEW_OBJECT_ID,
            controller_route_options['IPv6_to_hub']
        )
        self.assertRaises(
            ObjectNotCreatedException,
            controller_route.save,
        )
        self.assertIsNone(controller_route.get_id(), msg='IPv6 route to hub is created in controller')

    def test_create_station_ipv6_to_hub(self):
        """Create IPv6 route to hub in station test"""
        station_route_options = OptionsProvider.get_options(options_path, 'route_values')
        station_route = StationRoute.create(
            self.driver,
            station_route_options['station_id'],
            station_route_options['IPv6_to_hub']
        )
        self.assertIsNotNone(station_route.get_id(), msg='IPv6 route to hub is not created in station')

    def test_create_controller_ipv6_net_tx(self):
        """Create IPv6 net TX in controller test"""
        controller_route_options = OptionsProvider.get_options(options_path, 'route_values')
        controller_route = ControllerRoute.create(
            self.driver,
            controller_route_options['controller_id'],
            controller_route_options['IPv6_net_tx']
        )
        self.assertIsNotNone(controller_route.get_id(), msg='IPv6 net TX is not created in controller')

    def test_create_station_ipv6_net_tx(self):
        """Create IPv6 route to hub in station test"""
        station_route_options = OptionsProvider.get_options(options_path, 'route_values')
        station_route = StationRoute.create(
            self.driver,
            station_route_options['station_id'],
            station_route_options['IPv6_net_tx']
        )
        self.assertIsNotNone(station_route.get_id(), msg='IPv6 net TX is not created in station')

    def test_create_controller_ipv6_net_rx(self):
        """Create IPv6 net RX in controller test"""
        controller_route_options = OptionsProvider.get_options(options_path, 'route_values')
        controller_route = ControllerRoute.create(
            self.driver,
            controller_route_options['controller_id'],
            controller_route_options['IPv6_net_rx']
        )
        self.assertIsNotNone(controller_route.get_id(), msg='IPv6 net RX is not created in controller')

    def test_create_station_ipv6_net_rx(self):
        """Create IPv6 net RX in station test"""
        station_route_options = OptionsProvider.get_options(options_path, 'route_values')
        station_route = StationRoute.create(
            self.driver,
            station_route_options['station_id'],
            station_route_options['IPv6_net_rx']
        )
        self.assertIsNotNone(station_route.get_id(), msg='IPv6 net RX is not created in station')
