import re

from src import test_api, nms_api
from src.custom_test_case import CustomTestCase
from src.enum_types_constants import StationModes, ControllerModes, ControlModes, ControllerModesStr
from utilities.utils import serial_to_human_read

options_path = 'test_scenarios.statistics.star_network'
backup_name = 'mf_hub_3_stations.txt'


class StarNetworkStatisticsCase(CustomTestCase):
    """Dashboard statistics (excluding traffic) for a star network with 3 stations"""
    # Star network with 1 MF Hub controller, 3 real stations, 2 off stations, 4 dummy stations, 4 off controllers,
    # 2 unreachable controllers

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.22'
    __execution_time__ = 110  # approximate test case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        nms_options = test_api.get_nms()
        test_options = test_api.get_options(options_path)
        cls.controllers, cls.stations = test_api.get_uhp_controllers_stations(1, ['UHP200', 'UHP200X'], 3, ['ANY'])

        nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))
        nms_api.load_config(backup_name)

        cls.mf_hub_uhp = cls.controllers[0].get('web_driver')
        cls.stn1_uhp = cls.stations[0].get('web_driver')
        cls.stn2_uhp = cls.stations[1].get('web_driver')
        cls.stn3_uhp = cls.stations[2].get('web_driver')

        # cls.mf_hub_uhp.load_default()
        cls.mf_hub_uhp.set_nms_permission(vlan=cls.controllers[0].get('device_vlan'), password='')

        nms_api.update('controller:0', {
            'uhp_model': cls.controllers[0].get('model'),
            'device_ip': cls.controllers[0].get('device_ip'),
            'device_vlan': cls.controllers[0].get('device_vlan'),
            'device_gateway': cls.controllers[0].get('device_gateway'),
            'tx_on': True,
        })
        nms_api.update('service:0', {'stn_vlan': cls.stations[0].get('device_vlan')})
        rx1_frq = nms_api.get_param('controller:0', 'rx1_frq')
        rx1_sr = nms_api.get_param('controller:0', 'rx1_sr')
        for i in range(3):
            # cls.stations[i].get('web_driver').load_default()
            cls.stations[i].get('web_driver').star_station(params={
                'rx1_frq': rx1_frq,
                'rx1_sr': rx1_sr,
                'tx_level': test_options.get('tx_level')
            })
            nms_api.update(f'station:{i}', {'serial': cls.stations[i].get('serial')})
            nms_api.update(f'route:{i}', {'ip': cls.stations[i].get('device_ip')})
            nms_api.update(f'route:{i+3}', {'gateway': cls.stations[i].get('device_gateway')})

        # Adding dummy off controllers
        for i in range(1, 5):
            nms_api.create('network:0', 'controller', {
                'name': f'dummy_off_ctrl{i}',
                'mode': ControllerModes.MF_HUB,
                'teleport': 'teleport:0',
                'control': ControlModes.NO_ACCESS,
            })
        # Adding dummy unreachable controllers
        for i in range(1, 3):
            nms_api.create('network:0', 'controller', {
                'name': f'dummy_unr_ctrl{i}',
                'mode': ControllerModes.MF_HUB,
                'teleport': 'teleport:0',
            })

        # Adding dummy off stations
        for i in range(1, 3):
            nms_api.create('vno:0', 'station', {
                f'name': f'dummy_off_stn{i}',
                'enable': False,
                'serial': 10 + i,
                'mode': StationModes.STAR,
                'rx_controller': 'controller:0',
            })
        # Adding dummy on stations
        for i in range(1, 5):
            nms_api.create('vno:0', 'station', {
                f'name': f'dummy_on_stn{i}',
                'enable': True,
                'serial': 20 + i,
                'mode': StationModes.STAR,
                'rx_controller': 'controller:0',
            })

        if not nms_api.wait_up('controller:0', timeout=60):
            test_api.error('MF HUB is not in UP state')
        for i in range(3):
            if not nms_api.wait_up(f'station:{i}', timeout=60):
                test_api.error(f'Station {i+1} is not in UP state')

        # Getting station 3 fault by setting station_low_cn and station_high_cn to zero
        nms_api.update('station:2', {'station_low_cn': 0, 'station_high_cn': 1})

        if not nms_api.wait_fault('station:2'):
            test_api.error(f'Station 3 is not in FAULT state')
        nms_api.wait_ticks(3)

    def test_network_stats(self):
        """Network dashboard statistics"""
        nms_values = nms_api.get_params(f'network:0')
        uhp_values = self.mf_hub_uhp.get_stations_state()
        with self.subTest('Network controllers Up'):
            self.assertEqual(1, nms_values.get('up_controllers'))
        with self.subTest('Network controllers Down'):
            self.assertEqual(2, nms_values.get('down_controllers'))
        with self.subTest('Network controllers Fault'):
            self.assertEqual(0, nms_values.get('fault_controllers'))
        with self.subTest('Network controllers Off'):
            self.assertEqual(4, nms_values.get('off_controllers'))
        with self.subTest('Network stations Up'):
            self.assertEqual(3, nms_values.get('up_stations'))
        with self.subTest('Network stations Fault'):
            self.assertEqual(1, nms_values.get('fault_stations'))
        with self.subTest('Network stations Down'):
            self.assertEqual(4, nms_values.get('down_stations'))
        with self.subTest('Network stations Off'):
            self.assertEqual(
                2,
                nms_values.get('off_stations'),
                msg=f'Expected 2 off stations, got {nms_values.get("off_stations")}'
            )
        with self.subTest('Network stn_cn_avg'):
            uhp_stn_cn_avg = self.get_stations_cn_avg(uhp_values)
            self.assertAlmostEqual(nms_values.get('stn_cn_avg'), uhp_stn_cn_avg, delta=0.9)
        with self.subTest('Network hub_cn_avg'):
            uhp_hub_cn_avg = self.get_hub_cn_avg(uhp_values)
            self.assertAlmostEqual(nms_values.get('hub_cn_avg'), uhp_hub_cn_avg, delta=0.9)

    def test_controller_stats(self):
        """Controller dashboard statistics"""
        nms_values = nms_api.get_params(f'controller:0')
        uhp_values = self.mf_hub_uhp.get_stations_state()
        with self.subTest('Controller state UP'):
            self.assertEqual('Up', nms_values.get('state'))
        with self.subTest('Controller profile state'):
            self.assertEqual(self.mf_hub_uhp.get_state(), nms_values.get('a_profile_state').lower())
        with self.subTest('Controller current IP'):
            self.assertEqual(self.controllers[0].get('device_ip'), nms_values.get('current_ip'))
        with self.subTest('Controller mode'):
            self.assertEqual(ControllerModesStr.MF_HUB, nms_values.get('mode'))
        with self.subTest('Controller CPU load'):
            self.assertEqual(
                self.mf_hub_uhp.get_support_info_value(regex=re.compile(r'cpuload:\s[0-9]+')),
                str(nms_values.get('cpu_load'))
            )
        with self.subTest('Controller stations Up'):
            self.assertEqual(3, nms_values.get('tx_up_stations'))
        with self.subTest('Controller stations Fault'):
            self.assertEqual(1, nms_values.get('tx_fault_stations'))
        with self.subTest('Controller stations Down'):
            self.assertEqual(4, nms_values.get('tx_down_stations'))
        with self.subTest('Controller stations Off'):
            self.assertEqual(2, nms_values.get('tx_off_stations'))
        with self.subTest('Controller stn_cn_avg'):
            uhp_stn_cn_avg = self.get_stations_cn_avg(uhp_values)
            self.assertAlmostEqual(nms_values.get('stn_cn_avg'), uhp_stn_cn_avg, delta=0.9)
        with self.subTest('Controller hub_cn_avg'):
            uhp_hub_cn_avg = self.get_hub_cn_avg(uhp_values)
            self.assertAlmostEqual(nms_values.get('hub_cn_avg'), uhp_hub_cn_avg, delta=0.9)
        with self.subTest('Controller hub_own_cn'):
            uhp_own_cn = self.mf_hub_uhp.get_demodulator_statistics().get('cn')
            self.assertAlmostEqual(float(nms_values.get('hub_own_cn')), float(uhp_own_cn), delta=0.9)
        with self.subTest('Controller hub_tx_level'):
            uhp_hub_tx_level = self.mf_hub_uhp.get_modulator_stats().get('out_lvl')
            self.assertEqual(abs(float(nms_values.get('hub_tx_level'))), abs(float(uhp_hub_tx_level)))
        with self.subTest('Controller hub_rf_lvl'):
            uhp_hub_rf_lvl = self.mf_hub_uhp.get_demodulator_statistics().get('rf_lvl')
            if uhp_hub_rf_lvl != 'NoSig':
                self.assertAlmostEqual(abs(float(nms_values.get('hub_rf_lvl'))), abs(float(uhp_hub_rf_lvl)), delta=0.9)
        with self.subTest('Controller serial'):
            self.assertEqual(str(nms_values.get('a_serial')), self.mf_hub_uhp.get_serial_number())
        with self.subTest('Controller SW version'):
            self.assertEqual(
                serial_to_human_read(nms_values.get('a_sw_version')),
                self.mf_hub_uhp.get_software_version().split(' ')[0]
            )

    def test_vno_stats(self):
        """Vno dashboard statistics"""
        nms_values = nms_api.get_params(f'vno:0')
        uhp_values = self.mf_hub_uhp.get_stations_state()
        with self.subTest('Vno stations Up'):
            self.assertEqual(3, nms_values.get('up_stations'))
        with self.subTest('Vno stations Fault'):
            self.assertEqual(1, nms_values.get('fault_stations'))
        with self.subTest('Vno stations Down'):
            self.assertEqual(4, nms_values.get('down_stations'))
        with self.subTest('Vno stations Off'):
            self.assertEqual(
                2,
                nms_values.get('off_stations'),
                msg=f'Expected 2 Off stations, got {nms_values.get("off_stations")}'
            )
        with self.subTest('Vno stn_cn_avg'):
            uhp_stn_cn_avg = self.get_stations_cn_avg(uhp_values)
            self.assertAlmostEqual(nms_values.get('stn_cn_avg'), uhp_stn_cn_avg, delta=0.9)
        with self.subTest('Vno hub_cn_avg'):
            uhp_hub_cn_avg = self.get_hub_cn_avg(uhp_values)
            self.assertAlmostEqual(nms_values.get('hub_cn_avg'), uhp_hub_cn_avg, delta=0.9)

    def test_stations_stats(self):
        """Stations dashboard statistics"""
        for i in range(3):
            nms_values = nms_api.get_params(f'station:{i}')
            uhp_values = self.mf_hub_uhp.get_stations_state().get(str(i + 2))
            with self.subTest(f'Station {i + 1} state'):
                if i == 2:
                    self.assertEqual(nms_values.get('state'), 'Fault')
                else:
                    self.assertEqual(nms_values.get('state'), 'Up')
            with self.subTest(f'Station {i + 1} state'):
                if i == 2:
                    self.assertEqual(nms_values.get('num_state'), 4)
                else:
                    self.assertEqual(nms_values.get('num_state'), 2)
            with self.subTest(f'Station {i + 1} current IP'):
                self.assertEqual(nms_values.get('current_ip'), nms_api.get_param(f'route:{i}', 'ip'))
            with self.subTest(f'Station {i + 1} station_cn'):
                self.assertAlmostEqual(
                    float(nms_values.get('station_cn')),
                    float(uhp_values.get('strx')),
                    delta=0.9,
                )
            with self.subTest(f'Station {i + 1} station_tx'):
                self.assertAlmostEqual(
                    -float(nms_values.get('station_tx')),
                    float(uhp_values.get('sttx')),
                    delta=0.9,
                )
            with self.subTest(f'Station {i + 1} tx_margin'):
                self.assertEqual(
                    nms_values.get('tx_margin'),
                    abs(1 + float(uhp_values.get('sttx'))),
                )
            with self.subTest(f'Station {i + 1} cn_on_hub'):
                self.assertAlmostEqual(
                    float(nms_values.get('cn_on_hub')),
                    float(uhp_values.get('bdrx')),
                    delta=0.9
                )

    @staticmethod
    def get_stations_cn_avg(uhp_values):
        uhp_values_stn1 = uhp_values.get(str(2))
        uhp_values_stn2 = uhp_values.get(str(3))
        uhp_values_stn3 = uhp_values.get(str(4))
        uhp_stn1_cn = float(uhp_values_stn1.get('strx'))
        uhp_stn2_cn = float(uhp_values_stn2.get('strx'))
        uhp_stn3_cn = float(uhp_values_stn3.get('strx'))
        uhp_stn_cn_avg = (uhp_stn1_cn + uhp_stn2_cn + uhp_stn3_cn) / 3
        return uhp_stn_cn_avg

    @staticmethod
    def get_hub_cn_avg(uhp_values):
        uhp_values_stn1 = uhp_values.get(str(2))
        uhp_values_stn2 = uhp_values.get(str(3))
        uhp_values_stn3 = uhp_values.get(str(4))
        uhp_stn1_bdrx = float(uhp_values_stn1.get('bdrx'))
        uhp_stn2_bdrx = float(uhp_values_stn2.get('bdrx'))
        uhp_stn3_bdrx = float(uhp_values_stn3.get('bdrx'))
        uhp_hub_cn_avg = (uhp_stn1_bdrx + uhp_stn2_bdrx + uhp_stn3_bdrx) / 3
        return uhp_hub_cn_avg
