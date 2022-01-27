import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select

from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.exceptions import ObjectNotFoundException
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.paths_manager import PathsManager
from src.options_providers.options_provider import OptionsProvider, CHROME_CONNECT

options_path = 'test_scenarios.backup.load_default_config'
backup_name = 'default_config.txt'


class WebLoadDefaultConfigCase(CustomTestCase):
    """WEB save and load config test case (ticket 8277)"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.21'
    __execution_time__ = 20  # approximate case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)

        cls.net = Network.create(cls.driver, 0, {'name': 'test_net'})

        cls.web_driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(options_path, CHROME_CONNECT),
            driver_id='case_web_load_default_config',
            store_driver=False
        )
        cls.options = OptionsProvider.get_options(options_path)

    def test_web_save_config(self):
        """`Save config as` should save config, therefore, the filename will appear in load_config"""
        nms_edit_path = PathsManager.nms_read(self.web_driver.get_type(), 0)
        self.web_driver.load_data(nms_edit_path)
        save_filename_input = self.web_driver._get_element_by(By.ID, 'save_filename')
        if not save_filename_input:
            self.fail(f'Cannot locate save_filename input field')
        save_filename_input.send_keys(Keys.CONTROL + "a")
        save_filename_input.send_keys(Keys.DELETE)
        save_filename_input.send_keys('case_web_save_load_config')
        save_config_as_btn = self.web_driver._get_element_by(By.ID, 'save_config_as')
        if not save_config_as_btn:
            self.fail(f'Save_config_as button id={save_config_as_btn} cannot be located')
        save_config_as_btn.click()
        time.sleep(1)
        modal_mask = self.web_driver._get_element_by(By.ID, 'modalMask')
        if not modal_mask:
            self.fail(f'Modal mask cannot be located after clicking save button')
        are_you_sure = self.web_driver._get_element_by(By.CLASS_NAME, 'modal-body')
        if not are_you_sure:
            self.fail(f'Cannot locate modal-body class inside modal mask')
        self.assertEqual('Are you sure?', are_you_sure.text)
        yes_btn = self.web_driver._get_element_by(By.ID, 'applyModalButton')
        if not yes_btn:
            self.fail(f'`Yes` confirmation button cannot be located ')
        yes_btn.click()
        time.sleep(5)
        self.web_driver.load_data(nms_edit_path)
        load_filename_dropdown = self.web_driver._get_element_by(By.ID, 'load_filename')
        if not load_filename_dropdown:
            self.fail(f'Load_filename dropdown id={load_filename_dropdown} cannot be located')
        selector = Select(load_filename_dropdown)
        try:
            selector.select_by_value('case_web_save_load_config')
        except NoSuchElementException:
            self.fail(f'Saved filename is not in the load_filename dropdown')

    def test_web_load_config(self):
        """`Load config` should apply default_config.txt, therefore, created network will be no longer available"""
        nms_edit_path = PathsManager.nms_read(self.web_driver.get_type(), 0)
        self.web_driver.load_data(nms_edit_path)
        load_filename_dropdown = self.web_driver._get_element_by(By.ID, 'load_filename')
        if not load_filename_dropdown:
            self.fail(f'Load_filename dropdown id={load_filename_dropdown} cannot be located')
        selector = Select(load_filename_dropdown)
        selector.select_by_value('default_config.txt')
        load_config_btn = self.web_driver._get_element_by(By.ID, 'load_config')
        if not load_config_btn:
            self.fail(f'Load_config button id={load_config_btn} cannot be located')
        load_config_btn.click()
        time.sleep(1)
        modal_mask = self.web_driver._get_element_by(By.ID, 'modalMask')
        if not modal_mask:
            self.fail(f'Modal mask cannot be located after clicking save button')
        # are_you_sure = modal_mask.find_element_by_class_name('modal-body')
        are_you_sure = self.web_driver._get_element_by(By.CLASS_NAME, 'modal-body')
        if not are_you_sure:
            self.fail(f'Cannot locate modal-body class inside modal mask')
        self.assertEqual('Are you sure?', are_you_sure.text)
        yes_btn = self.web_driver._get_element_by(By.ID, 'applyModalButton')
        if not yes_btn:
            self.fail(f'`Yes` confirmation button cannot be located ')
        yes_btn.click()
        time.sleep(5)
        with self.assertRaises(
                ObjectNotFoundException,
                msg=f'network:0 is still in place after loading default config via WEB'
        ):
            self.net.read_param('name')
