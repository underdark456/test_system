import random
import time

from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import TdmaInputModes, RouteTypes, ControllerModes, StationModes, RouteIds
from src.exceptions import UhpUpStateException
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.nms import Nms
from src.nms_entities.basic_entities.service import Service
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.station_route import StationRoute
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.statistics.faults'
backup_name = 'default_config.txt'


class HublessNetworkStatesCase(CustomTestCase):
    """NMS show correct controller and station states in a hubless network"""

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.options = OptionsProvider.get_options(options_path)
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)

        cls.controllers, cls.stations = OptionsProvider.get_uhp_controllers_stations(
            1, ['UHP200', 'UHP200X', ], 1, ['ANY', ]
        )

        cls.nms = Nms(cls.driver, 0, 0)
        cls.net = Network.create(cls.driver, 0, params=cls.options.get('network'))
        cls.tp = Teleport.create(cls.driver, cls.net.get_id(), params=cls.options.get('teleport'))
        ctrl_options = cls.options.get('controller_hbl')
        ctrl_options['uhp_model'] = cls.controllers[0].get('model')
        cls.ctrl = Controller.create(cls.driver, cls.net.get_id(), params=ctrl_options)
        cls.vno = Vno.create(cls.driver, cls.net.get_id(), params={'name': 'vno-0'})
        cls.stn = Station.create(cls.driver, cls.vno.get_id(), params=cls.options.get('station'))

        cls.master_uhp = cls.controllers[0].get('web_driver')
        cls.stn_uhp = cls.stations[0].get('web_driver')

        cls.stn_uhp.hubless_station(params={
            'frame_length': cls.options.get('controller').get('frame_length'),
            'slot_length': cls.options.get('controller').get('slot_length'),
            'stn_number': cls.options.get('controller').get('stn_number'),
            'mf1_tx': cls.options.get('controller').get('mf1_tx'),
            'mf1_rx': cls.options.get('controller').get('mf1_rx'),
            'tdma_mc': cls.options.get('controller').get('tdma_mc'),
            'tdma_sr': cls.options.get('controller').get('tdma_sr'),
            'tx_level': cls.options.get('tx_level')
        })

        ser = Service.create(cls.driver, cls.net.get_id(), params={'name': 'ser-0'})
        StationRoute.create(cls.driver, ser.get_id(), params={
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:{ser.get_id()}',
            'ip': cls.stations[0].get('device_ip'),
            'id': RouteIds.PRIVATE,
        })
        StationRoute.create(cls.driver, ser.get_id(), params={
            'type': RouteTypes.STATIC_ROUTE,
            'service': f'service:{ser.get_id()}',
            'ip': '0.0.0.0',
            'mask': '/0',
            'gateway': cls.stations[0].get('device_gateway'),
            'id': RouteIds.PRIVATE,
        })
        # if not cls.ctrl.wait_up():
        #     raise NmsControlledModeException('Hubless Master is not UP')
        # if not cls.stn.wait_up():
        #     raise NmsControlledModeException('Hubless Station is not UP')

    def set_up(self) -> None:
        self.ctrl.send_params({
            'mf1_rx': 1100000,
            'tx_on': 'OFF',
            'device_ip': '0.0.0.0',
            'tx_level': self.options.get('tx_level')
        })
        self.stn.send_param('serial', 10000)

    def test_controller_states(self):
        # state = self.ctrl.get_state()
        # # Initial state is `Unknown`
        # with self.subTest('Expected state `Unknown`'):
        #     self.assertEqual('Unknown', state.get('state'))

        self.nms.wait_next_tick()
        # Next state is `Unreachable` as `device_ip` and `dev_password` are not set
        state = self.ctrl.get_state()
        with self.subTest('Expected state `Unreachable`'):
            self.assertEqual('Unreachable', state.get('state'))

        self.ctrl.send_param('device_ip', self.controllers[0].get('device_ip'))
        self.master_uhp.set_nms_permission(
            vlan=self.controllers[0].get('device_vlan'),
            password=self.options.get('network').get('dev_password'),
        )
        self.nms.wait_next_tick()
        self.nms.wait_next_tick()
        # Next expected state is 'Start_hub_TX' as `tx_on` is `OFF`
        state = self.ctrl.get_state()
        with self.subTest('Expected profile state `Start_hub_TX`'):
            self.assertEqual('Start_hub_TX', state.get('a_profile_state'))

        self.ctrl.send_param('tx_on', 'ON')
        self.nms.wait_next_tick()
        state = self.ctrl.get_state()
        # Next expected profile state is `No_RX`
        with self.subTest('Expected profile state `No_RX`'):
            self.assertEqual('No_RX', state.get('a_profile_state'))

        self.ctrl.send_param('mf1_rx', 1000000)
        self.ctrl.wait_up()
        state = self.ctrl.get_state()
        # Next expected state is `UP`
        with self.subTest('Expected state `Up`'):
            self.assertEqual('Up', state.get('state'))

    def test_station_state(self):
        self.ctrl.send_param('mf1_rx', 1000000)
        self.ctrl.send_param('tx_on', 'ON')
        self.ctrl.send_param('device_ip', self.controllers[0].get('device_ip'))

        if not self.ctrl.wait_up():
            raise UhpUpStateException('Hub is not in UP state')

        state = self.stn.get_state()
        # Expected initial state is `Off`
        with self.subTest('Expected state `Off`'):
            self.assertEqual('Off', state.get('state'))

        self.stn.send_param('enable', 'ON')
        self.nms.wait_next_tick()
        state = self.stn.get_state()
        # Expected next state is `Down`
        with self.subTest('Expected state `Down`'):
            self.assertEqual('Down', state.get('state'))

        self.stn_uhp.set_profile_tdma_rf(profile_number=1, params={
            'tdma_input': TdmaInputModes.RX1,
            'tdma_mc': self.options.get('controller').get('tdma_mc'),
            'mf1_tx': self.options.get('controller').get('mf1_tx'),
            'mf1_rx': 1000000
        })
        self.stn.send_param('serial', self.stations[0].get('serial'))
        if not self.stn.wait_up():
            raise UhpUpStateException('Station is not in UP state')

    def test_overall_states(self):
        self.ctrl.send_param('mf1_rx', 1000000)
        self.ctrl.send_param('tx_on', 'ON')
        self.ctrl.send_param('device_ip', self.controllers[0].get('device_ip'))
        self.stn.send_param('enable', 'ON')
        if not self.ctrl.wait_up():
            raise UhpUpStateException('Hub is not in UP state')
        self.stn_uhp.set_profile_tdma_rf(profile_number=1, params={
            'tdma_input': TdmaInputModes.RX1,
            # TODO: change when the modcod bug is fixed
            # 'tdma_mc': cls.options.get('controller').get('tdma_mc'),
            'tdma_mc': 4,
            'mf1_tx': self.options.get('controller').get('mf1_tx'),
            'mf1_rx': 1000000
        })
        self.stn.send_param('serial', self.stations[0].get('serial'))
        if not self.stn.wait_up():
            raise UhpUpStateException('Station is not in UP state')
        # Adding some dummy controllers
        num_ctrls = random.randint(120, 127)
        for i in range(num_ctrls):
            Controller.create(self.driver, self.net.get_id(), params={
                'name': f'ctrl-{i+1}',
                'mode': ControllerModes.HUBLESS_MASTER,
                'teleport': 'teleport:0',
            })
        num_stns_en = 80
        for i in range(num_stns_en):
            Station.create(self.driver, self.vno.get_id(), params={
                'name': f'stn-{i+1}',
                'enable': 'ON',
                'serial': i + 1,
                'mode': StationModes.MESH,
                'rx_controller': 'controller:0'
            })
        num_stns_dis = 90
        for i in range(num_stns_dis):
            Station.create(self.driver, self.vno.get_id(), params={
                'name': f'stn-{num_stns_en + i + 1}',
                'enable': 'OFF',
                'serial': i + 1,
                'mode': StationModes.MESH,
                'rx_controller': 'controller:0'
            })
        self.nms.wait_next_tick()
        time.sleep(20)
        with self.subTest('Number of UP controllers in Network'):
            self.assertEqual(1, self.net.get_state().get('up_controllers'))
        with self.subTest('Number of DOWN controllers in Network'):
            self.assertEqual(num_ctrls, self.net.get_state().get('down_controllers'))
        with self.subTest('Number of UP stations in Network'):
            self.assertEqual(1, self.net.get_state().get('up_stations'))
        with self.subTest('Number of UP stations in Controller'):
            self.assertEqual(1, self.net.get_state().get('tx_up_stations'))
        with self.subTest('Number of OFF stations in Network'):
            self.assertEqual(num_stns_dis, self.net.get_state().get('off_stations'))
        with self.subTest('Number of OFF stations in Controller'):
            self.assertEqual(num_stns_dis, self.net.get_state().get('tx_off_stations'))
        with self.subTest('Number of DOWN stations in Network'):
            self.assertEqual(num_stns_en, self.net.get_state().get('down_stations'))
        with self.subTest('Number of DOWN stations in Controller'):
            self.assertEqual(num_stns_en, self.net.get_state().get('tx_down_stations'))
