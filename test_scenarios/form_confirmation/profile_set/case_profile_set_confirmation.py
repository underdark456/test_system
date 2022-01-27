from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import CheckboxStr, StationModes, ProfileSetModes, RouteTypes, ControllerModes, \
    RxVoltageStr, TdmaModcod
from src.exceptions import NmsControlledModeException
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.nms import Nms
from src.nms_entities.basic_entities.profile import Profile
from src.nms_entities.basic_entities.service import Service
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.station_route import StationRoute
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.form_confirmation.profile_set'
backup_name = 'default_config.txt'


class ProfileSetConfirmationCase(CustomTestCase):
    """Confirm that station gets correct profile set"""

    driver = None
    __author__ = 'dkudryashov'
    __version__ = '4.0.0.20'
    __execution_time__ = 85  # approximate test case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        controllers, stations = OptionsProvider.get_uhp_controllers_stations(1, ['UHP200', 'UHP200X'], 1, ['ANY', ])
        cls.mf_hub_uhp = controllers[0].get('web_driver')
        cls.star_uhp = stations[0].get('web_driver')

        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)
        cls.options = OptionsProvider.get_options(options_path)

        cls.nms = Nms(cls.driver, 0, 0)
        cls.net = Network.create(cls.driver, 0, {'name': 'test_net'})
        cls.tp = Teleport.create(cls.driver, 0, {'name': 'test_tp', 'tx_lo': 0, 'rx1_lo': 0, 'rx2_lo': 0})
        cls.ctrl = Controller.create(cls.driver, 0, {
            'name': 'test_ctrl',
            'mode': ControllerModes.MF_HUB,
            'teleport': 'teleport:0',
            'device_ip': controllers[0].get('device_ip'),
            'device_vlan': controllers[0].get('device_vlan'),
            'device_gateway': controllers[0].get('device_gateway'),
            'tx_on': CheckboxStr.ON,
            'tx_level': cls.options.get('tx_level'),
            'tx_sr': 2345,
            'rx1_sr': 2345,
        })

        cls.mf_hub_uhp.set_nms_permission(
            vlan=controllers[0].get('device_vlan'),
            password=cls.net.read_param('dev_password')
        )

        cls.profile_set = cls.create_profile_set()
        cls.vno = Vno.create(cls.driver, 0, {'name': 'test_vno'})
        cls.ser = Service.create(cls.driver, 0, {'name': 'test_ser', 'stn_vlan': stations[0].get('device_vlan')})
        cls.stn = Station.create(cls.driver, 0, {
            'name': 'test_stn',
            'serial': stations[0].get('serial'),
            'enable': CheckboxStr.ON,
            'mode': StationModes.STAR,
            'rx_controller': 'controller:0',
            'profile_set': 'profile_set:0',
        })

        cls.stn_route = StationRoute.create(cls.driver, 0, {
            'type': RouteTypes.IP_ADDRESS,
            'service': 'service:0',
            'ip': stations[0].get('device_ip'),
        })
        cls.stn_default = StationRoute.create(cls.driver, 0, {
            'type': RouteTypes.STATIC_ROUTE,
            'service': 'service:0',
            'ip': stations[0].get('device_ip'),
            'mask': '/0',
            'gateway': stations[0].get('device_gateway'),
        })

        # Preconfiguring station
        cls.star_uhp.star_station(
            params={
                'rx1_frq': cls.ctrl.read_param("tx_frq"),
                'rx1_sr': cls.ctrl.read_param("tx_sr"),
                'tx_level': cls.options.get('tx_level')
            }
        )

        # Used to check No change Profile set
        cls.star_uhp.scpc_modem(
            profile_number=2,
            params={
                'autorun': 0,
                'tx_on': 0,
                'tx_level': 40,
            },
            run_profile=False
        )

        if not cls.ctrl.wait_up(timeout=60):
            raise NmsControlledModeException('Controller is not in UP state')

        if not cls.stn.wait_up(timeout=60):
            raise NmsControlledModeException('Station is not in UP state')

        # To let station receive config
        cls.nms.wait_ticks(3)

    @classmethod
    def create_profile_set(cls):
        profile_set = Profile.create(cls.driver, 0, {
            'name': 'test_set',
            'mode2': ProfileSetModes.NO_CHANGE,
            'mode3': ProfileSetModes.NONE,

            'mode4': ProfileSetModes.STAR_STATION,
            'rx_frq4': 971001,
            'sym_rate4': 3166,
            'demod_power4': RxVoltageStr.DC13V,
            'lvl_offset4': 4,

            'mode5': ProfileSetModes.HUBLESS_STATION,
            'rx_frq5': 987123,
            'tx_frq5': 967342,
            'sym_rate5': 3343,
            'demod_power5': RxVoltageStr.DC13V,
            'lvl_offset5': 6,
            'frame_len5': 100,
            'slot_len5': 10,
            'stn_number5': 15,
            'modcod5': TdmaModcod._QPSK_5_6,

            'mode6': ProfileSetModes.DAMA_STATION,
            'rx_frq6': 999234,
            'sym_rate6': 6530,
            'demod_power6': RxVoltageStr.DC13V,
            'lvl_offset6': 1,

            'mode7': ProfileSetModes.MESH_STATION,
            'rx_frq7': 1002001,
            'sym_rate7': 2302,
            'demod_power7': RxVoltageStr.DC13V,
            'lvl_offset7': 2,

            'mode8': ProfileSetModes.CROSSPOL_TEST,
            'rx_frq8': 1203400,
            'tx_frq8': 1190001,
            'sym_rate8': 982,
            'demod_power8': RxVoltageStr.DC13V,
            'lvl_offset8': 3,
        })
        return profile_set

    def test_profile_set(self):
        """Profile set get by UHP confirmation"""
        self.no_change2()
        self.none3()
        self.star4()
        self.hubless5()
        self.dama6()
        self.mesh7()
        self.cross8()

    def no_change2(self):
        # Profile 2 should stay SCPC as it is No_change
        mode = self.star_uhp.get_basic_form(profile_number=2).get('mode')
        self.assertEqual('1', mode, msg=f'Profile 2 mode should be left untouched `1` (SCPC). Current mode {mode}')

    def none3(self):
        # Profile 3 should be None
        mode = self.star_uhp.get_basic_form(profile_number=3).get('mode')
        self.assertEqual('0', mode, msg=f'Profile 3 mode should be `0` (none). Current mode {mode}')

    def star4(self):
        # Profile 4 should be Star Station
        mode = self.star_uhp.get_basic_form(profile_number=4).get('mode')
        with self.subTest(msg=f'Profile 4 mode should be `2` (Star station)'):
            self.assertEqual('2', mode, msg=f'Current mode {mode}')

        rx_frq_set = str(self.profile_set.read_param('rx_frq4'))
        rx_frq = self.star_uhp.get_tdm_rx_form(profile_number=4).get('rx1_frq')
        with self.subTest(msg=f'Profile 4 `rx_frq` should be {rx_frq_set}'):
            self.assertEqual(rx_frq_set, rx_frq, msg=f'Current value {rx_frq}')

        sr_set = str(self.profile_set.read_param('sym_rate4'))
        sr = self.star_uhp.get_tdm_rx_form(profile_number=4).get('rx1_sr')
        with self.subTest(msg=f'Profile 4 `sym_rate` should be {sr_set}'):
            self.assertEqual(sr_set, sr, msg=f'Current value {sr}')

        demod_power_set = str(self.profile_set.read_param('demod_power4'))
        demod_power = self.star_uhp.get_tdm_rx_form(profile_number=4).get('rx_voltage').upper()
        with self.subTest(msg=f'Profile 4 `demod_power` should be {demod_power_set}'):
            self.assertEqual(demod_power_set, demod_power, msg=f' Current value {demod_power}')

        # Level offset is evaluated related to profile 1 modulator tx_level
        pro1_tx_level = int(float(self.star_uhp.get_modulator_form(profile_number=1).get('tx_level')))
        tx_level_set = pro1_tx_level - self.profile_set.read_param('lvl_offset4')
        tx_level = self.star_uhp.get_modulator_form(profile_number=4).get('tx_level')
        with self.subTest(msg=f'Profile 4 `tx_level` should be {tx_level_set}'):
            self.assertEqual(str(tx_level_set), tx_level, msg=f' Current value {tx_level}')

    def hubless5(self):
        # Profile 5 should be Hubless Station
        mode = self.star_uhp.get_basic_form(profile_number=5).get('mode')
        with self.subTest(msg=f'Profile 5 mode should be `4` (Hubless station)'):
            self.assertEqual('4', mode, msg=f'Current mode {mode}')

        rx_frq_set = str(self.profile_set.read_param('rx_frq5'))
        rx_frq = self.star_uhp.get_tdma_rf_form(profile_number=5).get('mf1_rx')
        with self.subTest(msg=f'Profile 5 `rx_frq` should be {rx_frq_set}'):
            self.assertEqual(rx_frq_set, rx_frq, msg=f'Current value {rx_frq}')

        tx_frq_set = str(self.profile_set.read_param('tx_frq5'))
        tx_frq = self.star_uhp.get_tdma_rf_form(profile_number=5).get('mf1_tx')
        with self.subTest(msg=f'Profile 5 `tx_frq` should be {tx_frq_set}'):
            self.assertEqual(tx_frq_set, tx_frq, msg=f'Current value {tx_frq}')

        sr_set = str(self.profile_set.read_param('sym_rate5'))
        sr = self.star_uhp.get_tdma_rf_form(profile_number=5).get('tdma_sr')
        with self.subTest(msg=f'Profile 5 `tdma_sr` should be {sr_set}'):
            self.assertEqual(sr_set, sr, msg=f'Current value {sr}')

        demod_power_set = str(self.profile_set.read_param('demod_power5'))
        demod_power = self.star_uhp.get_tdm_rx_form(profile_number=5).get('rx_voltage').upper()
        with self.subTest(msg=f'Profile 5 `demod_power` should be {demod_power_set}'):
            self.assertEqual(demod_power_set, demod_power, msg=f' Current value {demod_power}')

        # Level offset is evaluated related to profile 1 modulator tx_level
        pro1_tx_level = int(float(self.star_uhp.get_modulator_form(profile_number=1).get('tx_level')))
        tx_level_set = pro1_tx_level - self.profile_set.read_param('lvl_offset5')
        tx_level = self.star_uhp.get_modulator_form(profile_number=5).get('tx_level')
        with self.subTest(msg=f'Profile 5 `tx_level` should be {tx_level_set}'):
            self.assertEqual(str(tx_level_set), tx_level, msg=f' Current value {tx_level}')

        fr_len_set = str(self.profile_set.read_param('frame_len5'))
        fr_len = self.star_uhp.get_tdma_protocol_form(profile_number=5).get('frame_length')
        with self.subTest(msg=f'Profile 5 `frame_length` should be {fr_len_set}'):
            self.assertEqual(fr_len_set, fr_len, msg=f'Current value {fr_len}')

        slot_len_set = str(self.profile_set.read_param('slot_len5'))
        slot_len = self.star_uhp.get_tdma_protocol_form(profile_number=5).get('slot_length')
        with self.subTest(msg=f'Profile 5 `slot_length` should be {slot_len_set}'):
            self.assertEqual(slot_len_set, slot_len, msg=f'Current value {slot_len}')

        stn_num_set = str(self.profile_set.read_param('stn_number5'))
        stn_num = self.star_uhp.get_tdma_protocol_form(profile_number=5).get('stn_number')
        with self.subTest(msg=f'Profile 5 `stn_number` should be {stn_num_set}'):
            self.assertEqual(stn_num_set, stn_num, msg=f'Current value {stn_num}')

        modcod_set = str(self.profile_set.read_param('modcod5'))
        modcod = self.star_uhp.get_tdma_rf_form(profile_number=5).get('tdma_mc')
        with self.subTest(msg=f'Profile 5 `tdma_mc` should be {modcod_set}'):
            self.assertEqual(modcod_set, modcod.upper(), msg=f'Current value {modcod}')

    def dama6(self):
        # Profile 6 should be DAMA Station
        mode = self.star_uhp.get_basic_form(profile_number=6).get('mode')
        with self.subTest(msg=f'Profile 6 mode should be `5` (DAMA station)'):
            self.assertEqual('5', mode, msg=f'Current mode {mode}')

        rx_frq_set = str(self.profile_set.read_param('rx_frq6'))
        rx_frq = self.star_uhp.get_tdm_rx_form(profile_number=6).get('rx1_frq')
        with self.subTest(msg=f'Profile 6 `rx_frq` should be {rx_frq_set}'):
            self.assertEqual(rx_frq_set, rx_frq, msg=f'Current value {rx_frq}')

        sr_set = str(self.profile_set.read_param('sym_rate6'))
        sr = self.star_uhp.get_tdm_rx_form(profile_number=6).get('rx1_sr')
        with self.subTest(msg=f'Profile 6 `sym_rate` should be {sr_set}'):
            self.assertEqual(sr_set, sr, msg=f'Current value {sr}')

        demod_power_set = str(self.profile_set.read_param('demod_power6'))
        demod_power = self.star_uhp.get_tdm_rx_form(profile_number=6).get('rx_voltage').upper()
        with self.subTest(msg=f'Profile 6 `demod_power` should be {demod_power_set}'):
            self.assertEqual(demod_power_set, demod_power, msg=f' Current value {demod_power}')

        # Level offset is evaluated related to profile 1 modulator tx_level
        pro1_tx_level = int(float(self.star_uhp.get_modulator_form(profile_number=1).get('tx_level')))
        tx_level_set = pro1_tx_level - self.profile_set.read_param('lvl_offset6')
        tx_level = self.star_uhp.get_modulator_form(profile_number=6).get('tx_level')
        with self.subTest(msg=f'Profile 6 `tx_level` should be {tx_level_set}'):
            self.assertEqual(str(tx_level_set), tx_level, msg=f' Current value {tx_level}')

    def mesh7(self):
        # Profile 7 should be Mesh Station
        mode = self.star_uhp.get_basic_form(profile_number=7).get('mode')
        with self.subTest(msg=f'Profile 7 mode should be `3` (Mesh station)'):
            self.assertEqual('3', mode, msg=f'Current mode {mode}')

        rx_frq_set = str(self.profile_set.read_param('rx_frq7'))
        rx_frq = self.star_uhp.get_tdm_rx_form(profile_number=7).get('rx1_frq')
        with self.subTest(msg=f'Profile 7 `rx_frq` should be {rx_frq_set}'):
            self.assertEqual(rx_frq_set, rx_frq, msg=f'Current value {rx_frq}')

        sr_set = str(self.profile_set.read_param('sym_rate7'))
        sr = self.star_uhp.get_tdm_rx_form(profile_number=7).get('rx1_sr')
        with self.subTest(msg=f'Profile 7 `sym_rate` should be {sr_set}'):
            self.assertEqual(sr_set, sr, msg=f'Current value {sr}')

        demod_power_set = str(self.profile_set.read_param('demod_power7'))
        demod_power = self.star_uhp.get_tdm_rx_form(profile_number=7).get('rx_voltage').upper()
        with self.subTest(msg=f'Profile 7 `demod_power` should be {demod_power_set}'):
            self.assertEqual(demod_power_set, demod_power, msg=f' Current value {demod_power}')

        # Level offset is evaluated related to profile 1 modulator tx_level
        pro1_tx_level = int(float(self.star_uhp.get_modulator_form(profile_number=1).get('tx_level')))
        tx_level_set = pro1_tx_level - self.profile_set.read_param('lvl_offset7')
        tx_level = self.star_uhp.get_modulator_form(profile_number=7).get('tx_level')
        with self.subTest(msg=f'Profile 7 `tx_level` should be {tx_level_set}'):
            self.assertEqual(str(tx_level_set), tx_level, msg=f' Current value {tx_level}')

    def cross8(self):
        # Profile 8 should be CrossPol_test
        mode = self.star_uhp.get_basic_form(profile_number=8).get('mode')
        with self.subTest(msg=f'Profile 8 mode should be `6` (CrossPol test)'):
            self.assertEqual('6', mode, msg=f'Current mode {mode}')

        rx_frq_set = str(self.profile_set.read_param('rx_frq8'))
        rx_frq = self.star_uhp.get_tdma_rf_form(profile_number=8).get('mf1_rx')
        with self.subTest(msg=f'Profile 8 `rx_frq` should be {rx_frq_set}'):
            self.assertEqual(rx_frq_set, rx_frq, msg=f'Current value {rx_frq}')

        tx_frq_set = str(self.profile_set.read_param('tx_frq8'))
        tx_frq = self.star_uhp.get_crosspol_rf(profile_number=8).get('tx_frq')
        with self.subTest(msg=f'Profile 8 `tx_frq` should be {tx_frq_set}'):
            self.assertEqual(tx_frq_set, tx_frq, msg=f'Current value {tx_frq}')

        sr_set = str(self.profile_set.read_param('sym_rate8'))
        sr = self.star_uhp.get_tdm_rx_form(profile_number=8).get('rx1_sr')
        with self.subTest(msg=f'Profile 8 `sym_rate` should be {sr_set}'):
            self.assertEqual(sr_set, sr, msg=f'Current value {sr}')

        demod_power_set = str(self.profile_set.read_param('demod_power8'))
        demod_power = self.star_uhp.get_tdm_rx_form(profile_number=8).get('rx_voltage').upper()
        with self.subTest(msg=f'Profile 8 `demod_power` should be {demod_power_set}'):
            self.assertEqual(demod_power_set, demod_power, msg=f' Current value {demod_power}')

        # Level offset is evaluated related to profile 1 modulator tx_level
        pro1_tx_level = int(float(self.star_uhp.get_modulator_form(profile_number=1).get('tx_level')))
        tx_level_set = pro1_tx_level - self.profile_set.read_param('lvl_offset8')
        tx_level = self.star_uhp.get_modulator_form(profile_number=8).get('tx_level')
        with self.subTest(msg=f'Profile 8 `tx_level` should be {tx_level_set}'):
            self.assertEqual(str(tx_level_set), tx_level, msg=f' Current value {tx_level}')
