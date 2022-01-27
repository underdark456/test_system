import json
import os
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

from global_options.options import PROJECT_DIR
from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import AlertModes, BindingModes, RuleTypes, ActionTypes
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
from src.nms_entities.basic_entities.qos import Qos
from src.nms_entities.basic_entities.scheduler import Scheduler
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

options_path = 'test_scenarios.web.web_data_types'
backup_name = 'case_dropdowns.txt'


class WebDynamicDropdownsCase(CustomTestCase):
    """WEB check items in dynamic dropdowns case. The number of items are maximum"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.20'
    __execution_time__ = 850  # test case approximate execution time is seconds
    __express__ = False

    @classmethod
    def set_up_class(cls):
        cls.start_time = time.perf_counter()
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(options_path), driver_id='case_web_dynamic_dropdowns'
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)

        cls.nms = Nms(cls.driver, 0, 0)
        cls.nms_version = cls.nms.get_version().replace('.', '_')
        cls.class_logger.info(f'NMS version {cls.nms_version}')

        with open(f'{PROJECT_DIR}{os.sep}utilities{os.sep}get_meta{os.sep}meta_{cls.nms_version}.txt', 'r') as file:
            cls.meta = json.load(file)

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
            'scheduler': Scheduler,
            'sch_task': SchTask,
            'shaper': Shaper,
            'sr_controller': SrController,
            'sr_license': SrLicense,
            'sr_teleport': SrTeleport,
            'station': Station,
            'sw_upload': SwUpload,
            'teleport': Teleport,
            'user': User,
            'vno': Vno,
        }
    
    def test_dynamic_dropdowns(self):
        """Test all type 14 fields in WEB"""
        # Controller ID 0 (MF Hub) is used to check teleport dropdown
        # Controller ID 508 (Inroute) is used to check tx_controller dropdown
        # Controller ID 509 (Hubless Master) is used to check shaper
        # Controller ID 250 is used to check sr_controller dropdowns
        # Station ID 1 is used to check tx_controller
        # Rule ID 0 is used to check shaper
        # Rule ID 1 is used to check policy
        for entity in self.meta.keys():
            for section_json in self.meta.get(entity):
                for var in section_json.get('vars'):
                    if var.get('type') == 14:
                        name = var.get('name')

                        with self.subTest(f'entity={entity} field={name}'):
                            if name == 'group':
                                # Second access is used for tests
                                obj = Access(self.driver, 0, 1)
                                obj.load()
                                # Checking that all the options are in the selector
                                var_elem = self.driver._get_element_by(By.ID, name)
                                selector_options = var_elem.find_elements_by_tag_name("option")
                                options = set()
                                for o in selector_options:
                                    options.add(o.get_attribute('value'))
                                for i in range(512):
                                    self.assertIn(
                                        f'group:{str(i)}',
                                        options,
                                        msg=f'group:{str(i)} in selector options'
                                    )
                                for option in ('group:511', 'group:250'):
                                    obj.send_param(name, option)
                                    var_elem = self.driver._get_element_by(By.ID, name)
                                    selected_option = Select(var_elem).first_selected_option.get_attribute('value')
                                    self.assertEqual(
                                        option,
                                        selected_option,
                                        msg=f'Clicked option={option}, set option={selected_option}'
                                    )
                            elif name == 'set_alert':
                                obj = self.entity_name_to_class.get(entity)(self.driver, 0, 0)
                                obj.load()
                                for option in ('alert:2047', 'alert:1000'):
                                    obj.send_params({'alert_mode': AlertModes.SPECIFY, name: option})
                                    var_elem = self.driver._get_element_by(By.ID, name)
                                    selected_option = Select(var_elem).first_selected_option.get_attribute('value')
                                    self.assertEqual(
                                        option,
                                        selected_option,
                                        msg=f'Clicked option={option}, set option={selected_option}'
                                    )
                                # Checking that all the options are in the selector
                                var_elem = self.driver._get_element_by(By.ID, name)
                                selector_options = var_elem.find_elements_by_tag_name("option")
                                options = set()
                                for o in selector_options:
                                    options.add(o.get_attribute('value'))
                                for i in range(2048):
                                    self.assertIn(
                                        f'alert:{str(i)}',
                                        options,
                                        msg=f'alert:{str(i)} in selector options'
                                    )
                            elif name == 'sr_controller':
                                obj = Controller(self.driver, 0, 250)
                                obj.load()
                                for option in ('sr_controller:0', 'sr_controller:15', 'sr_controller:31'):
                                    obj.send_params(
                                        {'binding': BindingModes.SMART, 'sr_controller': option})
                                    var_elem = self.driver._get_element_by(By.ID, name)
                                    selected_option = Select(var_elem).first_selected_option.get_attribute('value')
                                    self.assertEqual(
                                        option,
                                        selected_option,
                                        msg=f'Clicked option={option}, set option={selected_option}'
                                    )
                                # Checking that all the options are in the selector
                                var_elem = self.driver._get_element_by(By.ID, name)
                                selector_options = var_elem.find_elements_by_tag_name("option")
                                options = set()
                                for o in selector_options:
                                    options.add(o.get_attribute('value'))
                                for i in range(32):
                                    self.assertIn(
                                        f'sr_controller:{str(i)}',
                                        options,
                                        msg=f'sr_controller:{str(i)} in selector options'
                                    )
                            elif name == 'tx_controller':
                                if entity == 'controller':
                                    obj = Controller(self.driver, 0, 508)
                                elif entity == 'station':
                                    obj = Station(self.driver, 0, 1)
                                else:
                                    obj = self.entity_name_to_class.get(entity)(self.driver, 0, 0)
                                obj.load()
                                # Except for controller itself
                                for option in ('controller:1', 'controller:250', 'controller:500'):
                                    obj.send_param('tx_controller', option)
                                    var_elem = self.driver._get_element_by(By.ID, name)
                                    selected_option = Select(var_elem).first_selected_option.get_attribute('value')
                                    self.assertEqual(
                                        option,
                                        selected_option,
                                        msg=f'Clicked option={option}, set option={selected_option}'
                                    )
                                # Checking that all the options are in the selector
                                var_elem = self.driver._get_element_by(By.ID, name)
                                selector_options = var_elem.find_elements_by_tag_name("option")
                                options = set()
                                for o in selector_options:
                                    options.add(o.get_attribute('value'))
                                for i in range(512):
                                    self.assertIn(
                                        f'controller:{str(i)}',
                                        options,
                                        msg=f'controller:{str(i)} in selector options'
                                    )
                            elif name == 'rx_controller':
                                obj = self.entity_name_to_class.get(entity)(self.driver, 0, 0)
                                obj.load()
                                # Except for controller itself
                                for option in ('controller:1', 'controller:250', 'controller:500'):
                                    obj.send_param('rx_controller', option)
                                    var_elem = self.driver._get_element_by(By.ID, name)
                                    selected_option = Select(var_elem).first_selected_option.get_attribute('value')
                                    self.assertEqual(
                                        option,
                                        selected_option,
                                        msg=f'Clicked option={option}, set option={selected_option}'
                                    )
                                # Checking that all the options are in the selector
                                var_elem = self.driver._get_element_by(By.ID, name)
                                selector_options = var_elem.find_elements_by_tag_name("option")
                                options = set()
                                for o in selector_options:
                                    options.add(o.get_attribute('value'))
                                for i in range(512):
                                    self.assertIn(
                                        f'controller:{str(i)}',
                                        options,
                                        msg=f'controller:{str(i)} in selector options'
                                    )
                            elif name == 'teleport':
                                # Teleport is used in Controller and SrTeleport
                                if entity == 'controller':
                                    obj = Controller(self.driver, 0, 0)
                                elif entity == 'sr_teleport':
                                    obj = SrTeleport(self.driver, 0, 0)
                                else:
                                    raise InvalidOptionsException(f'{entity} is not tested yet')
                                obj.load()
                                # Except for controller itself
                                for option in ('teleport:1', 'teleport:50', 'teleport:127'):
                                    obj.send_param('teleport', option)
                                    var_elem = self.driver._get_element_by(By.ID, name)
                                    selected_option = Select(var_elem).first_selected_option.get_attribute('value')
                                    self.assertEqual(
                                        option,
                                        selected_option,
                                        msg=f'Clicked option={option}, set option={selected_option}'
                                    )
                                # Checking that all the options are in the selector
                                var_elem = self.driver._get_element_by(By.ID, name)
                                selector_options = var_elem.find_elements_by_tag_name("option")
                                options = set()
                                for o in selector_options:
                                    options.add(o.get_attribute('value'))
                                for i in range(32):
                                    self.assertIn(
                                        f'teleport:{str(i)}',
                                        options,
                                        msg=f'teleport:{str(i)} in selector options'
                                    )

                            elif name in ('hub_shaper', 'stn_shaper', 'shaper'):
                                if entity == 'controller' and name == 'hub_shaper' and var.get('dep_value') == 16:
                                    # Hubless Master
                                    obj = Controller(self.driver, 0, 509)
                                else:
                                    obj = self.entity_name_to_class.get(entity)(self.driver, 0, 0)
                                obj.load()
                                for option in ('shaper:0', 'shaper:1000', 'shaper:2047'):
                                    if entity == 'polrule':
                                        obj.send_params({
                                            'type': RuleTypes.ACTION,
                                            'action_type': ActionTypes.SET_TS_CH,
                                            'shaper': option,
                                        })
                                    else:
                                        obj.send_param(name, option)
                                    var_elem = self.driver._get_element_by(By.ID, name)
                                    selected_option = Select(var_elem).first_selected_option.get_attribute('value')
                                    self.assertEqual(
                                        option,
                                        selected_option,
                                        msg=f'Clicked option={option}, set option={selected_option}'
                                    )
                                # Checking that all the options are in the selector
                                var_elem = self.driver._get_element_by(By.ID, name)
                                selector_options = var_elem.find_elements_by_tag_name("option")
                                options = set()
                                for o in selector_options:
                                    options.add(o.get_attribute('value'))
                                for i in range(2048):
                                    self.assertIn(
                                        f'shaper:{str(i)}',
                                        options,
                                        msg=f'shaper:{str(i)} in selector options'
                                    )
                            elif name == 'profile_set':
                                obj = self.entity_name_to_class.get(entity)(self.driver, 0, 0)
                                obj.load()
                                for option in ('profile_set:0', 'profile_set:63', 'profile_set:127'):
                                    obj.send_param(name, option)
                                    var_elem = self.driver._get_element_by(By.ID, name)
                                    selected_option = Select(var_elem).first_selected_option.get_attribute('value')
                                    self.assertEqual(
                                        option,
                                        selected_option,
                                        msg=f'Clicked option={option}, set option={selected_option}'
                                    )
                                # Checking that all the options are in the selector
                                var_elem = self.driver._get_element_by(By.ID, name)
                                selector_options = var_elem.find_elements_by_tag_name("option")
                                options = set()
                                for o in selector_options:
                                    options.add(o.get_attribute('value'))
                                for i in range(128):
                                    self.assertIn(
                                        f'profile_set:{str(i)}',
                                        options,
                                        msg=f'profile_set:{str(i)} in selector options'
                                    )
                            elif name in ('hub_policy', 'stn_policy', 'policy'):
                                if name == 'policy':
                                    obj = PolicyRule(self.driver, 0, 1)
                                else:
                                    obj = self.entity_name_to_class.get(entity)(self.driver, 0, 0)
                                obj.load()
                                for option in ('policy:2', 'policy:250', 'policy:511'):
                                    obj.send_param(name, option)
                                    var_elem = self.driver._get_element_by(By.ID, name)
                                    selected_option = Select(var_elem).first_selected_option.get_attribute('value')
                                    self.assertEqual(
                                        option,
                                        selected_option,
                                        msg=f'Clicked option={option}, set option={selected_option}'
                                    )
                                # Checking that all the options are in the selector
                                var_elem = self.driver._get_element_by(By.ID, name)
                                selector_options = var_elem.find_elements_by_tag_name("option")
                                options = set()
                                for o in selector_options:
                                    options.add(o.get_attribute('value'))
                                for i in range(512):
                                    self.assertIn(
                                        f'policy:{str(i)}',
                                        options,
                                        msg=f'policy:{str(i)} in selector options'
                                    )
                            elif name == 'service':
                                obj = self.entity_name_to_class.get(entity)(self.driver, 0, 0)
                                obj.load()
                                for option in ('service:0', 'service:250', 'service:511'):
                                    obj.send_param(name, option)
                                    var_elem = self.driver._get_element_by(By.ID, name)
                                    selected_option = Select(var_elem).first_selected_option.get_attribute('value')
                                    self.assertEqual(
                                        option,
                                        selected_option,
                                        msg=f'Clicked option={option}, set option={selected_option}'
                                    )
                                # Checking that all the options are in the selector
                                var_elem = self.driver._get_element_by(By.ID, name)
                                selector_options = var_elem.find_elements_by_tag_name("option")
                                options = set()
                                for o in selector_options:
                                    options.add(o.get_attribute('value'))
                                for i in range(512):
                                    self.assertIn(
                                        f'service:{str(i)}',
                                        options,
                                        msg=f'service:{str(i)} in selector options'
                                    )
                            elif name == 'bal_controller':
                                obj = self.entity_name_to_class.get(entity)(self.driver, 0, 0)
                                obj.load()
                                for option in ('bal_controller:0', 'bal_controller:15', 'bal_controller:31'):
                                    obj.send_params({'bal_enable': 1, name: option})
                                    var_elem = self.driver._get_element_by(By.ID, name)
                                    selected_option = Select(var_elem).first_selected_option.get_attribute('value')
                                    self.assertEqual(
                                        option,
                                        selected_option,
                                        msg=f'Clicked option={option}, set option={selected_option}'
                                    )
                                # Checking that all the options are in the selector
                                var_elem = self.driver._get_element_by(By.ID, name)
                                selector_options = var_elem.find_elements_by_tag_name("option")
                                options = set()
                                for o in selector_options:
                                    options.add(o.get_attribute('value'))
                                for i in range(32):
                                    self.assertIn(
                                        f'bal_controller:{str(i)}',
                                        options,
                                        msg=f'bal_controller:{str(i)} in selector options'
                                    )
                            elif name == 'scheduler':
                                obj = self.entity_name_to_class.get(entity)(self.driver, 0, 0)
                                obj.load()
                                for option in ('scheduler:0', 'scheduler:31', 'scheduler:63'):
                                    obj.send_param(name, option)
                                    var_elem = self.driver._get_element_by(By.ID, name)
                                    selected_option = Select(var_elem).first_selected_option.get_attribute('value')
                                    self.assertEqual(
                                        option,
                                        selected_option,
                                        msg=f'Clicked option={option}, set option={selected_option}'
                                    )
                                # Checking that all the options are in the selector
                                var_elem = self.driver._get_element_by(By.ID, name)
                                selector_options = var_elem.find_elements_by_tag_name("option")
                                options = set()
                                for o in selector_options:
                                    options.add(o.get_attribute('value'))
                                for i in range(64):
                                    self.assertIn(
                                        f'scheduler:{str(i)}',
                                        options,
                                        msg=f'scheduler:{str(i)} in selector options'
                                    )
                            elif name in ('forward_qos', 'return_qos'):
                                obj = self.entity_name_to_class.get(entity)(self.driver, 0, 0)
                                obj.load()
                                for option in ('qos:0', 'qos:31', 'qos:63'):
                                    obj.send_param(name, option)
                                    var_elem = self.driver._get_element_by(By.ID, name)
                                    selected_option = Select(var_elem).first_selected_option.get_attribute('value')
                                    self.assertEqual(
                                        option,
                                        selected_option,
                                        msg=f'Clicked option={option}, set option={selected_option}'
                                    )
                                # Checking that all the options are in the selector
                                var_elem = self.driver._get_element_by(By.ID, name)
                                selector_options = var_elem.find_elements_by_tag_name("option")
                                options = set()
                                for o in selector_options:
                                    options.add(o.get_attribute('value'))
                                for i in range(1024):
                                    self.assertIn(
                                        f'qos:{str(i)}',
                                        options,
                                        msg=f'qos:{str(i)} in selector options'
                                    )
                            elif name == 'ext_gateway':
                                obj = self.entity_name_to_class.get(entity)(self.driver, 0, 0)
                                obj.load()
                                for option in ('controller:0', 'controller:255', 'controller:511'):
                                    obj.send_param(name, option)
                                    var_elem = self.driver._get_element_by(By.ID, name)
                                    selected_option = Select(var_elem).first_selected_option.get_attribute('value')
                                    self.assertEqual(
                                        option,
                                        selected_option,
                                        msg=f'Clicked option={option}, set option={selected_option}'
                                    )
                                # Checking that all the options are in the selector
                                var_elem = self.driver._get_element_by(By.ID, name)
                                selector_options = var_elem.find_elements_by_tag_name("option")
                                options = set()
                                for o in selector_options:
                                    options.add(o.get_attribute('value'))
                                for i in range(512):
                                    self.assertIn(
                                        f'controller:{str(i)}',
                                        options,
                                        msg=f'controller:{str(i)} in selector options'
                                    )
                            elif name == 'sch_service':
                                obj = self.entity_name_to_class.get(entity)(self.driver, 0, 0)
                                obj.load()
                                for option in ('sch_service:0', 'sch_service:63', 'sch_service:127'):
                                    obj.send_param(name, option)
                                    var_elem = self.driver._get_element_by(By.ID, name)
                                    selected_option = Select(var_elem).first_selected_option.get_attribute('value')
                                    self.assertEqual(
                                        option,
                                        selected_option,
                                        msg=f'Clicked option={option}, set option={selected_option}'
                                    )
                                # Checking that all the options are in the selector
                                var_elem = self.driver._get_element_by(By.ID, name)
                                selector_options = var_elem.find_elements_by_tag_name("option")
                                options = set()
                                for o in selector_options:
                                    options.add(o.get_attribute('value'))
                                for i in range(128):
                                    self.assertIn(
                                        f'sch_service:{str(i)}',
                                        options,
                                        msg=f'controller:{str(i)} in selector options'
                                    )
                            else:
                                self.fail(f'{name} is not tested yet')
