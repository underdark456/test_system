from src.custom_test_case import CustomTestCase
from src import nms_api, test_api
from src.enum_types_constants import ControllerModes
from src.exceptions import ObjectNotUpdatedException

options_path = 'test_scenarios.form_validation.modulator_queues'
backup_name = 'default_config.txt'


class ModulatorSumQueuesValidationCase(CustomTestCase):
    """Controllers and stations modulator sum_of_all_queues validation case"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.22'
    __execution_time__ = 10  # approximate case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        nms_options = test_api.get_nms()
        nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))
        nms_api.load_config(backup_name)
        cls.test_options = test_api.get_options(options_path)

        net = nms_api.create('nms:0', 'network', {'name': 'net'})
        tp = nms_api.create(net, 'teleport', {'name': 'net'})
        vno = nms_api.create(net, 'vno', {'name': 'vno'})
        for m in cls.test_options.get('controller_modes'):
            if m == ControllerModes.GATEWAY:
                nms_api.create(net, 'controller', {
                    'name': f'ctrl{m}',
                    'teleport': tp,
                    'mode': m,
                    'tx_controller': 'controller:0'
                })
            else:
                nms_api.create(net, 'controller', {
                    'name': f'ctrl{m}',
                    'teleport': tp,
                    'mode': m,
                })
        for m in cls.test_options.get('station_modes'):
            nms_api.create(vno, 'station', {
                'name': f'stn{m}',
                'serial': 10000 + m,
            })

    def test_controller(self):
        """Each supported controller mod queues length test"""
        _iterations = 50
        for j in range(len(self.test_options.get('controller_modes'))):
            for i in range(_iterations):
                p1 = 10 + 6000 // _iterations * i
                p2 = 10 + 6000 // _iterations * i
                p3 = 10 + 4000 // _iterations * i
                p4 = 10 + 4000 // _iterations * i
                p5 = 10 + 3000 // _iterations * i
                p6 = 10 + 2000 // _iterations * i
                p7 = 10 + 1000 // _iterations * i
                ctl = 10 + 6000 // _iterations * i
                _sum = p1 + p2 + p3 + p4 + p5 + p6 + p7 + ctl
                if _sum < self.test_options.get('sum_of_all_queues') and p1 in range(10, 5000) \
                        and p2 in range(10, 5000) and p3 in range(10, 3000) and p4 in range(10, 3000) \
                        and p5 in range(10, 2000) and p6 in range(10, 1000) and p7 in range(10, 500) \
                        and ctl in range(10, 5000):
                    try:
                        nms_api.update(f'controller:{j}', {
                            'mod_queue1': p1,
                            'mod_queue2': p2,
                            'mod_queue3': p3,
                            'mod_queue4': p4,
                            'mod_queue5': p5,
                            'mod_queue6': p6,
                            'mod_queue7': p7,
                            'mod_que_ctl': ctl,
                        })
                    except ObjectNotUpdatedException:
                        self.fail(f'Sum of all queue={_sum} is not applied')
                else:
                    with self.assertRaises(ObjectNotUpdatedException):
                        nms_api.update(f'controller:{j}', {
                            'mod_queue1': p1,
                            'mod_queue2': p2,
                            'mod_queue3': p3,
                            'mod_queue4': p4,
                            'mod_queue5': p5,
                            'mod_queue6': p6,
                            'mod_queue7': p7,
                            'mod_que_ctl': ctl,
                        })

    def test_station(self):
        """Each supported station mod queues test"""
        _iterations = 50
        for j in range(len(self.test_options.get('station_modes'))):
            for i in range(_iterations):
                p1 = 10 + 6000 // _iterations * i
                p2 = 10 + 6000 // _iterations * i
                p3 = 10 + 4000 // _iterations * i
                p4 = 10 + 4000 // _iterations * i
                p5 = 10 + 3000 // _iterations * i
                p6 = 10 + 2000 // _iterations * i
                p7 = 10 + 1000 // _iterations * i
                ctl = 10 + 1000 // _iterations * i
                _sum = p1 + p2 + p3 + p4 + p5 + p6 + p7 + ctl
                if _sum < self.test_options.get('sum_of_all_queues') and p1 in range(10, 5000) and p2 in range(10, 5000) \
                        and p3 in range(10, 3000) and p4 in range(10, 3000) and p5 in range(10, 2000) \
                        and p6 in range(10, 1000) and p7 in range(10, 500) and ctl in range(10, 500):
                    try:
                        nms_api.update(f'station:{j}', {
                            'mod_queue1': p1,
                            'mod_queue2': p2,
                            'mod_queue3': p3,
                            'mod_queue4': p4,
                            'mod_queue5': p5,
                            'mod_queue6': p6,
                            'mod_queue7': p7,
                            'mod_que_ctl': ctl,
                        })
                    except ObjectNotUpdatedException:
                        self.fail(f'Sum of all queue={_sum} is not applied')
                else:
                    with self.assertRaises(ObjectNotUpdatedException):
                        nms_api.update(f'station:{j}', {
                            'mod_queue1': p1,
                            'mod_queue2': p2,
                            'mod_queue3': p3,
                            'mod_queue4': p4,
                            'mod_queue5': p5,
                            'mod_queue6': p6,
                            'mod_queue7': p7,
                            'mod_que_ctl': ctl,
                        })