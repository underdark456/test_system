import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes, RouteTypes
from src.file_manager.file_manager import FileManager
from src.nms_entities.basic_entities.access import Access
from src.nms_entities.basic_entities.alert import Alert
from src.nms_entities.basic_entities.bal_controller import BalController
from src.nms_entities.basic_entities.camera import Camera
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.controller_port_map import ControllerPortMap
from src.nms_entities.basic_entities.controller_rip import ControllerRip
from src.nms_entities.basic_entities.controller_route import ControllerRoute
from src.nms_entities.basic_entities.dashboard import Dashboard
from src.nms_entities.basic_entities.device import Device
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.nms import Nms
from src.nms_entities.basic_entities.policy import Policy
from src.nms_entities.basic_entities.policy_rule import PolicyRule
from src.nms_entities.basic_entities.profile import Profile
from src.nms_entities.basic_entities.qos import Qos
from src.nms_entities.basic_entities.scheduler import Scheduler
from src.nms_entities.basic_entities.scheduler_range import SchRange
from src.nms_entities.basic_entities.scheduler_service import SchService
from src.nms_entities.basic_entities.scheduler_task import SchTask
from src.nms_entities.basic_entities.server import Server
from src.nms_entities.basic_entities.service import Service
from src.nms_entities.basic_entities.shaper import Shaper
from src.nms_entities.basic_entities.sr_controller import SrController
from src.nms_entities.basic_entities.sr_license import SrLicense
from src.nms_entities.basic_entities.sr_teleport import SrTeleport
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.station_port_map import StationPortMap
from src.nms_entities.basic_entities.station_rip import StationRip
from src.nms_entities.basic_entities.station_route import StationRoute
from src.nms_entities.basic_entities.sw_upload import SwUpload
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.user import User
from src.nms_entities.basic_entities.user_group import UserGroup
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider, CHROME_CONNECT

options_path = 'test_scenarios.web.search'
backup_name = 'default_config.txt'


