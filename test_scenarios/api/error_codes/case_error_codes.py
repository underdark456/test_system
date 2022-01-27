from src.backup_manager.backup_manager import BackupManager
from src.constants import *
from src.enum_types_constants import CheckTypes, RuleTypes, ControllerModes, ModelTypes
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.policy import Policy
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.paths_manager import PathsManager
from test_scenarios.api.abstract_case import _AbstractCase
from src.drivers.drivers_provider import DriversProvider
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.api.error_codes'
backup_name = 'default_config.txt'


class ApiErrorCodesCase(_AbstractCase):
    """NMS API expected error codes case, except for -4, -6, -7, -10, -11 error codes"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.26'
    __execution_time__ = 85  # approximate test case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(options_path)
        )
        cls.backup = BackupManager()
        cls.options = OptionsProvider.get_options(options_path)

    def set_up(self) -> None:
        self.backup.apply_backup(backup_name)

    def test_1_no_such_table(self):
        """Test error_code `-1` No such table (aka `wrong table name`)"""
        for name in self.options.get('invalid_tables'):
            for path in self.options.get('get_paths'):
                path = path.format(name, 0)
                _, _, error_code = self.driver.custom_get(path)
                self.assertEqual(NO_SUCH_TABLE, error_code, msg=path)
        for name in self.options.get('invalid_tables'):
            for path in self.options.get('post_paths'):
                path = path.format(name, 0)
                _, _, error_code = self.driver.custom_post(path, payload={'name': 'test'})
                self.assertEqual(NO_SUCH_TABLE, error_code, msg=path)

    def test_2_no_such_row(self):
        """Test error_code `-2` No such row (aka `too high row number for current table`)"""
        table_rows = self.options.get('invalid_rows', None)
        for row in table_rows:
            for path in self.options.get('get_paths'):
                path = path.format('network', row)
                _, _, error_code = self.driver.custom_get(path)
                self.assertEqual(NO_SUCH_ROW, error_code, msg=f'Getting data from network ID {row}')
        for row in table_rows:
            for path in self.options.get('post_paths'):
                path = path.format('network', row)
                _, _, error_code = self.driver.custom_post(path, payload={'name': 'none'})
                self.assertEqual(NO_SUCH_ROW, error_code, msg=f'Write data to a network ID {row}')

    def test_3_no_such_variable(self):
        """Test error_code `-3` No such variable (aka `wrong variable name`)"""
        Network.create(self.driver, 0, {'name': 'test_net'})
        for var in ('nonexistingvar', 'qwerty', 65534):
            path = f'api/object/write/network=0'
            _, _, error_code = self.driver.custom_post(path, payload={var: 'none'})
            self.assertEqual(NO_SUCH_VARIABLE, error_code, msg=f'{path} var={var}')

    def test_5_bad_value(self):
        """Test error_code `-5` Bad value (aka `wrong variable value`)"""
        Network.create(self.driver, 0, params={'name': 'none'})
        path = f'api/object/write/network=0'
        for name in (None, ' ', ''):
            _, _, error_code = self.driver.custom_post(path, payload={'name': name})
            self.assertEqual(WRONG_VARIABLE_VALUE, error_code, msg=f'{path} name={name}')
        for traffic_scale in (-1, 5000001, 'traffic_scale'):
            _, _, error_code = self.driver.custom_post(path, payload={'traffic_scale': traffic_scale})
            self.assertEqual(WRONG_VARIABLE_VALUE, error_code, msg=f'{path} traffic_scale={traffic_scale}')

    def test_8_table_full(self):
        """Test error_code `-8` Table full (aka `no space in table`)"""
        for i in range(200):
            path = 'api/form/write/nms=0/new_item=network'
            _, _, error_code = self.driver.custom_post(path, payload={'name': f'net-{i}'})
            if error_code != 0:
                self.assertEqual(TABLE_FULL, error_code)
                break

    def test_9_no_hierarchy(self):
        """Test error_code `-9` No hierarchy (aka `hierarchical conditions are not met in request or storage`)"""
        net = Network.create(self.driver, 0, {'name': 'net-0'})
        Teleport.create(self.driver, net.get_id(), {'name': 'test_tp', 'sat_name': 'test_sat'})
        path = 'api/form/write/nms=0/new_item=controller'
        _, _, error_code = self.driver.custom_post(
            path,
            payload={'name': 'test_ctrl', 'teleport': 'teleport:0', 'mode': ControllerModes.MF_HUB})
        self.assertEqual(NO_HIERARCHY, error_code, msg=path)

        path = 'api/form/write/nms=0/new_item=vno'
        _, _, error_code = self.driver.custom_post(path, payload={'name': 'vno-0'})
        self.assertEqual(NO_HIERARCHY, error_code, msg=path)

    def test_12_object_exists(self):
        """Test error_code `-12` Object exists (aka `object with the same name / ID exists`)"""
        # Issues the following queries:
        #     - API queries to create new networks with identical names;
        #     - API queries to create new controllers with identical names;
        #     - API queries to create new policy rules with identical sequences.

        path = 'api/object/write/nms=0/new_item=network'
        _, _, error_code = self.driver.custom_post(path, payload={'name': 'net'})
        for i in range(2):
            _, _, error_code = self.driver.custom_post(path, payload={'name': 'net'})
            self.assertEqual(OBJECT_EXISTS, error_code)
        Network.create(self.driver, 0, {'name': 'test_net'})
        Teleport.create(self.driver, 0, {'name': 'test_tp', 'sat_name': 'test_sat'})
        path = 'api/object/write/network=0/new_item=controller'
        _, _, error_code = self.driver.custom_post(
            path,
            payload={'name': 'ctrl', 'mode': ControllerModes.MF_HUB, 'teleport': 'teleport:0'})

        for i in range(2):
            _, _, error_code = self.driver.custom_post(
                path,
                payload={'name': 'ctrl', 'mode': ControllerModes.MF_HUB, 'teleport': 'teleport:0'}
            )
            self.assertEqual(OBJECT_EXISTS, error_code)

        # Policy rule block
        pol = Policy.create(self.driver, 0, {'name': 'pol'})
        path = f'api/object/write/policy={pol.get_id()}/new_item=polrule'
        _, _, error_code = self.driver.custom_post(path, payload={
            'type': RuleTypes.CHECK,
            'check_type': CheckTypes.VLAN,
            'sequence': 1
        })
        for i in range(2):
            _, _, error_code = self.driver.custom_post(path, payload={
                'type': RuleTypes.CHECK,
                'check_type': CheckTypes.VLAN,
                'sequence': 1}
                                                       )
            self.assertEqual(OBJECT_EXISTS, error_code)

    def test_13_cannot_delete(self):
        """Test error_code `-13` Cannot delete (aka `deletion is not possible as object is referenced in the others`)"""
        net = Network.create(self.driver, 0, {'name': 'net'})
        tp = Teleport.create(self.driver, 0, {'name': 'tp', 'sat_name': 'test_sat'})
        ctrl_params = {'name': 'ctrl', 'mode': ControllerModes.MF_HUB, 'teleport': f'teleport:{tp.get_id()}'}
        Controller.create(self.driver, net.get_id(), ctrl_params)
        path = f'api/object/delete/teleport={tp.get_id()}'
        _, _, error_code = self.driver.custom_get(path)
        self.assertEqual(CANNOT_DELETE, error_code)

    def test_14_bad_arguments(self):
        """Test error_code `-14` Bad arguments (aka `wrong request arguments`)"""
        wrong_args = self.options.get('invalid_requests')
        for path in wrong_args:
            _, _, error_code = self.driver.custom_get(path)
            self.assertEqual(BAD_ARGUMENTS, error_code, path)
        # No input vars
        net = Network.create(self.driver, 0, {'name': 'net'})
        tp = Teleport.create(self.driver, 0, {'name': 'tp', 'sat_name': 'test_sat'})
        ctrl_params = {'name': 'ctrl', 'mode': ControllerModes.MF_HUB, 'teleport': f'teleport:{tp.get_id()}'}
        Controller.create(self.driver, net.get_id(), ctrl_params)
        path = 'api/object/write/controller=0'
        _, _, error_code = self.driver.custom_get(path)
        self.assertEqual(BAD_ARGUMENTS, error_code, msg=path)

    def test_15_access_denied(self):
        """Test error_code `-15` Access denied (aka `no access to object`)"""
        path = 'api/list/get/nms=0/list_items=network'
        _, _, error_code = self.driver.custom_post(path, cookies='')
        self.assertEqual(ACCESS_DENIED, error_code, msg='No cookies in request')

    def test_16_wrong_source(self):
        """Test error_code `-16` Wrong source (aka `wrong source supplied in request`)"""
        net = Network.create(self.driver, 0, params={'name': 'net-0'})
        tp = Teleport.create(self.driver, net.get_id(), params={'name': 'tp-0'})
        payload = {'name': 'ctrl-0', 'mode': ControllerModes.HUBLESS_MASTER, 'teleport': 'teleport:0'}
        ctrl = Controller.create(self.driver, net.get_id(), params=payload)

        path = f'api/object/write/controller={ctrl.get_id()}/new_item=true'
        _, _, error_code = self.driver.custom_post(path, payload={'name': 'name'})
        self.assertEqual(WRONG_SOURCE, error_code, msg='Create an invalid item in controller ID 0')
        path = f'api/object/write/nms=0/new_item=     '
        _, _, error_code = self.driver.custom_post(path, payload={'name': 'name'})
        self.assertEqual(WRONG_SOURCE, error_code, msg='Create an invalid item in NMS ID 0')
        path = f'api/object/write/teleport={tp.get_id()}/new_item=none'
        _, _, error_code = self.driver.custom_post(path, payload={'name': 'name'})
        self.assertEqual(WRONG_SOURCE, error_code, msg='Create an invalid item in Teleport ID 0')

    def test_17_no_such_object(self):
        """Test error_code `-17` No such object (aka `Object does not exist`)"""
        path = 'api/object/get/network=100'
        _, _, error_code = self.driver.custom_get(path)
        self.assertEqual(NO_SUCH_OBJECT, error_code, msg=path)
        path = 'api/object/delete/network=100'
        _, _, error_code = self.driver.custom_get(path)
        self.assertEqual(NO_SUCH_OBJECT, error_code, msg=path)
        path = 'api/object/write/controller=3'
        _, _, error_code = self.driver.custom_post(path, payload={'name': 'name'})
        self.assertEqual(NO_SUCH_OBJECT, error_code, msg=path)

    def test_18_string_too_long(self):
        """Test error_code `-18` String too long (aka `too long string specified`)"""
        # Create a network with a 40-characters long name.
        path = PathsManager.network_create(self.driver.get_type(), 0)
        _, _, error_code = self.driver.custom_post(path, payload={'name': 'a' * 40})
        self.assertEqual(STRING_TOO_LONG, error_code, msg='Network name too long')

    def test_19_value_too_high(self):
        """Test error_code `-19` Value too high (aka `too high value for select vars`)"""
        # Set network alert_mode to 10. Set alert priority to 5.

        path = PathsManager.network_create(self.driver.get_type(), 0)
        _, _, error_code = self.driver.custom_post(path, payload={'name': 'net-0', 'alert_mode': 10})
        self.assertEqual(VALUE_TOO_HIGH, error_code, msg='Network alert_mode too high')
        path = PathsManager.alert_create(self.driver.get_type(), 0)
        _, _, error_code = self.driver.custom_post(path, payload={'name': 'net-0', 'priority': 5})
        self.assertEqual(VALUE_TOO_HIGH, error_code, msg='Alert priority too high')

    def test_20_value_too_low(self):
        """Test error_code `-20` Value too low (aka `too low value for select vars`)"""
        Network.create(self.driver, 0, {'name': 'net'})
        Teleport.create(self.driver, 0, {'name': 2})
        path = 'api/object/write/network=0/new_item=controller'

        _, _, error_code = self.driver.custom_post(path, payload={
            'name': 'mf1',
            'mode': 0,
            'teleport': 'teleport:0',
        })
        self.assertEqual(VALUE_TOO_LOW, error_code, 'Value too low is not triggered upon setting ctrl mode to None')

        _, _, error_code = self.driver.custom_post(path, payload={
            'name': 'mf2',
            'mode': ControllerModes.MF_HUB,
            'teleport': 'teleport:0',
            'uhp_model': ModelTypes.UHP200X,
            'tx_modcod': 0,
        })
        self.assertEqual(VALUE_TOO_LOW, error_code, 'Value too low is not triggered upon setting tx_modcod to 0')

    def test_21_one_time_set(self):
        """Test error_code `-21` One time set (aka `variable can be changed only in newly created objects`)"""
        # The test creates a network, a teleport, a controller, a vno, and a station.
        # Issues API queries to change the controller mode

        net = Network.create(self.driver, 0, params={'name': 'net-0'})
        tp = Teleport.create(self.driver, net.get_id(), params={'name': 'tp-0'})
        ctrl = Controller.create(self.driver, net.get_id(), params={
            'name:': 'ctrl-0',
            'mode': ControllerModes.HUBLESS_MASTER,
            'teleport': f'teleport:{tp.get_id()}'}
        )
        path = f'api/object/write/controller={ctrl.get_id()}'
        reply, _, error_code = self.driver.custom_post(path, payload={'mode': ControllerModes.MF_HUB})
        self.assertEqual(ONE_TIME_SET, error_code, msg='Change created controller mode')
