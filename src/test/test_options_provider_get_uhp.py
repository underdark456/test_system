import re
import time
import unittest

from src.drivers.uhp.uhp_requests_driver import UhpRequestsDriver
from src.options_providers.options_provider import OptionsProvider


class OptionsProviderGetUhp(unittest.TestCase):
    """get_uhp throughput test case"""

    max_time = 0

    def test_load_default(self):
        # expected_ips = ['10.56.24.11', '10.56.24.12', '10.56.24.13', '10.56.24.14']
        drivers = [
            UhpRequestsDriver('10.56.24.11'),
            UhpRequestsDriver('10.56.24.12'),
            UhpRequestsDriver('10.56.24.13'),
            UhpRequestsDriver('10.56.24.14'),
        ]

        for i in range(1, 101):
            _iter_st_time = time.perf_counter()
            print(f'Iteration {i} started...')

            for d in drivers:
                d.star_station(profile_number=1)
                self.assertEqual('2', d.get_basic_form(profile_number=1).get('mode'))
            time.sleep(2)
            st_time = time.perf_counter()
            uhp = OptionsProvider.get_uhp(number=4)
            end_time = time.perf_counter()
            if end_time - st_time > self.max_time:
                self.max_time = end_time - st_time

            self.assertEqual(4, len(uhp), msg=f'Number of available UHPs is not 4, actual number is {len(uhp)}')

            for u in uhp:
                _ip = u.get('device_ip')
                driver = u.get('web_driver')

                self.assertEqual(0, u.get('device_vlan'), msg=f'{_ip} Device vlan is not 0')
                self.assertEqual('10.56.24.1', u.get('device_gateway'), msg=f'{_ip} Device gateway is not 10.56.24.1')
                self.assertIsNotNone(u.get('serial'), msg=f'{_ip} Serial is None')
                self.assertIsNotNone(u.get('model'), msg=f'{_ip} Model is None')
                self.assertEqual(
                    '1',
                    driver.get_basic_form(profile_number=1).get('mode'),
                    msg=f'{_ip} Profile 1 mode is not SCPC modem after default',
                )

                _data = driver.get_request(f'http://{u.get("device_ip")}/ss33').text.lower()
                self.assertEqual(
                    'administratively',
                    driver.get_support_info_value(
                        regex=re.compile(r'demodulator-1 interface is [a-z]+'),
                        data=_data,
                    ),
                    msg=f'{_ip} Demodulator-1 interface is not Administratively disabled\n{_data}',
                )

                _data = driver.get_request(f'http://{u.get("device_ip")}/ss27').text.lower()
                self.assertEqual(
                    'administratively',
                    driver.get_support_info_value(
                        regex=re.compile(r'demodulator-2 interface is [a-z]+'),
                        data=_data,
                    ),
                    msg=f'{_ip} Demodulator-2 interface is not Administratively disabled\n{_data}',
                )

                _data = driver.get_request(f'http://{u.get("device_ip")}/ss32').text.lower()
                self.assertEqual(
                    'down',
                    driver.get_support_info_value(
                        regex=re.compile(r'modulator interface is [a-z]+'),
                        data=_data,
                    ),
                    msg=f'{_ip} Modulator interface is not DOWN\n{_data}',
                )

            _iter_end_time = time.perf_counter()
            print(f'Iteration {i} execution time is {round(_iter_end_time - _iter_st_time, 3)} seconds')
        print(f'Max get_uhp execution time is {round(self.max_time, 3)} seconds')
