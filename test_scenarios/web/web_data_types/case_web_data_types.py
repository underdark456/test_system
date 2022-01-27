import ipaddress
import json
import os
from unittest import skip

from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from global_options.options import PROJECT_DIR
from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.exceptions import InvalidOptionsException
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
from src.nms_entities.basic_entities.sw_upload import SwUpload
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.user import User
from src.nms_entities.basic_entities.user_group import UserGroup
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider
from src.values_presenters import ValidIpAddr, ValidIpMask, ValidIpv6Addr, ValidIpv6Mask
from utilities.get_meta.get_meta import get_meta

options_path = 'test_scenarios.web.web_data_types'
backup_name = 'each_entity.txt'


class WebDataTypesCase(CustomTestCase):
    """Web forms data types case"""

    __author__ = 'dkudryashov'
    __version__ = '0.1'
    __execution_time = 330  # approximate test case execution time in seconds

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(options_path), driver_id='case_web_data_types'
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)

        cls.nms = Nms(cls.driver, 0, 0)
        cls.nms_version = cls.nms.get_version()
        if cls.nms_version is None:
            raise InvalidOptionsException(f'Cannot determine NMS version: {cls.nms_version}')
        cls.class_logger.info(f'NMS version {cls.nms_version}')
        cls.nms_version = cls.nms_version.replace('.', '_')

        # If meta for the current version is not generated yet
        if not os.path.isfile(f'{PROJECT_DIR}{os.sep}utilities{os.sep}get_meta{os.sep}meta_{cls.nms_version}.txt'):
            cls.class_logger.info('Meta for the current version is not generated yet. Generating...')
            get_meta()

        with open(f'{PROJECT_DIR}{os.sep}utilities{os.sep}get_meta{os.sep}meta_{cls.nms_version}.txt', 'r') as file:
            cls.meta = json.load(file)

        with open(f'{PROJECT_DIR}{os.sep}utilities{os.sep}get_meta{os.sep}modcodes_uhp_200x.txt', 'r') as file:
            cls.modcodes = json.load(file)

        cls.entity_name_to_class = {
            'access': Access,
            'alert': Alert,
            'bal_controller': BalController,
            'camera': Camera,
            'controller': Controller,
            'dashboard': Dashboard,
            'device': Device,
            'group': UserGroup,
            'network': Network,
            'nms': Nms,
            'policy': Policy,
            'polrule': PolicyRule,
            'port_map': ControllerPortMap,
            'profile_set': Profile,
            'rip_router': ControllerRip,
            'route': ControllerRoute,
            'server': Server,
            'service': Service,
            'shaper': Shaper,
            'sr_controller': SrController,
            'sr_license': SrLicense,
            'sr_teleport': SrTeleport,
            'station': Station,
            'sw_upload': SwUpload,
            'teleport': Teleport,
            'user': User,
            'vno': Vno,
            'scheduler': Scheduler,
            'sch_range': SchRange,
            'sch_service': SchService,
            'sch_task': SchTask,
        }

        # Creating a user in order to leave default user untouched (password field test)
        cls.user2 = User.create(cls.driver, 0, {'name': 'test_user'})

    @skip('Debug test')
    def test_sample(self):
        obj = self.entity_name_to_class.get('route')(self.driver, 0, 0)
        obj.load()
        self.validate_next_data_type(
            obj,
            'route',
            {
                "dep_value": 1920,
                "dep_var": "type",
                "help": "",
                "name": "v6_ip",
                "type": 18,
                "value": "::"
            },
            18
        )

    def test_data_types(self):
        """Test each data type from meta on an individual field via WEB browser"""
        self.data_types = set()
        for entity in self.meta.keys():
            for section_json in self.meta.get(entity):
                for var in section_json.get('vars'):
                    self.data_types.add(var.get('type'))
        self.data_types = list(self.data_types)
        self.data_types.sort()
        for data_type in self.data_types:
            entity, var = self.get_type_field(data_type)
            with self.subTest(f'Data type={data_type}, entity={entity}, var={var.get("name")}'):
                if entity not in self.entity_name_to_class.keys():
                    self.fail(f'Entity {entity} is not found in classes')
                obj = self.entity_name_to_class.get(entity)(self.driver, 0, 0)
                obj.load()
                self.validate_next_data_type(obj, entity, var, data_type)

    def get_type_field(self, data_type):
        for entity in self.meta.keys():
            # Do not get vars from the following entities
            if entity in ('access', 'group', 'controller'):
                continue
            for section_json in self.meta.get(entity):
                for var in section_json.get('vars'):
                    if var.get('name') == 'set_alert':
                        continue
                    if var.get('type') == data_type:
                        return entity, var
        self.fail(f'Cannot find var for data type={data_type}')

    def get_dep_var_dict(self, entity_name, dep_var_name):
        meta = self.meta.get(entity_name)
        for section in meta:
            for var in section.get('vars'):
                if var.get('name') == dep_var_name:
                    return var
        return None

    def expand_dep_vars(self, obj, entity_name, var):
        dep_var = var.get('dep_var')
        dep_value = var.get('dep_value')
        if dep_var is not None:
            dep_var_dict = self.get_dep_var_dict(entity_name, dep_var)
            if dep_var_dict is None:
                self.fail(f'Cannot find referenced dep_var={dep_var} in meta')

            if dep_value is None:
                self.fail('No `dep_value`!')
            self.expand_dep_vars(obj, entity_name, dep_var_dict)

            # Getting bit-mask out of `dep_value` - first value first
            dep_value_bin = bin(dep_value)[2:][::-1]

            dep_var_elem = self.driver._get_element_by(By.ID, dep_var)
            self.assertIsNotNone(dep_var_elem, msg=f'dep_var={dep_var} element is not located in the page')
            for i in range(len(dep_value_bin)):
                if dep_value_bin[i] == '1':
                    obj.set_param(dep_var, str(i))
                    break

    def validate_next_data_type(self, obj, entity_name, var, data_type):
        name = var.get('name')
        if var.get('dep_var') is not None:
            self.expand_dep_vars(obj, entity_name, var)

        # Input integer field (0 - int 4 bytes, 3 - short 2 bytes, 4 - ?)
        if data_type in (0, 3, 4):
            # Checking WEB element type - should be input
            var_elem = self.driver._get_element_by(By.ID, name)
            self.assertEqual(var_elem.tag_name, 'input', msg=f'type {data_type} element is not an input field')

            from_ = var.get('from')
            to_ = var.get('to')
            if from_ is None or to_ is None:
                self.fail('from or to is not found in the meta')

            valid, invalid = self.get_from_to_int_values(from_, to_)
            for value in valid:
                obj.send_param(name, str(value))
                nms_res = obj.get_param(name)
                self.assertEqual(str(value), str(nms_res), msg=f'Valid sent value={value}, set value={nms_res}')
            for value in invalid:
                obj.send_param(name, str(value))
                nms_res = obj.get_param(name)
                self.assertNotEqual(str(value), str(nms_res), msg=f'Invalid sent value={value}, set value={nms_res}')
            # Fractions should be returned as integers
            obj.send_param(name, str(from_ + 0.5))
            nms_res = obj.get_param(name)
            self.assertEqual(str(from_), str(nms_res), msg=f'Valid sent value={from_ + 0.5}, set value={nms_res}')

        # Input float field
        elif data_type == 1:
            # Checking WEB element type - should be input
            var_elem = self.driver._get_element_by(By.ID, name)
            self.assertEqual(var_elem.tag_name, 'input', msg=f'type {data_type} element is not an input field')

            from_ = var.get('from')
            to_ = var.get('to')
            if from_ is None or to_ is None:
                self.fail('from or to is not found in the meta')

            valid, invalid = self.get_from_to_float_values(from_, to_)
            for value in valid:
                obj.send_param(name, str(value))
                nms_res = obj.get_param(name)
                if value == int(value):
                    self.assertIn(
                        str(nms_res),
                        (str(value), str(int(value))),
                        msg=f'Valid sent value={value}, set value={nms_res}'
                    )
                else:
                    self.assertEqual(str(value), str(nms_res), msg=f'Valid sent value={value}, set value={nms_res}')
            for value in invalid:
                obj.send_param(name, str(value))
                nms_res = obj.get_param(name)
                self.assertNotEqual(str(value), str(nms_res), msg=f'Invalid sent value={value}, set value={nms_res}')

        # Checkbox field
        elif data_type == 8:
            # Checking WEB element type - should be a checkbox
            var_elem = self.driver._get_element_by(By.ID, name)
            self.assertEqual(
                var_elem.get_attribute('type'),
                'checkbox',
                msg=f'type {data_type} element is not a checkbox'
            )
            # Trying to click a couple of times
            for _ in range(2):
                if var_elem.get_attribute('checked'):
                    obj.send_param(name, 0)
                    var_elem = self.driver._get_element_by(By.ID, name)
                    self.assertFalse(var_elem.get_attribute('checked'), msg=f'Checkbox is clicked but stayed checked')
                else:
                    obj.send_param(name, 1)
                    var_elem = self.driver._get_element_by(By.ID, name)
                    self.assertTrue(var_elem.get_attribute('checked'), msg=f'Checkbox is clicked but stayed unchecked')

        # Select field
        elif data_type in (9, 14, 32):
            # Checking WEB element type - should be a select
            var_elem = self.driver._get_element_by(By.ID, name)
            self.assertEqual(var_elem.tag_name, 'select', msg=f'type {data_type} element is not a select field')

            for option in var.get('select'):
                obj.send_param(name, option.get('val'))
                nms_res = obj.get_param(name)
                var_elem = self.driver._get_element_by(By.ID, name)
                # Getting a text value of the selected option
                selected_option = Select(var_elem).first_selected_option.text
                if var.get('nonzero') is not None and option.get('val') in ('', 0, '0'):
                    self.assertNotEqual(
                        option.get('txt'),
                        selected_option,
                        msg=f'option sent={option.get("txt")}, option set={selected_option}'
                    )
                else:
                    if name == 'file_name':
                        self.assertEqual(
                            option.get('txt').split()[0],
                            selected_option.split()[0],
                            msg=f'option sent={option.get("txt")}, option set={selected_option}'
                        )
                    else:
                        self.assertEqual(
                            option.get('txt'),
                            selected_option,
                            msg=f'option sent={option.get("txt")}, option set={selected_option}'
                        )

        # Input text field
        elif data_type == 10:
            # Checking WEB element type - should be input
            var_elem = self.driver._get_element_by(By.ID, name)
            self.assertEqual(var_elem.tag_name, 'input', msg=f'type {data_type} element is not an input field')

            nonzero = var.get('nonzero', False)
            if name == 'name':
                nonzero = True

            valid, invalid = self.get_text_input_values(nonzero)
            for value in valid:
                obj.send_param(name, str(value))
                nms_res = obj.get_param(name)
                self.assertEqual(str(value), str(nms_res), msg=f'Valid sent value={value}, set value={nms_res}')
            for value in invalid:
                obj.send_param(name, str(value))
                nms_res = obj.get_param(name)
                self.assertNotEqual(str(value), str(nms_res), msg=f'Invalid sent value={value}, set value={nms_res}')

        # Button
        elif data_type == 11:
            # Checking WEB element type - should be a button
            var_elem = self.driver._get_element_by(By.ID, name)
            self.assertEqual(var_elem.tag_name, 'button', msg=f'type {data_type} element is not a button')

        # Input IPv4 address field
        elif data_type == 16:
            # Checking WEB element type - should be input
            var_elem = self.driver._get_element_by(By.ID, name)

            self.assertEqual(var_elem.tag_name, 'input', msg=f'type {data_type} element is not an input field')
            test_values = self.get_ipv4_test_values()
            for i in test_values:
                obj.send_param(name, i)
                nms_res = obj.get_param(name)
                if i in ValidIpAddr():
                    self.assertEqual(i, nms_res, msg=f'valid ipv4 address={i}, set address={nms_res}')
                else:
                    self.assertNotEqual(i, nms_res, msg=f'test ipv4 address={i}, set address={nms_res}')

        # Input IPv4 mask field
        elif data_type == 17:
            # Checking WEB element type - should be input
            var_elem = self.driver._get_element_by(By.ID, name)

            self.assertEqual(var_elem.tag_name, 'input', msg=f'type {data_type} element is not an input field')
            for i in self.get_ipv4_mask_test_values():
                obj.send_param(name, i)
                nms_res = obj.get_param(name)
                if i in ValidIpMask():
                    # Converting mask to prefix as NMS stores masks as prefixes
                    if not i.startswith('/'):
                        i = '/' + str(ipaddress.IPv4Network(f'127.0.0.0/{i}').prefixlen)
                    self.assertEqual(i, nms_res, msg=f'valid ipv4 mask={i}, set mask={nms_res}')
                else:
                    self.assertNotEqual(i, nms_res, msg=f'test ipv4 mask={i}, set mask={nms_res}')

        # Input IPv6 field
        elif data_type == 18:
            # Checking WEB element type - should be input
            var_elem = self.driver._get_element_by(By.ID, name)
            self.assertEqual(var_elem.tag_name, 'input', msg=f'type {data_type} element is not an input field')

            for i in self.get_ipv6_test_values():
                # obj.send_param(name, i)
                obj.send_params({'service': 'service:0', name: i})
                nms_res = obj.get_param(name)
                if i in ValidIpv6Addr():
                    i = ipaddress.ip_address(i).compressed
                    self.assertEqual(i.lower(), nms_res.lower(), msg=f'valid ipv6 address={i}, set address={nms_res}')
                else:
                    self.assertNotEqual(i.lower(), nms_res.lower(), msg=f'invalid ipv6 address={i}, set address={nms_res}')

        # Input IPv6 prefix field
        elif var.get('type') == 19:
            # Checking WEB element type - should be input
            var_elem = self.driver._get_element_by(By.ID, name)
            self.assertEqual(var_elem.tag_name, 'input', msg=f'type {data_type} element is not an input field')

            for i in self.get_ipv6_prefix_test_values():
                # obj.send_param(name, i)
                obj.send_params({'service': 'service:0', name: i})
                nms_res = obj.get_param(name)
                if i in ValidIpv6Mask():
                    self.assertEqual(i, nms_res, msg=f'valid ipv6 prefix={i}, set prefix={nms_res}')
                else:
                    self.assertNotEqual(i, nms_res, msg=f'invalid ipv6 prefix={i}, set prefix={nms_res}')

        # Password field
        elif var.get('type') == 24:
            # Checking WEB element type - should be input
            var_elem = self.driver._get_element_by(By.ID, name)
            self.assertEqual(var_elem.tag_name, 'input', msg=f'type {data_type} element is not an input field')

            for i in self.get_password_test_values():
                self.user2.send_param(name, i)
                self.assertFalse(self.user2.has_param_error(name))
                # Make sure that password is not shown
                nms_res = self.user2.get_param(name)
                self.assertTrue(nms_res.count('*') == len(nms_res))

        # Select field for TDM modcodes
        elif var.get('type') == 26:
            # As long as controller is not used for the test, type 26 is checked in station. Setting mode to DAMA
            self.assertEqual(obj.get_param('name'), 'test_sch_service', msg=f'type 26 test object is not a sch_service')
            # obj.send_param('mode', StationModes.DAMA)

            # Checking WEB element type - should be a select
            var_elem = self.driver._get_element_by(By.ID, name)
            self.assertEqual(var_elem.tag_name, 'select', msg=f'type {data_type} element is not a select field')

            for modcod in self.modcodes.get('tx_modcod'):
                obj.send_param(name, modcod.get('value'))
                nms_res = obj.get_param(name)
                var_elem = self.driver._get_element_by(By.ID, name)
                # Getting a text value of the selected option
                selected_option = Select(var_elem).first_selected_option.text
                self.assertEqual(
                    modcod.get('name'),
                    selected_option,
                    msg=f'applied modcod={modcod.get("name")}, selected option text={selected_option}'
                )
                self.assertEqual(
                    str(modcod.get('value')),
                    str(nms_res),
                    f'applied modcod value={modcod.get("value")}, selected option value={nms_res}',
                )

        # Select field for TDMA modcodes
        elif var.get('type') == 27:
            # Checking WEB element type - should be a select
            var_elem = self.driver._get_element_by(By.ID, name)
            self.assertEqual(var_elem.tag_name, 'select', msg=f'type {data_type} element is not a select field')

            for modcod in self.modcodes.get('tdma_mc'):
                obj.send_param(name, modcod.get('value'))
                nms_res = obj.get_param(name)
                var_elem = self.driver._get_element_by(By.ID, name)
                # Getting a text value of the selected option
                selected_option = Select(var_elem).first_selected_option.text
                self.assertEqual(
                    modcod.get('name'),
                    selected_option,
                    msg=f'applied modcod={modcod.get("name")}, selected option text={selected_option}'
                )
                self.assertEqual(
                    str(modcod.get('value')),
                    str(nms_res),
                    msg=f'applied modcod value={modcod.get("value")}, selected option value={nms_res}',
                )
        else:
            self.fail(f'data type={data_type} is not validated yet')

    @staticmethod
    def get_password_test_values():
        return ['', 'qwerty', '#$&^%@$#)(~', ]

    @staticmethod
    def get_text_input_values(nonzero=False):
        if nonzero:
            valid = ['qwerty', 'кириллица', 'True', '!$@%#&%*^)(|/.,`~']
            invalid = ['', 'a' * 100]
        else:
            valid = ['', 'qwerty', 'кириллица', 'True', '!$@%#&%*^)(|/.,`~']
            invalid = ['a' * 100]
        return valid, invalid

    @staticmethod
    def get_ipv4_test_values():
        return ['1.1.1.1', '256.1.1.1', '1.1.1.1.1', '12.23.45', '1', '22', '192.300.22.1']

    @staticmethod
    def get_ipv6_test_values():
        return [
            '2345:0425:2CA1:0000:0000:0567:5673:23b5',
            '2345:0425:2CA1::0567:5673:23b5',
            '2001:db8::1',
            '2001::0567:7829',
        ]

    @staticmethod
    def get_ipv6_prefix_test_values():
        return ['/64', '/128', 'qwerty', '/0', '/333', ]

    @staticmethod
    def get_ipv4_mask_test_values():
        return ['/24', '/32', '/33', '/5555555', 20, '255.255.256.0', '/-30', 'qwerty', '/16', '255.255.255.0']

    @staticmethod
    def get_from_to_int_values(from_, to_):
        valid = [from_, to_, (from_ + to_) // 2, from_ + 1, to_ - 1]
        invalid = ['qwerty', from_ - 1, to_ + 1]
        return valid, invalid

    @staticmethod
    def get_from_to_float_values(from_, to_):
        valid = [
            from_,
            to_,
            (from_ + to_) / 2,
            (from_ + to_) / 2 - 0.5,
            (from_ + to_) / 2 + 0.5,
            from_ + 0.1, to_ - 0.1
        ]
        invalid = [
            'qwerty',
            from_ - 0.1,
            to_ + 0.1
        ]
        return valid, invalid
