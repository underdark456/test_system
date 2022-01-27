from multiprocessing import Process
from time import sleep
from unittest import skip

from src.exceptions import UhpResponseException, NmsControlledModeException
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.service import Service
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.station_route import StationRoute
from src.options_providers.options_provider import OptionsProvider
from src.utils.traffic import TrafficGenerator
from test_scenarios.composite_scenarios.abstract_case import _AbstractCase

__author__ = 'dkudryashov'
__version__ = '0.2'
options_path = 'test_scenarios.composite_scenarios.all_queues'
backup_name = 'all_queues_policies_star.txt'


@skip('Need to be modified in order to check auto routing creation')
class AllQueuesTrafficStarCase(_AbstractCase):
    """Traffic statistics for an MF hub controller, station, vno, and network case"""
    # A simple star network containing the hub and a station. Traffic is generated in 14 VLANs (ICMP echo requests).
    # The config is built in a manner that the traffic gets into all the seven queues in the hub and the station.
    # The traffic statistics is checked in NMS to compare with the expected values.

    uhp1_driver = None
    backup = None
    driver = None

    @classmethod
    def set_up_class(cls):
        super().set_up_class()
        cls.backup.apply_backup(backup_name)
        cls.options = OptionsProvider.get_options(options_path)
        uhp_options = OptionsProvider.get_uhp_by_model('UHP200', 'UHP200X', number=2)

        cls.net = Network(cls.driver, 0, 0)
        dev_password = cls.net.get_param('dev_password')

        cls.mf_hub = Controller(cls.driver, 0, 0)
        cls.mf_hub.send_params({
            'uhp_model': uhp_options[0].get('model'),
            'device_ip': uhp_options[0].get('device_ip'),
            'device_vlan': uhp_options[0].get('device_vlan'),
            'device_gateway': uhp_options[0].get('device_gateway'),
            'tx_level': cls.options.get('tx_level'),
        })
        cls.stn1 = Station(cls.driver, 0, 0)
        cls.stn1.send_param('serial', uhp_options[1].get('serial'))

        cls.ser = Service(cls.driver, 0, 0)
        cls.ser.send_param('stn_vlan', uhp_options[0].get('device_vlan'))

        cls.stn_route = StationRoute(cls.driver, cls.stn1.get_id(), 0)
        cls.stn_route.send_param('ip', uhp_options[1].get('device_ip'))

        cls.stn_default_route = StationRoute(cls.driver, cls.stn1.get_id(), 1)
        cls.stn_route.send_param('gateway', uhp_options[1].get('device_gateway'))

        # Set UHP NMS controlled mode
        if not uhp_options[0].get('web_driver').set_nms_permission(
                vlan=uhp_options[0].get('device_vlan'),
                password=dev_password):
            raise UhpResponseException('Cannot set UHP NMS permissions')

        uhp_options[1].get('web_driver').star_station(
            params={
                'rx1_frq': cls.mf_hub.get_param('tx_frq'),
                'rx1_sr': cls.mf_hub.get_param('tx_sr'),
                'tx_level': cls.options.get('tx_level'),
            }
        )
        cls.t1 = TrafficGenerator(uhp_options[0].get('device_ip'))
        cls.t2 = TrafficGenerator(uhp_options[1].get('device_ip'))
        if not cls.mf_hub.wait_up(timeout=60):
            raise NmsControlledModeException('MF HUB is not in UP state')
        if not cls.stn1.wait_up(timeout=60):
            raise NmsControlledModeException('Star station 1 is not in UP state')

    def test_traffic_stats(self):
        """Get traffic statistics for an MF hub controller, station, vno, and network"""
        processes = []
        pps = 14
        target_duration = 60  # traffic generation in seconds
        # ICMP echo requests in HUB
        for i in range(7):
            vlan = 206 + i
            t = Process(target=self.t1.send_icmp, kwargs={
                'vlan': vlan, 'pps': pps, 'count': pps * target_duration, 'dst_ip': '172.16.111.3', 'payload_size': 1468
            })
            t.start()
            processes.append(t)
            pps -= 2

        pps = 7
        # ICMP echo requests in Station
        for i in range(7):
            vlan = 306 + i
            t = Process(target=self.t2.send_icmp, kwargs={
                'vlan': vlan, 'pps': pps, 'count': pps * target_duration, 'dst_ip': '172.16.111.3', 'payload_size': 1468
            })
            t.start()
            processes.append(t)
            pps -= 1

        sleep(target_duration)

        controller_state = self.mf_hub.get_state()
        station_state = self.stn1.get_state()
        network_state = self.net.get_state()
        # Processing results (each packet is of size 1500 bytes)
        # Test system traffic generator is not intended for committing to strict pps,
        # therefore, a deviation in the results is expected.
        expected_rate_all = 0
        for i in range(1, 8):
            exp_val = int(1500 * 8 * (14 - 2 * (i - 1)) / 1024)  # expected kbps
            expected_rate_all += exp_val
            with self.subTest(f'Hub forward traffic queue P{i}', value=f'{exp_val} kbps'):
                rate = controller_state.get(f'forward_rate{i}')
                if isinstance(rate, float):
                    rate = int(rate)
                self.assertIn(rate, range(exp_val - (8 - i) - 1, exp_val + (8 - i) + 1))
            with self.subTest(f'Network forward traffic queue P{i}', value=f'{exp_val} kbps'):
                rate = network_state.get(f'forward_rate{i}')
                if isinstance(rate, float):
                    rate = int(rate)
                self.assertIn(rate, range(exp_val - (8 - i) - 1, exp_val + (8 - i) + 1))
            with self.subTest(f'Station return traffic queue P{i}', value=f'{exp_val} kbps'):
                rate = station_state.get(f'forward_rate{i}')
                if isinstance(rate, float):
                    rate = int(rate)
                self.assertIn(rate, range(exp_val - (8 - i) - 1, exp_val + (8 - i) + 1))
        rate_all = controller_state.get(f'forward_rate_all')
        if isinstance(rate_all, float):
            rate_all = int(rate_all)
        with self.subTest(f'Hub forward total traffic', value=f'{expected_rate_all} kbps'):
            self.assertIn(rate_all, range(expected_rate_all - 14, expected_rate_all + 14))
        rate_all = network_state.get(f'forward_rate_all')
        if isinstance(rate_all, float):
            rate_all = int(rate_all)
        with self.subTest(f'Station return total traffic', value=f'{expected_rate_all} kbps'):
            self.assertIn(rate_all, range(expected_rate_all - 14, expected_rate_all + 14))
        rate_all = station_state.get(f'return_rate_all')
        if isinstance(rate_all, float):
            rate_all = int(rate_all)
        with self.subTest(f'Network forward total traffic', value=f'{expected_rate_all} kbps'):
            self.assertIn(rate_all, range(expected_rate_all - 14, expected_rate_all + 14))

        expected_rate_all = 0
        for i in range(1, 8):
            exp_val = int(1500 * 8 * (7 - (i - 1)) / 1024)  # expected kbps
            expected_rate_all += exp_val
            with self.subTest(f'Hub return traffic queue P{i}', value=f'{exp_val} kbps'):
                rate = controller_state.get(f'return_rate{i}')
                if isinstance(rate, float):
                    rate = int(rate)
                self.assertIn(rate, range(exp_val - (8 - i) - 1, exp_val + (8 - i) + 1))
            with self.subTest(f'Station forward traffic queue P{i}', value=f'{exp_val} kbps'):
                rate = station_state.get(f'forward_rate{i}')
                if isinstance(rate, float):
                    rate = int(rate)
                self.assertIn(rate, range(exp_val - (8 - i) - 1, exp_val + (8 - i) + 1))
            with self.subTest(f'Network return traffic queue P{i}', value=f'{exp_val} kbps'):
                rate = network_state.get(f'return_rate{i}')
                if isinstance(rate, float):
                    rate = int(rate)
                self.assertIn(rate, range(exp_val - (8 - i) - 1, exp_val + (8 - i) + 1))
        rate_all = controller_state.get(f'return_rate_all')
        if isinstance(rate_all, float):
            rate_all = int(rate_all)
        with self.subTest(f'Hub return total traffic', value=f'{expected_rate_all} kbps'):
            self.assertIn(rate_all, range(expected_rate_all - 14, expected_rate_all + 14))
        rate_all = network_state.get(f'return_rate_all')
        if isinstance(rate_all, float):
            rate_all = int(rate_all)
        with self.subTest(f'Station forward total traffic', value=f'{expected_rate_all} kbps'):
            self.assertIn(rate_all, range(expected_rate_all - 14, expected_rate_all + 14))
        rate_all = station_state.get(f'forward_rate_all')
        if isinstance(rate_all, float):
            rate_all = int(rate_all)
        with self.subTest(f'Network return total traffic', value=f'{expected_rate_all} kbps'):
            self.assertIn(rate_all, range(expected_rate_all - 14, expected_rate_all + 14))

        # Wait for all the traffic generator processes to finish
        for p in processes:
            p.join()
