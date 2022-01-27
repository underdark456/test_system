import ipaddress
import json
import os
import time

from global_options.options import PROJECT_DIR
from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
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
from src.nms_entities.basic_entities.sw_upload import SwUpload
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.user import User
from src.nms_entities.basic_entities.user_group import UserGroup
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider

__author__ = 'dkudryashov'
__version__ = '0.1'

from src.values_presenters import ValidIpAddr, ValidIpMask, ValidIpv6Addr, ValidIpv6Mask

from utilities.get_meta.get_meta import get_meta

options_path = 'test_scenarios.api.api_data_types'
backup_name = 'each_entity.txt'


class ApiDataTypesCase(CustomTestCase):
    """API data types validation case"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.21'
    __execution_time__ = 5  # approximate test case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(options_path)
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)

        cls.nms = Nms(cls.driver, 0, 0)
        cls.nms_version = cls.nms.get_version()
        cls.class_logger.info(f'NMS version {cls.nms_version}')

        if cls.nms_version is not None:
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
            'qos': Qos,
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

    def test_data_types(self):
        """Test each data type from meta on an individual field via API"""
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
                self.validate_next_data_type(obj, entity, var, data_type)

    def get_type_field(self, data_type):
        for entity in self.meta.keys():
            # Do not get vars from the following entities
            if entity in ('access', 'group', 'controller', 'alert'):
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

    def expand_dep_vars(self, obj, entity_name, var, vars_dict=None) -> dict:
        """Getting a dict of vars that should be sent along with a test value"""
        if vars_dict is None:
            vars_dict = {}
        dep_var = var.get('dep_var')
        dep_value = var.get('dep_value')
        if dep_var is not None:
            dep_var_dict = self.get_dep_var_dict(entity_name, dep_var)
            if dep_var_dict is None:
                self.fail(f'Cannot find referenced dep_var={dep_var} in meta')

            if dep_value is None:
                self.fail('No `dep_value`!')
            self.expand_dep_vars(obj, entity_name, dep_var_dict, vars_dict)

            # Getting bit-mask out of `dep_value` - first value first
            dep_value_bin = bin(dep_value)[2:][::-1]

            for i in range(len(dep_value_bin)):
                if dep_value_bin[i] == '1':
                    vars_dict[dep_var] = i
                    return vars_dict

    def validate_next_data_type(self, obj, entity_name, var, data_type):
        name = var.get('name')
        if var.get('dep_var') is not None:
            _vars = self.expand_dep_vars(obj, entity_name, var)
        else:
            _vars = {}

        # Input integer field (0 - int 4 bytes, 3 - short 2 bytes, 4 - ?)
        if data_type in (0, 3, 4):
            from_ = var.get('from')
            to_ = var.get('to')
            if from_ is None or to_ is None:
                self.fail('from or to is not found in the meta')

            valid, invalid = self.get_from_to_int_values(from_, to_)
            for value in valid:
                _vars[name] = value
                obj.send_params(_vars)
                nms_res = obj.get_param(name)
                self.assertEqual(str(value), str(nms_res), msg=f'Valid sent value={value}, set value={nms_res}')
            for value in invalid:
                _vars[name] = value
                obj.send_params(_vars)
                nms_res = obj.get_param(name)
                self.assertNotEqual(str(value), str(nms_res), msg=f'Invalid sent value={value}, set value={nms_res}')
            # Fractions should be returned as integers
            _vars[name] = str(from_ + 0.5)
            obj.send_params(_vars)
            nms_res = obj.get_param(name)
            self.assertEqual(str(from_), str(nms_res), msg=f'Valid sent value={from_ + 0.5}, set value={nms_res}')

        # Input float field
        elif data_type == 1:
            from_ = var.get('from')
            to_ = var.get('to')
            if from_ is None or to_ is None:
                self.fail('from or to is not found in the meta')

            valid, invalid = self.get_from_to_float_values(from_, to_)
            for value in valid:
                _vars[name] = value
                obj.send_params(_vars)
                nms_res = obj.get_param(name)
                if value == int(value):
                    self.assertIn(
                        str(nms_res),
                        (str(value), str(int(value)), value, int(value)),
                        msg=f'Valid sent value={value}, set value={nms_res}'
                    )
                else:
                    self.assertEqual(str(value), str(nms_res), msg=f'Valid sent value={value}, set value={nms_res}')
            for value in invalid:
                _vars[name] = value
                obj.send_params(_vars)
                nms_res = obj.get_param(name)
                self.assertNotEqual(str(value), str(nms_res), msg=f'Invalid sent value={value}, set value={nms_res}')

        # Checkbox field
        elif data_type == 8:
            for value in self.get_api_checkbox_on():
                obj.send_param(name, False)
                _vars[name] = value
                obj.send_params(_vars)
                nms_res = obj.get_param(name)
                self.assertIn(
                    str(nms_res),
                    ('ON', 'ON ', 1, '1', 'On', 'On ', 'on', 'on '),
                    msg=f'Valid checkbox value={value}, set value={nms_res}'
                )
                self.assertFalse(obj.has_param_error(name))
            for value in self.get_api_checkbox_off():
                obj.send_param(name, True)
                _vars[name] = value
                obj.send_params(_vars)
                nms_res = obj.get_param(name)
                self.assertIn(
                    str(nms_res),
                    ('OFF', 'Off', 0, '0', 'off'),
                    msg=f'Valid checkbox value={value}, set value={nms_res}'
                )
                self.assertFalse(obj.has_param_error(name))
            for value in self.get_api_checkbox_invalid():
                obj.send_param(name, 1)
                _vars[name] = value
                obj.send_params(_vars)
                nms_res = obj.get_param(name)
                self.assertNotEqual(str(value), str(nms_res), msg=f'Invalid checkbox value={value},set value={nms_res}')

        # Select static field
        elif data_type == 9:
            for option in var.get('select'):
                # By value
                _vars[name] = option.get('val')
                obj.send_params(_vars)
                nms_res = obj.get_param(name)
                if var.get('nonzero') is not None and option.get('value') in ('', 0, '0'):
                    self.assertNotEqual(
                        option.get('txt'),
                        nms_res,
                        msg=f'option sent={option.get("val")}, option set={nms_res}'
                    )
                else:
                    self.assertEqual(
                        option.get('txt'),
                        nms_res,
                        msg=f'option sent={option.get("val")}, option set={nms_res}'
                    )
                # By text
                _vars[name] = option.get('txt')
                obj.send_params(_vars)
                nms_res = obj.get_param(name)
                if var.get('nonzero') is not None and option.get('val') in ('', 0, '0'):
                    self.assertNotEqual(
                        option.get('txt'),
                        nms_res,
                        msg=f'option sent={option.get("txt")}, option set={nms_res}'
                    )
                else:
                    self.assertEqual(
                        option.get('txt'),
                        nms_res,
                        msg=f'option sent={option.get("txt")}, option set={nms_res}'
                    )
                # Non-valid
                for v in ('justasimpletext', 223):
                    _vars[name] = v
                    obj.send_params(_vars)
                    nms_res = obj.get_param(name)
                    self.assertNotEqual(
                        v,
                        nms_res,
                        msg=f'option sent={v}, option set={nms_res}'
                    )

        # Select dynamic field
        elif data_type in (14, 32):
            for option in var.get('select'):
                _vars[name] = option.get('val')
                obj.send_params(_vars)
                nms_res = obj.get_param(name)
                if var.get('nonzero') is not None and option.get('val') in ('', 0, '0'):
                    self.assertNotEqual(
                        option.get('txt'),
                        nms_res,
                        msg=f'option sent={option.get("val")}, option set={nms_res}'
                    )
                else:
                    # Have to compare with val+txt as well (i.e. shaper:0 test_shaper)
                    self.assertIn(
                        nms_res,
                        (option.get('val'), f'{option.get("val")} {option.get("txt")}'),
                        msg=f'option sent={option.get("val")}, option set={nms_res}'
                    )
                # Non-valid
                for v in ('justasimpletext', 223):
                    _vars[name] = v
                    obj.send_params(_vars)
                    nms_res = obj.get_param(name)
                    self.assertNotEqual(
                        v,
                        nms_res,
                        msg=f'Invalid option sent={v}, option set={nms_res}'
                    )

        # Input text field
        elif data_type == 10:
            nonzero = var.get('nonzero', False)
            if name == 'name':
                nonzero = True

            valid, invalid = self.get_text_input_values(nonzero)
            for value in valid:
                _vars[name] = value
                obj.send_params(_vars)
                nms_res = obj.get_param(name)
                self.assertEqual(str(value), str(nms_res), msg=f'Valid sent value={value}, set value={nms_res}')
            for value in invalid:
                _vars[name] = value
                obj.send_params(_vars)
                nms_res = obj.get_param(name)
                self.assertNotEqual(str(value), str(nms_res), msg=f'Invalid sent value={value}, set value={nms_res}')

        # Button
        elif data_type == 11:
            self.info('Type 11 - button - not checking via API')

        # Input IPv4 address field
        elif data_type == 16:
            test_values = self.get_ipv4_test_values()
            for i in test_values:
                _vars[name] = i
                obj.send_params(_vars)
                nms_res = obj.get_param(name)
                if i in ValidIpAddr():
                    self.assertEqual(i, nms_res, msg=f'valid ipv4 address={i}, set address={nms_res}')
                else:
                    self.assertNotEqual(i, nms_res, msg=f'test ipv4 address={i}, set address={nms_res}')

        # Input IPv4 mask field
        elif data_type == 17:
            for i in self.get_ipv4_mask_test_values():
                _vars[name] = i
                obj.send_params(_vars)
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
            for i in self.get_ipv6_test_values():
                _vars[name] = i
                obj.send_params(_vars)
                nms_res = obj.get_param(name)
                if i in ValidIpv6Addr():
                    i = ipaddress.ip_address(i).compressed
                    self.assertEqual(i.lower(), nms_res.lower(), msg=f'valid ipv6 address={i}, set address={nms_res}')
                else:
                    self.assertNotEqual(i.lower(), nms_res.lower(), msg=f'invalid ipv6 addr={i}, set addr={nms_res}')

        # Input IPv6 prefix field
        elif var.get('type') == 19:
            for i in self.get_ipv6_prefix_test_values():
                _vars[name] = i
                obj.send_params(_vars)
                nms_res = obj.get_param(name)
                if i in ValidIpv6Mask():
                    self.assertEqual(i, nms_res, msg=f'valid ipv6 prefix={i}, set prefix={nms_res}')
                else:
                    self.assertNotEqual(i, nms_res, msg=f'invalid ipv6 prefix={i}, set prefix={nms_res}')

        # Password field
        elif var.get('type') == 24:
            for i in self.get_password_test_values():
                _vars[name] = i
                self.user2.send_params(_vars)
                self.assertFalse(self.user2.has_param_error(name))
                # Make sure that password is not shown
                nms_res = self.user2.get_param(name)
                self.assertTrue(nms_res.count('*') == len(nms_res))

        # Select field for TDM modcodes
        elif var.get('type') == 26:
            # As long as controller is not used for the test, type 26 is checked in sch_service. Setting mode to DAMA
            self.assertEqual(obj.get_param('name'), 'test_sch_service', msg=f'type 26 test object is not a sch_service')

            for modcod in self.modcodes.get('tx_modcod'):
                _vars[name] = modcod.get('value')
                obj.send_params(_vars)
                nms_res = obj.get_param(name)
                self.assertEqual(
                    modcod.get('name'),
                    nms_res,
                    msg=f'sent modcod={modcod.get("value")}, set modcod={nms_res}'
                )
            # Non-existing modcod
            for m in ('reboot', 'shaper:0'):
                _vars[name] = m
                obj.send_params(_vars)
                # nms_res = obj.get_param(name)
                self.assertTrue(
                    obj.has_param_error(name),
                    msg=f'sent modcod={m}, causes no error')

        # Select field for TDMA modcodes
        elif var.get('type') == 27:
            for modcod in self.modcodes.get('tdma_mc'):
                _vars[name] = modcod.get('value')
                obj.send_params(_vars)
                nms_res = obj.get_param(name)
                self.assertEqual(
                    modcod.get('name'),
                    nms_res,
                    msg=f'sent modcod={modcod.get("value")}, set modcod={nms_res}'
                )
            # Non-existing modcod
            for m in ('reboot', 'shaper:0'):
                _vars[name] = m
                obj.send_params(_vars)
                # nms_res = obj.get_param(name)
                self.assertTrue(
                    obj.has_param_error(name),
                    msg=f'sent modcod={m}, causes no error')
        # Start and end time for sch_task
        elif data_type == 7:
            valid, invalid = self.get_time_test_values()
            for v in valid:
                _vars[name] = v
                obj.send_params(_vars)
                nms_res = obj.get_param(name)
                self.assertEqual(str(v), str(nms_res), msg=f'Valid sent value={v}, set value={nms_res}')
            for i in invalid:
                _vars[name] = i
                obj.send_params(_vars)
                nms_res = obj.get_param(name)
                self.assertNotEqual(str(i), str(nms_res), msg=f'Invalid sent value={i}, set value={nms_res}')
        else:
            self.fail(f'data type={data_type} is not validated yet')

    @staticmethod
    def get_time_test_values():
        valid = [int(time.time()), int(time.time()) + 86200, int(time.time()) - 86200]
        invalid = ['qwerty', ' ', True]
        return valid, invalid

    @staticmethod
    def get_api_checkbox_on():
        return 1, '1', 'ON', 'ON ', 'c', 'on', 'ON ', 'On'

    @staticmethod
    def get_api_checkbox_off():
        return 0, '0', 'OFF', 'Off ', 'off', 'ff'

    @staticmethod
    def get_api_checkbox_invalid():
        return 'qwerty', 2, '2', 'reboot'

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
