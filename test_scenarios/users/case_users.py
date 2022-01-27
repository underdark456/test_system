import random

from src.backup_manager.backup_manager import BackupManager
from src.constants import ACCESS_DENIED, NO_ERROR
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import LanguageTypes, ControllerModes, Checkbox
from src.exceptions import DriverInitException, ObjectNotDeletedException, ObjectNotFoundException, \
    ObjectNotCreatedException
from src.nms_entities.basic_entities.access import Access
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.nms import Nms
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.user import User
from src.nms_entities.basic_entities.user_group import UserGroup
from src.nms_entities.basic_entities.vno import Vno
from src.nms_entities.paths_manager import PathsManager
from src.options_providers.options_provider import OptionsProvider, CHROME_CONNECT, API_CONNECT

backup_name = 'default_config.txt'
options_path = 'test_scenarios.users'


class UsersGroupsAccessesCase(CustomTestCase):
    """Case tests users, user groups, and access capabilities of NMS"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.19'  # edited to comply with this version
    __execution_time__ = 365

    @classmethod
    def set_up_class(cls):
        cls.backup = BackupManager()

        cls.options = OptionsProvider.get_options(options_path)
        cls.system_options = OptionsProvider.get_system_options(options_path)
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(), driver_id='case_users_api', store_driver=False
        )
        cls.web_driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(options_path, CHROME_CONNECT), driver_id='case_users_web', store_driver=False
        )
        cls.username = OptionsProvider.get_connection().get('username')
        cls.password = OptionsProvider.get_connection().get('password')
        cls.nms = Nms(cls.driver, 0, 0)

    def set_up(self):
        self.driver.login(self.username, self.password)

    def test_delete_own_user_group_access(self):
        """Try to delete own user and its group while it is logged in (WEB and API)"""
        self.backup.apply_backup(backup_name)
        new_group = UserGroup.create(self.driver, 0, {'name': 'new_group', 'active': Checkbox.ON})
        username = 'new_user'
        password = 'password'
        new_user = User.create(
            self.driver,
            new_group.get_id(),
            {'name': username, 'enable': Checkbox.ON, 'password': password},
        )
        new_access = Access.create(
            self.driver,
            0,
            {'group': f'group:{new_group.get_id()}', 'edit': Checkbox.ON, 'use': Checkbox.ON},
        )
        api_options = OptionsProvider.get_connection(options_path, API_CONNECT)
        api_options['username'] = username
        api_options['password'] = password

        web_options = OptionsProvider.get_connection(options_path, CHROME_CONNECT)
        web_options['username'] = username
        web_options['password'] = password

        api_driver = DriversProvider.get_driver_instance(
            api_options,
            driver_id=f'case_users_test_delete_own_user_group_api',
            store_driver=False
        )
        web_driver = DriversProvider.get_driver_instance(
            web_options,
            driver_id=f'case_users_test_delete_own_user_group_web',
            store_driver=False
        )

        for driver in (api_driver, web_driver):
            Access(driver, 0, new_access.get_id())
            grp = UserGroup(driver, 0, new_group.get_id())
            usr = User(driver, new_group.get_id(), new_user.get_id())

            with self.assertRaises(
                    ObjectNotDeletedException,
                    msg=f'User has been deleted themself via {driver.get_driver_name()} driver'
            ):
                usr.delete()
            with self.assertRaises(
                    ObjectNotDeletedException,
                    msg=f'User has been deleted their group via {driver.get_driver_name()} driver',
            ):
                grp.delete()
        del driver
        del web_driver

    def test_unauthorized_access(self):
        """WEB unauthorized access test. Invalid credentials used to load various NMS pages"""
        self.backup.apply_backup('each_entity.txt')
        web_options = OptionsProvider.get_connection(options_path, CHROME_CONNECT)
        web_options['username'] = 'qwerty'
        web_options['password'] = 'qwerty'
        web_driver = DriversProvider.get_driver_instance(
            web_options,
            driver_id=f'case_users_test_unauthorized_access',
            store_driver=False
        )
        for path in (
            PathsManager._OBJECT_CREATE.format('nms', 0, 'network'),
            PathsManager._OBJECT_EDIT.format('network', 0),
            PathsManager._OBJECTS_LIST.format('network', 0, 'station'),
            PathsManager._OBJECT_STATUS.format('controller', 0),
            PathsManager._OBJECT_LOG.format('controller', 0),
            PathsManager._REALTIME.format('controller', 0),
            PathsManager._OBJECT_MAP.format('vno', 0),
            PathsManager._OBJECT_GRAPH.format('station', 0),
            PathsManager._OBJECT_STATION.format('network', 0),
            'faults/get',
            'fs/dirs/nms=0',
            'investigator/get/nms=0',
            'list/get/network=0/list_items=dashboard',
        ):
            web_driver.load_data(path)
            self.assertTrue(web_driver.get_current_url().find('login') != -1, msg=f'Unauthorized access: {path}')
        del web_driver

    def test_users_login(self):
        """Max number of groups and users with full access. Check that all of them can login via API"""
        self.backup.apply_backup(backup_name)
        users = {}
        for i in range(self.options.get('number_of_groups') - 1):
            group = UserGroup.create(self.driver, 0, params={'name': f'group-{i}', 'active': 'ON'})
            self.assertIsNotNone(group.get_id())
            user = User.create(self.driver, group.get_id(), params={
                'name': f'user-{i}',
                'enable': 'ON',
                'email': f'user{i}@comtechtel.com',
                'first_name': f'Firstname{i}',
                'last_name': f'Lastname{i}',
                'language': LanguageTypes.ENGLISH,
                'password': f'qwerty{i}'
            })
            self.assertIsNotNone(user.get_id())
            users[f'user-{i}'] = f'qwerty{i}'
            access = Access.create(self.driver, 0, params={'group': f'group:{i+1}', 'use': 'ON', 'edit': 'ON'})
            self.assertIsNotNone(access.get_id())

        api_options = OptionsProvider.get_connection(options_path, API_CONNECT)
        api_options['auto_login'] = False
        api_driver = DriversProvider.get_driver_instance(
            api_options,
            driver_id=f'case_users_test_delete_own_user_group_api',
            store_driver=False
        )
        for username, password in users.items():
            api_driver.login(username, password)
            reply, error, error_log = api_driver.custom_get(PathsManager.nms_read(api_driver.get_type(), 0))
            self.assertEqual(
                NO_ERROR,
                error_log,
                f'Getting NMS params by username={username}, password={password} failed'
            )
            self.assertGreater(
                len(reply),
                0,
                msg=f'Empty reply upon getting nms params by username={username}, password={password}'
            )
            api_driver.logout()
        del api_driver

    def test_users_no_access(self):
        """Max number of users (unique usernames and passwords) with no access. Check that they cannot login"""
        self.backup.apply_backup(backup_name)
        users = {}
        for i in range(self.options.get('number_of_groups') - 1):
            group = UserGroup.create(self.driver, 0, params={'name': f'group-{i}', 'active': 'ON'})
            User.create(self.driver, group.get_id(), params={
                'name': f'user-{i}',
                'enable': 'ON',
                'email': f'user{i}@comtechtel.com',
                'first_name': f'Firstname{i}',
                'last_name': f'Lastname{i}',
                'language': LanguageTypes.ENGLISH,
                'password': f'qwerty{i}'
            })
            users[f'user-{i}'] = f'qwerty{i}'
            # Give user no access
            Access.create(self.driver, 0, params={
                'group': f'group:{i+1}',
                'edit': Checkbox.OFF,
                'use': Checkbox.OFF
            })
        api_options = OptionsProvider.get_connection(options_path, API_CONNECT)
        api_options['auto_login'] = False
        api_driver = DriversProvider.get_driver_instance(
            api_options,
            driver_id=f'case_users_test_users_no_access',
            store_driver=False
        )

        for username, password in users.items():
            api_driver.login(username, password)
            payload = {'name': f'alert-{username}'}
            path = 'api/object/write/nms=0/new_item=alert'
            reply, error, error_code = api_driver.custom_post(path, payload=payload)
            self.assertEqual(
                ACCESS_DENIED,
                error_code,
                msg=f'Returned error_code {error_code}, expected {ACCESS_DENIED}'
            )
            api_driver.logout()
        del api_driver

    def test_edit_disable(self):
        """Check if user cannot create objects with edit disable access"""
        self.backup.apply_backup(backup_name)
        group = UserGroup.create(self.driver, 0, params={'name': f'group-0', 'active': 'ON'})
        User.create(self.driver, group.get_id(), params={
            'name': 'user-0',
            'enable': 'ON',
            'email': f'user0@comtechtel.com',
            'first_name': f'Firstname0',
            'last_name': f'Lastname0',
            'language': LanguageTypes.ENGLISH,
            'password': 'qwerty0'
        })
        Access.create(self.driver, 0, params={'group': f'group:{group.get_id()}', 'use': 'ON', 'edit': 'OFF'})
        api_options = OptionsProvider.get_connection(options_path, API_CONNECT)
        api_options['username'] = 'user-0'
        api_options['password'] = 'qwerty0'
        api_driver = DriversProvider.get_driver_instance(
            api_options,
            driver_id=f'case_users_test_edit_disable',
            store_driver=False
        )
        reply, error, error_log = api_driver.custom_post('api/object/write/nms=0', payload={'name': 'net-0'})
        self.assertEqual(ACCESS_DENIED, error_log, msg=f'Network is created via API by user with edit disable')
        del api_driver

        web_options = OptionsProvider.get_connection(options_path, CHROME_CONNECT)
        web_options['username'] = 'user-0'
        web_options['password'] = 'qwerty0'
        web_driver = DriversProvider.get_driver_instance(
            web_options,
            driver_id=f'case_users_test_edit_disable',
            store_driver=False
        )
        with self.assertRaises(ObjectNotFoundException, msg=f'Network is created via WEB by user with edit disable'):
            Network.create(web_driver, 0, {'name': 'net-0'})
        del web_driver

    def test_disabled_users(self):
        """Check if disabled users cannot login"""
        self.backup.apply_backup(backup_name)
        group = UserGroup.create(self.driver, 0, params={'name': f'group-0', 'active': 'ON'})
        User.create(self.driver, group.get_id(), params={
            'name': f'user-0',
            'enable': 'OFF',
            'email': f'user0@comtechtel.com',
            'first_name': f'Firstname0',
            'last_name': f'Lastname0',
            'language': LanguageTypes.ENGLISH,
            'password': f'qwerty0'
        })
        Access.create(self.driver, 0, params={'group': f'group:{group.get_id()}', 'use': 'ON', 'edit': 'ON'})
        api_options = OptionsProvider.get_connection(options_path, API_CONNECT)
        api_options['username'] = 'user-0'
        api_options['password'] = 'qwerty0'
        api_driver = DriversProvider.get_driver_instance(
            api_options,
            driver_id=f'case_users_test_disabled users',
            store_driver=False
        )
        reply, error, error_code = api_driver.custom_get('api/object/get/nms=0')
        self.assertEqual(ACCESS_DENIED, error_code, msg=f'Disabled user is able to login via API')
        del api_driver

        web_options = OptionsProvider.get_connection(options_path, CHROME_CONNECT)
        web_options['username'] = 'user-0'
        web_options['password'] = 'qwerty0'
        web_driver = DriversProvider.get_driver_instance(
            web_options,
            driver_id=f'case_users_test_edit_disable',
            store_driver=False
        )
        web_driver.load_data(PathsManager.nms_read(web_driver.get_type(), 0))
        self.assertTrue(
            web_driver.get_current_url().find('login?redirect') != -1,
            msg=f'Disabled user is able to login via WEB'
        )
        del web_driver

    def test_wrong_credentials(self):
        """Check if wrong credentials cannot be used to login and manipulate NMS"""
        self.backup.apply_backup(backup_name)
        api_options = OptionsProvider.get_connection(options_path, API_CONNECT)
        api_options['auto_login'] = False
        api_driver = DriversProvider.get_driver_instance(
            api_options,
            driver_id=f'case_users_test_wrong_credentials',
            store_driver=False
        )
        for i in range(10):
            username = f'user{i}'
            password = f'qwerty{i}'
            try:
                api_driver.login(username, password)
            except DriverInitException:
                pass
            reply, error, error_code = api_driver.custom_get('api/object/get/nms=0')
            self.assertEqual(
                ACCESS_DENIED,
                error_code,
                msg=f'Username {username}, password {password} is able to login'
            )
            api_driver.logout()
        del api_driver

    def test_change_credentials(self):
        """Check if it is possible to login after changing username and password"""
        self.backup.apply_backup(backup_name)
        group = UserGroup.create(self.driver, 0, params={'name': 'test_group'})
        username = 'test_user'
        password = 'nousecryingoverspiltmilk'
        user = User.create(self.driver, group.get_id(), params={'name': username, 'password': password})
        Access.create(self.driver, 0, params={'group': f'group:{group.get_id()}', 'edit': 'ON', 'use': 'ON'})
        api_options = OptionsProvider.get_connection(options_path, API_CONNECT)
        api_options['username'] = username
        api_options['password'] = password
        api_driver = DriversProvider.get_driver_instance(
            api_options,
            driver_id=f'case_users_test_disabled users',
            store_driver=False
        )
        reply, error, error_code = api_driver.custom_get('api/object/get/nms=0')
        self.assertEqual(NO_ERROR, error_code)
        new_username = 'test_user2'
        new_password = 'comeandgetsome'
        user.send_params({'name': new_username, 'password': new_password})
        api_driver.logout()
        api_driver.login(new_username, new_password)
        reply, error, error_code = self.driver.custom_get('api/object/get/nms=0')
        self.assertEqual(
            NO_ERROR,
            error_code,
            msg=f'Cannot get NMS params after changing credentials, error_code={error_code}'
        )
        del api_driver

    def test_limited_access(self):
        """Check that users' access scope is correct (e.g. VNO users get access to their VNO only)"""
        self.backup.apply_backup('groups_limited_scopes.txt')
        api_options = OptionsProvider.get_connection(options_path, API_CONNECT)
        api_options['auto_login'] = False
        api_driver = DriversProvider.get_driver_instance(
            api_options,
            driver_id=f'case_users_test_limited_access',
            store_driver=False
        )
        # Network 0 user
        api_driver.login('user_net_1', 'qwerty')
        for obj in ('network', 'controller'):
            with self.subTest(f'User net 0 access {obj} 0'):
                reply, error, error_code = api_driver.custom_get(f'api/object/get/{obj}=0')
                self.assertEqual(NO_ERROR, error_code)
            with self.subTest(f'User net 0 access {obj} 1'):
                reply, error, error_code = api_driver.custom_get(f'api/object/get/{obj}=1')
                self.assertEqual(ACCESS_DENIED, error_code)
        with self.subTest(f'User net 0 access NMS'):
            reply, error, error_code = api_driver.custom_get(f'api/object/get/nms=0')
            self.assertEqual(ACCESS_DENIED, error_code)
        with self.subTest(f'User net 0 access vno 0'):
            reply, error, error_code = api_driver.custom_get(f'api/object/get/vno=0')
            self.assertEqual(NO_ERROR, error_code)
        with self.subTest(f'User net 0 access vno 1'):
            reply, error, error_code = api_driver.custom_get(f'api/object/get/vno=1')
            self.assertEqual(NO_ERROR, error_code)
        with self.subTest('User net 0 access vno 2'):
            reply, error, error_code = api_driver.custom_get(f'api/object/get/vno=2')
            self.assertEqual(ACCESS_DENIED, error_code)
        with self.subTest('User net 0 access vno 3'):
            reply, error, error_code = api_driver.custom_get(f'api/object/get/vno=3')
            self.assertEqual(ACCESS_DENIED, error_code)
        api_driver.logout()
        # Network 1 user
        api_driver.login('user_net_2', 'qwerty')
        for obj in ('network', 'controller'):
            with self.subTest(f'User net 1 access {obj} 1'):
                reply, error, error_code = api_driver.custom_get(f'api/object/get/{obj}=1')
                self.assertEqual(NO_ERROR, error_code)
            with self.subTest(f'User net 1 access {obj} 0'):
                reply, error, error_code = api_driver.custom_get(f'api/object/get/{obj}=0')
                self.assertEqual(ACCESS_DENIED, error_code)
        with self.subTest(f'User net 1 access NMS'):
            reply, error, error_code = api_driver.custom_get(f'api/object/get/nms=0')
            self.assertEqual(ACCESS_DENIED, error_code)
        with self.subTest(f'User net 1 access vno 2'):
            reply, error, error_code = api_driver.custom_get(f'api/object/get/vno=2')
            self.assertEqual(NO_ERROR, error_code)
        with self.subTest(f'User net 1 access vno 3'):
            reply, error, error_code = api_driver.custom_get(f'api/object/get/vno=3')
            self.assertEqual(NO_ERROR, error_code)
        with self.subTest('User net 0 access vno 0'):
            reply, error, error_code = api_driver.custom_get(f'api/object/get/vno=0')
            self.assertEqual(ACCESS_DENIED, error_code)
        with self.subTest('User net 0 access vno 1'):
            reply, error, error_code = api_driver.custom_get(f'api/object/get/vno=1')
            self.assertEqual(ACCESS_DENIED, error_code)
        api_driver.logout()
        # VNO 0 user
        api_driver.login('user_vno_1', 'qwerty')
        for obj in ('network', 'controller', 'nms'):
            with self.subTest(f'User vno 0 access {obj} 0'):
                reply, error, error_code = api_driver.custom_get(f'api/object/get/{obj}=0')
                self.assertEqual(ACCESS_DENIED, error_code)
        for obj in ('network', 'controller'):
            with self.subTest(f'User vno 0 access {obj} 1'):
                reply, error, error_code = api_driver.custom_get(f'api/object/get/{obj}=1')
                self.assertEqual(ACCESS_DENIED, error_code)
        for i in range(2):
            with self.subTest(f'User vno 0 access vno {i}'):
                reply, error, error_code = api_driver.custom_get(f'api/object/get/vno={i}')
                self.assertEqual(NO_ERROR, error_code)
        for i in range(2, 4):
            with self.subTest(f'User vno 0 access vno {i}'):
                reply, error, error_code = api_driver.custom_get(f'api/object/get/vno={i}')
                self.assertEqual(ACCESS_DENIED, error_code)
        api_driver.logout()
        # VNO 1 user (Sub-VNO)
        api_driver.login('user_sub_vno_1', 'qwerty')
        for obj in ('nms', 'network', 'controller', 'vno'):
            with self.subTest(f'User vno 1 (Sub-VNO) access {obj} 0'):
                reply, error, error_code = api_driver.custom_get(f'api/object/get/{obj}=0')
                self.assertEqual(ACCESS_DENIED, error_code)
        for obj in ('network', 'controller'):
            with self.subTest(f'User vno 1 (Sub-VNO) access {obj} 1'):
                reply, error, error_code = api_driver.custom_get(f'api/object/get/{obj}=1')
                self.assertEqual(ACCESS_DENIED, error_code)
        with self.subTest(f'User vno 1 (Sub-VNO) access vno 1 (Sub-VNO)'):
            reply, error, error_code = api_driver.custom_get(f'api/object/get/vno=1')
            self.assertEqual(NO_ERROR, error_code)
        with self.subTest(f'User vno 1 (Sub-VNO) access vno 3 (Sub-VNO)'):
            reply, error, error_code = api_driver.custom_get(f'api/object/get/vno=3')
            self.assertEqual(ACCESS_DENIED, error_code)
        api_driver.logout()
        # CTRL 0 user
        api_driver.login('user_ctrl_1', 'qwerty')
        with self.subTest(f'User ctrl 0 access NMS'):
            reply, error, error_code = api_driver.custom_get(f'api/object/get/nms=0')
            self.assertEqual(ACCESS_DENIED, error_code)
        for i in range(2):
            with self.subTest(f'User ctrl 0 access network {i}'):
                reply, error, error_code = api_driver.custom_get(f'api/object/get/network={i}')
                self.assertEqual(ACCESS_DENIED, error_code)
        for i in range(4):
            with self.subTest(f'User ctrl 0 access vno {i}'):
                reply, error, error_code = api_driver.custom_get(f'api/object/get/vno={i}')
                self.assertEqual(ACCESS_DENIED, error_code)
        with self.subTest(f'User ctrl 0 access ctrl 0'):
            reply, error, error_code = api_driver.custom_get(f'api/object/get/controller=0')
            self.assertEqual(NO_ERROR, error_code)
        with self.subTest(f'User ctrl 0 access ctrl 1'):
            reply, error, error_code = api_driver.custom_get(f'api/object/get/controller=1')
            self.assertEqual(ACCESS_DENIED, error_code)
        del api_driver

    def test_extremely_long_password(self):
        """Check the maximum length of the user password. Does not cause fail if 800 or less characters are allowed"""
        self.backup.apply_backup(backup_name)
        username = 'test_user'
        password = '1'
        group = UserGroup.create(self.driver, 0, params={'name': 'test_group'})
        user = User.create(self.driver, group.get_id(), params={
            'name': username,
            'password': password,
            'enable': 'ON'
        })
        Access.create(self.driver, 0, params={'group': f'group:{group.get_id()}', 'edit': 'ON', 'use': 'ON'})
        api_options = OptionsProvider.get_connection(options_path, API_CONNECT)
        api_options['auto_login'] = False
        api_driver = DriversProvider.get_driver_instance(
            api_options,
            driver_id=f'case_users_test_extremely_long_password',
            store_driver=False
        )

        for i in range(1, 1001):
            user.send_param('password', password * i)
            try:
                api_driver.logout()
                api_driver.login(username, password * i)
            except DriverInitException:
                if i < 800:
                    self.fail(f'Password {i} characters long cannot be used to login')
                else:
                    self.info(f'Password {i} characters long cannot be used to login')
                    break
        del api_driver

    def test_login_loop_with_long_pass(self):
        """Login loop for a single user having 50 characters long password, 1000 login logout iterations"""
        self.backup.apply_backup(backup_name)
        username = 'test'
        password = '1' * 50
        group = UserGroup.create(self.driver, 0, params={'name': 'test_group'})
        User.create(self.driver, group.get_id(), params={'name': username, 'password': password})
        Access.create(self.driver, 0, params={
            'group': f'group:{group.get_id()}',
            'edit': 'ON',
            'use': 'ON'
        })
        api_options = OptionsProvider.get_connection(options_path, API_CONNECT)
        api_options['auto_login'] = False
        api_driver = DriversProvider.get_driver_instance(
            api_options,
            driver_id=f'case_users_test_login_loop_with_long_pass',
            store_driver=False
        )
        for i in range(1000):
            with self.subTest(f'iteration {i}'):
                api_driver.logout()
                api_driver.login(username, password)
                reply, error, error_code = api_driver.custom_get(f'api/object/get/nms=0')
                self.assertEqual(NO_ERROR, error_code, msg=f'Error {error_code} upon getting NMS params')
        del api_driver

    def test_multiple_access(self):
        """Multiple access with the same credentials case. Login 1000 times without logout"""
        self.backup.apply_backup(backup_name)
        for i in range(1000):
            driver = DriversProvider.get_driver_instance(
                OptionsProvider.get_connection('test_scenarios.users'),
                driver_id=f'case_users_test_multiple_access{i}',
                store_driver=False
            )
            path = 'api/object/dashboard/nms=0'
            reply, error, error_code = driver.custom_post(path)
            del driver
            self.assertEqual(NO_ERROR, error_code, msg=f'Error {error_code} upon getting NMS params')

    def test_invalid_credentials(self):
        """Login 1000 times using wrong credentials case"""
        self.backup.apply_backup(backup_name)
        driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection('test_scenarios.users'),
            driver_id=f'case_users_test_invalid_credentials',
            store_driver=False
        )
        for _ in range(1000):
            username = self._generate_random_string()
            password = self._generate_random_string()
            self.assertRaises(DriverInitException, driver.login, username, password)
        del driver

    def test_no_cookies_access(self):
        """API requests with no cookies case"""
        self.backup.apply_backup(backup_name)
        for _ in range(1000):
            reply, error, error_code = self.driver.custom_get('api/object/dashboard/nms=0', cookies='')
            self.assertEqual(
                ACCESS_DENIED,
                error_code,
                msg=f'{error_code} instead of {ACCESS_DENIED} upon getting NMS params without valid cookies'
            )

    def test_modified_cookies_access(self):
        """API requests with modified cookies case"""
        self.backup.apply_backup(backup_name)
        nms_cookies = self.driver.get_cookies()
        # Wrong token
        cookies = {
            'locale': nms_cookies.get('locale'),
            'token': str(int(nms_cookies.get('token')) + 1),
            'user_id': nms_cookies.get('user_id')
        }
        reply, error, error_code = self.driver.custom_get('api/object/dashboard/nms=0', cookies=cookies)
        self.assertEqual(ACCESS_DENIED, error_code, msg=f'Wrong token get NMS dashboard successful')
        # Wrong user_id
        cookies = {
            'locale': nms_cookies.get('locale'),
            'token': nms_cookies.get('token'),
            'user_id': str(int(nms_cookies.get('user_id')) + 1),
        }
        reply, error, error_code = self.driver.custom_get('api/object/dashboard/nms=0', cookies=cookies)
        self.assertEqual(ACCESS_DENIED, error_code, msg=f'Wrong user_id get NMS dashboard successful')

    def test_apply_same_password(self):
        """Submitting existing user form without editing password field"""
        self.backup.apply_backup('default_config.txt')
        self.web_driver.login('admin', '12345')
        username = 'test_user'
        password = 'qwerty'
        group = UserGroup.create(self.web_driver, 0, params={'name': 'test_group'})
        user = User.create(self.web_driver, group.get_id(), params={'name': username, 'password': password})
        Access.create(self.web_driver, 0, params={
            'group': f'group:{group.get_id()}',
            'edit': 'ON',
            'use': 'ON'
        })
        # Applying web form without touching the hidden password field
        self.web_driver.load_data(PathsManager.user_update(self.web_driver.get_type(), user.get_id()))
        self.web_driver.send_data()

        opt = OptionsProvider.get_connection(options_path, CHROME_CONNECT)
        opt['username'] = username
        opt['password'] = password
        driver = DriversProvider.get_driver_instance(
            opt,
            driver_id=f'case_users_test_apply_same_password',
            store_driver=False
        )

        driver.load_data(PathsManager.nms_read(driver.get_type(), 0))
        self.assertTrue(
            driver.get_current_url().find(PathsManager.nms_read(driver.get_type(), 0)) != -1
        )
        del driver

    def test_apply_same_username(self):
        """Create users with the same names in different groups"""
        self.backup.apply_backup(backup_name)
        net = Network.create(self.driver, 0, {'name': 'test_net'})
        Teleport.create(self.driver, net.get_id(), {'name': 'test_tp'})
        vno = Vno.create(self.driver, net.get_id(), {'name': 'test_vno'})
        nms_gr = UserGroup.create(self.driver, 0, {'name': 'nms_group'}, parent_type='nms')
        net_gr = UserGroup.create(self.driver, net.get_id(), {'name': 'net_group'}, parent_type='network')
        vno_gr = UserGroup.create(self.driver, vno.get_id(), {'name': 'vno_group'}, parent_type='vno')
        User.create(self.driver, nms_gr.get_id(), {'name': 'john_doe'})
        for i in range(3):
            with self.assertRaises(
                    ObjectNotCreatedException,
                    msg=f'Two users with the same name are created in NMS group'
            ):
                User.create(self.driver, nms_gr.get_id(), {'name': 'john_doe'})
        for i in range(3):
            with self.assertRaises(
                    ObjectNotCreatedException,
                    msg=f'User with an existing name for NMS user is created in network'
            ):
                User.create(self.driver, net_gr.get_id(), {'name': 'john_doe'})
        for i in range(3):
            with self.assertRaises(
                    ObjectNotCreatedException,
                    msg=f'User with an existing name for NMS user is created in vno'
            ):
                User.create(self.driver, vno_gr.get_id(), {'name': 'john_doe'})

    def test_vno_users_correct_redirect(self):
        """Vno group having access to the Vno and a controller login case (ticket 8067)"""
        self.backup.apply_backup(backup_name)
        Network.create(self.driver, 0, {'name': 'test_net'})
        Teleport.create(self.driver, 0, {'name': 'test_tp'})
        mf_hub = Controller.create(
            self.driver,
            0,
            {'name': 'mf', 'teleport': 'teleport:0', 'mode': ControllerModes.MF_HUB}
        )
        vno = Vno.create(self.driver, 0, {'name': 'test_vno'})
        gr = UserGroup.create(self.driver, vno.get_id(), {'name': 'vno-gr'}, parent_type='vno')
        usr = User.create(self.driver, gr.get_id(), {'name': 'vno-usr', 'password': 'qwerty'})
        Access.create(
            self.driver,
            vno.get_id(),
            {'group': f'group:{gr.get_id()}', 'edit': True, 'use': True},
            parent_type='vno'
        )
        Access.create(
            self.driver,
            mf_hub.get_id(),
            {'group': f'group:{gr.get_id()}', 'edit': True, 'use': True},
            parent_type='controller'
        )
        api_options = OptionsProvider.get_connection(options_path, API_CONNECT)
        api_options['username'] = usr.read_param('name')
        api_options['password'] = 'qwerty'
        api_driver = DriversProvider.get_driver_instance(
            api_options,
            driver_id=f'case_users_test_vno_users_correct_redirect_api',
            store_driver=False
        )
        reply, error, error_code = api_driver.custom_get(PathsManager._API_OBJECT_TREE.format('nms', '0'))
        self.assertEqual(2, len(reply.get('tree')), msg=f'Unexpectedly number of objects in the tree is not 2')
        self.assertEqual(
            mf_hub.read_param('name'),
            reply.get('tree')[0].get('na'),
            msg='Cannot find controller in the tree'
        )
        self.assertEqual(
            vno.read_param('name'),
            reply.get('tree')[1].get('na'),
            msg='Cannot find vno in the tree'
        )

        web_options = OptionsProvider.get_connection(options_path, CHROME_CONNECT)
        web_options['username'] = usr.read_param('name')
        web_options['password'] = 'qwerty'
        web_driver = DriversProvider.get_driver_instance(
            web_options,
            driver_id=f'case_users_test_vno_users_correct_redirect_web',
            store_driver=False
        )
        # Should be redirected to Controller 0 dashboard
        self.assertTrue(
            web_driver.get_current_url().find('object/dashboard/controller=0'),
            msg=f'User is not redirected to Controller 0 dashboard after login'
        )
        del api_driver
        del web_driver

    @staticmethod
    def _generate_random_string(max_length=50):
        whitespace = ' \t\n\r\v\f'
        ascii_lowercase = 'abcdefghijklmnopqrstuvwxyz'
        ascii_uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        ascii_letters = ascii_lowercase + ascii_uppercase
        digits = '0123456789'
        punctuation = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""
        printable = digits + ascii_letters + punctuation + whitespace
        random_string = ''
        for _ in range(random.randint(1, max_length+1)):
            # Keep appending random characters using chr(x)
            random_string += printable[random.randint(0, len(printable) - 1)]
        return random_string
