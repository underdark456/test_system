from src.backup_manager.backup_manager import BackupManager
from src.constants import NO_ERROR, WRONG_VARIABLE_VALUE
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.teleport import Teleport
from src.options_providers.options_provider import OptionsProvider

__author__ = 'dkudryashov'
__version__ = '0.1'
options_path = 'test_scenarios.tickets.subtests.7709'
backup_name = 'default_config.txt'


class ModQueuesCombinationsCase(CustomTestCase):
    """Ticket 7709. Queues minimum and maximum sizes"""

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.options = OptionsProvider.get_options(options_path)
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)
        cls.net = Network.create(cls.driver, 0, {'name': 'net-0'})
        cls.tp = Teleport.create(cls.driver, cls.net.get_id(), {'name': 'tp-0'})
        cls.ctrl = Controller.create(cls.driver, cls.net.get_id(), {
            'name': 'ctrl-0',
            'mode': ControllerModes.HUBLESS_MASTER,
            'teleport': f'teleport:{cls.tp.get_id()}'
        })

    def test_valid_combinations(self):
        """Test valid combinations of a controller queues"""
        valid_combinations = self.options.get('valid_combinations')
        for comb in valid_combinations:
            params = {
                'mod_queue1': comb[0],
                'mod_queue2': comb[1],
                'mod_queue3': comb[2],
                'mod_queue4': comb[3],
                'mod_queue5': comb[4],
                'mod_queue6': comb[5],
                'mod_queue7': comb[6],
                'mod_que_ctl': comb[7],
            }
            with self.subTest(comb):
                _, _, error_code = self.driver.custom_post(
                    f'api/object/write/controller={self.ctrl.get_id()}',
                    payload=params
                )
                self.assertEqual(NO_ERROR, error_code)

    def test_invalid_combinations(self):
        """Test invalid combinations of a controller queues"""
        invalid_combinations = self.options.get('invalid_combinations')
        for comb in invalid_combinations:
            params = {
                'mod_queue1': comb[0],
                'mod_queue2': comb[1],
                'mod_queue3': comb[2],
                'mod_queue4': comb[3],
                'mod_queue5': comb[4],
                'mod_queue6': comb[5],
                'mod_queue7': comb[6],
                'mod_que_ctl': comb[7],
            }
            with self.subTest(comb):
                _, _, error_code = self.driver.custom_post(
                    f'api/object/write/controller={self.ctrl.get_id()}',
                    payload=params
                )
                self.assertEqual(WRONG_VARIABLE_VALUE, error_code)
