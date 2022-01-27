from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.paths_manager import PathsManager
from src.options_providers.options_provider import OptionsProvider

__author__ = 'dkudryashov'
__version__ = '0.1'
options_path = 'test_scenarios.tickets.subtests.7762'
backup_name = 'default_config.txt'


class TdmaModcodWebCase(CustomTestCase):
    """Ticket 7762. TDMA modcod via WEB"""

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(options_path)
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)
        cls.options = OptionsProvider.get_options(options_path)
        cls.net = Network.create(cls.driver, 0, {'name': 'net-0'})

    def test_tdma_modcod_options(self):
        """Check that all the TDMA modcodes are seen in the options of `tdma_mc`"""
        # Loading `/form/new/network=0/new_item=controller` page
        path = PathsManager.controller_create(self.driver.get_type(), self.net.get_id())
        self.driver.load_data(path)

        # Setting `mode` to `MF Hub` in order to get TDMA options
        self.driver.set_value('mode', ControllerModes.MF_HUB)

        # TODO: private method is used. Make a new public method
        tdma_mc = self.driver._get_element_by(By.ID, 'tdma_mc')
        self.assertIsNotNone(tdma_mc, 'Cannot locate `tdma_mc` parameter')
        self.assertEqual('select', tdma_mc.tag_name, 'tdma_mc` tag is not select')

        tdma_mc_options = [x.text for x in tdma_mc.find_elements_by_tag_name("option")]
        for option in self.options.get('tdma_modcodes'):
            with self.subTest(option):
                self.assertIn(option, tdma_mc_options)
        self.assertEqual(len(self.options.get('tdma_modcodes')), len(tdma_mc_options))

    def test_mf_channels_visibility(self):
        """Check that MF channels section of a controller is visible"""
        path = PathsManager.controller_create(self.driver.get_type(), self.net.get_id())
        self.driver.load_data(path)
        # Setting `mode` to `MF Hub` in order to get MF channels
        self.driver.set_value('mode', ControllerModes.MF_HUB)

        if self.driver._get_element_by(By.ID, 'mf17_en') is None:
            # Probably MF channels are folded
            mf_channels_title = self.driver._get_element_by(By.ID, 'MF Channels_title')
            self.assertIsNotNone(mf_channels_title, 'MF channels section is absent')
            action = ActionChains(self.driver.driver)
            action.move_to_element(mf_channels_title)
            action.click().perform()

        for i in range(1, 17):
            with self.subTest(f'mf{i}_en'):
                self.assertIsNotNone(self.driver._get_element_by(By.ID, f'mf{i}_en'))
            with self.subTest(f'mf{i}_tx'):
                self.assertIsNotNone(self.driver._get_element_by(By.ID, f'mf{i}_tx'))
            with self.subTest(f'mf{i}_rx'):
                self.assertIsNotNone(self.driver._get_element_by(By.ID, f'mf{i}_rx'))

    def tear_down(self) -> None:
        pass

    @classmethod
    def tear_down_class(cls) -> None:
        pass