import json
import os

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from global_options.options import PROJECT_DIR
from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.exceptions import NoSuchParamException
from src.nms_entities.basic_entities.nms import Nms
from src.nms_entities.paths_manager import PathsManager
from src.options_providers.options_provider import OptionsProvider, CHROME_CONNECT
from utilities.get_meta.get_meta import get_meta

options_path = 'test_scenarios.web.fields'
backup_name = 'each_entity.txt'


class WebMissingFormFieldsCase(CustomTestCase):
    """Each NMS entity missing form fields according to meta data case"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.26'
    __execution_time__ = 475  # approximate test case execution time in seconds

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection('global_options', CHROME_CONNECT)
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)

        cls.nms = Nms(cls.driver, 0, 0)
        cls.nms_version = cls.nms.get_version()
        if cls.nms_version is None:
            raise NoSuchParamException('Cannot determine NMS version')
        cls.nms_version = cls.nms_version.replace('.', '_')

        # If meta for the current version is not generated yet
        if not os.path.isfile(f'{PROJECT_DIR}{os.sep}utilities{os.sep}get_meta{os.sep}meta_{cls.nms_version}.txt'):
            get_meta()

        with open(f'{PROJECT_DIR}{os.sep}utilities{os.sep}get_meta{os.sep}meta_{cls.nms_version}.txt', 'r') as file:
            cls.meta = json.load(file)

        with open(f'{PROJECT_DIR}{os.sep}utilities{os.sep}get_meta{os.sep}modcodes_4_0_0_11.txt', 'r') as file:
            cls.modcodes = json.load(file)

    def get_recursive_dep_vars(self, entity_name, section_name, initial_var, var):
        """Recursively call same method until there is a dep_var"""
        name = initial_var.get('name')
        select = initial_var.get('select')
        dep_var = var.get('dep_var')
        dep_value = var.get('dep_value')

        # There is a `dep_var` in the current var
        if dep_var is not None:

            # Getting dep_var dictionary
            dep_var_dict = self.get_dep_var_dict(entity_name, dep_var)
            if dep_var_dict is None:
                self.fail('Cannot find referenced dep_var')

            if dep_value is None:
                self.fail('No `dep_value`!')

            # Getting bit-mask out of `dep_value` - first value first
            dep_value_bin = bin(dep_value)[2:][::-1]
            dep_var_elem = self.driver._get_element_by(By.ID, dep_var)
            self.assertIsNotNone(dep_var_elem)

            if dep_var_elem.get_attribute("type") == 'checkbox':
                if not dep_var_elem.get_attribute('checked'):
                    # Clicking the parent element of the checkbox
                    parent_div = dep_var_elem.find_element_by_xpath('..')
                    parent_div.click()
                self.get_recursive_dep_vars(entity_name, section_name, initial_var, dep_var_dict)

            # Checking all dep values in select
            elif dep_var_elem.tag_name == 'select':
                # External gateway dropdown value is controller:0
                if dep_var == 'ext_gateway':
                    selector = Select(dep_var_elem)
                    selector.select_by_value('controller:0')
                else:
                    for i in range(len(dep_value_bin)):
                        if i >= len(dep_var_dict.get('select')):
                            break
                        if dep_value_bin[i] == '1':
                            selector = Select(dep_var_elem)
                            selector.select_by_value(str(i))
                            self.get_recursive_dep_vars(entity_name, section_name, initial_var, dep_var_dict)

            # Checking all dep values in input
            elif dep_var_elem.tag_name == 'input':
                for i in range(len(dep_value_bin)):
                    if i > dep_var_dict.get('to'):
                        break
                    if dep_value_bin[i] == '1':
                        dep_var_elem.click()
                        dep_var_elem.send_keys(Keys.CONTROL + "a")
                        dep_var_elem.send_keys(Keys.DELETE)
                        dep_var_elem.send_keys(str(i))
                        self.get_recursive_dep_vars(entity_name, section_name, initial_var, dep_var_dict)
            else:
                self.fail('dep_var element is neither a checkbox nor a select nor an input')

        # No `dep_var` - proceeding to checkout
        else:
            # Checking that section title is visible
            nms_section = self.driver._get_element_by(By.ID, f'{section_name}_title')
            #
            if name.startswith('epsk') or name.startswith('apsk') or name.startswith('t_epsk'):
                return
            self.assertIsNotNone(nms_section)
            self.assertEqual(section_name, nms_section.text)

            param = self.driver._get_element_by(By.ID, name)
            self.assertIsNotNone(param)

            # Dropdown
            if select is not None:
                # Checking that all expected options are in the current dropdown
                if name in ('beam1_file', 'beam2_file', 'beam3_file', 'beam4_file'):
                    return
                for meta_option in select:
                    # meta_option_value = meta_option.get('val')
                    meta_option_txt = meta_option.get('txt')
                    for option in param.find_elements_by_tag_name("option"):
                        # option_value = option.get_attribute('value')
                        option_txt = option.text
                        if option_txt.startswith(meta_option_txt[:20]):
                            break
                    else:
                        self.fail(f'{meta_option_txt} not found in the dropdown')
                # Make sure that the number of options are the same
                self.assertEqual(len(select), len(param.find_elements_by_tag_name("option")))

            # TDM and TDMA modcodes are not in meta data
            if name in ('tx_modcod', 'dama_modcod') or name.startswith('acm_mc'):
                options = {}
                for option in param.find_elements_by_tag_name("option"):
                    option_value = str(option.get_attribute('value'))
                    option_name = option.text
                    options[option_value] = option_name
                for modcod in self.modcodes.get('tx_modcod'):
                    modcod_value = modcod.get('value')
                    modcod_name = modcod.get('name').rstrip()

                    # print(modcod_value, modcod_name, option_value, option_name)
                    if str(modcod_value) not in options.keys() or modcod_name != options.get(str(modcod_value)):
                        self.fail(f'{modcod_name} not found in the dropdown')
                # Make sure that the number of options are the same
                self.assertEqual(len(self.modcodes.get('tx_modcod')), len(param.find_elements_by_tag_name("option")))

            if entity_name == 'controller' and name == 'tdma_mc':
                # TODO: make it faster
                for modcod in self.modcodes.get('tdma_mc'):
                    modcod_value = modcod.get('value')
                    modcod_name = modcod.get('name')
                    for option in param.find_elements_by_tag_name("option"):
                        option_value = option.get_attribute('value')
                        option_name = option.text
                        if str(modcod_value) == str(option_value) and modcod_name == option_name:
                            break
                    else:
                        self.fail(f'{modcod_name} not found in the dropdown')
                # Make sure that the number of options are the same
                self.assertEqual(len(self.modcodes.get('tdma_mc')), len(param.find_elements_by_tag_name("option")))

    def get_dep_var_dict(self, entity_name, dep_var_name):
        meta = self.meta.get(entity_name)
        for section in meta:
            for var in section.get('vars'):
                if var.get('name') == dep_var_name:
                    return var
        return None

    def check_entity(self, parent_name, entity_name):
        meta = self.meta.get(entity_name)
        self.driver.load_data(PathsManager._OBJECT_CREATE.format(parent_name, 0, entity_name))
        for section in meta:
            section_name = section.get('section')
            if section_name is None:
                section_name = section.get('table')
                if section_name is None:
                    self.fail('!!!Cannot get neither section name nor table name!!!')
            for var in section.get('vars'):
                with self.subTest(f'{entity_name}, section={section_name} param={var.get("name")}'):
                    self.get_recursive_dep_vars(entity_name, section_name, var, var)

    def test_access(self):
        """Missing fields in access form"""
        self.check_entity('nms', 'access')

    def test_alert(self):
        """Missing fields in alert form"""
        self.check_entity('nms', 'alert')

    def test_bal_controller(self):
        """Missing fields in bal_controller form"""
        self.check_entity('network', 'bal_controller')

    def test_camera(self):
        """Missing fields in camera form"""
        self.check_entity('network', 'camera')

    def test_controller(self):
        """Missing fields in controller form"""
        self.check_entity('network', 'controller')

    def test_dashboard(self):
        """Missing fields in dashboard form"""
        self.check_entity('network', 'dashboard')

    def test_device(self):
        """Missing fields in sr_teleport form"""
        self.check_entity('sr_teleport', 'device')

    def test_group(self):
        """Missing fields in group form"""
        self.check_entity('nms', 'group')

    def test_network(self):
        """Missing fields in network form"""
        self.check_entity('nms', 'network')

    def test_policy(self):
        """Missing fields in policy form"""
        self.check_entity('network', 'policy')

    def test_polrule(self):
        """Missing fields in pol_rule form"""
        self.check_entity('policy', 'polrule')

    def test_port_map(self):
        """Missing fields in port_map form"""
        self.check_entity('controller', 'port_map')

    def test_profile_set(self):
        """Missing fields in profile_set form"""
        self.check_entity('network', 'profile_set')

    def test_rip_router(self):
        """Missing fields in rip_router form"""
        self.check_entity('controller', 'rip_router')

    def test_route(self):
        """Missing fields in route form"""
        self.check_entity('controller', 'route')

    def test_server(self):
        """Missing fields in server form"""
        self.check_entity('nms', 'server')

    def test_service(self):
        """Missing fields in service form"""
        self.check_entity('network', 'service')

    def test_shaper(self):
        """Missing fields in shaper form"""
        self.check_entity('network', 'shaper')

    def test_sr_controller(self):
        """Missing fields in sr_controller form"""
        self.check_entity('network', 'sr_controller')

    def test_sr_license(self):
        self.check_entity('network', 'sr_license')

    def test_sr_teleport(self):
        """Missing fields in sr_teleport form"""
        self.check_entity('sr_controller', 'sr_teleport')

    def test_station(self):
        """Missing fields in station form"""
        self.check_entity('vno', 'station')

    def test_sw_upload(self):
        """Missing fields in sw_upload form"""
        self.check_entity('network', 'sw_upload')

    def test_teleport(self):
        """Missing fields in teleport form"""
        self.check_entity('network', 'teleport')

    def test_user(self):
        """Missing fields in user form"""
        self.check_entity('group', 'user')

    def test_vno(self):
        """Missing fields in vno form"""
        self.check_entity('network', 'vno')

    def test_scheduler(self):
        """Missing fields in scheduler form"""
        self.check_entity('network', 'scheduler')

    def test_sch_range(self):
        """Missing fields in sch_range form"""
        self.check_entity('scheduler', 'sch_range')

    def test_sch_service(self):
        """Missing fields in sch_service form"""
        self.check_entity('scheduler', 'sch_service')

    def test_sch_task(self):
        """Missing fields in sch_task form"""
        self.check_entity('station', 'sch_task')
