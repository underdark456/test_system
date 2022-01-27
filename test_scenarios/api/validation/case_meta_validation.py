import json
import os
import random
import time
from unittest import skip

from global_options.options import PROJECT_DIR
from src.backup_manager.backup_manager import BackupManager
from src.constants import NEW_OBJECT_ID
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.exceptions import InvalidOptionsException, ObjectNotCreatedException
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
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider

__author__ = 'dkudryashov'
__version__ = '0.1'

from src.values_presenters import IP_TEST_VALUES, ValidIpAddr, IP_MASK_TEST_VALUES, ValidIpMask, ValidIpv6Addr, \
    IPV6_TEST_VALUES, IPV6_PREFIX_TEST_VALUES, ValidIpv6Mask

from utilities.get_meta.get_meta import get_meta

options_path = 'test_scenarios.api.validation'
backup_name = 'each_entity.txt'


@skip('Data types validation case exists. This one is probably not needed.')
class ApiAllFormsValidationCase(CustomTestCase):
    """Not needed as data types test exists? API validate form fields according to meta data"""

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(options_path)
        )

        cls.nms = Nms(cls.driver, 0, 0)
        cls.nms_version = cls.nms.get_param('version').split()[1].replace('.', '_')

        # If meta fo the current version is not generated yet
        if not os.path.isfile(f'{PROJECT_DIR}{os.sep}utilities{os.sep}get_meta{os.sep}meta_{cls.nms_version}.txt'):
            get_meta()

        # Obtaining meta data for the current version
        with open(f'{PROJECT_DIR}{os.sep}utilities{os.sep}get_meta{os.sep}meta_{cls.nms_version}.txt', 'r') as file:
            cls.meta = json.load(file)

        with open(f'{PROJECT_DIR}{os.sep}utilities{os.sep}get_meta{os.sep}modcodes_uhp_200x.txt', 'r') as file:
            modcodes = json.load(file)
            cls.tdma_mc = modcodes.get('tdma_mc')
            cls.tx_modcod_uhp200x = modcodes.get('tx_modcod')

        with open(f'{PROJECT_DIR}{os.sep}utilities{os.sep}get_meta{os.sep}modcodes_uhp_200.txt', 'r') as file:
            modcodes = json.load(file)
            cls.tx_modcod_uhp200 = modcodes.get('tx_modcod')

        cls.options = OptionsProvider.get_options(options_path)
        cls.depending_params = cls.options.get('depending_params')
        cls.checked_params = set()  # to store depending params that are already checked in validate_depending_params
        cls.controller_names = set()

        cls.checkbox_test_values = cls.options.get('checkbox_test_values')
        cls.checkbox_test_values_on = cls.options.get('checkbox_test_values_on')
        cls.checkbox_test_values_off = cls.options.get('checkbox_test_values_off')
        cls.checkbox_response_on = cls.options.get('checkbox_response_on')
        cls.checkbox_response_off = cls.options.get('checkbox_response_off')

        cls.text_input_test_values = cls.options.get('text_input_test_values')
        cls.pass_test_values = cls.options.get('pass_test_values')

        cls.backup = BackupManager()

    # Has to call between each test method in order to leave objects' params untouched
    def set_up(self):
        self.backup.apply_backup(backup_name)

    def validate_entity(self, obj, entity_name):
        meta = self.meta.get(entity_name)
        for section in meta:
            section_name = section.get('section')
            if section_name is None:
                section_name = section.get('table')
                if section_name is None:
                    self.fail('!!!Cannot get neither section name nor table name!!!')
            for var in section.get('vars'):
                name = var.get('name')
                # TODO: make special wfq and queues test
                # param is already checked in validate_depending params or wfq
                if name in self.checked_params:
                    continue
                if name.startswith('wfq') or name.startswith('mod_que'):
                    continue
                # Special case for policy
                if name in ('policy', ):
                    continue
                # Skip buttons such as `return_all`, `save_config` etc.
                if var.get('type') == 11:
                    continue
                # Special case for alert mode and set alert as they depend on each over
                if name == 'alert_mode':
                    with self.subTest(f'{entity_name} section={section_name} param={var.get("name")}'):
                        self.validate_alert_mode(obj, var, name, entity_name)
                    continue
                # Set alert is checked along with alert mode
                if name == 'set_alert':
                    continue
                else:
                    with self.subTest(f'{entity_name} section={section_name} param={var.get("name")}'):
                        self.validate_next_param(obj, var, name, entity_name)

    def validate_frame_length(self, ctrl, var, name):
        from_ = var.get('from')
        to_ = var.get('to')
        # Probably a simple text input
        if from_ is None or to_ is None:
            raise InvalidOptionsException('Cannot get from or to for param frame_length')
        valid_values = [from_, from_ + 4, to_, to_ - 4]
        invalid_values = [from_ + 1, from_ + 5, to_ - 1, to_ - 5]
        for v in valid_values:
            ctrl.send_param(name, v)
            nms_res = ctrl.get_param(name)
            self.assertEqual(v, nms_res, msg=f'sent value={v} set value={nms_res}')
        for i in invalid_values:
            ctrl.send_param(name, i)
            nms_res = ctrl.get_param(name)
            self.assertNotEqual(i, nms_res, msg=f'sent value={i} set value={nms_res}')

    def validate_binding_section(self, ctrl, section, mode):
        for var in section.get('vars'):
            name = var.get('name')
            if name == 'binding':
                continue
            if name in self.checked_params:
                continue
            dep_var = var.get('dep_var')
            dep_value = var.get('dep_value')
            with self.subTest(f'controller {mode} section={section.get("section")} param={name}'):
                self.validate_next_param(ctrl, var, name, 'controller')

    def validate_alert_mode(self, obj, var, name, entity_name):
        set_alert_dict = self.get_dep_var_dict(entity_name, 'set_alert')
        if var.get('dep_var') is not None:
            dep_vars = self.prepare_dep_vars(entity_name, var)
            params = {}
            # Pick a random mode for each dep_var that is not exceed the number of options
            for key, value in dep_vars.items():
                params[key] = random.choice(value)
            obj.send_params(params)

        for option in var.get('select'):
            obj.send_param(name, option.get('val'))
            if option.get('val') == 2:
                self.assertNotEqual(option.get('txt'), obj.get_param(name))
            else:
                self.assertEqual(option.get('txt'), obj.get_param(name))

            obj.send_param(name, option.get('txt'))
            if option.get('val') == 2:
                self.assertNotEqual(option.get('txt'), obj.get_param(name))
            else:
                self.assertEqual(option.get('txt'), obj.get_param(name))

        # Validating set alert along with alert mode
        for option in set_alert_dict.get('select'):
            obj.send_params({name: 2, 'set_alert': option.get('val')})
            if option.get('val') == '':
                self.assertNotEqual('Specify', obj.get_param(name))
            else:
                self.assertEqual('Specify', obj.get_param(name))
                self.assertEqual(f"{option.get('val')} {option.get('txt')}", obj.get_param('set_alert'))

            obj.send_params({name: 2, 'set_alert': option.get('txt')})
            if option.get('val') == '':
                self.assertNotEqual('Specify', obj.get_param(name))
            else:
                self.assertEqual('Specify', obj.get_param(name))
                self.assertEqual(f"{option.get('val')} {option.get('txt')}", obj.get_param('set_alert'))

        obj.send_params({name: 2, 'set_alert': '#^!(^@(@'})
        self.assertNotEqual('#^!(^@(@', obj.get_param('set_alert'))

    def validate_next_param(self, obj, var, name, entity_name):
        if name in self.depending_params.keys():
            depending_param = True
        else:
            depending_param = False

        if var.get("nonzero") is None:
            nonzero = False
        else:
            nonzero = True

        if var.get('dep_var') is None:
            dep_var = False
        else:
            dep_var = True

        if dep_var:
            dep_vars = self.prepare_dep_vars(entity_name, var)
            params = {}
            # Pick a random mode for each dep_var that is not exceed the number of options
            for key, value in dep_vars.items():
                params[key] = random.choice(value)
            # if len(params.keys()) == 1:
            #obj.send_param(list(params.keys())[0], list(params.values())[0])
            # else:
            obj.send_params(params)

        # Checkbox
        if var.get("type") == 8:
            for value in self.checkbox_test_values:
                obj.send_param(name, value)
                nms_res = obj.get_param(name)
                if value in self.checkbox_test_values_on:
                    self.assertIn(nms_res, self.checkbox_response_on)
                else:
                    self.assertIn(nms_res, self.checkbox_response_off)

        # Text input
        elif var.get('type') == 10 or (var.get('type') == 0 and var.get('from') is None):
            if name in ('snmp_user', 'snmp_read', 'snmp_write', 'rip_pass'):
                for value in self.pass_test_values:
                    obj.send_param(name, value)
                    nms_res = obj.get_param(name)
                    self.assertEqual(value, nms_res, msg=f'sent value={value}, set value={nms_res}')
            else:
                for value in self.text_input_test_values:
                    obj.send_param(name, value)
                    nms_res = obj.get_param(name)
                    # Name or nonzero params cannot be empty
                    if (value == '' or value.count(' ') == len(value)) and (nonzero or name == 'name'):
                        self.assertNotEqual(value, nms_res, msg=f'sent value={value}, set value={nms_res}')
                    else:
                        # self.assertEqual(value.lstrip(), nms_res)
                        self.assertEqual(value.strip(), nms_res.strip(), msg=f'sent value={value}, set value={nms_res}')

        # Static dropdown
        elif var.get('type') == 9:
            for option in var.get('select'):
                if option.get('txt') in ('CALL_policy', 'GOTO_policy'):
                    continue
                # Checking sending digital value
                obj.send_param(name, option.get('val'))
                nms_res = obj.get_param(name)
                if nonzero and option.get('val') in ('', 0, '0'):
                    self.assertNotEqual(option.get('txt'), nms_res)
                else:
                    # Special case for Route to Hub - it should not applied to a controller route
                    if entity_name == 'route' and name == 'type' and option.get('txt') in ('Route_to_hub', 'IPv6_to_hub'):
                        self.assertNotEqual(option.get('txt'), nms_res)
                    else:
                        self.assertEqual(option.get('txt'), nms_res)

                # Testing sending text value
                obj.send_param(name, option.get('txt'))
                if nonzero and option.get('val') in ('', 0, '0'):
                    self.assertNotEqual(option.get('txt'), nms_res)
                else:
                    # Special case for Route to Hub - it should not applied to a controller route
                    if entity_name == 'route' and name == 'type' and option.get('txt') in ('Route_to_hub', 'IPv6_to_hub'):
                        self.assertNotEqual(option.get('txt'), nms_res)
                    else:
                        self.assertEqual(option.get('txt'), nms_res)
            obj.send_param(name, 'nousecryingoverspiltmilk')
            self.assertNotEqual('nousecryingoverspiltmilk', obj.get_param(name))

            # Passing to a selector value that is equaled to the number of options is currently acceptable
            with self.subTest('selector value equals to the number of options'):
                number_of_options = len(var.get('select'))
                obj.send_param(name, number_of_options)
                self.assertNotEqual(number_of_options, obj.get_param(name))
            if name == 'mode':
                obj.send_param(name, number_of_options - 1)

        # Dynamic dropdown (i.e. file_name in alert)
        elif var.get('type') in (32, 14):
            for option in var.get('select'):
                # Checking sending digital value
                obj.send_param(name, option.get('val'))
                nms_res = obj.get_param(name)
                if nonzero and option.get('val') == '':
                    self.assertNotEqual(
                        option.get('val'),
                        nms_res,
                        msg=f'sent value={option.get("val")}, set value={nms_res}'
                    )
                else:
                    self.assertTrue(
                        option.get('val') == nms_res or f"{option.get('val')} {option.get('txt')}" == nms_res,
                        msg=f'sent value={option.get("val")}, set value={nms_res}'
                    )

                # Testing sending text value
                obj.send_param(name, option.get('txt'))
                nms_res = obj.get_param(name)
                if nonzero and option.get('val') == '':
                    self.assertNotEqual(
                        option.get('val'),
                        nms_res,
                        f'sent value={option.get("txt")}, set value={nms_res}'
                    )
                else:
                    self.assertTrue(
                        option.get('val') == nms_res or f"{option.get('val')} {option.get('txt')}" == nms_res,
                        msg=f'sent value={option.get("txt")}, set value={nms_res}'
                    )

            # TODO: probably not needed
            obj.send_param(name, 'nousecryingoverspiltmilk')
            self.assertNotEqual('nousecryingoverspiltmilk', obj.get_param(name))

            number_of_options = len(var.get('select'))
            obj.send_param(name, number_of_options)
            self.assertNotEqual(number_of_options, obj.get_param(name))

        # Text input for numbers with `from` and `to` parameters
        elif var.get('type') in (0, 3, 4):
            if depending_param:
                self.validate_depending_params(var, obj)
            else:
                from_ = var.get('from')
                to_ = var.get('to')
                # Probably a simple text input
                if from_ is None or to_ is None:
                    raise InvalidOptionsException('Cannot get from or to for param type 0')
                valid = [
                    from_, to_, from_ + 1, to_ - 1, (from_ + to_) // 2,
                    str(from_), str(to_), str(from_ + 1), str(to_ - 1), str((from_ + to_) // 2)
                ]
                # TODO: remove when NMS stops accepting negative values as absolute
                if from_ == 0:
                    invalid = [to_ + 1, 'qwerty', str(to_ + 1)]
                else:
                    invalid = [from_ - 1, to_ + 1, 'qwerty', str(from_ - 1), str(to_ + 1)]
                # print(obj.get_param('mode3'))
                for v in valid:
                    obj.send_param(name, v)
                    nms_res = obj.get_param(name)
                    self.assertEqual(str(v), str(nms_res), msg=f'test_value={v}({type(v)}) nms_value={nms_res}({type(nms_res)})')
                for i in invalid:
                    obj.send_param(name, i)
                    nms_res = obj.get_param(name)
                    self.assertNotEqual(str(i), str(nms_res),
                                        msg=f'test_value={i}({type(i)}) nms_value={nms_res}({type(nms_res)})')

        # Input IP field
        elif var.get('type') == 16:
            for i in IP_TEST_VALUES:
                obj.send_param(name, i)
                if i in ValidIpAddr():
                    self.assertFalse(obj.has_param_error(name))
                else:
                    self.assertTrue(obj.has_param_error(name))

        # Input IPv6 field
        elif var.get('type') == 18:
            for i in IPV6_TEST_VALUES:
                obj.send_param(name, i)
                if i in ValidIpv6Addr():
                    self.assertFalse(obj.has_param_error(name), msg=f'test ipv6 address={i}')
                else:
                    self.assertTrue(obj.has_param_error(name), msg=f'test ipv6 address={i}')

        # Input MASK field
        elif var.get('type') == 17:
            for i in IP_MASK_TEST_VALUES:
                obj.send_param(name, i)
                if i in ValidIpMask():
                    self.assertFalse(obj.has_param_error(name))
                else:
                    self.assertTrue(obj.has_param_error(name))

        # Input IPv6 prefix field
        elif var.get('type') == 19:
            for i in IPV6_PREFIX_TEST_VALUES:
                obj.send_param(name, i)
                if i in ValidIpv6Mask():
                    self.assertFalse(obj.has_param_error(name), msg=f'test ipv6 prefix={i}')
                else:
                    self.assertTrue(obj.has_param_error(name), msg=f'test ipv6 prefix={i}')

        # Input float field
        elif var.get('type') == 1:
            from_ = var.get('from')
            to_ = var.get('to')
            if from_ is None or to_ is None:
                raise Exception('Cannot get from or to for param type 1')
            if depending_param:
                self.validate_depending_params(var, obj)
            else:
                valid = [from_, to_, (from_ + to_) / 2 + 0.7, from_ + 0.1, to_ - 0.1]
                # TODO: remove when NMS stops accepting negative values as absolute
                if from_ == 0:
                    invalid = ['qwerty', to_ + 0.1]
                else:
                    invalid = ['qwerty', from_ - 1.1, to_ + 0.1]
                for v in valid:
                    obj.send_param(name, v)
                    self.assertFalse(obj.has_param_error(name), msg=f'valid value={v}')
                for i in invalid:
                    obj.send_param(name, i)
                    self.assertTrue(obj.has_param_error(name), msg=f'invalid value={i}')

        # Tdma modcodes
        elif var.get('type') == 27:
            for m in self.tdma_mc:
                # TODO: probably not needed to set TDMA modcodes via text
                # obj.send_param(name, m.get('name'))
                # nms_res = obj.get_param(name)
                # self.assertEqual(m.get('name'), nms_res, msg=f'sent value={m.get("name")}, set value={nms_res}')
                obj.send_param(name, m.get('value'))
                nms_res = obj.get_param(name)
                self.assertEqual(m.get('name'), obj.get_param(name), msg=f'sent value={m.get("value")}, set value={nms_res}')

            # TODO: uncomment when fixed
            # Testing non-valid value
            # obj.send_param(name, len(self.tdma_mc))
            # self.assertTrue(obj.has_param_error(name), msg=f'sent value={len(self.tdma_mc)} is applied')

        else:
            self.fail(f'Type {var.get("type")} is not tested yet')

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
            time.sleep(1)
            nms_res_name = obj.get_param(name)
            nms_res_dep_name = obj.get_param(dep_name)

            self.assertEqual(name_val, nms_res_name, msg=f'{name}={name_val}, {dep_name}={dep_name_val}')
            self.assertEqual(dep_name_val, nms_res_dep_name, msg=f'{name}={name_val}, {dep_name}={dep_name_val}')

        for i in invalid_combinations:
            if lower == name:
                name_val = i[0]
                dep_name_val = i[1]
                obj.send_params({name: name_val, dep_name: dep_name_val})
            else:
                name_val = i[0]
                dep_name_val = i[1]
                obj.send_params({name: name_val, dep_name: dep_name_val})
            nms_res_name = obj.get_param(name)
            nms_res_dep_name = obj.get_param(dep_name)
            self.assertFalse(name_val == nms_res_name and dep_name_val == nms_res_dep_name,
                             msg=f'sent {name}={name_val}, sent {dep_name}={dep_name_val},'
                                 f' set {name}={nms_res_name}, set {dep_name}={nms_res_dep_name}')

    def prepare_dep_vars(self, entity_name, var, dep_vars=None):
        if dep_vars is None:
            dep_vars = {}
        dep_var = var.get('dep_var')
        dep_var_dict = self.get_dep_var_dict(entity_name, dep_var)

        dep_vars[dep_var] = []

        # Getting bit-mask out of `dep_value` - first value first
        dep_value = var.get('dep_value')
        dep_value_bin = bin(dep_value)[2:][::-1]

        # Dropdown
        if dep_var_dict.get('select') is not None:
            number_of_options = len(dep_var_dict.get('select'))
            # Getting all the supported modes (but looking at the size of the options)
            for i in range(len(dep_value_bin)):
                if i == number_of_options:
                    break
                if dep_value_bin[i] == '1':
                    dep_vars[dep_var].append(i)

        # Checkbox
        else:
            dep_vars[dep_var].append(1)

        if dep_var_dict.get('dep_var') is not None:
            self.prepare_dep_vars(entity_name, dep_var_dict, dep_vars=dep_vars)
        return dep_vars

    def get_dep_var_dict(self, entity_name, dep_var_name):
        meta = self.meta.get(entity_name)
        for section in meta:
            for var in section.get('vars'):
                if var.get('name') == dep_var_name:
                    return var
        return None

    def test_access(self):
        pass

    def test_alert(self):
        alert = Alert(self.driver, 0, 0)
        self.validate_entity(alert, 'alert')

    def test_bal_controller(self):
        bal_ctrl = BalController(self.driver, 0, 0)
        self.validate_entity(bal_ctrl, 'bal_controller')

    def test_camera(self):
        cam = Camera(self.driver, 0, 0)
        self.validate_entity(cam, 'camera')

    # Special validation for Controller as the mode cannot be changed after creation
    def test_controller(self):
        ctrl_meta = self.meta.get('controller')
        for section in ctrl_meta:
            if section.get('section') == 'Basic settings':
                for var in section.get('vars'):
                    if var.get('name') == 'mode':
                        nonzero = var.get('nonzero')
                        modes = var.get('select')
                        break
                else:
                    raise InvalidOptionsException('Cannot get controller modes from meta')

        with self.subTest('Controller mode is nonzero'):
            self.assertTrue(nonzero)

        for mode in modes:
            ctrl = Controller(self.driver, 0, NEW_OBJECT_ID, {
                'name': f'ctrl-{mode.get("txt")}',
                'mode': mode.get('val'),
                'teleport': f'teleport:0',
            })
            ctrl_mode = mode.get('txt')
            # Check that mode None is not applied
            if mode.get('val') == 0:
                self.assertRaises(ObjectNotCreatedException, ctrl.save)
                continue
            # Additional params for specific controller
            elif ctrl_mode in ('Inroute', 'DAMA_inroute', 'Gateway'):
                # Check that required params are indeed required
                self.assertRaises(ObjectNotCreatedException, ctrl.save)
                if mode.get('txt') == 'Inroute':
                    ctrl.set_params({
                        'name': f'ctrl-{mode.get("txt")}',
                        'mode': mode.get('val'),
                        'teleport': f'teleport:0',
                    })
                    self.assertRaises(ObjectNotCreatedException, ctrl.save)
                    ctrl.set_param('inroute', 250)
                ctrl.set_params({
                    'name': f'ctrl-{mode.get("txt")}',
                    'mode': mode.get('val'),
                    'teleport': f'teleport:0',
                    'tx_controller': f'controller:0',
                })
                ctrl.save()
                self.assertIsNotNone(ctrl.get_id(), msg=f'controller mode {mode.get("txt")} created')
            else:
                ctrl.save()
                self.assertIsNotNone(ctrl.get_id(), msg=f'controller mode {mode.get("txt")} created')

            # Proceeding to parameters validation
            for section in ctrl_meta:
                section_name = section.get('section')
                if section_name is None:
                    section_name = section.get('table')
                    if section_name is None:
                        self.fail('!!!Cannot get neither section name nor table name!!!')
                # Special case for binding mode as it depends on SR controller in smart mode
                if section_name.find('binding') != -1:
                    self.validate_binding_section(ctrl, section, ctrl_mode)
                    continue
                if section_name is None:
                    section_name = section.get('table')
                    if section_name is None:
                        self.fail('!!!Cannot get neither section name nor table name!!!')
                for var in section.get('vars'):
                    name = var.get('name')
                    dep_var = var.get('dep_var')
                    dep_value = var.get('dep_value')
                    # Do not test controller mode, name, tx_modcod and depending params
                    if name in ('mode', 'name', 'tx_modcod') or name in self.checked_params:
                        continue
                    # Special case for alert mode and set alert as they depend on each over
                    elif name == 'alert_mode':
                        with self.subTest(f'controller {ctrl_mode} section={section_name} param={name}'):
                            self.validate_alert_mode(ctrl, var, name, 'controller')
                        continue
                    # Set alert is checked along with alert mode
                    elif name == 'set_alert':
                        continue
                    elif name.startswith('mod_que'):
                        # TODO: add test method for modulator queues
                        pass
                    elif name == 'frame_length':
                        with self.subTest(f'controller {ctrl_mode} section={section_name} param={name}'):
                            self.validate_frame_length(ctrl, var, name)
                        continue
                    elif name == 'acm_enable':
                        continue
                    elif name.startswith('acm_mc'):
                        continue

                    if dep_var == 'mode':
                        dep_value_bin = bin(dep_value)[2:][::-1]
                        # Do not check incompatible controller mode
                        if dep_value_bin[mode.get('val')] == '0':
                            continue
                    with self.subTest(f'controller {ctrl_mode} section={section_name} param={var.get("name")}'):
                        self.validate_next_param(ctrl, var, name, 'controller')

    def test_dashboard(self):
        dash = Dashboard(self.driver, 0, 0)
        self.validate_entity(dash, 'dashboard')

    def test_device(self):
        dev = Device(self.driver, 0, 0)
        self.validate_entity(dev, 'device')

    def test_group(self):
        pass

    def test_network(self):
        net = Network(self.driver, 0, 0)
        self.validate_entity(net, 'network')

    def test_nms(self):
        nms = Nms(self.driver, 0, 0)
        self.validate_entity(nms, 'nms')

    def test_policy(self):
        pol = Policy(self.driver, 0, 0)
        self.validate_entity(pol, 'policy')

    def test_rule(self):
        rule = PolicyRule(self.driver, 0, 0)
        self.validate_entity(rule, 'polrule')

    def test_port_map(self):
        port_map = ControllerPortMap(self.driver, 0, 0)
        self.validate_entity(port_map, 'port_map')

    def test_profile_set(self):
        pro = Profile(self.driver, 0, 0)
        self.validate_entity(pro, 'profile_set')

    def test_rip_router(self):
        rip = ControllerRip(self.driver, 0, 0)
        self.validate_entity(rip, 'rip_router')

    def test_route(self):
        route = ControllerRoute(self.driver, 0, 0)
        self.validate_entity(route, 'route')

    def test_server(self):
        ser = Server(self.driver, 0, 0)
        self.validate_entity(ser, 'server')

    def test_service(self):
        service = Service(self.driver, 0, 0)
        self.validate_entity(service, 'service')

    def test_shaper(self):
        shaper = Shaper(self.driver, 0, 0)
        self.validate_entity(shaper, 'shaper')

    def test_sr_controller(self):
        sr_ctrl = SrController(self.driver, 0, 0)
        self.validate_entity(sr_ctrl, 'sr_controller')

    def test_sr_license(self):
        sr_lic = SrLicense(self.driver, 0, 0)
        self.validate_entity(sr_lic, 'sr_license')

    def test_sr_teleport(self):
        sr_tp = SrTeleport(self.driver, 0, 0)
        self.validate_entity(sr_tp, 'sr_teleport')

    # TODO: validate station separately
    def test_station(self):
        stn = Station(self.driver, 0, 0)
        self.validate_entity(stn, 'station')

    def test_sw_upload(self):
        sw = SwUpload(self.driver, 0, 0)
        self.validate_entity(sw, 'sw_upload')

    def test_teleport(self):
        tp = Teleport(self.driver, 0, 0)
        self.validate_entity(tp, 'teleport')

    def test_user(self):
        pass

    def test_vno(self):
        vno = Vno(self.driver, 0, 0)
        self.validate_entity(vno, 'vno')