class WebSearchCase(CustomTestCase):
    """WEB search created objects by names, sequence, ip adresses"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.24'
    __execution_time__ = 115  # approximate case execution time in seconds
    __express__ = True
    _wait_time_out = 3

    @classmethod
    def set_up_class(cls):
        cls.fm = FileManager()
        cls.fm.upload_uhp_software('dummy_soft.240')
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(options_path, CHROME_CONNECT),
            driver_id='case_web_search',
            store_driver=False
        )

        cls.search_input_class = 'searchmodal__input'
        cls.search_apply_class = 'searchmodal__apply'
        cls.search_result_container_class = 'ag-center-cols-viewport'

        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)
        cls.options = OptionsProvider.get_options(options_path)
        cls.nms = Nms(cls.driver, 0, 0)
        cls.names = cls.options.get('search_tool_unique_names')
        cls.nms.send_param('name', cls.names.get('nms'))
        cls.network = Network.create(cls.driver, 0, {'name': cls.names.get('network')})
        cls.server = Server.create(cls.driver, 0, {'name': cls.names.get('server')})
        cls.group = UserGroup.create(cls.driver, 0, {'name': cls.names.get('group')})
        cls.user = User.create(cls.driver, cls.group.get_id(), {'name': cls.names.get('user')})
        cls.alert = Alert.create(cls.driver, 0, {'name': cls.names.get('alert'), 'popup': True})
        cls.access = Access.create(cls.driver, 0, {'group': f'group:{cls.group.get_id()}', 'edit': True, 'use': True})
        cls.dashboard = Dashboard.create(cls.driver, 0, {'name': cls.names.get('dashboard')})
        cls.teleport = Teleport.create(cls.driver, 0, {'name': cls.names.get('teleport'), 'sat_name': 'sat'})
        cls.controller = Controller.create(
            cls.driver,
            0,
            {'name': cls.names.get('controller'), 'mode': ControllerModes.MF_HUB, 'teleport': f'teleport:0'}
        )
        cls.vno = Vno.create(cls.driver, 0, {'name': cls.names.get('vno')})
        cls.service = Service.create(cls.driver, 0, {'name': cls.names.get('service')})
        cls.shaper = Shaper.create(cls.driver, 0, {'name': cls.names.get('shaper')})
        cls.policy = Policy.create(cls.driver, 0, {'name': cls.names.get('policy')})
        cls.pol_rule = PolicyRule.create(cls.driver, 0, {'sequence': 11223})
        cls.sr_controller = SrController.create(cls.driver, 0, {'name': cls.names.get('sr_controller')})
        cls.sr_teleport = SrTeleport.create(
            cls.driver,
            0,
            {'name': cls.names.get('sr_teleport'), 'teleport': 'teleport:0'}
        )
        cls.device = Device.create(cls.driver, 0, {'name': cls.names.get('device')})
        cls.license = SrLicense.create(cls.driver, 0, {'name': cls.names.get('sr_license')})
        cls.bal_controller = BalController.create(cls.driver, 0, {'name': cls.names.get('bal_controller')})
        cls.profile = Profile.create(cls.driver, 0, {'name': cls.names.get('profile_set')})
        cls.sw_upload = SwUpload.create(cls.driver, 0, {'name': cls.names.get('sw_upload'), 'sw_file': 'dummy_soft.240'})
        cls.camera = Camera.create(cls.driver, 0, {'name': cls.names.get('camera')})
        cls.scheduler = Scheduler.create(cls.driver, 0, {'name': cls.names.get('scheduler')})
        cls.sch_range = SchRange.create(cls.driver, 0, {'name': cls.names.get('sch_range')})
        cls.sch_service = SchService.create(cls.driver, 0, {'name': cls.names.get('sch_service')})
        cls.qos = Qos.create(cls.driver, 0, {'name': cls.names.get('qos')})

        cls.station = Station.create(cls.driver, 0, {'name': cls.names.get('station'), 'serial': 54321})
        cls.sch_task = SchTask.create(cls.driver, 0, {'name': cls.names.get('sch_task')})

        cls.controller_rip = ControllerRip.create(cls.driver, 0,
                                                  {'service': 'service:0', 'rip_next_hop': '192.168.1.1'})
        cls.station_rip = StationRip.create(cls.driver, 0,
                                            {'service': 'service:0', 'rip_next_hop': '192.168.2.1'})
        cls.controller_nat = ControllerPortMap.create(
            cls.driver,
            0,
            {'external_port': 17542, 'internal_ip': '172.16.1.2', 'internal_port': 34212})
        cls.station_nat = StationPortMap.create(
            cls.driver,
            0,
            {'external_port': 5623, 'internal_ip': '172.16.2.3', 'internal_port': 7212})

        cls.controller_ip = ControllerRoute.create(
            cls.driver,
            0,
            {'type': RouteTypes.IP_ADDRESS, 'service': 'service:0', 'ip': '172.16.1.1'}
        )
        cls.station_ip = StationRoute.create(
            cls.driver,
            0,
            {'type': RouteTypes.IP_ADDRESS, 'service': 'service:0', 'ip': '172.16.2.1'}
        )
        cls.controller_static = ControllerRoute.create(
            cls.driver,
            0,
            {'type': RouteTypes.STATIC_ROUTE, 'service': 'service:0', 'ip': '172.16.3.0', 'gateway': '172.16.30.1'}
        )
        cls.station_static = StationRoute.create(
            cls.driver,
            0,
            {'type': RouteTypes.STATIC_ROUTE, 'service': 'service:0', 'ip': '172.16.4.0', 'gateway': '172.16.40.1'}
        )
        cls.controller_network_tx = ControllerRoute.create(
            cls.driver,
            0,
            {'type': RouteTypes.NETWORK_TX, 'service': 'service:0', 'ip': '172.16.5.0'}
        )
        cls.station_static = StationRoute.create(
            cls.driver,
            0,
            {'type': RouteTypes.NETWORK_TX, 'service': 'service:0', 'ip': '172.16.6.0'}
        )
        cls.station_route_to_hub = StationRoute.create(
            cls.driver,
            0,
            {'type': RouteTypes.ROUTE_TO_HUB, 'service': 'service:0', 'ip': '172.16.7.0'}
        )

    def set_up(self) -> None:
        self.nms.load()

    def test_search_by_name(self):
        """Search created objects by their unique names. Click at the resulting links, check for 404 and 400"""
        for _obj, name in self.names.items():
            if self._is_404() or self._is_400():
                self.return_to_nms()
            search_btn = self.get_search_button()
            search_btn.click()
            with self.subTest(f'Searching {_obj} by its name {name}'):
                self.send_keys_to_search_input(name)
                self.check_search_output(_obj, name)

    def test_search_polrule_by_sequence(self):
        """Search pol_rule by its sequence number. Click at the resulting link, check for 404 or 400"""
        search_btn = self.get_search_button()
        search_btn.click()
        self.send_keys_to_search_input('11223')
        self.check_search_output('polrule', '11223')

    def test_search_rip_router_by_rip_next_hop(self):
        """Search pol_rule by its sequence number. Click at the resulting link, check for 404 or 400"""
        for _ip in ['192.168.1.1', '192.168.2.1']:
            if self._is_404() or self._is_400():
                self.return_to_nms()
            search_btn = self.get_search_button()
            search_btn.click()
            with self.subTest(f'Searching Rip_router by its rip_next_hop ip {_ip}'):
                self.send_keys_to_search_input(_ip)
                self.check_search_output('rip_router', 'service:0 elegant_service')

    def test_search_port_map_by_internal_ip(self):
        """Search NAT ports by their internal_ip. Click at the resulting link, check for 404 or 400"""
        for _ip, ext_port in {'172.16.1.2': '17542', '172.16.2.3': '5623'}.items():
            if self._is_404() or self._is_400():
                self.return_to_nms()
            search_btn = self.get_search_button()
            search_btn.click()
            with self.subTest(f'Searching NAT port by its internal_ip {_ip}'):
                self.send_keys_to_search_input(_ip)
                self.check_search_output('port_map', ext_port)

    def test_search_by_ip_address(self):
        """Search routes by their ip or gateway. Click at the resulting link, check for 404 or 400"""
        for _ip in ['172.16.1.1', '172.16.2.1']:
            if self._is_404() or self._is_400():
                self.return_to_nms()
            search_btn = self.get_search_button()
            search_btn.click()
            with self.subTest(f'Searching Route IP_address by its ip {_ip}'):
                self.send_keys_to_search_input(_ip)
                self.check_search_output('route', 'IP_address')
        for _ip in ['172.16.3.0', '172.16.4.0', '172.16.30.1', '172.16.40.1']:
            if self._is_404() or self._is_400():
                self.return_to_nms()
            search_btn = self.get_search_button()
            search_btn.click()
            with self.subTest(f'Searching Route IP_address by its ip {_ip}'):
                self.send_keys_to_search_input(_ip)
                self.check_search_output('route', 'Static_route')
        if self._is_404() or self._is_400():
            self.return_to_nms()
        search_btn = self.get_search_button()
        search_btn.click()
        with self.subTest(f'Searching Route Route_to_hub by its ip {_ip}'):
            self.send_keys_to_search_input('172.16.7.0')
            self.check_search_output('route', 'Route_to_hub')

    def check_search_output(self, expected_type, expected_name):
        search_result_el = self.driver._get_element_by(By.CLASS_NAME, self.search_result_container_class)
        self.assertIsNotNone(
            search_result_el,
            msg=f'Cannot locate search result container element by its class name {self.search_result_container_class}'
        )
        try:
            search_result_el.find_element_by_xpath(".//*[contains(text(), '" + expected_type + "')]")
        except NoSuchElementException:
            self.fail(f'Cannot locate expected object type {expected_type} in search results')

        try:
            a_tag = search_result_el.find_element_by_xpath(".//a[contains(text(), '" + expected_name + "')]")
        except NoSuchElementException:
            self.fail(f'Cannot locate expected object type {expected_name} in search results')
        href = a_tag.get_attribute('href')
        self.assertTrue(href.find(expected_type) != -1, msg=f'href {href} does not contain {expected_type}')
        a_tag.click()
        time.sleep(0.2)
        self.assertFalse(self._is_404(), msg=f'404 at clicking search result href={href}')
        self.assertFalse(self._is_400(), msg=f'400 at clicking search result href={href}')

    def send_keys_to_search_input(self, search_string):
        input_el = self.driver._get_element_by(By.CLASS_NAME, self.search_input_class)
        self.assertIsNotNone(
            input_el,
            msg=f'Cannot locate search input element by its class name {self.search_input_class}'
        )
        apply_el = self.driver._get_element_by(By.XPATH, "//button[@class = '" + self.search_apply_class + "']")
        self.assertIsNotNone(
            apply_el,
            msg=f'Cannot locate search apply button element by xpath'
        )
        ActionChains(self.driver.driver) \
            .click(input_el) \
            .key_down(Keys.CONTROL) \
            .send_keys("a") \
            .key_up(Keys.CONTROL) \
            .send_keys(Keys.DELETE) \
            .send_keys(search_string) \
            .perform()
        apply_el.click()

    def get_search_button(self):
        tree_el = self.driver._get_element_by(By.CLASS_NAME, 'tree')
        self.assertIsNotNone(tree_el, msg=f'Cannot locate tree element by its class name `tree`')
        buttons = tree_el.find_elements_by_tag_name('button')
        # Locating search button (probably ask to add ID to that button)
        for btn in buttons:
            try:
                btn.find_element_by_xpath(".//*[contains(text(), 'Search')]")
                break
            except NoSuchElementException:
                continue
        else:
            self.fail(f'Cannot locate search button')
        return btn

    def return_to_nms(self):
        return_link = self.driver._get_element_by(By.XPATH, "//a[contains(text(), 'Return to NMS')]")
        self.assertIsNotNone(return_link, msg='Cannot locate return to NMS link at 404 or 400 page')
        return_link.click()
        self._wait_load_page()

    def _is_404(self):
        return self.driver.get_current_url().find('notfound') != -1

    def _is_400(self):
        return self.driver.get_current_url().find('badrequest') != -1

    def _wait_load_page(self):
        WebDriverWait(self.driver.driver, self._wait_time_out) \
            .until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, 'body')))
