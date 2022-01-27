import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select

from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.exceptions import ObjectNotFoundException
from src.nms_entities.abstract_basic_object import AbstractBasicObject
from src.nms_entities.basic_entities.bal_controller import BalController
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.device import Device
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.nms import Nms
from src.nms_entities.basic_entities.sr_controller import SrController
from src.nms_entities.basic_entities.sr_teleport import SrTeleport
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.sw_upload import SwUpload
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider, CHROME_CONNECT

options_path = 'test_scenarios.web.investigator'
backup_name = 'each_entity.txt'


class WebInvestigatorCase(CustomTestCase):
    """WEB Investigator functionality test case"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.27'
    __execution_time__ = 160  # approximate case execution time in seconds
    __express__ = True
    driver = None
    _wait_time_out = 1

    @classmethod
    def set_up_class(cls):
        cls.backup = BackupManager()
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(options_path, CHROME_CONNECT),
            driver_id='case_web_investigator',
            store_driver=False
        )
        cls.options = OptionsProvider.get_options(options_path)
        # a dict containing names of supported entities and a flag indicated if it is possible to get the graph
        cls.devices_graphs = cls.options.get('devices_graphs')
        cls.inv_search_title_class = 'investigator__search-title'
        cls.inv_search_input_class = 'investigator__search-input'
        cls.inv_tag_class = 'inv-tag'
        cls.search_results_class = 'search-util__modal.investigator__search-modal'
        cls.inv_tag_select_class = 'inv-tag__select'
        cls.tree_body_class = 'tree__body'
        cls.nms = Nms(cls.driver, 0, 0)
        cls.net = Network(cls.driver, 0, 0)
        cls.vno = Vno(cls.driver, 0, 0)
        cls.ctrl = Controller(cls.driver, 0, 0)
        cls.sr_ctrl = SrController(cls.driver, 0, 0)
        cls.sr_tp = SrTeleport(cls.driver, 0, 0)
        cls.dev = Device(cls.driver, 0, 0)
        cls.bal_ctrl = BalController(cls.driver, 0, 0)
        cls.stn = Station(cls.driver, 0, 0)
        cls.sw_upload = SwUpload(cls.driver, 0, 0)

    def set_up(self):
        self.devices_added = 0
        self.backup.apply_backup(backup_name)
        self.driver.driver.execute_script('window.localStorage.clear();')

    def test_add_devices(self):
        """Add all supported devices via logs and graphs. Check Investigator output. Check Clear All as well"""
        self.add_nms()
        self.add_network()
        self.add_vno()
        self.add_controller()
        self.add_sr_controller()
        self.add_sr_teleport()
        self.add_device()
        self.add_bal_controller()
        self.add_station()
        self.add_sw_upload()

        self.nms.investigator()
        self.clear_all()
        self.number_of_devices()

    def test_delete_added_object(self):
        """Delete added device via form edit (ticket 8352)"""
        self.net.delete()
        self.devices_added -= 1
        self.check_investigator()

    def test_delete_added_devices(self):
        """Delete added devices via investigator form"""
        self.log_add_device(self.nms)
        self.log_add_device(self.net)
        self.log_add_device(self.vno)
        self.log_add_device(self.ctrl)
        self.log_add_device(self.sr_ctrl)
        self.log_add_device(self.sr_tp)
        self.log_add_device(self.dev)
        self.log_add_device(self.bal_ctrl)
        self.log_add_device(self.stn)
        self.log_add_device(self.sw_upload)

        self.check_investigator()
        dev_list = self.driver._get_elements_by(By.CLASS_NAME, self.inv_tag_class)
        self.assertIsNotNone(dev_list, msg=f'Cannot get list of added devices in Investigator')
        # Getting a list of added devices in Investigator, delete first found device, start over again
        for _ in range(100):
            dev_list = self.driver._get_elements_by(By.CLASS_NAME, self.inv_tag_class)
            if dev_list is None:  # No devices found, breaking the deletion cycle
                break
            for dev in dev_list:
                try:
                    name_tag = dev.find_element_by_id('name')
                except NoSuchElementException:
                    self.fail('Cannot find next device name via id=name')
                self.assertIn(
                    name_tag.text,
                    self.devices_graphs.keys(),
                    msg=f'{name_tag.text} is unexpectedly not in devices names'
                )
                try:
                    delete_btn = dev.find_element_by_id('deleteButton')
                except NoSuchElementException:
                    self.fail(f'Cannot find delete button for {name_tag.text}')
                delete_btn.click()  # deleting next device
                time.sleep(0.2)
                break
        self.number_of_devices()  # Checking the number of devices in Investigator after deleting all, should be zero

    def test_logs_graphs(self):
        """Check graphs label for supported objects, should be disabled for the unsupported ones"""
        self.log_add_device(self.nms)
        self.log_add_device(self.net)
        self.log_add_device(self.vno)
        self.log_add_device(self.ctrl)
        self.log_add_device(self.sr_ctrl)
        self.log_add_device(self.sr_tp)
        self.log_add_device(self.dev)
        self.log_add_device(self.bal_ctrl)
        self.log_add_device(self.stn)
        self.log_add_device(self.sw_upload)
        self.check_investigator()

        for name, flag in self.devices_graphs.items():
            dev_list = self.driver._get_elements_by(By.CLASS_NAME, self.inv_tag_class)
            self.assertIsNotNone(dev_list, msg=f'Cannot get list of added devices in Investigator')
            for dev in dev_list:
                try:
                    name_tag = dev.find_element_by_id('name')
                except NoSuchElementException:
                    self.fail('Cannot find next device name via id=name')
                if name_tag.text == name:
                    try:
                        log_label = dev.find_element_by_id('tagLogLabel')
                        log_label_input = log_label.find_element_by_id('logs')
                    except NoSuchElementException:
                        self.fail('Cannot find next device log label by id')
                    try:
                        graph_label = dev.find_element_by_id('tagGraphLabel')
                    except NoSuchElementException:
                        self.fail('Cannot find next device graph label by id')
                    if flag:
                        self.assertIsNone(log_label_input.get_attribute('disabled'))
                        graph_label.click()
                    else:
                        graph_label_input = graph_label.find_element_by_id('graph')
                        self.assertIsNotNone(
                            graph_label_input.get_attribute('disabled'),
                            msg=f'Graphs label is not disabled for {name}'
                        )
                    time.sleep(0.2)
                    break
            else:
                self.fail(f'{name} is not found in added devices')

    def test_search(self):
        """Find devices via search field in Investigator"""
        self.nms.send_param('name', 'test_nms')
        self.nms.investigator()
        search_field = self.driver._get_element_by(By.CLASS_NAME, self.inv_search_input_class)
        self.assertIsNotNone(
            search_field,
            msg=f'Cannot locate search input field by it class name {self.inv_search_input_class}'
        )
        search_field.send_keys('test')
        time.sleep(1)
        search_result = self.driver._get_element_by(By.CLASS_NAME, self.search_results_class)
        self.assertIsNotNone(
            search_result,
            f'Cannot locate search result by its class name {self.search_results_class}'
        )
        for name in self.devices_graphs.keys():
            with self.subTest(f'{name} in search results'):
                if name == 'UHP NMS':
                    name = 'test_nms'
                try:
                    search_result.find_element_by_xpath(".//*[contains(text(), '" + name + "')]")
                except NoSuchElementException:
                    self.fail(msg=f'Cannot locate {name} in search results')

    def test_add_via_search(self):
        """Add device via search in Investigator"""
        self.nms.investigator()
        search_field = self.driver._get_element_by(By.CLASS_NAME, self.inv_search_input_class)
        self.assertIsNotNone(
            search_field,
            msg=f'Cannot locate search input field by it class name {self.inv_search_input_class}'
        )
        search_field.send_keys('test_ctrl')
        time.sleep(1)
        search_result = self.driver._get_element_by(By.CLASS_NAME, self.search_results_class)
        self.assertIsNotNone(
            search_result,
            f'Cannot locate search result by its class name {self.search_results_class}'
        )
        try:
            el = search_result.find_element_by_xpath(".//*[contains(text(), 'test_ctrl')]")
        except NoSuchElementException:
            self.fail(msg=f'Cannot locate test_ctrl in search results')
        el.click()
        time.sleep(1)
        self.devices_added += 1
        self.number_of_devices(1)

    def test_graphs_options(self):
        """Check expected graphs options for devices supported graphs"""
        self.log_add_device(self.nms)
        self.graph_add_device(self.net)
        self.graph_add_device(self.vno)
        self.graph_add_device(self.ctrl)
        self.graph_add_device(self.stn)
        self.nms.investigator()

        self.check_graph_options('UHP NMS', ['CPU load'])
        self.check_graph_options('test_network', self.options.get('graph_options_net'))
        self.check_graph_options('test_vno', self.options.get('graph_options_vno'))
        self.check_graph_options('test_ctrl', self.options.get('graph_options_ctrl'))
        self.check_graph_options('test_stn', self.options.get('graph_options_stn'))

    def test_add_device_from_tree(self):
        """Add devices from tree using Shift + Ctrl + left click"""
        self.nms.load()
        self.driver.expand_tree()
        tree = self.driver._get_element_by(By.CLASS_NAME, self.tree_body_class)
        self.assertIsNotNone(tree, msg=f'Cannot get tree container by its class name {self.tree_body_class}')

        names = self.options.get('devices_graphs').keys()
        for name in names:
            if name == 'test_sw_up':
                continue
            try:
                next_element = tree.find_element_by_xpath(".//*[contains(text(), '" + name + "')]")
            except NoSuchElementException:
                self.fail(f'Cannot locate {name} in the tree')
            self.add_from_tree(next_element)
            self.devices_added += 1
        self.check_investigator()

    def add_from_tree(self, element):
        ActionChains(self.driver.driver) \
            .key_down(Keys.SHIFT) \
            .key_down(Keys.CONTROL) \
            .click(element) \
            .key_up(Keys.CONTROL) \
            .key_up(Keys.SHIFT) \
            .perform()

    def check_graph_options(self, obj_name, options):
        for option in options:
            dev_list = self.driver._get_elements_by(By.CLASS_NAME, self.inv_tag_class)
            self.assertIsNotNone(dev_list, msg=f'Cannot locate inv tags')
            for dev in dev_list:
                try:
                    name_tag = dev.find_element_by_id('name')
                except NoSuchElementException:
                    self.fail('Cannot find next device name via id=name')
                if name_tag.text == obj_name:
                    try:
                        select_tag = dev.find_element_by_class_name(self.inv_tag_select_class)
                    except NoSuchElementException:
                        self.fail(f'Cannot locate graphs options selector for {obj_name}')
                    self.assertEqual('select', select_tag.tag_name, f'Found element is not selector')
                    select = Select(select_tag)
                    for select_option in select.options:
                        if select_option.text == option:
                            select.select_by_visible_text(option)
                            time.sleep(0.2)
                            break
                    else:
                        self.fail(f'Option {option} is not found in selector for {obj_name}')
                    break
            else:
                self.fail(f'Device {obj_name} is not found in Investigator added devices')

    def add_nms(self):
        self.log_add_device(self.nms)
        self.log_sync_add(self.nms)
        self.check_investigator(added='nms')

    def add_network(self):
        self.log_add_device(self.net)
        self.log_sync_add(self.net)
        self.graph_add_device(self.net)
        self.graph_sync_add(self.net)

    def add_vno(self):
        self.log_add_device(self.vno)
        self.log_sync_add(self.vno)
        self.graph_add_device(self.net)
        self.graph_sync_add(self.net)

    def add_controller(self):
        self.log_add_device(self.ctrl)
        self.log_sync_add(self.ctrl)
        self.graph_add_device(self.net)
        self.graph_sync_add(self.net)

    def add_sr_controller(self):
        self.log_add_device(self.sr_ctrl)
        self.log_sync_add(self.sr_ctrl)

    def add_sr_teleport(self):
        self.log_add_device(self.sr_tp)
        self.log_sync_add(self.sr_tp)

    def add_device(self):
        self.log_add_device(self.dev)
        self.log_sync_add(self.dev)

    def add_bal_controller(self):
        self.log_add_device(self.bal_ctrl)
        self.log_sync_add(self.bal_ctrl)

    def add_station(self):
        self.log_add_device(self.stn)
        self.log_sync_add(self.stn)
        self.graph_add_device(self.stn)
        self.graph_sync_add(self.stn)

    def add_sw_upload(self):
        self.log_add_device(self.sw_upload)
        self.log_sync_add(self.sw_upload)

    def log_add_device(self, _obj: AbstractBasicObject):
        _obj.log_add_device_investigator()
        self.devices_added += 1
        self.check_investigator()

    def log_sync_add(self, _obj: AbstractBasicObject):
        _obj.log_sync_add_investigator()
        self.devices_added += 1
        self.check_investigator()

    def graph_add_device(self, _obj: AbstractBasicObject):
        _obj.graph_add_device_investigator()
        self.devices_added += 1
        self.check_investigator()

    def graph_sync_add(self, _obj: AbstractBasicObject):
        _obj.graph_sync_add_investigator()
        self.devices_added += 1
        self.check_investigator()

    def check_investigator(self, added='not specified'):
        try:
            self.nms.investigator()
        except ObjectNotFoundException as exc:
            self.fail(msg=f'Cannot get NMS investigator: {exc}')
        self.assertFalse(self._is_404(), msg=f'404 upon getting NMS investigator')
        self.assertFalse(self._is_400(), msg=f'400 upon getting NMS investigator')

        self.number_of_devices(self.devices_added)

    def number_of_devices(self, expected=0):
        title = self.driver._get_element_by(By.CLASS_NAME, self.inv_search_title_class)
        self.assertIsNotNone(title, msg=f'Cannot locate investigator search title')
        num_of_devices = title.text.split()[1].lstrip('[').rstrip(']')  # string
        self.assertEqual(
            str(expected),
            num_of_devices,
            msg=f'Expected {expected} in investigator title list, got {num_of_devices}'
        )
        inv_tags = self.driver._get_elements_by(By.CLASS_NAME, self.inv_tag_class)
        if not expected:
            self.assertIsNone(inv_tags, msg=f'Number of inv tags should be 0')
        else:
            self.assertEqual(expected, len(inv_tags), msg=f'Number of inv tags is {len(inv_tags)}, expected {expected}')

    def clear_all(self):
        self.click_element_by_visible_text('Clear All')

    @classmethod
    def tear_down_class(cls) -> None:
        if cls.driver is not None:
            cls.driver.driver.execute_script('window.localStorage.clear();')

    def click_element_by_id(self, _id):
        el = self.driver._get_element_by(By.ID, _id, timeout=self._wait_time_out)
        if el is None:
            self.fail(f'WEB element id={_id} cannot be located and clicked at {self.driver.get_current_url()}')
        el.click()
        time.sleep(1)

    def click_element_by_visible_text(self, text):
        el = self.driver._get_element_by(By.XPATH, "//*[contains(text(), '" + text + "')]", timeout=self._wait_time_out)
        if el is None:
            self.fail(f'WEB element text={text} cannot be located and clicked at {self.driver.get_current_url()}')
        el.click()
        time.sleep(1)

    def _is_404(self):
        return self.driver.get_current_url().find('notfound') != -1

    def _is_400(self):
        return self.driver.get_current_url().find('badrequest') != -1
