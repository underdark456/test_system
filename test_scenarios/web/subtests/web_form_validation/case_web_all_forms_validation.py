import json
import os
import time
from unittest import skip

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select

from global_options.options import PROJECT_DIR
from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import RuleTypes, ActionTypes, AlertModes
from src.exceptions import NoSuchParamException
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
from src.nms_entities.basic_entities.server import Server
from src.nms_entities.basic_entities.service import Service
from src.nms_entities.basic_entities.shaper import Shaper
from src.nms_entities.basic_entities.sr_controller import SrController
from src.nms_entities.basic_entities.sr_license import SrLicense
from src.nms_entities.basic_entities.sr_teleport import SrTeleport
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.sw_upload import SwUpload
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.user import User
from src.nms_entities.basic_entities.user_group import UserGroup
from src.nms_entities.basic_entities.vno import Vno
from src.nms_entities.paths_manager import PathsManager
from src.options_providers.options_provider import OptionsProvider, CHROME_CONNECT

__author__ = 'dkudryashov'
__version__ = '0.1'

from src.values_presenters import IP_TEST_VALUES, ValidIpAddr, IP_MASK_TEST_VALUES, ValidIpMask, IPV6_TEST_VALUES, \
    ValidIpv6Addr, IPV6_PREFIX_TEST_VALUES, ValidIpv6Mask

from utilities.get_meta.get_meta import get_meta

options_path = 'test_scenarios.web.subtests.form_validation'
backup_name = 'each_entity.txt'


