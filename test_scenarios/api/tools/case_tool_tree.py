from src.backup_manager.backup_manager import BackupManager
from src.constants import NO_ERROR
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.nms import Nms
from src.nms_entities.basic_entities.service import Service
from src.nms_entities.basic_entities.vno import Vno
from src.nms_entities.paths_manager import PathsManager
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.api.tools'
backup_name = '32768_stations_1_vno.txt'


class ApiTreeToolCase(CustomTestCase):
    """API tree tool requests test case"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.20'
    __execution_time__ = 315  # approximate case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)
        cls.nms = Nms(cls.driver, 0, 0)
        cls.network = Network(cls.driver, 0, 0)
        cls.controller = Controller(cls.driver, 0, 0)
        cls.vno = Vno(cls.driver, 0, 0)
        Service.create(cls.driver, 0, {'name': 'test_ser'})

    def test_get_nms_tree(self):
        """API parse tree test. Getting tree with 32768 stations. Check all elements: Networks, Controllers, Stations"""
        path = PathsManager._API_OBJECT_TREE.format('nms', 0)
        reply, error, error_code = self.driver.custom_get(path)
        sequence = reply.get('sequence')
        path = f'{path}/sequence={sequence}&filters=2047'
        reply, error, error_code = self.driver.custom_get(path)
        self.assertEqual(NO_ERROR, error_code, msg=f'NMS get tree error_code {error_code}')
        tree = reply.get('tree')
        self.assertIsNotNone(tree, msg=f'No tree key in the reply')
        self.assertEqual(2, len(tree), msg=f'Tree list contain {len(tree)} elements')
        self.assertEqual(self.nms.read_param('name'), tree[0].get('na'), msg=f'Wrong NMS name in tree')
        self.assertEqual('Networks', tree[1].get('na'), msg=f'No Networks in the tree')
        networks = tree[1].get('ch')
        self.assertEqual(self.network.read_param('name'), networks[0].get('na'), msg=f'Wrong Network name in the tree')
        network_elements = networks[0].get('ch')
        self.assertEqual(
            'Controllers',
            network_elements[0].get('na'),
            msg=f'No Controllers in the tree'
        )
        controller = network_elements[0].get('ch')
        self.assertEqual(
            self.controller.read_param('name'),
            controller[0].get('na'),
            msg=f'Wrong Controller name in the tree',
        )
        stations = network_elements[1]
        self.assertEqual('Stations', stations.get('na'), msg=f'No Stations in the tree')
        vnos = stations.get('ch')
        self.assertEqual(self.vno.read_param('name'), vnos[0].get('na'))
        stations_list = vnos[0].get('ch')
        self.assertEqual(32768, len(stations_list), msg=f'Number of stations {len(stations_list)}')
        for stn in stations_list:
            if not stn.get('na').startswith('stn') or int(stn.get('na').split('-')[1]) not in range(32769):
                self.fail(f'Unexpected station name {stn.get("na")}')
            if stn.get('id') is None:
                self.fail('No ID for station')

    def test_get_tree_with_filters(self):
        """Filters ranged 0 - 2048 applied to get tree requests"""
        # TODO: probably parse result for valid filters
        for _filter in range(2049):
            path = PathsManager._API_OBJECT_TREE.format('nms', 0)
            path = f'{path}/sequence=1&filters={_filter}'
            reply, error, error_code = self.driver.custom_get(path)
            self.assertEqual(NO_ERROR, error_code)

    def test_get_tree_with_sequence(self):
        """Sequence ranged 0 - 1000000 applied to get tree requests"""
        for sequence in range(1, 1_000_000, 10000):
            path = PathsManager._API_OBJECT_TREE.format('nms', 0)
            path = f'{path}/sequence={sequence}&filters=2047'
            reply, error, error_code = self.driver.custom_get(path)
            self.assertEqual(NO_ERROR, error_code)

    def test_invalid_tree_object(self):
        """Getting tree of various objects, i.e. api/tree/get/service=0"""
        path = PathsManager._API_OBJECT_TREE.format('nms', 0)
        reply, error, error_code = self.driver.custom_get(path)
        sequence = reply.get('sequence')
        for obj in ('controller', 'vno', 'network', 'service'):
            path = PathsManager._API_OBJECT_TREE.format(obj, 0)
            path = f'{path}/sequence={sequence}&filters=2047'
            reply, error, error_code = self.driver.custom_get(path)
            self.assertEqual(NO_ERROR, error_code)
