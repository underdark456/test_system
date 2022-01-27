import ipaddress
import random

from src import nms_api, test_api
from src.enum_types_constants import RouteTypes, PriorityTypes, StationModes, ShaperUpQueueStr, ControllerModes
from utilities.network_up.mf_hub_1stn_up import MfHub1StnUp

options_path = 'test_scenarios.form_confirmation.shaper'
backup_name = 'default_config.txt'


class ShaperConfirmationCase(MfHub1StnUp):
    """"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.25'
    __execution_time__ = None  # approximate case execution time in seconds
    mf_hub_uhp = None
    stn1_uhp = None

    @classmethod
    def set_up_class(cls):
        super().set_up_class()
        # test_options = test_api.get_options(options_path)

        # nms_options = test_api.get_nms()
        # nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))
        # nms_api.load_config(backup_name)
        # net = nms_api.create('nms:0', 'network', {'name': 'test_net'})
        # tp = nms_api.create(net, 'teleport', {'name': 'test_tp'})
        # nms_api.create(net, 'controller', {'name': 'test_ctrl', 'mode': ControllerModes.MF_HUB, 'teleport': tp})
        cls.nms_shapers = []
        # Creating 2040 shapers
        for i in range(1):
            next_shp = cls.get_random_shaper(f'up{i}')
            cls.nms_shapers.append(next_shp)
            shp = nms_api.create('network:0', 'shaper', next_shp)
            for j in range(7):
                next_shp = cls.get_random_shaper(f'in{j}_out{i}')
                cls.nms_shapers.append(next_shp)
                shp = nms_api.create(shp, 'shaper', next_shp)
            ser = nms_api.create(
                'network:0',
                'service',
                {
                    'name': f'ser{i}',
                    'hub_vlan': i + 1,
                    'stn_vlan': 1000 + i + 1,
                    'ctr_normal': False,
                 }
            )
            qos = nms_api.create('network:0', 'qos', {'name': f'qos{i}', 'shaper': shp})
            # Creating Network_TX route in order to let NMS send shapers' config to UHP
            nms_api.create(
                'controller:0',
                'route',
                {
                    'type': RouteTypes.NETWORK_TX,
                    'service': ser,
                    'forward_qos': qos,
                    'ip': str(ipaddress.IPv4Address('192.168.0.1') + i),
                    'mask': '/32',
                }
            )
        nms_api.wait_ticks(2)

    def test_sample(self):
        uhp_shapers = self.mf_hub_uhp.get_shapers()
        # Checking that UHP gets all the created shapers
        for nms_shp in self.nms_shapers:
            found = False
            for uhp_shp in uhp_shapers.values():
                for nms_key, nms_value in nms_shp.items():
                    if nms_key == 'template':
                        pass
                    elif nms_key in uhp_shp.keys() and nms_value == uhp_shp.get(nms_key):
                        pass
                    else:
                        found = False
                        break
                else:
                    found = True
                    break
            print(found, nms_shp)

    @staticmethod
    def get_random_shaper(name):
        """Get random shaper. All values are strings"""
        max_enable = random.choice(['ON', 'OFF'])
        min_enable = random.choice(['ON', 'OFF'])
        wfq_enable = random.choice(['ON', 'OFF'])
        night_enable = random.choice(['ON', 'OFF'])
        params = {
            'name': name,
            'template': random.choice(['ON', 'OFF']),
            'cir': str(random.randint(1, 250000)),
            'up_queue': random.choice([*ShaperUpQueueStr()]),
            'max_enable': max_enable,
            'min_enable': min_enable,
            'wfq_enable': wfq_enable,
            'night_enable': night_enable,
        }
        if max_enable == 'ON':
            params['max_cir'] = str(random.randint(1, 250000))
            params['max_slope'] = str(random.randint(1, 16))
        if min_enable == 'ON':
            params['min_cir'] = str(random.randint(1, 250000))
            params['down_slope'] = str(random.randint(1, 16))
            params['up_slope'] = str(random.randint(1, 16))
        if wfq_enable == 'ON':
            wfq1 = random.randint(0, 100)
            wfq2 = random.randint(0, 100 - wfq1)
            wfq3 = random.randint(0, 100 - wfq1 - wfq2)
            wfq4 = random.randint(0, 100 - wfq1 - wfq2 - wfq3)
            wfq5 = random.randint(0, 100 - wfq1 - wfq2 - wfq3 - wfq4)
            wfq6 = 100 - wfq1 - wfq2 - wfq3 - wfq4 - wfq5
            params['wfq1'] = str(wfq1)
            params['wfq2'] = str(wfq2)
            params['wfq3'] = str(wfq3)
            params['wfq4'] = str(wfq4)
            params['wfq5'] = str(wfq5)
            params['wfq6'] = str(wfq6)
        if night_enable == 'ON':
            params['night_cir'] = str(random.randint(1, 250000))
            params['night_start'] = str(random.randint(0, 23))
            params['night_end'] = str(random.randint(0, 23))
        return params