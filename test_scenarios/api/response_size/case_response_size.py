from src.backup_manager.backup_manager import BackupManager
from src.constants import NO_ERROR
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.nms_entities.paths_manager import PathsManager
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.api.response_size'
backup_name = 'case_database_performance.txt'


class ResponseSizeCase(CustomTestCase):
    """Getting lists of tables using same vars as in WEB interface to test that JSON is not truncated (ticket 7917)"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.20'
    __execution_time__ = 8  # approximate case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)
        cls.options = OptionsProvider.get_options(options_path)

    def test_network_list(self):
        """Test that network list in NMS can be fully received using vars requested by frontend"""
        path = PathsManager.network_list(self.driver.get_type(), 0, vars_=self.options.get('list_items_network_vars'))
        reply, error, error_log = self.driver.custom_get(path)
        self.assertEqual(NO_ERROR, error_log)
        self.assertEqual(128, len(reply))

    def test_server_list(self):
        """Test that server list in NMS can be fully received using vars requested by frontend"""
        path = PathsManager.server_list(self.driver.get_type(), 0, vars_=self.options.get('list_items_server_vars'))
        reply, error, error_log = self.driver.custom_get(path)
        self.assertEqual(NO_ERROR, error_log)
        self.assertEqual(64, len(reply))

    def test_group_list(self):
        """Test that group list in NMS can be fully received"""
        path = PathsManager.group_list(self.driver.get_type(), 0)
        reply, error, error_log = self.driver.custom_get(path)
        self.assertEqual(NO_ERROR, error_log)
        self.assertEqual(512, len(reply))

    def test_user_list(self):
        """Test that user list in NMS can be fully received using vars requested by frontend"""
        path = PathsManager.user_list(self.driver.get_type(), 0, vars_=self.options.get('list_items_user_vars'))
        reply, error, error_log = self.driver.custom_get(path)
        self.assertEqual(NO_ERROR, error_log)
        self.assertEqual(512, len(reply))

    def test_alert_list(self):
        """Test that alert list in NMS can be fully received using vars requested by frontend"""
        path = PathsManager.alert_list(self.driver.get_type(), 0, vars_=self.options.get('list_items_alert_vars'))
        reply, error, error_log = self.driver.custom_get(path)
        self.assertEqual(NO_ERROR, error_log)
        self.assertEqual(2048, len(reply))

    def test_dashboard_list(self):
        """Test that dashboard list in NMS can be fully received using vars requested by frontend"""
        path = PathsManager.dashboard_list(
            self.driver.get_type(),
            0,
            vars_=self.options.get('list_items_dashboard_vars')
        )
        reply, error, error_log = self.driver.custom_get(path)
        self.assertEqual(NO_ERROR, error_log)
        self.assertEqual(256, len(reply))

    def test_teleport_list(self):
        """Test that teleport list in NMS can be fully received using vars requested by frontend"""
        path = PathsManager.teleport_list(self.driver.get_type(), 0, vars_=self.options.get('list_items_teleport_vars'))
        reply, error, error_log = self.driver.custom_get(path)
        self.assertEqual(NO_ERROR, error_log)
        self.assertEqual(128, len(reply))

    def test_controller_list(self):
        """Test that controller list in NMS can be fully received using vars requested by frontend"""
        path = PathsManager.controller_list(
            self.driver.get_type(),
            0,
            vars_=self.options.get('list_items_controller_vars')
        )
        reply, error, error_log = self.driver.custom_get(path)
        self.assertEqual(NO_ERROR, error_log)
        self.assertEqual(512, len(reply))

    def test_vno_list(self):
        """Test that vno list in NMS can be fully received using vars requested by frontend"""
        path = PathsManager.vno_list(self.driver.get_type(), 0, vars_=self.options.get('list_items_vno_vars'))
        reply, error, error_log = self.driver.custom_get(path)
        self.assertEqual(NO_ERROR, error_log)
        self.assertEqual(512, len(reply))

    def test_service_list(self):
        """Test that service list in NMS can be fully received using vars requested by frontend"""
        path = PathsManager.service_list(self.driver.get_type(), 0, vars_=self.options.get('list_items_service_vars'))
        reply, error, error_log = self.driver.custom_get(path)
        self.assertEqual(NO_ERROR, error_log)
        self.assertEqual(512, len(reply))

    def test_shaper_list(self):
        """Test that shaper list in NMS can be fully received"""
        path = PathsManager.shaper_list(self.driver.get_type(), 0)
        reply, error, error_log = self.driver.custom_get(path)
        self.assertEqual(NO_ERROR, error_log)
        self.assertEqual(2048, len(reply))

    def test_policy_list(self):
        """Test that policy list in NMS can be fully received"""
        path = PathsManager.policy_list(self.driver.get_type(), 0)
        reply, error, error_log = self.driver.custom_get(path)
        self.assertEqual(NO_ERROR, error_log)
        self.assertEqual(512, len(reply))

    def test_polrule_list(self):
        """Test that polrule list in NMS can be fully received using vars requested by frontend"""
        path = PathsManager.policy_rule_list(
            self.driver.get_type(),
            0,
            vars_=self.options.get('list_items_polrule_vars')
        )
        reply, error, error_log = self.driver.custom_get(path)
        self.assertEqual(NO_ERROR, error_log)
        self.assertEqual(10000, len(reply))

    def test_sr_controller_list(self):
        """Test that sr_controller list in NMS can be fully received using vars requested by frontend"""
        path = PathsManager.sr_controller_list(
            self.driver.get_type(),
            0,
            vars_=self.options.get('list_items_sr_controller_vars')
        )
        reply, error, error_log = self.driver.custom_get(path)
        self.assertEqual(NO_ERROR, error_log)
        self.assertEqual(32, len(reply))

    def test_sr_teleport_list(self):
        """Test that sr_teleport list in NMS can be fully received using vars requested by frontend"""
        path = PathsManager.sr_teleport_list(
            self.driver.get_type(),
            0,
            vars_=self.options.get('list_items_sr_teleport_vars')
        )
        reply, error, error_log = self.driver.custom_get(path)
        self.assertEqual(NO_ERROR, error_log)
        self.assertEqual(128, len(reply))

    def test_device_list(self):
        """Test that device list in NMS can be fully received using vars requested by frontend"""
        path = PathsManager.device_list(self.driver.get_type(), 0, vars_=self.options.get('list_items_device_vars'))
        reply, error, error_log = self.driver.custom_get(path)
        self.assertEqual(NO_ERROR, error_log)
        self.assertEqual(2048, len(reply))

    def test_license_list(self):
        """Test that sr_license list in NMS can be fully received using vars requested by frontend"""
        path = PathsManager.sr_license_list(
            self.driver.get_type(),
            0,
            vars_=self.options.get('list_items_license_vars')
        )
        reply, error, error_log = self.driver.custom_get(path)
        self.assertEqual(NO_ERROR, error_log)
        self.assertEqual(256, len(reply))

    def test_bal_controller_list(self):
        """Test that bal_controller list in NMS can be fully received using vars requested by frontend"""
        path = PathsManager.bal_controller_list(
            self.driver.get_type(),
            0,
            vars_=self.options.get('list_items_bal_controller_vars')
        )
        reply, error, error_log = self.driver.custom_get(path)
        self.assertEqual(NO_ERROR, error_log)
        self.assertEqual(32, len(reply))

    def test_profile_list(self):
        """Test that profile list in NMS can be fully received using vars requested by frontend"""
        path = PathsManager.profile_list(
            self.driver.get_type(),
            0,
            vars_=self.options.get('list_items_profile_vars')
        )
        reply, error, error_log = self.driver.custom_get(path)
        self.assertEqual(NO_ERROR, error_log)
        self.assertEqual(128, len(reply))

    def test_sw_upload_list(self):
        """Test that sw_upload list in NMS can be fully received using vars requested by frontend"""
        path = PathsManager.sw_upload_list(
            self.driver.get_type(),
            0,
            vars_=self.options.get('list_items_sw_upload_vars')
        )
        reply, error, error_log = self.driver.custom_get(path)
        self.assertEqual(NO_ERROR, error_log)
        self.assertEqual(32, len(reply))

    def test_camera_list(self):
        """Test that camera list in NMS can be fully received using vars requested by frontend"""
        path = PathsManager.camera_list(
            self.driver.get_type(),
            0,
            vars_=self.options.get('list_items_camera_vars')
        )
        reply, error, error_log = self.driver.custom_get(path)
        self.assertEqual(NO_ERROR, error_log)
        self.assertEqual(64, len(reply))

    def test_scheduler_list(self):
        """Test that scheduler list in NMS can be fully received using vars requested by frontend"""
        path = PathsManager.scheduler_list(
            self.driver.get_type(),
            0,
            vars_=self.options.get('list_items_scheduler_vars')
        )
        reply, error, error_log = self.driver.custom_get(path)
        self.assertEqual(NO_ERROR, error_log)
        self.assertEqual(64, len(reply))

    def test_qos_list(self):
        """Test that qos list in NMS can be fully received using vars requested by frontend"""
        path = PathsManager.qos_list(
            self.driver.get_type(),
            0,
            vars_=self.options.get('list_items_qos_vars')
        )
        reply, error, error_log = self.driver.custom_get(path)
        self.assertEqual(NO_ERROR, error_log)
        self.assertEqual(1024, len(reply))

    def test_station_list(self):
        """Test that station list using station tool in NMS can be fully received using vars requested by frontend"""
        path = 'api/station/list/network=0'
        _vars = ','.join(self.options.get('list_items_default_station_vars'))
        reply, error, error_log = self.driver.custom_post(path, payload={'vars': _vars})
        self.assertEqual(NO_ERROR, error_log)
        self.assertEqual(32768, len(reply.get('list')))

        _vars = ','.join(self.options.get('list_items_30_station_vars'))
        reply, error, error_log = self.driver.custom_post(path, payload={'vars': _vars})
        self.assertEqual(NO_ERROR, error_log)
        self.assertEqual(32768, len(reply.get('list')))

    def test_route_list(self):
        """Test that route list in NMS can be fully received using vars requested by frontend"""
        path = PathsManager.controller_route_list(
            self.driver.get_type(),
            0,
            vars_=self.options.get('list_items_route_vars'),
            max_=65000
        )
        reply, error, error_log = self.driver.custom_get(path)
        self.assertEqual(NO_ERROR, error_log)
        self.assertEqual(65000, len(reply))

    def test_rip_router_list(self):
        """Test that rip_router list in NMS can be fully received using vars requested by frontend"""
        path = PathsManager.controller_rip_list(
            self.driver.get_type(),
            0,
            vars_=self.options.get('list_items_rip_router_vars'),
        )
        reply, error, error_log = self.driver.custom_get(path)
        self.assertEqual(NO_ERROR, error_log)
        self.assertEqual(256, len(reply))

    def test_nat_port_list(self):
        """Test that nat_port list in NMS can be fully received using vars requested by frontend"""
        path = PathsManager.controller_port_map_list(
            self.driver.get_type(),
            0,
            vars_=self.options.get('list_items_port_map_vars'),
        )
        reply, error, error_log = self.driver.custom_get(path)
        self.assertEqual(NO_ERROR, error_log)
        self.assertEqual(16000, len(reply))
