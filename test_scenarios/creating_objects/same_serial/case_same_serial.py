from src.custom_test_case import CustomTestCase
from src import nms_api, test_api
from src.enum_types_constants import ControllerModes, StationModes
from src.exceptions import ObjectNotCreatedException, ObjectNotUpdatedException

options_path = 'test_scenarios.creating_objects.same_serial'
backup_name = 'default_config.txt'


class SameSerialCase(CustomTestCase):
    """Station's serial number must be unique in a given controller"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.21'
    __execution_time__ = 5  # approximate case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        nms_options = test_api.get_nms()
        nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))
        nms_api.load_config(backup_name)

        net = nms_api.create('nms:0', 'network', {'name': 'net'})
        tp = nms_api.create(net, 'teleport', {'name': 'tp'})
        cls.mf_hub1 = nms_api.create(net, 'controller', {
            'name': 'mf_hub1',
            'mode': ControllerModes.MF_HUB,
            'teleport': tp,
        })
        cls.mf_hub2 = nms_api.create(net, 'controller', {
            'name': 'mf_hub2',
            'mode': ControllerModes.MF_HUB,
            'teleport': tp,
        })
        cls.vno1 = nms_api.create(net, 'vno', {'name': 'vno1'})
        cls.vno2 = nms_api.create(net, 'vno', {'name': 'vno2'})
        for i in range(10000, 110000, 10000):
            nms_api.create(cls.vno1, 'station', {
                'name': f'mf_hub1_stn{i}',
                'enable': True,
                'serial': i,
                'mode': StationModes.STAR,
                'rx_controller': cls.mf_hub1,
            })
        for i in range(10000, 110000, 10000):
            nms_api.create(cls.vno2, 'station', {
                'name': f'mf_hub2_stn{i}',
                'enable': True,
                'serial': i,
                'mode': StationModes.STAR,
                'rx_controller': cls.mf_hub2,
            })

    def test_station_enabled(self):
        """Create enabled station with the existing serial in controller"""
        for i in range(10000, 110000, 10000):
            with self.assertRaises(ObjectNotCreatedException, msg=f'Station with existing serial in MF hub 1'):
                self.create_station(f'mf1_new_stn{i}', self.vno1, i, self.mf_hub1)
            if i == 100000:
                continue
            with self.assertRaises(ObjectNotCreatedException, msg=f'Station with existing serial in MF hub 2'):
                self.create_station(f'mf2_new_stn{i}', self.vno2, i, self.mf_hub2)

    def test_station_disabled(self):
        """Create disabled station with the existing serial in controller"""
        for i in range(10000, 110000, 10000):
            with self.assertRaises(ObjectNotCreatedException, msg=f'Station with existing serial in MF hub 1'):
                self.create_station(f'mf1_new_stn{i}', self.vno1, i, self.mf_hub1, enable=False)
            if i == 100000:
                continue
            with self.assertRaises(ObjectNotCreatedException, msg=f'Station with existing serial in MF hub 2'):
                self.create_station(f'mf2_new_stn{i}', self.vno2, i, self.mf_hub2, enable=False)

    def test_station_disabled_no_controller(self):
        """Create disabled station no rx_controller with the existing serial in controller"""
        for i in range(10000, 110000, 10000):
            stn = self.create_station(f'mf1_no_rx{i}', self.vno1, i, '', enable=False)
            with self.assertRaises(ObjectNotUpdatedException, msg=f'Station with existing serial in MF hub 1'):
                nms_api.update(stn, {'rx_controller': self.mf_hub1})
            if i == 100000:
                continue
            stn = self.create_station(f'mf2_no_rx{i}', self.vno2, i, '', enable=False)
            with self.assertRaises(ObjectNotUpdatedException, msg=f'Station with existing serial in MF hub 2'):
                nms_api.update(stn, {'rx_controller': self.mf_hub2})

    def test_switch_to_another_controller(self):
        """Switch stations to another controller with existing stations' serials"""
        for i in range(9):
            with self.assertRaises(ObjectNotUpdatedException, msg=f'Station:{i} from MF hub 1 to MF hub 2'):
                nms_api.update(f'station:{i}', {'rx_controller': 'controller:1'})

    @staticmethod
    def create_station(name, vno, serial, rx_controller, enable=True, mode=StationModes.STAR):
        return nms_api.create(vno, 'station', {
            'name': name,
            'enable': enable,
            'serial': serial,
            'mode': mode,
            'rx_controller': rx_controller,
        })
