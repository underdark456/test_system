from src.backup_manager.backup_manager import BackupManager
from src.constants import NO_ERROR
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.nms_entities.basic_entities.dashboard import Dashboard
from src.options_providers.options_provider import OptionsProvider

__author__ = 'dkudryashov'
__version__ = '0.1'
options_path = 'test_scenarios.tickets.subtests.7780'
backup_name = 'default_config.txt'


# TODO: probably not needed as a specialized `load_default_config` case has been created
class DashboardCase(CustomTestCase):
    """Ticket 7780. Link to dashboard=1 in the tree"""

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)

    def test_dashboard(self):
        """Test that calling default config removes the dashboards"""
        for i in range(256):
            Dashboard.create(self.driver, 0, {'name': i})
        # Checking correct JSON format in the tree
        reply, error, error_code = self.driver.custom_get('api/tree/get/nms=0')
        self.assertEqual(NO_ERROR, error_code)

        # Loading default config to check if Dashboard table is empty
        path = 'api/list/get/nms=0/list_items=dashboard'
        reply, error, error_code = self.driver.custom_get(path)
        self.assertEqual(NO_ERROR, error_code)
        self.backup.apply_backup(backup_name)
        path = 'api/list/get/nms=0/list_items=dashboard'
        reply, error, error_code = self.driver.custom_get(path)
        self.assertEqual(NO_ERROR, error_code)
        # Dashboards should be empty
        self.assertEqual('', reply)
