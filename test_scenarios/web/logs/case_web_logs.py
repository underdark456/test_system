import time
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.options_providers.options_provider import OptionsProvider, CHROME_CONNECT

backup_name = 'each_entity.txt'
options_path = 'test_scenarios.web.logs'


class WebLogsCase(CustomTestCase):
    """WEB Logs page for supported objects control elements and options"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.24'
    __execution_time__ = 65
    __express__ = True
    _wait_time_out = 3

    @classmethod
    def set_up_class(cls):
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)
        time.sleep(5)
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(options_path, CHROME_CONNECT),
            driver_id='case_web_logs',
            store_driver=False
        )
        cls.options = OptionsProvider.get_options(options_path)
        cls.sidepanel_box_class = cls.options.get('sidepanel_box_class')
        cls.resize_box = cls.options.get('resize_box')
        cls.filter = cls.options.get('Filter')
        cls.last_statistics = cls.options.get('Last statistics')
        cls.range_selection = cls.options.get('Range selection')
        cls.problem_investigator = cls.options.get('Problem investigator')

    def set_up(self):
        self.driver.expand_tree()

    def test_nms(self):
        self.click_element_by_id('nms:0')
        self.click_element_by_id('Logs')
        self.check_next_object_logs()

    def test_network(self):
        self.click_element_by_id('net:0')
        self.click_element_by_id('Logs')
        self.check_next_object_logs()

    def test_controller(self):
        self.click_element_by_id('chb:0')
        self.click_element_by_id('Logs')
        self.check_next_object_logs()

    def test_sr_controller(self):
        self.click_element_by_id('src:0')
        self.click_element_by_id('Logs')
        self.check_next_object_logs()

    def test_sr_teleport(self):
        self.click_element_by_id('tlp:0')
        self.click_element_by_id('Logs')
        self.check_next_object_logs()

    def test_device(self):
        self.click_element_by_id('dev:0')
        self.click_element_by_id('Logs')
        self.check_next_object_logs()

    def test_bal_controller(self):
        self.click_element_by_id('bal:0')
        self.click_element_by_id('Logs')
        self.check_next_object_logs()

    def test_vno(self):
        self.click_element_by_id('vno:0')
        self.click_element_by_id('Logs')
        self.check_next_object_logs()

    def test_station(self):
        self.click_element_by_id('stn:0')
        self.click_element_by_id('Logs')
        self.check_next_object_logs()

    def test_sw_upload(self):
        self.click_element_by_id('net:0')
        self.click_element_by_id('SW upload_config')
        self.click_element_by_xpath("//a[contains(@href, 'sw_upload=0')]")
        self.click_element_by_id('Logs')
        self.check_next_object_logs()

    def check_next_object_logs(self):
        self.check_filters()
        self.check_last_statistics()
        self.check_range_selection()
        self.check_problem_investigator()
        self.check_resize()

    def check_resize(self):
        resize_box = self.driver._get_element_by(By.ID, self.resize_box.get('id'))
        self.assertIsNotNone(resize_box, msg=f'Cannot locate resize box by its id={self.resize_box.get("id")}')
        for btn_text in self.resize_box.get('buttons'):
            try:
                resize_box.find_element_by_xpath("//*[contains(text(), '" + btn_text + "')]")
            except NoSuchElementException:
                self.fail(f'Cannot locate button {btn_text} inside resize box')

    def check_filters(self):
        self.sidepanel_boxes = self.driver._get_elements_by(By.CLASS_NAME, self.sidepanel_box_class)
        for sidepanel_box in self.sidepanel_boxes:
            try:
                sidepanel_box.find_element_by_xpath("*[contains(text(), 'Filter')]")
                break
            except NoSuchElementException:
                continue
        else:
            self.fail('Cannot locate correct sidepanel box with title Filter')

        for f_name, f_id in self.filter.items():
            try:
                _filter = sidepanel_box.find_element_by_id(f_id)
            except NoSuchElementException:
                self.fail(f'Cannot locate Filter element id={f_id}')
            try:
                _filter.find_element_by_xpath("*[contains(text(), '" + f_name + "')]")
            except NoSuchElementException:
                self.fail(f'Cannot locate text {f_name} inside filter id={f_id}')
            try:
                _filter.click()
            except Exception as exc:
                self.fail(f'Cannot click {f_name} id={f_id}: {exc}')

    def check_last_statistics(self):
        sidepanel_boxes = self.driver._get_elements_by(By.CLASS_NAME, self.sidepanel_box_class)
        for sidepanel_box in sidepanel_boxes:
            try:
                sidepanel_box.find_element_by_xpath("*[contains(text(), 'Last statistics')]")
                break
            except NoSuchElementException:
                continue
        else:
            self.fail('Cannot locate correct sidepanel box with title Last statistics')
        for f_name, f_id in self.last_statistics.items():
            try:
                _filter = sidepanel_box.find_element_by_id(f_id)
            except NoSuchElementException:
                self.fail(f'Cannot locate Last statistics element id={f_id}')
            self.assertEqual(f_name, _filter.text, msg=f'Expected filter text={f_name}, got {_filter.text}')
            try:
                _filter.click()
            except Exception as exc:
                self.fail(f'Cannot click {f_name} id={f_id}: {exc}')

    def check_range_selection(self):
        sidepanel_boxes = self.driver._get_elements_by(By.CLASS_NAME, self.sidepanel_box_class)
        for sidepanel_box in sidepanel_boxes:
            try:
                sidepanel_box.find_element_by_xpath("*[contains(text(), 'Range selection')]")
                break
            except NoSuchElementException:
                continue
        else:
            self.fail('Cannot locate correct sidepanel box with title Range selection')
        for f_name, f_id in self.range_selection.items():
            try:
                _filter = sidepanel_box.find_element_by_id(f_id)
            except NoSuchElementException:
                self.fail(f'Cannot locate Range selection element id={f_id}')
            if f_name == 'Apply':
                self.assertEqual(f_name, _filter.text, msg=f'Expected filter text={f_name}, got {_filter.text}')
            else:
                parent_div = _filter.find_element_by_xpath('./..')
                try:
                    parent_div.find_element_by_xpath("*[contains(text(), '" + f_name + "')]")
                except NoSuchElementException:
                    self.fail(f'Cannot locate text {f_name} inside filter id={f_id}')
            try:
                WebDriverWait(self.driver.driver, 1).until(
                    expected_conditions.element_to_be_clickable((By.ID, f_id))
                )
            except TimeoutException:
                self.fail(f'Cannot click {f_name} id={f_id}')

    def check_problem_investigator(self):
        sidepanel_boxes = self.driver._get_elements_by(By.CLASS_NAME, self.sidepanel_box_class)
        for sidepanel_box in sidepanel_boxes:
            try:
                sidepanel_box.find_element_by_xpath("*[contains(text(), 'Problem investigator')]")
                break
            except NoSuchElementException:
                continue
        else:
            self.fail('Cannot locate correct sidepanel box with title Problem investigator')
        for f_name, f_id in self.problem_investigator.items():
            try:
                _filter = sidepanel_box.find_element_by_id(f_id)
            except NoSuchElementException:
                self.fail(f'Cannot locate Problem investigator element id={f_id}')
            self.assertEqual(f_name, _filter.text, msg=f'Expected filter text={f_name}, got {_filter.text}')

            self.assertTrue(_filter.is_displayed() and _filter.is_enabled(), msg=f'Cannot click {f_name} id={f_id}')

    def click_element_by_id(self, _id):
        el = self.driver._get_element_by(By.ID, _id, timeout=self._wait_time_out)
        if el is None:
            self.fail(f'WEB element id={_id} cannot be located and clicked at {self.driver.get_current_url()}')
        el.click()
        time.sleep(1)

    def click_element_by_xpath(self, xpath):
        el = self.driver._get_element_by(By.XPATH, xpath, timeout=self._wait_time_out)
        if el is None:
            self.fail(f'WEB element xpath={xpath} cannot be located and clicked at {self.driver.get_current_url()}')
        el.click()
        time.sleep(1)
