from src.backup_manager.backup_manager import BackupManager
from src.constants import NEW_OBJECT_ID
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.exceptions import ObjectNotCreatedException
from src.nms_entities.basic_entities.network import Network
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.creating_objects.same_name'
backup_name = 'default_config.txt'


class SameObjectsNameCase(CustomTestCase):
    """Create/edit objects to get existing names"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.20'
    __execution_time__ = 55  # approximate test execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()

    def set_up(self) -> None:
        self.backup.apply_backup(backup_name)

    def test_same_name_net_create(self):
        """Same name network create test"""
        for i in range(128):
            net = Network(self.driver, 0, NEW_OBJECT_ID, {'name': f'test_net'})
            if i == 0:
                net.save()
                continue
            with self.assertRaises(ObjectNotCreatedException, msg=f'Network with the existing name has been created'):
                net.save()

    def test_same_name_net_edit(self):
        """Same name network edit test"""
        for i in range(128):
            Network.create(self.driver, 0, {'name': f'test_net{i}'})
        for i in range(1, 128):
            net = Network(self.driver, 0, i)
            net.send_param('name', 'test_net0')
            self.assertNotEqual(
                'test_net0',
                net.read_param('name'),
                msg=f'Network name has been changed to the existing one'
            )

    def test_same_name_next_object(self):
        """Same name network edit test (ticket 8056)"""
        # According to ticket 8056 it is possible to apply the same name as for the next object
        for i in range(127):
            Network.create(self.driver, 0, {'name': f'net{i}'})
        Network.create(self.driver, 0, {'name': 'same_name_net'})

        index = 127
        for _ in range(128):
            for i in range(128):
                net = Network(self.driver, 0, i)
                next_ = net.read_param('next')
                if next_ == '':
                    continue
                else:
                    next_ = next_.split()[0]
                if next_ == f'network:{index}':
                    prev_net = Network(self.driver, 0, i)
                    prev_net.send_param('name', 'same_name_net')
                    self.assertTrue(
                        prev_net.has_param_error('name'),
                        msg=f'Sending same name as for next row does not cause error'
                    )
                    self.assertNotEqual(
                        'same_name_net',
                        prev_net.read_param('name'),
                        msg='Same network name has been applied'
                    )
                    index = i
                    break
