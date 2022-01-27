from unittest import skip

from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.drivers.uhp.uhp_requests_driver import UhpRequestsDriver
from src.drivers.uhp.uhp_telnet_driver import UhpTelnetDriver
from src.enum_types_constants import RouteTypes
from src.exceptions import InvalidOptionsException, NmsControlledModeException
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.nms import Nms
from src.nms_entities.basic_entities.service import Service
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.station_route import StationRoute
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider

__author__ = 'dkudryashov'
__version__ = '0.1'
options_path = 'test_scenarios.statistics.controller'
backup_name = 'default_config.txt'


@skip('Debug')
class MfHubControllerDashCase(CustomTestCase):
    """"""
    uhp1_telnet = None
    uhp2_telnet = None
    uhp3_telnet = None

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.system_options = OptionsProvider.get_system_options(options_path)
        cls.options = OptionsProvider.get_options(options_path)
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)
        cls.uhp1_ip = cls.system_options.get('uhp1_ip')
        cls.uhp2_ip = cls.system_options.get('uhp2_ip')
        cls.uhp3_ip = cls.system_options.get('uhp3_ip')
        if cls.uhp1_ip is None or cls.uhp2_ip is None or cls.uhp3_ip is None:
            raise InvalidOptionsException('Controller or stations IP addresses are not provided in the options')
        cls.uhp1 = UhpRequestsDriver(cls.uhp1_ip)
        cls.uhp2 = UhpRequestsDriver(cls.uhp2_ip)
        cls.uhp3 = UhpRequestsDriver(cls.uhp3_ip)
        cls.addClassCleanup(cls.close_telnet)
        cls.uhp1_telnet = UhpTelnetDriver(cls.uhp1_ip)
        cls.uhp2_telnet = UhpTelnetDriver(cls.uhp2_ip)
        cls.uhp3_telnet = UhpTelnetDriver(cls.uhp3_ip)
        ctrl_options = cls.options.get('mf_hub1')
        ctrl_options['device_ip'] = cls.uhp1_ip
        cls.nms = Nms(cls.driver, 0, 0)
        cls.net = Network.create(cls.driver, 0, cls.options.get('network'))
        cls.vno = Vno.create(cls.driver, cls.net.get_id(), {'name': 'test_vno'})
        cls.tp = Teleport.create(cls.driver, cls.net.get_id(), cls.options.get('teleport1'))
        cls.ctrl = Controller.create(cls.driver, cls.net.get_id(), ctrl_options)

        # Configuring station
        stn1_options = cls.options.get('star_stn1')
        stn1_options['serial'] = cls.uhp2.get_serial_number()
        cls.stn1 = Station.create(cls.driver, cls.vno.get_id(), stn1_options)
        stn2_options = cls.options.get('star_stn2')
        stn2_options['serial'] = cls.uhp3.get_serial_number()
        cls.stn2 = Station.create(cls.driver, cls.vno.get_id(), stn2_options)

        # Leave station IP address untouched
        cls.ser = Service.create(cls.driver, cls.net.get_id(), cls.options.get('service1'))
        cls.stn1_route = StationRoute.create(cls.driver, cls.stn1.get_id(), {
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:{cls.ser.get_id()}',
            'ip': cls.uhp2_ip,
        })

        cls.stn2_route = StationRoute.create(cls.driver, cls.stn2.get_id(), {
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:{cls.ser.get_id()}',
            'ip': cls.uhp3_ip,
        })
        cls.uhp1_telnet.get_raw_result('ip update off')
        cls.uhp1_telnet.get_raw_result('config load default all')
        cls.uhp1_telnet.get_raw_result('rf lo 0 0 0')
        cls.uhp1_telnet.get_raw_result(f'ip address {cls.uhp1_ip} /24')
        cls.uhp1_telnet.get_raw_result('config save')
        cls.uhp1_telnet.get_raw_result('reboot')
        cls.uhp1_telnet.get_raw_result('y')

        cls.uhp2_telnet.get_raw_result('ip update off')
        cls.uhp2_telnet.get_raw_result('config load default all')
        cls.uhp2_telnet.get_raw_result('rf lo 0 0 0')
        cls.uhp1_telnet.get_raw_result(f'ip address {cls.uhp2_ip} /24')
        cls.uhp2_telnet.get_raw_result('config save')
        cls.uhp1_telnet.get_raw_result('reboot')
        cls.uhp1_telnet.get_raw_result('y')

        cls.uhp3_telnet.get_raw_result('ip update off')
        cls.uhp3_telnet.get_raw_result('config load default all')
        cls.uhp3_telnet.get_raw_result('rf lo 0 0 0')
        cls.uhp1_telnet.get_raw_result(f'ip address {cls.uhp3_ip} /24')
        cls.uhp2_telnet.get_raw_result('config save')
        cls.uhp1_telnet.get_raw_result('reboot')
        cls.uhp1_telnet.get_raw_result('y')

        cls.uhp1.set_nms_permission(password=cls.options.get('network').get('dev_password'))

        cls.uhp2_telnet.get_raw_result('pro 8 type manual station')
        cls.uhp2_telnet.get_raw_result('pro 8 autorun on')
        cls.uhp2_telnet.get_raw_result('pro 8 timeout 250')
        cls.uhp2_telnet.get_raw_result('profile 8 mod on 195')
        hub_tx = cls.options.get('mf_hub1').get('tx_frq')
        hub_sr = cls.options.get('mf_hub1').get('tx_sr')
        cls.uhp2_telnet.get_raw_result(f'profile 8 rx {hub_tx} {hub_sr}')
        cls.uhp2_telnet.get_raw_result('profile 8 run')

        cls.uhp3_telnet.get_raw_result('pro 8 type manual station')
        cls.uhp3_telnet.get_raw_result('pro 8 autorun on')
        cls.uhp3_telnet.get_raw_result('pro 8 timeout 250')
        cls.uhp3_telnet.get_raw_result('profile 8 mod on 206')
        cls.uhp3_telnet.get_raw_result(f'profile 8 rx {hub_tx} {hub_sr}')
        cls.uhp3_telnet.get_raw_result('profile 8 run')

        if not cls.ctrl.wait_up():
            raise NmsControlledModeException(f'MF HUB {cls.uhp1_ip} is not in UP state')

        if not cls.stn1.wait_up():
            raise NmsControlledModeException(f'Star station 1 {cls.uhp2_ip} is not in UP state')

        if not cls.stn2.wait_up():
            raise NmsControlledModeException(f'Star station 2 {cls.uhp3_ip} is not in UP state')

    def test_dashboards_rf_stats(self):
        """Dashboards RF values"""
        # Controller dashboard section
        with self.subTest('controller hub_own_cn value'):
            self.nms.wait_next_tick()
            hub_own_cn_nms = self.ctrl.get_param('hub_own_cn')
            hub_own_cn_uhp = self.uhp1.get_demodulator_statistics().get('cn')
            self.assertAlmostEqual(float(hub_own_cn_nms), float(hub_own_cn_uhp), delta=0.7)
        with self.subTest('controller hub_tx_level value'):
            self.nms.wait_next_tick()
            hub_tx_level_nms = self.ctrl.get_param('hub_tx_level')
            hub_tx_level_uhp = self.uhp1.get_modulator_stats().get('out_lvl')
            self.assertEqual(abs(float(hub_tx_level_nms)), abs(float(hub_tx_level_uhp)))
        with self.subTest('controller hub_rf_lvl value'):
            self.nms.wait_next_tick()
            hub_rf_lvl_nms = self.ctrl.get_param('hub_rf_lvl')
            hub_rf_lvl_uhp = self.uhp1.get_demodulator_statistics().get('rf_lvl')
            self.assertAlmostEqual(abs(float(hub_rf_lvl_nms)), abs(float(hub_rf_lvl_uhp)), delta=0.7)
        with self.subTest('controller hub_cn_avg value'):
            self.nms.wait_next_tick()
            hub_cn_avg_nms = self.ctrl.get_param('hub_cn_avg')
            hub_cn_avg_uhp1 = self.uhp1.get_stations_state().get('2').get('bdrx')
            hub_cn_avg_uhp2 = self.uhp1.get_stations_state().get('3').get('bdrx')
            hub_cn_avg_uhp = (float(hub_cn_avg_uhp1) + float(hub_cn_avg_uhp2)) / 2
            self.assertAlmostEqual(float(hub_cn_avg_nms), float(hub_cn_avg_uhp), delta=0.7)
        with self.subTest('controller stn_cn_avg value'):
            self.nms.wait_next_tick()
            stn_cn_avg_nms = self.ctrl.get_param('stn_cn_avg')
            stn1_cn_uhp = self.uhp1.get_stations_state().get('2').get('strx')
            stn2_cn_uhp = self.uhp1.get_stations_state().get('3').get('strx')
            stn_cn_avg_uhp = (float(stn1_cn_uhp) + float(stn2_cn_uhp)) / 2
            self.assertAlmostEqual(float(stn_cn_avg_nms), stn_cn_avg_uhp, delta=0.7)
        with self.subTest('controller mf_channels value'):
            self.assertEqual(1, self.ctrl.get_param('mf_channels'))
        with self.subTest('controller up_stations'):
            self.assertEqual(2, self.ctrl.get_param('tx_up_stations'))
            self.assertEqual(2, self.ctrl.get_param('rx_up_stations'))

        # Station1 dashboard section
        with self.subTest('station1 cn_on_hub value'):
            self.nms.wait_next_tick()
            cn_on_hub_stn1_nms = self.stn1.get_param('cn_on_hub')
            cn_on_hub_stn1_uhp = self.uhp1.get_stations_state().get('2').get('bdrx')
            self.assertAlmostEqual(float(cn_on_hub_stn1_nms), float(cn_on_hub_stn1_uhp), delta=0.7)

        with self.subTest('station1 station_cn value'):
            self.nms.wait_next_tick()
            cn_on_hub_stn1_nms = self.stn1.get_param('station_cn')
            cn_on_hub_stn1_uhp = self.uhp1.get_stations_state().get('2').get('strx')
            self.assertAlmostEqual(float(cn_on_hub_stn1_nms), float(cn_on_hub_stn1_uhp), delta=0.7)

        with self.subTest('station1 tx value'):
            self.nms.wait_next_tick()
            station_tx_nms = self.stn1.get_param('station_tx')
            self.assertAlmostEqual(float(station_tx_nms), 19.5, delta=0.2)

        # Station2 dashboard section
        with self.subTest('station2 cn_on_hub value'):
            self.nms.wait_next_tick()
            cn_on_hub_stn2_nms = self.stn2.get_param('cn_on_hub')
            cn_on_hub_stn2_uhp = self.uhp1.get_stations_state().get('3').get('bdrx')
            self.assertAlmostEqual(float(cn_on_hub_stn2_nms), float(cn_on_hub_stn2_uhp), delta=0.7)

        with self.subTest('station2 station_cn value'):
            self.nms.wait_next_tick()
            cn_on_hub_stn2_nms = self.stn2.get_param('station_cn')
            cn_on_hub_stn2_uhp = self.uhp1.get_stations_state().get('3').get('strx')
            self.assertAlmostEqual(float(cn_on_hub_stn2_nms), float(cn_on_hub_stn2_uhp), delta=0.7)

        with self.subTest('station2 tx value'):
            self.nms.wait_next_tick()
            station_tx_nms = self.stn2.get_param('station_tx')
            self.assertAlmostEqual(float(station_tx_nms), 20.6, delta=0.2)

        # Network dashboard section
        with self.subTest('network hub_cn_avg value'):
            self.nms.wait_next_tick()
            hub_cn_avg_nms = self.net.get_param('hub_cn_avg')
            hub_cn_avg_uhp1 = self.uhp1.get_stations_state().get('2').get('bdrx')
            hub_cn_avg_uhp2 = self.uhp1.get_stations_state().get('3').get('bdrx')
            hub_cn_avg_uhp = (float(hub_cn_avg_uhp1) + float(hub_cn_avg_uhp2)) / 2
            self.assertAlmostEqual(float(hub_cn_avg_nms), float(hub_cn_avg_uhp), delta=0.7)
        with self.subTest('network stn_cn_avg value'):
            self.nms.wait_next_tick()
            stn_cn_avg_nms = self.net.get_param('stn_cn_avg')
            stn1_cn_uhp = self.uhp1.get_stations_state().get('2').get('strx')
            stn2_cn_uhp = self.uhp1.get_stations_state().get('3').get('strx')
            stn_cn_avg_uhp = (float(stn1_cn_uhp) + float(stn2_cn_uhp)) / 2
            self.assertAlmostEqual(float(stn_cn_avg_nms), stn_cn_avg_uhp, delta=0.7)

        # VNO dashboard section
        with self.subTest('vno hub_cn_avg value'):
            self.nms.wait_next_tick()
            vno_cn_avg_nms = self.vno.get_param('hub_cn_avg')
            cn_avg_uhp1 = self.uhp1.get_stations_state().get('2').get('bdrx')
            cn_avg_uhp2 = self.uhp1.get_stations_state().get('3').get('bdrx')
            cn_avg_uhp = (float(cn_avg_uhp1) + float(cn_avg_uhp2)) / 2
            self.assertAlmostEqual(float(vno_cn_avg_nms), float(cn_avg_uhp), delta=0.7)
        with self.subTest('vno stn_cn_avg value'):
            self.nms.wait_next_tick()
            vno_stn_cn_avg_nms = self.vno.get_param('stn_cn_avg')
            stn1_cn_uhp = self.uhp1.get_stations_state().get('2').get('strx')
            stn2_cn_uhp = self.uhp1.get_stations_state().get('3').get('strx')
            stn_cn_avg_uhp = (float(stn1_cn_uhp) + float(stn2_cn_uhp)) / 2
            self.assertAlmostEqual(float(vno_stn_cn_avg_nms), stn_cn_avg_uhp, delta=0.7)

    @classmethod
    def close_telnet(cls):
        if cls.uhp1_telnet is not None:
            cls.uhp1_telnet.close()
        if cls.uhp2_telnet is not None:
            cls.uhp2_telnet.close()
        if cls.uhp3_telnet is not None:
            cls.uhp3_telnet.close()
