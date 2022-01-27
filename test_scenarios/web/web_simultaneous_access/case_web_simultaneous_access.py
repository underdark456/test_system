import time

from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import AlertModes, ControllerModes
from src.exceptions import ObjectNotCreatedException
from src.nms_entities.basic_entities.alert import Alert
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.user import User
from src.nms_entities.basic_entities.vno import Vno
from src.nms_entities.paths_manager import PathsManager
from src.options_providers.options_provider import OptionsProvider, CHROME_CONNECT

options_path = 'test_scenarios.web.web_simultaneous_access'
backup_name = 'case_simultaneous_access.txt'


class WebSimultaneousAccessCase(CustomTestCase):
    """Two users edit/delete same form"""

    __author__ = 'dkudryashov'
    __version__ = '0.1'
    __execution_time__ = 100  # approximate test case execution time in seconds

    @classmethod
    def set_up_class(cls):
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)

        cls.system_options = OptionsProvider.get_system_options(options_path)
        cls.nms_address_port = cls.system_options.get(CHROME_CONNECT).get('address')
        cls.driver_path = cls.system_options.get(CHROME_CONNECT).get('driver_path')
        user1_connection_options = cls.system_options.get('first_user')
        user1_connection_options['address'] = cls.nms_address_port
        user1_connection_options['driver_path'] = cls.driver_path
        user2_connection_options = cls.system_options.get('second_user')
        user2_connection_options['address'] = cls.nms_address_port
        user2_connection_options['driver_path'] = cls.driver_path
        user3_connection_options = cls.system_options.get('third_user')
        user3_connection_options['address'] = cls.nms_address_port
        user3_connection_options['driver_path'] = cls.driver_path
        cls.driver1 = DriversProvider.get_driver_instance(
            user1_connection_options, driver_id='case_web_simultaneous_access1'
        )
        cls.driver2 = DriversProvider.get_driver_instance(
            user2_connection_options, driver_id='case_web_simultaneous_access2'
        )
        cls.driver3 = DriversProvider.get_driver_instance(
            user3_connection_options, driver_id='case_web_simultaneous_access3'
        )

    def set_up(self) -> None:
        self.backup.apply_backup(backup_name)

    # Probably not needed, as it has no meaning
    def test_edit_same_table(self):
        """Two users edit the same table"""
        ctrl_user1 = Controller(self.driver1, 0, 0)
        ctrl_user1.load()
        ctrl_user2 = Controller(self.driver2, 0, 1)
        ctrl_user2.load()
        ctrl_user1.send_param('name', 'ctrl1_new')
        ctrl_user2.send_param('name', 'ctrl2_new')
        self.assertEqual('ctrl1_new', ctrl_user1.get_param('name'))
        self.assertEqual('ctrl2_new', ctrl_user2.get_param('name'))

    # Probably not needed, as it has no meaning
    def test_delete_same_object(self):
        """Two users delete the same object"""
        ctrl_user1 = Controller(self.driver1, 0, 0)
        ctrl_user1.load()
        ctrl_user2 = Controller(self.driver2, 0, 0)
        ctrl_user2.load()
        ctrl_user1.delete()
        ctrl_user2.delete()
        self.assertTrue(self.driver2.get_current_url().find('notfound') != -1)

    def test_edit_deleted_form(self):
        """First user starts editing form while the second one has just deleted the form object"""
        net_user1 = Network(self.driver1, 0, 0)
        net_user1.load()
        net_user2 = Network(self.driver2, 0, 0)
        net_user2.delete()
        net_user1.send_param('name', 'new_name')
        time.sleep(1)
        self.assertTrue(self.driver1.get_current_url().find('notfound') != -1)

    def test_apply_deleted_linked_object(self):
        """First user applies a form with a linked object that has just been deleted by the second user"""
        net_user1 = Network(self.driver1, 0, 0)
        alert_user2 = Alert(self.driver2, 0, 0)
        net_user1.load()
        alert_user2.delete()
        net_user1.send_params({'alert_mode': AlertModes.SPECIFY, 'set_alert': 'alert:0'})
        self.assertTrue(net_user1.has_param_error('set_alert'))

    def test_apply_modified_linked_object(self):
        """First user applies a form with a linked object that has just been modified by the second user"""
        net_user1 = Network(self.driver1, 0, 0)
        alert_user2 = Alert(self.driver2, 0, 0)
        net_user1.load()
        alert_user2.send_param('name', 'brand_new_alert')
        net_user1.send_params({'alert_mode': AlertModes.SPECIFY, 'set_alert': 'alert:0'})
        self.assertEqual('alert:0', net_user1.get_param('set_alert'))

    def test_apply_form_in_deleted_parent(self):
        """First user applies a new object while the second one has just deleted the parent object"""
        self.driver1.driver.get(f'{self.nms_address_port}{PathsManager.station_create(self.driver1, 0)}')
        self.driver1.set_value('name', 'test_stn')
        self.driver1.set_value('enable', 1)
        self.driver1.set_value('serial', '12345')
        self.driver1.set_value('rx_controller', 'controller:0')
        vno_user2 = Vno(self.driver2, 0, 0)
        vno_user2.delete()
        self.assertRaises(ObjectNotCreatedException, self.driver1.create_object)

    def test_realtime_deleted_controller(self):
        """First user applies getting controller realtime while the second one has just deleted the object"""
        self.driver1.driver.get(f'{self.nms_address_port}{PathsManager.realtime(self.driver1, "controller", 1)}')
        ctrl2_user2 = Controller(self.driver2, 0, 1)
        ctrl2_user2.delete()
        time.sleep(1)
        self.driver1.send_data('#show\ system')
        self.assertTrue(self.driver1.get_current_url().find('notfound') != -1)

    def test_modify_newly_created_object(self):
        """First user opens controller edit form while the second one deletes and creates a new controller with another mode"""
        ctrl2_user1 = Controller(self.driver1, 0, 1)
        ctrl2_user1.load()
        ctrl2_user2 = Controller(self.driver2, 0, 1)
        ctrl2_user2.delete()
        Controller.create(self.driver2, 0, {
            'name': 'brand_new_ctrl',
            'mode': ControllerModes.HUBLESS_MASTER,
            'teleport': 'teleport:0'
        })
        self.driver1.send_data()
        self.assertEqual(str(ControllerModes.HUBLESS_MASTER), str(ctrl2_user1.get_param('mode')))

    # Probably not needed, as it has no meaning
    def test_edit_same_object(self):
        """Two users edit the same form"""
        net_user1 = Network(self.driver1, 0, 0)
        net_user2 = Network(self.driver2, 0, 0)
        net_user1.load()
        net_user2.load()
        net_user1.send_param('name', 'new_name1')
        net_user2.send_param('name', 'new_name2')
        self.assertEqual('new_name2', net_user2.get_param('name'))

    def test_user_deletes_another_user(self):
        """User is being deleted upon editing a form"""
        user3_user1 = User(self.driver1, 0, 3)  # User who is gonna be deleted
        net_user3 = Network(self.driver3, 0, 0)
        net_user3.load()
        _url = self.driver3.get_current_url()  # User who is gonna be deleted is on the Newtwork edit page
        user3_user1.delete()
        # Deleted user should be redirected to login page
        self.assertTrue(
            WebDriverWait(self.driver3.driver, 5).until(expected_conditions.url_changes(_url)),
            msg=f'Deleted user current URL has not been changed: {self.driver3.get_current_url()}'
        )
        self.assertTrue(
            self.driver3.get_current_url().find('login') != -1,
            msg=f'Deleted user has not been redirected to login page, current page {self.driver3.get_current_url()}'
        )

    @staticmethod
    def _dict_merge(dct: dict, merge_dct: dict):
        """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
        updating only top-level keys, dict_merge recurses down into dicts nested
        to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
        ``dct``.
        :param dct: dict onto which the merge is executed
        :param merge_dct: dct merged into dct
        :returns: None
        """
        for k, v in merge_dct.items():
            if (k in dct and isinstance(dct[k], dict)
                    and isinstance(merge_dct[k], dict)):
                OptionsProvider._dict_merge(dct[k], merge_dct[k])
            else:
                dct[k] = merge_dct[k]
        return dct
