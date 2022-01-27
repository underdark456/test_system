from unittest import skip

from src.backup_manager.backup_manager import BackupManager
from src.constants import API_LOGOUT_PATH, WRONG_SOURCE, NO_SUCH_TABLE, BAD_ARGUMENTS, ACCESS_DENIED, NO_ERROR
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.nms import Nms
from src.nms_entities.basic_entities.service import Service
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.vno import Vno
from src.nms_entities.paths_manager import PathsManager
from src.options_providers.options_provider import OptionsProvider, CONNECTION
from src.drivers.drivers_provider import DriversProvider
from test_scenarios.api.abstract_case import _AbstractCase

options_path = 'test_scenarios.api.random_requests'
backup_name = 'default_config.txt'


class ApiRandomRequestsCase(_AbstractCase):
    """Various API requests case"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.21'
    __execution_time__ = 40  # approximate case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(options_path)
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)
        cls.options = OptionsProvider.get_options(options_path)
        cls.system_options = OptionsProvider.get_system_options(options_path)
        cls.username = cls.system_options[cls.system_options[CONNECTION]]['username']
        cls.password = cls.system_options[cls.system_options[CONNECTION]]['password']
        cls.net = Network.create(cls.driver, 0, {'name': 'test_net'})
        cls.tp = Teleport.create(cls.driver, 0, {'name': 'test_tp'})
        cls.vno = Vno.create(cls.driver, cls.net.get_id(), {'name': 'test_vno'})
        cls.service = Service.create(cls.driver, cls.net.get_id(), {'name': 'test_service'})

    def test_nms_table_object_write(self):
        """API Write non-existing objects to NMS case"""
        entities = self.options.get('random_objects', [])
        for entity in entities:
            path = f'api/object/write/nms=0/new_item={entity}'
            with self.subTest(value=entity):
                reply, error, error_code = self.driver.custom_post(path, {'name': 'name'})
                self.assertEqual(WRONG_SOURCE, error_code)
        with self.subTest('Create a new NMS in NMS'):
            path = f'api/object/write/nms=0/new_item=nms'
            reply, error, error_code = self.driver.custom_post(path, {'name': 'name'})
            self.assertEqual(ACCESS_DENIED, error_code)

    def test_nms_table_delete_nms(self):
        """API Delete NMS case"""
        nms = Nms(self.driver, 0, 0)
        path = f'api/object/delete/nms=0'
        reply, error, error_code = self.driver.custom_get(path)
        # NMS should be still be in place after the deletion attempt
        self.assertIsNotNone(nms.get_param('name'), msg=f'Cannot get NMS name after the deletion attempt')
        path = f'api/form/delete/nms=0'
        reply, error, error_code = self.driver.custom_post(path, payload={'recursive': 0})
        self.assertIsNotNone(nms.get_param('name'), msg=f'Cannot get NMS name after the deletion attempt')

    def test_nms_object_deletion(self):
        """API Delete non-existing objects case"""
        entities = self.options.get('random_objects', [])
        for entity in entities:
            path = f'api/object/delete/{entity}=0'
            with self.subTest(value=path):
                reply, error, error_code = self.driver.custom_post(path, {'name': 'name'})
                self.assertEqual(NO_SUCH_TABLE, error_code)
        path = 'api/object/delete/'
        with self.subTest(value=path):
            reply, error, error_code = self.driver.custom_post(path, {'name': 'name'})
            self.assertEqual(BAD_ARGUMENTS, error_code)

    def test_multiple_dashboard_calls(self):
        """API NMS dashboard requests. The test stops immediately at the assertion fault"""
        for _ in range(10000):
            _, _, error_code = self.driver.custom_get('api/object/dashboard/nms=0')
            self.assertEqual(NO_ERROR, error_code)

    def test_delete_invalid_table(self):
        """API delete non-existing objects"""
        # A simple test that tries to delete a non-existing object.
        # It should cause either `no such object` or `wrong request argument` reply.

        entities = self.options.get('delete_items', [])
        for entity in entities:
            path = f'api/object/delete/{entity}=0'
            with self.subTest(value=path):
                reply, error, error_code = self.driver.custom_get(path)
                self.assertEqual(NO_SUCH_TABLE, error_code)
        path = f'api/object/delete/'
        reply, error, error_code = self.driver.custom_get(path)
        self.assertEqual(BAD_ARGUMENTS, error_code)

    def test_write_invalid_table(self):
        """API write to non-existing tables"""
        entities = self.options.get('random_objects', [])
        for entity in entities:
            path = f'api/object/write/{entity}=0'
            with self.subTest(value=f'api/object/write/{entity}=0'):
                reply, error, error_code = self.driver.custom_post(path, payload={'name': 'name'})
                if entity == '#contr':
                    self.assertEqual(BAD_ARGUMENTS, error_code, msg=f'Expected -14 Bad arguments, got {error_code}')
                else:
                    self.assertEqual(NO_SUCH_TABLE, error_code, msg=f'Expected -1 No Such Table, got {error_code}')

    def test_write_invalid_new_item(self):
        """API write non-valid objects into Network ID 0"""
        entities = self.options.get('new_items', [])
        for entity in entities:
            path = f'api/object/write/nms=0/new_item={entity}'
            with self.subTest(value=f'api/object/write/nms=0/new_item={entity}'):
                reply, error, error_code = self.driver.custom_post(path, {'name': 'name'})
                if entity == 'nms':
                    self.assertEqual(ACCESS_DENIED, error_code, msg=f'Expected -15 Access denied, got {error_code}')
                else:
                    self.assertEqual(WRONG_SOURCE, error_code)

    def test_read_network(self):
        """Not needed?"""
        net_ids = self.options.get('ids')
        for net_id in net_ids:
            path = PathsManager.network_read(self.driver.get_type(), net_id)
            self.driver.set_path(path)
            with self.subTest(value=net_id):
                self.driver.send_data()

    def test_create_controller(self):
        """Not needed?"""
        ctrl_ids = self.options.get('ids')
        for ctrl_id in ctrl_ids:
            path = PathsManager.controller_create(self.driver.get_type(), ctrl_id)
            self.driver.set_path(path)
            with self.subTest(value=ctrl_id):
                self.driver.send_data()

    def test_non_digit_row(self):
        """API request to edit and delete an object with a non-digit ID"""
        net = Network(self.driver, 0, 0)
        net_name = net.get_param('name')
        edit_path = PathsManager.network_update(self.driver.get_type(), 'qwerty')
        self.driver.custom_post(edit_path, payload={'name': 'new_name_net'})
        self.assertEqual(
            net_name,
            net.get_param('name'),
            msg=f'Name of the network ID 0 is changed upon requesting network=qwerty'
        )
        delete_path = PathsManager.network_delete(self.driver.get_type(), 'qwerty')
        self.driver.custom_post(delete_path, payload={'recursive': 0})
        self.assertIsNotNone(
            net.read_param('name'),
            msg=f'Network ID 0 is deleted upon requesting network=qwerty'
        )
