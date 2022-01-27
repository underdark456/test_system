import json
import os
import time
from urllib.parse import urlparse

from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotInteractableException, \
    StaleElementReferenceException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from global_options.options import PROJECT_DIR
from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.web.web_broken_links'
backup_name = 'case_web_broken_links.txt'


class WebWalkAllLinksNoRefreshCase(CustomTestCase):
    """Click all links in WEB interface without reloading page"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.22'
    __execution_time__ = None
    _wait_time_out = 3

    @classmethod
    def set_up_class(cls):
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(options_path), driver_id='case_web_broken_links_js', store_driver=False
        )
        # Getting a dictionary of used NMS menu items from JSON file
        with open(f'{PROJECT_DIR}{os.sep}{options_path.replace(".", os.sep)}{os.sep}newmenu.json') as f:
            cls.menu_elements = json.load(f)

        cls.options = OptionsProvider.get_options(options_path)  # to get class names used in menu
        cls.menu_main_class = cls.options.get('menu_main_class')
        cls.menu_config_class = cls.options.get('menu_config_class')
        cls.breadcrumbs_item_class = cls.options.get('breadcrumb_items_class')
        cls.dashboard = cls.options.get('dashboard_id')
        cls.names = cls.options.get('object_names')
        time.sleep(2)

    def set_up(self):
        self.driver.expand_tree()

    def check_menu_available(self):
        """
        Check if expected menu main and menu config are located

        :returns tuple: menu main and menu config web elements
        """
        menu_main = self.driver._get_element_by(By.CLASS_NAME, self.menu_main_class, timeout=self._wait_time_out)
        self.assertIsNotNone(menu_main, msg=f'Cannot locate menu main')
        menu_config = self.driver._get_element_by(By.CLASS_NAME, self.menu_config_class, timeout=self._wait_time_out)
        self.assertIsNotNone(menu_config, msg=f'Cannot locate menu config')
        return menu_main, menu_config

    def check_and_click_element(self, el, menu_main, menu_config):
        """Check if element is available and click it

        :param dict el: element dictionary from JSON file
        :param menu_main: web element representing menu main
        :param menu_config: web element representing menu_config
        :returns tuple: element ID and menu web element in which it is located
        """
        _id = el.get('title')
        href = self.get_expected_href(el)
        if el.get('icon') is not None:
            _obj = menu_main
        else:
            _obj = menu_config
        try:
            web_elem = _obj.find_element_by_id(_id)
        except NoSuchElementException:
            self.fail(f'Cannot locate element id={_id} inside menu')
        self.assertNotEqual(-1, web_elem.get_attribute('href').find(href), msg=f'{_id} href is unexpected')
        self.click_element_by_id(_id)
        time.sleep(0.5)
        return _id, _obj

    def check_expected_path(self, parent_name, el, _id, same_path_id):
        """Check if URL after right-clicking is as expected"""
        if _id == same_path_id:
            self.assertNotEqual(-1, self.driver.get_current_url().find(f'form/edit/{parent_name}=0'))
        else:
            nms_name = el.get('ext')[el.get('ext').find('=') + 1:]
            self.assertNotEqual(-1, self.driver.get_current_url().find(f'form/new/{parent_name}=0/new_item={nms_name}'))

    def check_dahsboard(self):
        self.click_element_by_id(self.dashboard)
        self.assertFalse(self._is_404())
        self.assertFalse(self._is_400())

    def check_breadcrumbs(self, breadcrumbs, dashboard=False, last_object=False):
        current = self.current_breadcrumbs()
        expected = self.expected_breadcrumbs(breadcrumbs, dashboard=dashboard, last_object=last_object)
        self.assertEqual(len(expected), len(current), msg=f'Current number of breadcrumbs is not {len(expected)}')
        for i in range(len(expected)):
            self.assertEqual(expected[i].split('_|_')[0], current[i].split('_|_')[0])
            self.assertEqual(expected[i].split('_|_')[1].lower(), current[i].split('_|_')[1].lower())

    def test_nms(self):
        """Clicking at all menu main and menu config NMS"""
        self.click_element_by_id('nms:0', breadcrumbs=['nms'], dashboard=True)  # starting at NMS dashboard
        menu_main, menu_config = self.check_menu_available()
        for el in self.menu_elements.get('nms'):
            _id, _obj = self.check_and_click_element(el, menu_main, menu_config)
            # Right clicking menu config items
            if _obj == menu_config:
                self.right_click_element_by_id(_id)
                if _id == 'NMS_config':  # Right clicking at NMS config btn is the same as left clicking
                    self.assertNotEqual(-1, self.driver.get_current_url().find('form/edit/nms=0'))
                elif _id == 'Files_config':  # Right clicking at Files config btn is the same as left clicking
                    self.assertNotEqual(-1, self.driver.get_current_url().find('fs/dirs/nms=0'))
                else:  # Right clicking at the rest NMS config elements should open a new object creation form
                    nms_name = el.get('ext')[el.get('ext').find('=') + 1:]
                    self.assertNotEqual(-1, self.driver.get_current_url().find(f'form/new/nms=0/new_item={nms_name}'))
        self.check_breadcrumbs(['nms', 'dashboard'])
        self.check_dahsboard()
        self.check_breadcrumbs(['nms', ], dashboard=True)

    def test_network(self):
        # Getting into network=0
        self.click_element_by_id('net:0', breadcrumbs=['nms', 'network'], dashboard=True, last_object=True)
        menu_main, menu_config = self.check_menu_available()
        for el in self.menu_elements.get('network'):
            _id, _obj = self.check_and_click_element(el, menu_main, menu_config)
            # Right clicking menu config items
            if _obj == menu_config:
                self.right_click_element_by_id(_id)
                self.check_expected_path('network', el, _id, 'Network_config')
        self.check_breadcrumbs(['nms', 'network', 'qos'])
        self.check_dahsboard()
        self.check_breadcrumbs(['nms', 'network'], dashboard=True, last_object=True)

    def test_vno(self):
        # Getting into vno=0
        self.click_element_by_id('vno:0')  # starting at Controller dashboard
        menu_main, menu_config = self.check_menu_available()
        for el in self.menu_elements.get('vno'):
            _id, _obj = self.check_and_click_element(el, menu_main, menu_config)
            # Right clicking menu config items
            if _obj == menu_config:
                self.right_click_element_by_id(_id)
                self.check_expected_path('vno', el, _id, 'VNO_config')
        self.check_dahsboard()

    def test_controller(self):
        # Getting into controller=0
        self.click_element_by_id('chb:0')  # starting at Controller dashboard
        menu_main, menu_config = self.check_menu_available()
        for el in self.menu_elements.get('controller'):
            _id, _obj = self.check_and_click_element(el, menu_main, menu_config)
            # Right clicking menu config items
            if _obj == menu_config:
                self.right_click_element_by_id(_id)
                self.check_expected_path('controller', el, _id, 'Controller_config')
        self.check_dahsboard()

    def test_sr_controller(self):
        self.click_element_by_id('src:0')
        menu_main, menu_config = self.check_menu_available()
        for el in self.menu_elements.get('sr_controller'):
            _id, _obj = self.check_and_click_element(el, menu_main, menu_config)
            # Right clicking menu config items
            if _obj == menu_config:
                self.right_click_element_by_id(_id)
                self.check_expected_path('sr_controller', el, _id, 'SR_ctrlr_config')
        self.check_dahsboard()

    def test_bal_controller(self):
        self.click_element_by_id('bal:0')
        menu_main, menu_config = self.check_menu_available()
        for el in self.menu_elements.get('bal_controller'):
            _id, _obj = self.check_and_click_element(el, menu_main, menu_config)
            # Right clicking menu config items
            if _obj == menu_config:
                self.right_click_element_by_id(_id)
                self.check_expected_path('bal_controller', el, _id, 'Bal_ctrlr_config')
        self.check_dahsboard()

    def test_sw_upload(self):
        self.click_element_by_id('net:0')
        self.click_element_by_id('SW upload_config')
        self.click_element_by_xpath("//a[contains(@href, 'sw_upload=0')]")
        menu_main, menu_config = self.check_menu_available()
        for el in self.menu_elements.get('sw_upload'):
            _id, _obj = self.check_and_click_element(el, menu_main, menu_config)
            # Right clicking menu config items
            if _obj == menu_config:
                self.right_click_element_by_id(_id)
                self.check_expected_path('sw_upload', el, _id, 'SW upload_config')
        self.check_dahsboard()

    def test_station(self):
        self.click_element_by_id('stn:0')
        menu_main, menu_config = self.check_menu_available()
        for el in self.menu_elements.get('station'):
            _id, _obj = self.check_and_click_element(el, menu_main, menu_config)
            # Right clicking menu config items
            if _obj == menu_config:
                self.right_click_element_by_id(_id)
                self.check_expected_path('station', el, _id, 'Station_config')
        self.check_dahsboard()

    def test_sr_teleport(self):
        self.click_element_by_id('net:0')
        self.click_element_by_id('SR_ctrlr')
        self.click_element_by_xpath("//a[contains(@href, 'sr_controller=0')]")
        self.click_element_by_id('SR teleports')
        self.click_element_by_xpath("//a[contains(@href, 'sr_teleport=0')]")
        menu_main, menu_config = self.check_menu_available()
        for el in self.menu_elements.get('sr_teleport'):
            _id, _obj = self.check_and_click_element(el, menu_main, menu_config)
            # Right clicking menu config items
            if _obj == menu_config:
                self.right_click_element_by_id(_id)
                self.check_expected_path('sr_teleport', el, _id, 'SR teleport_config')
        self.check_dahsboard()

    def test_device(self):
        self.click_element_by_id('net:0', breadcrumbs=['nms', 'network'], dashboard=True, last_object=True)
        self.click_element_by_id('SR_ctrlr', breadcrumbs=['nms', 'network', 'sr_controller'], dashboard=True)
        self.click_element_by_xpath(
            "//a[contains(@href, 'sr_controller=0')]",
            breadcrumbs=['nms', 'network', 'sr_controller'], dashboard=True, last_object=True
        )
        self.click_element_by_id(
            'SR teleports',
            breadcrumbs=['nms', 'network', 'sr_controller', 'sr_teleport'], dashboard=True,
        )
        self.click_element_by_xpath(
            "//a[contains(@href, 'sr_teleport=0')]",
            breadcrumbs=['nms', 'network', 'sr_controller', 'sr_teleport'], dashboard=True, last_object=True
        )
        self.click_element_by_id(
            'Devices_config',
            breadcrumbs=['nms', 'network', 'sr_controller', 'sr_teleport', 'device']
        )
        self.click_element_by_xpath(
            "//a[contains(@href, 'edit/device=0')]",
            breadcrumbs=['nms', 'network', 'sr_controller', 'sr_teleport', 'device'], last_object=True
        )
        menu_main, menu_config = self.check_menu_available()
        for el in self.menu_elements.get('device'):
            _id, _obj = self.check_and_click_element(el, menu_main, menu_config)
            # Right clicking menu config items
            if _obj == menu_config:
                self.right_click_element_by_id(_id)
                self.check_expected_path('device', el, _id, 'Device_config')
                self.check_breadcrumbs(['nms', 'network', 'sr_controller', 'sr_teleport', 'device'], last_object=True)
        self.check_breadcrumbs(['nms', 'network', 'sr_controller', 'sr_teleport', 'device'], last_object=True)
        self.check_dahsboard()
        self.check_breadcrumbs(['nms', 'network', 'sr_controller', 'sr_teleport', 'device'], dashboard=True, last_object=True)

    def test_group(self):
        self.click_element_by_id('nms:0')
        self.click_element_by_id('User groups_config')
        self.click_element_by_xpath("//a[contains(@href, 'group=0')]")
        menu_main, menu_config = self.check_menu_available()
        for el in self.menu_elements.get('group'):
            _id, _obj = self.check_and_click_element(el, menu_main, menu_config)
            # Right clicking menu config items
            if _obj == menu_config:
                self.right_click_element_by_id(_id)
                self.check_expected_path('group', el, _id, None)

    def test_alert(self):
        self.click_element_by_id('nms:0')
        self.click_element_by_id('Alerts_config')
        self.click_element_by_xpath("//a[contains(@href, 'alert=0')]")
        menu_main, menu_config = self.check_menu_available()
        for el in self.menu_elements.get('alert'):
            _id, _obj = self.check_and_click_element(el, menu_main, menu_config)
            # Right clicking menu config items
            if _obj == menu_config:
                self.right_click_element_by_id(_id)
                self.check_expected_path('alert', el, _id, 'Alert_config')

    def test_service(self):
        self.click_element_by_id('net:0')
        self.click_element_by_id('Services_config')
        self.click_element_by_xpath("//a[contains(@href, 'service=0')]")
        menu_main, menu_config = self.check_menu_available()
        for el in self.menu_elements.get('service'):
            _id, _obj = self.check_and_click_element(el, menu_main, menu_config)
            # Right clicking menu config items
            if _obj == menu_config:
                self.right_click_element_by_id(_id)
                self.check_expected_path('service', el, _id, 'Service_config')
        self.check_dahsboard()

    def test_shaper(self):
        self.click_element_by_id('net:0')
        self.click_element_by_id('Shapers_config')
        self.click_element_by_xpath("//a[contains(@href, 'shaper=0')]")
        menu_main, menu_config = self.check_menu_available()
        for el in self.menu_elements.get('shaper'):
            _id, _obj = self.check_and_click_element(el, menu_main, menu_config)
            # Right clicking menu config items
            if _obj == menu_config:
                self.right_click_element_by_id(_id)
                self.check_expected_path('shaper', el, _id, 'Shaper_config')

    def test_policy(self):
        self.click_element_by_id('net:0')
        self.click_element_by_id('Policies_config')
        self.click_element_by_xpath("//a[contains(@href, 'policy=0')]")
        menu_main, menu_config = self.check_menu_available()
        for el in self.menu_elements.get('policy'):
            _id, _obj = self.check_and_click_element(el, menu_main, menu_config)
            # Right clicking menu config items
            if _obj == menu_config:
                self.right_click_element_by_id(_id)
                self.check_expected_path('policy', el, _id, 'Policy_config')

    def test_dashboard(self):
        for dash in ('dsb:0', 'dsb:1'):
            self.click_element_by_id(dash)
            self.check_menu_available()
            _edit = self.driver.driver.find_element_by_id('dashEdit')  # input is hidden
            _edit_parent = _edit.find_element_by_xpath('./..')
            _edit_parent.click()
            time.sleep(1)
            # Checking that widgets appeared
            for _id in [f'_1_{j}' for j in range(1, 13)]:
                self.assertIsNotNone(self.driver._get_element_by(By.ID, _id))
        self.check_dahsboard()

    def test_scheduler(self):
        self.click_element_by_id('net:0')
        self.click_element_by_id('Schedulers_config')
        self.click_element_by_xpath("//a[contains(@href, 'scheduler=0')]")
        menu_main, menu_config = self.check_menu_available()
        for el in self.menu_elements.get('scheduler'):
            _id, _obj = self.check_and_click_element(el, menu_main, menu_config)
            # Right clicking menu config items
            if _obj == menu_config:
                self.right_click_element_by_id(_id)
                self.check_expected_path('scheduler', el, _id, 'Scheduler_config')
        self.check_dahsboard()

    def test_server(self):
        self.click_element_by_id('nms:0')
        self.click_element_by_id('Servers_config')
        self.click_element_by_xpath("//a[contains(@href, 'server=0')]")
        self.check_menu_available()
        self.check_dahsboard()

    @staticmethod
    def get_expected_href(el):
        _id = el.get('title')
        _url = el.get("url")
        _ext = el.get("ext")
        if _ext is None:
            href = f'{_url}0'  # getting expected href
        else:
            href = f'{_url}0{_ext}'
        return href

    def click_element_by_id(self, _id, breadcrumbs=None, dashboard=False, last_object=False):
        el = self.driver._get_element_by(By.ID, _id, timeout=self._wait_time_out)
        if el is None:
            self.fail(f'WEB element id={_id} cannot be located and clicked at {self.driver.get_current_url()}')
        el.click()
        time.sleep(1)
        self.assertFalse(self._is_404())
        self.assertFalse(self._is_400())
        if breadcrumbs is not None:
            self.check_breadcrumbs(breadcrumbs, dashboard=dashboard, last_object=last_object)

    def click_element_by_xpath(self, xpath, breadcrumbs=None, dashboard=False, last_object=False):
        el = self.driver._get_element_by(By.XPATH, xpath, timeout=self._wait_time_out)
        if el is None:
            self.fail(f'WEB element xpath={xpath} cannot be located and clicked at {self.driver.get_current_url()}')
        el.click()
        time.sleep(1)
        self.assertFalse(self._is_404())
        self.assertFalse(self._is_400())
        if breadcrumbs is not None:
            self.check_breadcrumbs(breadcrumbs, dashboard=dashboard, last_object=last_object)

    def right_click_element_by_id(self, _id):
        el = self.driver._get_element_by(By.ID, _id, timeout=self._wait_time_out)
        if el is None:
            self.fail(f'WEB element id={_id} cannot be located and right-clicked at {self.driver.get_current_url()}')
        ActionChains(self.driver.driver).context_click(el).perform()
        time.sleep(1)
        self.assertFalse(self._is_404())
        self.assertFalse(self._is_400())

    def current_breadcrumbs(self):
        breadcrumb_elements = self._get_elements_by(By.CLASS_NAME, self.breadcrumbs_item_class)
        path = []
        for el in breadcrumb_elements:
            _span = el.find_element_by_tag_name('span')
            path.append(f'{urlparse(el.get_attribute("href")).path}_|_{_span.text}')
        return path

    def expected_breadcrumbs(self, elements: list, dashboard=False, last_object=False):
        """Example:
        """
        if dashboard:
            expected = [f'/object/dashboard/{elements[0]}=0_|_{self.names.get(elements[0])}']
        else:
            expected = [f'/form/edit/{elements[0]}=0_|_{self.names.get(elements[0])}']
        for i in range(1, len(elements)):
            if elements[i] in ('qos', ):
                name = elements[i].capitalize() + 'es'
            else:
                name = elements[i].capitalize() + 's'
            if dashboard:
                if i > 0:
                    expected.append(
                        f'/list/get/{elements[i - 1]}=0/list_items={elements[i]}_|_{name}')
                if last_object or i < len(elements) - 1:
                    expected.append(f'/object/dashboard/{elements[i]}=0_|_{self.names.get(elements[i])}')
            else:
                if i > 0:
                    expected.append(
                        f'/list/edit/{elements[i - 1]}=0/list_items={elements[i]}_|_{name}')
                if last_object or i < len(elements) - 1:
                    expected.append(f'/form/edit/{elements[i]}=0_|_{self.names.get(elements[i])}')
        return expected

    @staticmethod
    def _get_href(el):
        for i in range(0, 30):
            try:
                href = el.get_attribute('href')
                break
            except ElementNotInteractableException:
                time.sleep(0.1)
            except StaleElementReferenceException:
                time.sleep(0.1)
        else:
            return False
        return href

    def _get_elements_by(self, by, search, timeout=None):
        if timeout is None:
            timeout = self._wait_time_out
        try:
            return WebDriverWait(self.driver.driver, timeout) \
                .until(expected_conditions.presence_of_all_elements_located((by, search)))
        except NoSuchElementException:
            return None
        except TimeoutException:
            return None

    def _is_404(self):
        return self.driver.get_current_url().find('notfound') != -1

    def _is_400(self):
        return self.driver.get_current_url().find('badrequest') != -1

    def _wait_load_page(self):
        WebDriverWait(self.driver.driver, self._wait_time_out) \
            .until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, 'body')))
