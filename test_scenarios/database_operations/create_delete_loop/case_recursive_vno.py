from src.backup_manager.backup_manager import BackupManager
from src.constants import NO_ERROR
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.vno import Vno
from src.nms_entities.paths_manager import PathsManager
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.database_operations.create_delete_loop'
backup_name = 'default_config.txt'


class RecursiveVnoCase(CustomTestCase):
    """Recursive Vno creation deletion test case"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.21'
    __execution_time__ = None  # approximate case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)

    def test_recursive_vnos(self):
        """Check if it is possible to create 511 Sub-VNOs inside each other, delete them afterwards"""
        Network.create(self.driver, 0, params={'name': 'net'})
        sub_vno = Vno.create(self.driver, 0, params={'name': 'UpperVno'})
        for i in range(511):
            sub_vno = Vno.create(self.driver, sub_vno.get_id(), params={'name': f'sub_vno-{i}'}, parent_type='vno')
            self.assertIsNotNone(sub_vno.get_id())
        for i in range(511, -1, -1):
            vno = Vno(self.driver, 0, i)
            vno.delete()
            path = PathsManager.vno_read(self.driver.get_type(), i)
            reply, error_code, error = self.driver.custom_get(path)
            self.assertNotEqual(NO_ERROR, error_code)