@skip('Not ready yet!')
class WebAllFormsValidationCase(CustomTestCase):
    """Not needed as data types test exists? Web all forms validation according to meta"""

    st_time = None

    @classmethod
    def set_up_class(cls):
        cls.st_time = time.perf_counter()
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection('global_options', CHROME_CONNECT)
        )
        cls.options = OptionsProvider.get_options(options_path)

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

        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)

        cls.depending_params = cls.options.get('depending_params')
        cls.checked_params = set()  # to store depending params that are already checked in validate_depending_params
        cls.CHECKBOX_ON = cls.options.get('checkbox_on')
        cls.CHECKBOX_OFF = cls.options.get('checkbox_off')
        cls.INPUT_VALID = cls.options.get('input_valid_values')
        cls.INPUT_TEST = cls.options.get('input_test_values')
        cls.INPUT_TEST_PASSWORD = cls.options.get('pass_test_values')

    def get_dep_var_dict(self, entity_name, dep_var_name):
        meta = self.meta.get(entity_name)
        for section in meta:
            for var in section.get('vars'):
                if var.get('name') == dep_var_name:
                    return var
        return None

    def expand_deps(self, obj, entity_name, section_name, initial_var, var):
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
                self.fail('Cannot find referenced dep_var in meta')

            if dep_value is None:
                self.fail('No `dep_value`!')

            # Getting bit-mask out of `dep_value` - first value first
            dep_value_bin = bin(dep_value)[2:][::-1]
            dep_var_elem = self.driver._get_element_by(By.ID, dep_var)
            self.assertIsNotNone(dep_var_elem, msg=f'dep_var={dep_var} element is not located in the page')

            # For station to change mode it is obligatory to detach it from a controller
            if entity_name == 'station' and dep_var == 'mode':
                rx_ctrl = obj.get_param('rx_controller')
                if rx_ctrl is not None and rx_ctrl != '':
                    obj.send_param('rx_controller', '')
                tx_ctrl = obj.get_param('tx_controller')
                if tx_ctrl is not None and tx_ctrl != '':
                    obj.send_param('tx_controller', '')

                # Getting element once again because applying rx_controller and tx_controller refreshes the page
                dep_var_elem = self.driver._get_element_by(By.ID, dep_var)

            if dep_var_elem.get_attribute("type") == 'checkbox':
                if not dep_var_elem.get_attribute('checked'):
                    # Clicking the parent element of the checkbox
                    obj.send_param(dep_var, 1)
                    # parent_div = dep_var_elem.find_element_by_xpath('..')
                    # parent_div.click()
                self.expand_deps(obj, entity_name, section_name, initial_var, dep_var_dict)

            # Picking a first correct dep_value in the dropdown
            elif dep_var_elem.tag_name == 'select':
                for i in range(len(dep_value_bin)):
                    # if i >= len(dep_var_dict.get('select')):
                    #     break
                    if dep_value_bin[i] == '1':
                        # Page can be refreshed
                        dep_var_elem = self.driver._get_element_by(By.ID, dep_var)
                        self.assertIsNotNone(dep_var_elem)
                        # selector = Select(dep_var_elem)
                        # selector.select_by_value(str(i))
                        obj.send_param(dep_var, str(i))
                        self.expand_deps(obj, entity_name, section_name, initial_var, dep_var_dict)
                        break

            # Picking a first correct value in input
            elif dep_var_elem.tag_name == 'input':
                for i in range(len(dep_value_bin)):
                    # if i > dep_var_dict.get('to'):
                    #     break
                    if dep_value_bin[i] == '1':
                        # dep_var_elem.click()
                        # dep_var_elem.send_keys(Keys.CONTROL + "a")
                        # dep_var_elem.send_keys(Keys.DELETE)
                        # dep_var_elem.send_keys(str(i))
                        obj.send_param(dep_var, str(i))
                        self.expand_deps(obj, entity_name, section_name, initial_var, dep_var_dict)
                        break
            else:
                self.fail('dep_var element is neither a checkbox nor a select nor an input')

        # No more depending vars
        else:
            if name in self.depending_params.keys():
                depending_param = True
            else:
                depending_param = False

            if initial_var.get("nonzero") is None:
                nonzero = False
            else:
                nonzero = True

            param = self.driver._get_element_by(By.ID, name)
            self.assertIsNotNone(param, msg=f'Cannot locate {name} in the page')
            # Checkbox
            if initial_var.get("type") == 8:
                self.assertEqual(
                    'checkbox',
                    param.get_attribute("type"),
                    msg=f'{name} type is 8 but it is not a checkbox'
                )
                for _ in range(2):
                    param = self.driver._get_element_by(By.ID, name)
                    if param.get_attribute('checked'):
                        obj.send_param(name, 0)
                        self.assertIn(
                            obj.get_param(name),
                            self.CHECKBOX_OFF,
                            msg=f'Checkbox is not unchecked as it should be'
                        )
                    else:
                        obj.send_param(name, 1)
                        self.assertIn(
                            obj.get_param(name),
                            self.CHECKBOX_ON,
                            msg=f'Checkbox is not checked as it should be'
                        )

            # Input IP field
            elif initial_var.get('type') == 16:
                for i in IP_TEST_VALUES:
                    obj.send_param(name, i)
                    if i in ValidIpAddr():
                        self.assertFalse(obj.has_param_error(name), msg=f'test ipv4 address={i}')
                    else:
                        self.assertTrue(obj.has_param_error(name), msg=f'test ipv4 address={i}')

            # Input IPv6 field
            elif var.get('type') == 18:
                for i in IPV6_TEST_VALUES:
                    obj.send_param(name, i)
                    if i in ValidIpv6Addr():
                        self.assertFalse(obj.has_param_error(name), msg=f'test ipv6 address={i}')
                    else:
                        self.assertTrue(obj.has_param_error(name), msg=f'test ipv6 address={i}')

            # Input IPv4 mask field
            elif initial_var.get('type') == 17:
                for i in IP_MASK_TEST_VALUES:
                    obj.send_param(name, i)
                    if i in ValidIpMask():
                        self.assertFalse(obj.has_param_error(name), msg=f'test ipv4 mask={i}')
                    else:
                        self.assertTrue(obj.has_param_error(name), msg=f'test ipv4 mask={i}')

            # Input IPv6 prefix field
            elif var.get('type') == 19:
                for i in IPV6_PREFIX_TEST_VALUES:
                    obj.send_param(name, i)
                    if i in ValidIpv6Mask():
                        self.assertFalse(obj.has_param_error(name), msg=f'test ipv6 prefix={i}')
                    else:
                        self.assertTrue(obj.has_param_error(name), msg=f'test ipv6 prefix={i}')

            # Input float field
            elif initial_var.get('type') == 1:
                if depending_param:
                    self.validate_depending_params(initial_var, obj)
                else:
                    from_ = initial_var.get('from')
                    to_ = initial_var.get('to')
                    if from_ is None or to_ is None:
                        raise Exception('Cannot get from or to for param type 1')
                    valid = [from_, to_, (from_ + to_) / 2 + 0.7, from_ + 0.1, to_ - 0.1]
                    invalid = ['qwerty', from_ - 1.1, to_ + 0.1]
                    for v in valid:
                        obj.send_param(name, v)
                        self.assertFalse(obj.has_param_error(name), msg=f'valid value={v}')
                    for i in invalid:
                        obj.send_param(name, i)
                        self.assertTrue(obj.has_param_error(name), msg=f'invalid value={i}')

            # Text input for numbers with `from` and `to` parameters
            elif initial_var.get('type') in (0, 3, 4):
                if depending_param:
                    self.validate_depending_params(initial_var, obj)
                else:
                    from_ = initial_var.get('from')
                    to_ = initial_var.get('to')
                    if from_ is None or to_ is None:
                        raise Exception('Cannot get from or to for param type 0')
                    valid = [from_, to_, from_ + 1, to_ - 1, (from_ + to_) // 2]
                    invalid = [from_ - 1, to_ + 1, 'qwerty']
                    for v in valid:
                        obj.send_param(name, v)
                        nms_res = obj.get_param(var.get(name))
                        self.assertEqual(str(v), str(nms_res), msg=f'Valid sent value={v}, set value={nms_res}')
                        # self.assertFalse(obj.has_param_error(name), msg=f'valid value={v}')
                    for i in invalid:
                        obj.send_param(name, i)
                        nms_res = obj.get_param(var.get(name))
                        self.assertNotEqual(str(i), str(nms_res), msg=f'Invalid sent value={i}, set value={nms_res}')
                        # self.assertTrue(obj.has_param_error(name), msg=f'invalid value={i}')

            # Text input
            elif initial_var.get("type") == 10:
                for value in self.INPUT_TEST:
                    obj.send_param(name, value)
                    if name == 'name' and value in self.INPUT_VALID:
                        self.assertFalse(obj.has_param_error(name))
                    elif name == 'name' and value not in self.INPUT_VALID:
                        self.assertTrue(obj.has_param_error(name))
                    # Password-like inputs are not entirely tolerant to cyrillic characters
                    elif value in ('кириллица', '!$@%#&%*^)(|/.,`~') \
                            and name in ('rip_pass', 'snmp_read', 'snmp_write', 'snmp_user'):
                        self.assertTrue(obj.has_param_error(name))
                    elif not nonzero and (value in self.INPUT_VALID or value == ''):
                        self.assertFalse(obj.has_param_error(name), msg=f'value={value}')
                    else:
                        self.assertTrue(obj.has_param_error(name), msg=f'value={value}')

            # Text input password field (like password in user)
            elif initial_var.get("type") == 24:
                for value in self.INPUT_TEST_PASSWORD:
                    obj.send_param(name, value)
                    if nonzero and value == '':
                        self.assertTrue(obj.has_param_error(name))
                    else:
                        self.assertFalse(obj.has_param_error(name))

            # DROPDOWN
            elif initial_var.get("type") in (9, 14, 32):
                self.assertEqual('select', param.tag_name, msg=f'{name} is of type {initial_var.get("type")} but'
                                                               f' it is not a dropdown')
                for option in initial_var.get('select'):
                    # Do not check alert specify without setting alert
                    if name == 'alert_mode' and option.get('txt') == 'Specify':
                        continue
                    if name == 'set_alert':
                        obj.send_params({
                            'alert_mode': AlertModes.SPECIFY,
                            name: option.get('txt'),
                        })
                    else:
                        obj.send_param(name, option.get('val'))
                    if nonzero and option.get('val') == '':
                        self.assertTrue(obj.has_param_error(name))
                    else:
                        self.assertFalse(obj.has_param_error(name))
                        # Check that param visible text is as expected
                        param = self.driver._get_element_by(By.ID, name)
                        self.assertTrue(Select(param).first_selected_option.text.startswith(option.get('txt')[:20]))

            # DAMA modcod dropdown
            elif initial_var.get("type") == 26:
                for m in self.modcodes.get('tx_modcod'):
                    obj.send_param(name, m.get('value'))
                    self.assertFalse(obj.has_param_error(name))

            else:
                self.fail(f'!!!Unknown TYPE!!! {initial_var.get("type")}')

    def validate_depending_params(self, initial_var, obj):
        """Validate depending params (i.e. vlan_min, vlan_max) at the same time"""
        name = initial_var.get('name')
        dep_dict = self.depending_params.get(name)
        dep_name = dep_dict.get('dep')

        self.checked_params.add(dep_name)

        lower = dep_dict.get('lower')
        # TODO: probably get from2 and to2 for the second param from meta
        from_ = initial_var.get('from')
        to_ = initial_var.get('to')
        valid_combinations = [
            [from_, from_ + 1],
            [from_, to_],
            [from_, from_],
            [from_ + 1, to_],
            [from_ + 1, from_ + 2],
            [to_, to_],
            [to_ - 1, to_],
        ]
        invalid_combinations = [
            [from_ + 1, from_],
            [to_, from_],
            [from_ + 1, from_],
            [from_ + 2, from_ + 1],
            [to_, to_ - 1],
            [to_ - 1, to_ - 2],
            [from_ - 1, from_],
            [from_ - 1, from_ - 1],
            [to_ + 1, to_],
            [to_ + 1, to_ + 1],
            [from_, from_ - 1],
            [to_, to_ + 1],
            ['qwerty', to_],
            [from_, 'qwerty']
        ]
        for v in valid_combinations:
            if lower == name:
                name_val = v[0]
                dep_name_val = v[1]
                obj.send_params({name: name_val, dep_name: dep_name_val})
            else:
                name_val = v[1]
                dep_name_val = v[0]
                obj.send_params({name: name_val, dep_name: dep_name_val})
            name_error = obj.has_param_error(name)
            dep_name_error = obj.has_param_error(dep_name)
            self.assertFalse(name_error, msg=f'{name}={name_val}, {dep_name}={dep_name_val} {name} error={name_error}')
            self.assertFalse(dep_name_error, msg=f'{name}={name_val}, {dep_name}={dep_name_val}, '
                                                 f'{dep_name} error={dep_name_error}')
        for i in invalid_combinations:
            if lower == name:
                name_val = i[0]
                dep_name_val = i[1]
                obj.send_params({name: name_val, dep_name: dep_name_val})
            else:
                name_val = i[0]
                dep_name_val = i[1]
                obj.send_params({name: name_val, dep_name: dep_name_val})
            name_error = obj.has_param_error(name)
            dep_name_error = obj.has_param_error(dep_name)
            self.assertTrue(
                name_error or dep_name_error,
                msg=f'{name}={name_val}, {dep_name}={dep_name_val}, {name} error={name_error}, '
                    f'{dep_name} error={dep_name_error}')

    def get_meta_dict_by_name(self, entity_name, name):
        pass

    def validate_form(self, obj, entity_name):
        meta = self.meta.get(entity_name)
        self.driver.load_data(PathsManager._OBJECT_EDIT.format(entity_name, obj.get_id()))
        for section in meta:
            section_name = section.get('section')
            if section_name is None:
                section_name = section.get('table')
                if section_name is None:
                    self.fail('!!!Cannot get neither section name nor table name!!!')

            for var in section.get('vars'):
                name = var.get('name')
                # TODO: make special wfq test
                # param is already checked in validate_depending params or wfq
                if name in self.checked_params or name.startswith('wfq'):
                    self.info(f'{name} is not checked. Should be checked in a separate test')
                    continue
                # TODO: make special test to check UHP model depending params
                if name == 'uhp_model':
                    self.info(f'{name} is not checked. Should be checked in a separate test')
                    continue
                # Skip buttons such as `return_all`, `save_config` etc.
                if var.get('type') == 11:
                    continue
                with self.subTest(f'{entity_name} section={section_name} param={var.get("name")}'):
                    self.expand_deps(obj, entity_name, section_name, var, var)

    @skip('Do not test initial access as it can lead to NMS access issues')
    def test_access(self):
        # group = UserGroup.create(self.driver, 0, {'name': 'test_group'})
        # access = Access.create(self.driver, 0, {'group': f'group:{group.get_id()}'})
        access = Access(self.driver, 0, 0)
        self.validate_form(access, 'access')

    def test_alert(self):
        alert = Alert(self.driver, 0, 0)
        self.validate_form(alert, 'alert')

    def test_bal_controller(self):
        bal_ctrl = BalController(self.driver, 0, 0)
        self.validate_form(bal_ctrl, 'bal_controller')

    def test_camera(self):
        cam = Camera(self.driver, 0, 0)
        self.validate_form(cam, 'camera')

    @skip('Too many dependencies to validate controller')
    def test_controller(self):
        ctrl = Controller(self.driver, 0, 0)
        self.validate_form(ctrl, 'controller')

    def test_dashboard(self):
        dash = Dashboard(self.driver, 0, 0)
        self.validate_form(dash, 'dashboard')

    def test_device(self):
        dev = Device(self.driver, 0, 0)
        self.validate_form(dev, 'device')

    @skip('Do not test initial access as it can lead to NMS access issues')
    def test_group(self):
        pass

    def test_network(self):
        net = Network(self.driver, 0, 0)
        self.validate_form(net, 'network')

    def test_nms(self):
        nms = Nms(self.driver, 0, 0)
        self.validate_form(nms, 'nms')

    def test_policy(self):
        pol = Policy(self.driver, 0, 0)
        self.validate_form(pol, 'policy')

    def test_policy_rule(self):
        rule = PolicyRule(self.driver, 0, 0)
        self.validate_form(rule, 'polrule')

    def test_port_map(self):
        port_map = ControllerPortMap(self.driver, 0, 0)
        self.validate_form(port_map, 'port_map')

    def test_profile_set(self):
        pro_set = Profile(self.driver, 0, 0)
        self.validate_form(pro_set, 'profile_set')

    def test_rip_router(self):
        rip = ControllerRip(self.driver, 0, 0)
        self.validate_form(rip, 'rip_router')

    def test_route(self):
        route = ControllerRoute(self.driver, 0, 0)
        self.validate_form(route, 'route')

    def test_server(self):
        server = Server(self.driver, 0, 0)
        self.validate_form(server, 'server')

    def test_service(self):
        service = Service(self.driver, 0, 0)
        self.validate_form(service, 'service')

    def test_shaper(self):
        shp = Shaper(self.driver, 0, 0)
        self.validate_form(shp, 'shaper')

    def test_sr_controller(self):
        sr_ctrl = SrController(self.driver, 0, 0)
        self.validate_form(sr_ctrl, 'sr_controller')

    def test_sr_license(self):
        sr_lic = SrLicense(self.driver, 0, 0)
        self.validate_form(sr_lic, 'sr_license')

    def test_sr_teleport(self):
        sr_tp = SrTeleport(self.driver, 0, 0)
        self.validate_form(sr_tp, 'sr_teleport')

    def test_station(self):
        stn = Station(self.driver, 0, 0)
        self.validate_form(stn, 'station')

    def test_sw_upload(self):
        sw_up = SwUpload(self.driver, 0, 0)
        self.validate_form(sw_up, 'sw_upload')

    def test_teleport(self):
        tp = Teleport(self.driver, 0, 0)
        self.validate_form(tp, 'teleport')

    def test_user(self):
        group = UserGroup(self.driver, 0, 0)
        user = User.create(self.driver, group.get_id(), {'name': 'test_user'})
        self.validate_form(user, 'user')

    def test_vno(self):
        vno = Vno(self.driver, 0, 0)
        self.validate_form(vno, 'vno')

    @skip('Debug test - not needed')
    def test_debug(self):
        net = Network.create(self.driver, 0, {'name': 'test_net'})
        pol = Policy.create(self.driver, net.get_id(), {'name': 'test_pol'})
        rule = PolicyRule.create(self.driver, pol.get_id(), {
            'sequence': 1,
            'type': RuleTypes.ACTION,
            'action_type': ActionTypes.ENCRYPT
        })
        rule.send_param('key', 22)

    @classmethod
    def tear_down_class(cls):
        if cls.st_time is not None:
            print(f'Execution time is {time.perf_counter() - cls.st_time} seconds')


