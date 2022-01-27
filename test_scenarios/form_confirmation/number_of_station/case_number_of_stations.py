from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes, StationModes
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.nms import Nms
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.form_confirmation.number_of_station'
backup_name = 'default_config.txt'


class NumberOfStationsConfirmationCase(CustomTestCase):
    """Check if all stations (25) bound to a controller appear in the UHP stations table"""

    backup = None
    __author__ = 'dkudryashov'
    __version__ = '4.0.0.20'
    __execution_time__ = 105  # approximate case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        cls.controller = OptionsProvider.get_uhp_by_model('UHP200', 'UHP200X', number=1)[0]
        cls.ctrl_uhp = cls.controller.get('web_driver')

        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()
        cls.nms = Nms(cls.driver, 0, 0)
        cls.options = OptionsProvider.get_options(options_path)
        cls.system_options = OptionsProvider.get_system_options(options_path)
        cls.nms = Nms(cls.driver, 0, 0)

    def set_up(self) -> None:
        self.backup.apply_backup(backup_name)
        self.nms.wait_next_tick()
        self.net = Network.create(self.driver, 0, {'name': 'net-0'})
        self.tp = Teleport.create(
            self.driver,
            self.net.get_id(),
            {'name': 'tp-0', 'tx_lo': '0', 'rx1_lo': '0', 'rx2_lo': '0'}
        )
        self.vno = Vno.create(self.driver, self.net.get_id(), {'name': 'vno-0'})

    def check_next_mode(self, nms_mode_value, mode_name, nms_stn_mode_value):
        number_of_stations = self.options.get('number_of_stations', 25)
        ctrl = Controller.create(self.driver, self.net.get_id(), params={
            'mode': nms_mode_value,
            'teleport': f'teleport:{self.tp.get_id()}',
            'name': mode_name,
            'device_ip': self.controller.get('device_ip'),
            'device_vlan': self.controller.get('device_vlan'),
            'device_gateway': self.controller.get('device_gateway'),
            'stn_number': number_of_stations + 1,
            'frame_length': 100,
        })

        for i in range(1, number_of_stations + 1):
            Station.create(self.driver, self.vno.get_id(), params={
                'name': f'stn-{i}',
                'serial': i,
                'enable': 1,
                'mode': nms_stn_mode_value,
                'rx_controller': f'controller:{ctrl.get_id()}'
            })
        self.ctrl_uhp.set_nms_permission(password='', vlan=self.controller.get('device_vlan'))
        self.nms.wait_next_tick()
        self.nms.wait_next_tick()

        uhp_stations = self.ctrl_uhp.get_stations()
        for i in range(1, number_of_stations + 1):
            for key, value in uhp_stations.items():
                if str(i) == uhp_stations[key]['serial']:
                    break
            else:
                with self.subTest(f'Station sn={i} is not in UHP stations table for {mode_name} controller'):
                    self.assertFalse(True)

    def test_mf_hub(self):
        """Test stations for MF hub controller"""
        self.check_next_mode(ControllerModes.MF_HUB, 'MF hub', StationModes.STAR)

    def test_dama_hub(self):
        number_of_stations = 2
        out = Controller.create(self.driver, self.net.get_id(), params={
            'name': 'dama_hub',
            'mode': ControllerModes.DAMA_HUB,
            'teleport': f'teleport:{self.tp.get_id()}',
            'device_ip': self.controller.get('device_ip'),
            'device_vlan': self.controller.get('device_vlan'),
            'device_gateway': self.controller.get('device_gateway'),
        })

        for i in range(0, number_of_stations):
            Station.create(self.driver, self.vno.get_id(), params={
                'name': f'stn-{i}',
                'enable': 1,
                'serial': 12345 + i,
                'red_serial': 20000 + i,
                'mode': StationModes.DAMA,
                'rx_controller': f'controller:{out.get_id()}',
                'dama_ab': i,
            })
        self.ctrl_uhp.set_nms_permission(password='', vlan=self.controller.get('device_vlan'))
        self.nms.wait_next_tick()
        self.nms.wait_next_tick()

        ret_ch_1 = self.ctrl_uhp.get_dama_return_channel_form(return_channel=1)
        self.assertEqual('1', ret_ch_1.get('stn_number'), msg=f'Return channel 1 station number is not 1')
        self.assertEqual('12345', ret_ch_1.get('serial'), msg=f'Return channel 1 serial is not 12345')
        self.assertEqual('20000', ret_ch_1.get('red_serial'), msg=f'Return channel 1 red_serial is not 20000')
        ret_ch_2 = self.ctrl_uhp.get_dama_return_channel_form(return_channel=2)
        self.assertEqual('2', ret_ch_2.get('stn_number'), msg=f'Return channel 2 station number is not 2')
        self.assertEqual('12346', ret_ch_2.get('serial'), msg=f'Return channel 2 serial is not 12346')
        self.assertEqual('20001', ret_ch_2.get('red_serial'), msg=f'Return channel 2 red_serial is not 20001')

    def test_hubless(self):
        """Test stations for Hubless master controller"""
        self.check_next_mode(ControllerModes.HUBLESS_MASTER, 'Hubless', StationModes.HUBLESS)

    def test_inroute(self):
        """Test stations for Inroute controller"""
        number_of_stations = self.options.get('number_of_stations', 25)
        mf_hub = Controller.create(self.driver, self.net.get_id(), params={
            'name': 'mf_hub',
            'mode': ControllerModes.MF_HUB,
            'teleport': f'teleport:{self.tp.get_id()}',
            'stn_number': number_of_stations + 1,
            'frame_length': 100,
        })
        inr = Controller.create(self.driver, self.net.get_id(), params={
            'name': 'inr',
            'mode': ControllerModes.INROUTE,
            'teleport': f'teleport:{self.tp.get_id()}',
            'tx_controller': f'controller:{mf_hub.get_id()}',
            'device_ip': self.controller.get('device_ip'),
            'device_vlan': self.controller.get('device_vlan'),
            'device_gateway': self.controller.get('device_gateway'),
            'inroute': 99,
            'stn_number': number_of_stations + 1,
            'frame_length': 100,
        })

        for i in range(1, number_of_stations + 1):
            Station.create(self.driver, self.vno.get_id(), params={
                'name': f'stn-{i}',
                'enable': 1,
                'serial': i,
                'mode': StationModes.STAR,
                'rx_controller': f'controller:{inr.get_id()}',
            })
        self.ctrl_uhp.set_nms_permission(password='', vlan=self.controller.get('device_vlan'))
        self.nms.wait_next_tick()
        self.nms.wait_next_tick()
        uhp_stations = self.ctrl_uhp.get_stations()
        for i in range(1, number_of_stations + 1):
            for key, value in uhp_stations.items():
                if str(i) == uhp_stations[key]['serial']:
                    break
            else:
                with self.subTest(f'Station sn={i} is not in UHP stations table for Inroute controller'):
                    self.assertFalse(True)

    def test_dama_inroute(self):
        number_of_stations = 2
        dama_hub = Controller.create(self.driver, self.net.get_id(), params={
            'name': 'dama_hub',
            'mode': ControllerModes.DAMA_HUB,
            'teleport': f'teleport:{self.tp.get_id()}',
        })

        dama_inr = Controller.create(self.driver, self.net.get_id(), params={
            'name': 'dama_inr',
            'mode': ControllerModes.DAMA_INROUTE,
            'teleport': f'teleport:{self.tp.get_id()}',
            'device_ip': self.controller.get('device_ip'),
            'device_vlan': self.controller.get('device_vlan'),
            'device_gateway': self.controller.get('device_gateway'),
            'tx_controller': f'controller:{dama_hub.get_id()}',
        })

        for i in range(0, number_of_stations):
            Station.create(self.driver, self.vno.get_id(), params={
                'name': f'stn-{i}',
                'enable': 1,
                'serial': 12345 + i,
                'red_serial': 20000 + i,
                'mode': StationModes.DAMA,
                'rx_controller': f'controller:{dama_inr.get_id()}',
                'dama_ab': i,
            })
        self.ctrl_uhp.set_nms_permission(password='', vlan=self.controller.get('device_vlan'))
        self.nms.wait_next_tick()
        self.nms.wait_next_tick()

        ret_ch_1 = self.ctrl_uhp.get_dama_return_channel_form(return_channel=1)
        self.assertEqual('3', ret_ch_1.get('stn_number'), msg=f'Return channel 1 station number is not 1')
        self.assertEqual('12345', ret_ch_1.get('serial'), msg=f'Return channel 1 serial is not 12345')
        self.assertEqual('20000', ret_ch_1.get('red_serial'), msg=f'Return channel 1 red_serial is not 20000')
        ret_ch_2 = self.ctrl_uhp.get_dama_return_channel_form(return_channel=2)
        self.assertEqual('4', ret_ch_2.get('stn_number'), msg=f'Return channel 2 station number is not 2')
        self.assertEqual('12346', ret_ch_2.get('serial'), msg=f'Return channel 2 serial is not 12346')
        self.assertEqual('20001', ret_ch_2.get('red_serial'), msg=f'Return channel 2 red_serial is not 20001')

    def tear_down(self):
        self.ctrl_uhp.set_nms_permission(password='qwerty')
