from src.backup_manager.backup_manager import BackupManager
from src.constants import NO_ERROR, WRONG_VARIABLE_VALUE
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.shaper import Shaper
from src.options_providers.options_provider import OptionsProvider

__author__ = 'dkudryashov'
__version__ = '0.1'
options_path = 'test_scenarios.tickets.subtests.7720'
backup_name = 'default_config.txt'


class WfqSumCase(CustomTestCase):
    """Ticket 7720. wfq weight >100"""

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.options = OptionsProvider.get_options(options_path)
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)

    def test_wfq_sum(self):
        """Check that WFQ sum equals to 100%"""
        net = Network.create(self.driver, 0, {'name': 'test_net'})
        valid_combinations = self.options.get('valid_combinations')
        for i in range(len(valid_combinations)):
            with self.subTest(valid_combinations[i]):
                _, _, error_code = self.driver.custom_post(
                    f'api/object/write/net={net.get_id()}/new_item=shaper',
                    payload={
                        'name': f'shaper-{i}',
                        'wfq_enable': 'ON',
                        'wfq1': valid_combinations[i][0],
                        'wfq2': valid_combinations[i][1],
                        'wfq3': valid_combinations[i][2],
                        'wfq4': valid_combinations[i][3],
                        'wfq5': valid_combinations[i][4],
                        'wfq6': valid_combinations[i][5],
                    }
                )
                self.assertEqual(NO_ERROR, error_code)
        invalid_combinations = self.options.get('invalid_combinations')
        for i in range(len(invalid_combinations)):
            with self.subTest(invalid_combinations[i]):
                _, _, error_code = self.driver.custom_post(
                    f'api/object/write/net={net.get_id()}/new_item=shaper',
                    payload={
                        'name': f'shaper-{i}',
                        'wfq_enable': 'ON',
                        'wfq1': invalid_combinations[i][0],
                        'wfq2': invalid_combinations[i][1],
                        'wfq3': invalid_combinations[i][2],
                        'wfq4': invalid_combinations[i][3],
                        'wfq5': invalid_combinations[i][4],
                        'wfq6': invalid_combinations[i][5],
                    }
                )
                self.assertEqual(WRONG_VARIABLE_VALUE, error_code)
