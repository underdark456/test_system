import ipaddress
import time

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By

from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.nms_entities.paths_manager import PathsManager
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.web.web_get_list'
backup_name = 'case_database_performance.txt'


class WebGetListAllTablesCase(CustomTestCase):
    """WEB interface get list of all objects in every table"""

    __author__ = 'dkudryashov'
    __version__ = '0.1'
    __execution_time__ = 9380  # approximate case execution time in seconds
    __express__ = False  # This test case is not intended to be part of express tests

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(options_path), driver_id='case_web_get_list_every_table'
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)

        cls.options = OptionsProvider.get_options(options_path)

    def _get_list(self, path, entity_name, names, by='name'):
        self.driver.load_data(path)
        time.sleep(2)
        for n in names:
            if by == 'route':
                _xpath = "//div[contains(text()," + f'"{str(n)}"' + ")]"
            else:
                _xpath = "//a[text()=" + f'"{str(n)}"' + " and starts-with(@href, '/form')]"
            # else:
            #     _xpath = "//a[text()=" + f'"{str(n)}"' + "]"
            for _ in range(3):
                try:
                    next_elem = self.driver._get_element_by(By.XPATH, _xpath)
                    if next_elem is None:
                        time.sleep(0.2)
                        continue
                    self.driver.driver.execute_script("return arguments[0].scrollIntoView();", next_elem)
                    break
                except StaleElementReferenceException:
                    time.sleep(0.2)
            else:
                self.fail(msg=f'{entity_name} with {by} {n} is not found in the list')

    def test_get_list_access(self):
        """WEB interface getting list of all Accesses"""
        # Accesses are split across 2 networks
        path = PathsManager.access_list(self.driver.get_type(), 0, parent_type='network')
        names = [f'grp{i}' for i in range(511)]
        names.insert(0, 'Admins')
        self._get_list(path, 'access', names)

        path = PathsManager.access_list(self.driver.get_type(), 1, parent_type='network')
        names = [f'grp{i}' for i in range(510)]
        names.insert(0, 'Admins')
        self._get_list(path, 'access', names)

    def test_get_list_alert(self):
        """WEB interface getting list of all Alert"""
        path = PathsManager.alert_list(self.driver.get_type(), 0)
        names = sorted([f'alr{i}' for i in range(self.options.get('number_of_alert'))])
        self._get_list(path, 'alert', names)

    def test_get_list_bal_controller(self):
        """WEB interface getting list of all Bal Controller"""
        path = PathsManager.bal_controller_list(self.driver.get_type(), 0)
        names = sorted([f'bal_ctr{i}' for i in range(self.options.get('number_of_bal_controller'))])
        self._get_list(path, 'bal_controller', names)

    def test_get_list_camera(self):
        """WEB interface getting list of all Camera"""
        path = PathsManager.camera_list(self.driver.get_type(), 0)
        names = sorted([f'cam{i}' for i in range(self.options.get('number_of_camera'))])
        self._get_list(path, 'camera', names)

    def test_get_list_controller(self):
        """WEB interface getting list of all Controller"""
        path = PathsManager.controller_list(self.driver.get_type(), 0)
        names = sorted([f'ctrl{i}' for i in range(self.options.get('number_of_controller'))])
        self._get_list(path, 'controller', names)

    def test_get_list_dashboard(self):
        """WEB interface getting list of all Dashboard"""
        path = PathsManager.dashboard_list(self.driver.get_type(), 0)
        names = sorted([f'dash{i}' for i in range(self.options.get('number_of_dashboard'))])
        self._get_list(path, 'dashboard', names)

    def test_get_list_device(self):
        """WEB interface getting list of all Device"""
        path = PathsManager.device_list(self.driver.get_type(), 0)
        names = sorted([f'dev{i}' for i in range(self.options.get('number_of_device'))])
        self._get_list(path, 'device', names)

    def test_get_list_group(self):
        """WEB interface getting list of all Groups"""
        path = PathsManager.group_list(self.driver.get_type(), 0)
        names = sorted([f'grp{i}' for i in range(self.options.get('number_of_group') - 1)])
        names.insert(0, 'Admins')
        self._get_list(path, 'group', names)

    def test_get_list_network(self):
        """WEB interface getting list of all Networks"""
        path = PathsManager.network_list(self.driver.get_type(), 0)
        names = sorted([f'net{i}' for i in range(self.options.get('number_of_network'))])
        self._get_list(path, 'network', names)

    def test_get_list_policy(self):
        """WEB interface getting list of all Policies"""
        path = PathsManager.policy_list(self.driver.get_type(), 0)
        names = sorted([f'pol{i}' for i in range(self.options.get('number_of_policy'))])
        self._get_list(path, 'policy', names)

    def test_get_list_polrule(self):
        """WEB interface getting list of all Policy Rules"""
        path = PathsManager.policy_rule_list(self.driver.get_type(), 0)
        names = [str(i) for i in range(2, self.options.get('number_of_polrule') + 2)]
        self._get_list(path, 'pol_rule', names, by='sequence')

    def test_get_list_port_map(self):
        """WEB interface getting list of all Port Maps"""
        path = PathsManager.controller_port_map_list(self.driver.get_type(), 0)
        names = [str(i) for i in range(1, self.options.get('number_of_port_map') + 1)]
        self._get_list(path, 'port_map', names, by='external_port')

    def test_get_list_profile_set(self):
        """WEB interface getting list of all Profile Sets"""
        path = PathsManager.profile_list(self.driver.get_type(), 0)
        names = sorted([f'pro{i}' for i in range(self.options.get('number_of_profile_set'))])
        self._get_list(path, 'profile_set', names)

    def test_get_list_rip_router(self):
        """WEB interface getting list of all RIP routers"""
        path = PathsManager.controller_rip_list(self.driver.get_type(), 0)
        names = [f'service{i}' for i in range(self.options.get('number_of_rip_router'))]
        self._get_list(path, 'rip_router', names)

    def test_get_list_route(self):
        """WEB interface getting list of all Routes"""
        path = PathsManager.controller_route_list(self.driver.get_type(), 0)
        ip = ipaddress.IPv4Address('127.1.0.0')
        names = [str(ip + i) for i in range(1, self.options.get('number_of_route') + 1)]
        names.sort(key=lambda s: list(map(int, s.split('.')))[::-1])
        self._get_list(path, 'route', names, by='route')

    def test_get_list_server(self):
        """WEB interface getting list of all Servers"""
        path = PathsManager.server_list(self.driver.get_type(), 0)
        names = sorted([f'serv{i}' for i in range(self.options.get('number_of_server'))])
        self._get_list(path, 'server', names)

    def test_get_list_service(self):
        """WEB interface getting list of all Services"""
        path = PathsManager.service_list(self.driver.get_type(), 0)
        names = sorted([f'service{i}' for i in range(self.options.get('number_of_service'))])
        self._get_list(path, 'service', names)

    def test_get_list_shaper(self):
        """WEB interface getting list of all Shapers"""
        path = PathsManager.shaper_list(self.driver.get_type(), 0)
        names = sorted([f'shp{i}' for i in range(self.options.get('number_of_shaper'))])
        self._get_list(path, 'shaper', names)

    def test_get_list_sr_controller(self):
        """WEB interface getting list of all Sr Controllers"""
        path = PathsManager.sr_controller_list(self.driver.get_type(), 0)
        names = sorted([f'sr_ctr{i}' for i in range(self.options.get('number_of_sr_controller'))])
        self._get_list(path, 'sr_controller', names)

    def test_get_list_sr_license(self):
        """WEB interface getting list of all Sr Licenses"""
        path = PathsManager.sr_license_list(self.driver.get_type(), 0)
        names = sorted([f'sr_lic{i}' for i in range(self.options.get('number_of_sr_license'))])
        self._get_list(path, 'sr_license', names)

    def test_get_list_sr_teleport(self):
        """WEB interface getting list of all Sr Teleports"""
        path = PathsManager.sr_teleport_list(self.driver.get_type(), 0)
        names = sorted([f'sr_tp{i}' for i in range(self.options.get('number_of_sr_teleport'))])
        self._get_list(path, 'sr_teleport', names)

    def test_get_list_station(self):
        """WEB interface getting list of all Stations"""
        path = PathsManager.station_list(self.driver.get_type(), 0)
        names = sorted([f'stn{i}' for i in range(self.options.get('number_of_station'))])
        self._get_list(path, 'station', names)

    def test_get_list_sw_upload(self):
        """WEB interface getting list of all Sw Uploads"""
        path = PathsManager.sw_upload_list(self.driver.get_type(), 0)
        names = sorted([f'sw{i}' for i in range(self.options.get('number_of_sw_upload'))])
        self._get_list(path, 'sw_upload', names)

    def test_get_list_teleport(self):
        """WEB interface getting list of all Teleports"""
        path = PathsManager.teleport_list(self.driver.get_type(), 0)
        names = sorted([f'tel{i}' for i in range(self.options.get('number_of_teleport'))])
        self._get_list(path, 'teleport', names)

    def test_get_list_user(self):
        """WEB interface getting list of all Users"""
        path = PathsManager.user_list(self.driver.get_type(), 0)
        names = sorted([f'usr{i}' for i in range(self.options.get('number_of_user') - 1)])
        names.insert(0, 'admin')
        self._get_list(path, 'user', names)

    def test_get_list_vno(self):
        """WEB interface getting list of all VNOs"""
        path = PathsManager.vno_list(self.driver.get_type(), 0)
        names = sorted([f'vno{i}' for i in range(self.options.get('number_of_vno'))])
        self._get_list(path, 'vno', names)

    def test_get_list_scheduler(self):
        """WEB interface getting list of all Schedulers"""
        path = PathsManager.scheduler_list(self.driver.get_type(), 0)
        names = sorted([f'sched{i}' for i in range(self.options.get('number_of_scheduler'))])
        self._get_list(path, 'scheduler', names)

    def test_get_list_sch_range(self):
        """WEB interface getting list of all Sch Ranges"""
        path = PathsManager.sch_range_list(self.driver.get_type(), 0)
        names = sorted([f'sch_r{i}' for i in range(self.options.get('number_of_sch_range'))])
        self._get_list(path, 'sch_range', names)

    def test_get_list_sch_service(self):
        """WEB interface getting list of all Sch Services"""
        path = PathsManager.sch_service_list(self.driver.get_type(), 0)
        names = sorted([f'sch_s{i}' for i in range(self.options.get('number_of_sch_service'))])
        self._get_list(path, 'sch_service', names)
