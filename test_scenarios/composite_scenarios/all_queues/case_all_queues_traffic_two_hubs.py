from multiprocessing import Process
from time import sleep
from unittest import skip

from src.exceptions import UhpResponseException, NmsControlledModeException
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.options_providers.options_provider import OptionsProvider
from src.utils.traffic import TrafficGenerator
from test_scenarios.composite_scenarios.abstract_case import _AbstractCase

__author__ = 'dkudryashov'
__version__ = '0.2'
options_path = 'test_scenarios.composite_scenarios.all_queues'
backup_name = 'all_queues_pol_two_hubs.txt'


@skip('Need to be modified in order to check auto routing creation')
class AllQueuesTrafficTwoHubsCase(_AbstractCase):
    """Traffic statistics for two hubless controllers, and network case"""
    # A simple star network containing two hubs. Traffic is generated in 14 VLANs (ICMP echo requests).
    # The config is built in a manner that the traffic gets into all the seven queues in each hub.
    # The traffic statistics is checked in NMS to compare with the expected values.

    uhp2_driver = None
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

        cls.controller1 = Controller(cls.driver, 0, 0)
        cls.controller1.send_params({
            'uhp_model': uhp_options[0].get('model'),
            'device_ip': uhp_options[0].get('device_ip'),
            'device_vlan': uhp_options[0].get('device_vlan'),
            'device_gateway': uhp_options[0].get('device_gateway'),
            'tx_level': cls.options.get('tx_level'),
        })
        cls.controller2 = Controller(cls.driver, 0, 1)
        cls.controller2.send_params({
            'uhp_model': uhp_options[1].get('model'),
            'device_ip': uhp_options[1].get('device_ip'),
            'device_vlan': uhp_options[1].get('device_vlan'),
            'device_gateway': uhp_options[1].get('device_gateway'),
            'tx_level': cls.options.get('tx_level'),
        })

        # Set UHP NMS controlled mode
        if not uhp_options[0].get('web_driver').set_nms_permission(
                vlan=uhp_options[0].get('device_vlan'),
                password=dev_password,
                ):
            raise UhpResponseException('Cannot set UHP1 NMS permissions')
        if not uhp_options[1].get('web_driver').set_nms_permission(
                vlan=uhp_options[1].get('device_vlan'),
                password=dev_password
        ):
            raise UhpResponseException('Cannot set UHP2 NMS permissions')

        cls.t1 = TrafficGenerator(uhp_options[0].get('device_ip'))
        cls.t2 = TrafficGenerator(uhp_options[1].get('device_ip'))
        if not cls.controller1.wait_up():
            raise NmsControlledModeException('HUB 1 controller is not in UP state')
        if not cls.controller2.wait_up():
            raise NmsControlledModeException('HUB 2 controller is not in UP state')

    def test_traffic_stats(self):
        """Get traffic statistics for two hubless controllers, and network"""
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
        for i in range(7, 14):
            vlan = 206 + i
            t = Process(target=self.t2.send_icmp, kwargs={
                'vlan': vlan, 'pps': pps, 'count': pps * target_duration, 'dst_ip': '172.16.111.3', 'payload_size': 1468
            })
            t.start()
            processes.append(t)
            pps -= 1

        sleep(target_duration)

        controller1_state = self.controller1.get_state()
        controller2_state = self.controller2.get_state()
        network_state = self.net.get_state()
        # Processing results (each packet is of size 1500 bytes)
        # Test system traffic generator is not intended for committing to strict pps,
        # therefore, a deviation in the results is expected.
        expected_rate_all1 = 0
        expected_rate_all2 = 0
        for i in range(1, 8):
            exp_val1 = int(1500 * 8 * (14 - 2 * (i - 1)) / 1024)  # expected kbps
            expected_rate_all1 += exp_val1
            with self.subTest(f'Hub1 forward traffic queue P{i}', value=f'{exp_val1} kbps'):
                rate = controller1_state.get(f'forward_rate{i}')
                if isinstance(rate, float):
                    rate = int(rate)
                self.assertIn(rate, range(exp_val1 - (8 - i) - 1, exp_val1 + (8 - i) + 1))

            exp_val2 = int(1500 * 8 * (7 - (i - 1)) / 1024)  # expected kbps
            expected_rate_all2 += exp_val2
            with self.subTest(f'Hub2 forward traffic queue P{i}', value=f'{exp_val2} kbps'):
                rate = controller2_state.get(f'forward_rate{i}')
                if isinstance(rate, float):
                    rate = int(rate)
                self.assertIn(rate, range(exp_val2 - (8 - i) - 1, exp_val2 + (8 - i) + 1))

            exp_val = exp_val1 + exp_val2
            with self.subTest(f'Network forward traffic queue P{i}', value=f'{exp_val} kbps'):
                rate = network_state.get(f'forward_rate{i}')
                if isinstance(rate, float):
                    rate = int(rate)
                self.assertIn(rate, range(exp_val - (8 - i) - 1, exp_val + (8 - i) + 1))

        rate_all1 = controller1_state.get(f'forward_rate_all')
        if isinstance(rate_all1, float):
            rate_all1 = int(rate_all1)
        with self.subTest(f'Hub1 forward total traffic', value=f'{expected_rate_all1} kbps'):
            self.assertIn(rate_all1, range(expected_rate_all1 - 14, expected_rate_all1 + 14))

        rate_all2 = controller2_state.get(f'forward_rate_all')
        if isinstance(rate_all2, float):
            rate_all2 = int(rate_all2)
        with self.subTest(f'Hub2 forward total traffic', value=f'{expected_rate_all2} kbps'):
            self.assertIn(rate_all2, range(expected_rate_all2 - 14, expected_rate_all2 + 14))

        expected_rate_all = expected_rate_all1 + expected_rate_all2
        rate_all = network_state.get(f'forward_rate_all')
        if isinstance(rate_all, float):
            rate_all = int(rate_all)
        with self.subTest(f'Network forward total traffic', value=f'{expected_rate_all} kbps'):
            self.assertIn(rate_all, range(expected_rate_all - 14, expected_rate_all + 14))

        # Wait for all the traffic generator processes to finish
        for p in processes:
            p.join()
