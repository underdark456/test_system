from src.custom_test_case import CustomTestCase
from src import nms_api, test_api
from src.exceptions import NmsErrorResponseException

options_path = 'test_scenarios.backup.load_default_config'
backup_name = 'case_database_performance.txt'


class LoadDefaultConfigCase(CustomTestCase):
    """Default config should erase all tables except for access, group, and user"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.20'
    __execution_time__ = 1300  # approximate case execution time in seconds

    @classmethod
    def set_up_class(cls):
        nms_options = test_api.get_nms()
        nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))
        nms_api.load_config(backup_name)
        cls.options = test_api.get_options(options_path)

    def check_next_table(self, table_name, row=0):
        for i in range(row, self.options.get(f'number_of_{table_name}')):
            with self.assertRaises(
                    NmsErrorResponseException,
                    msg=f'{table_name}:{i} is in place after loading default'
            ):
                nms_api.get_param(f'{table_name}:{i}', '%row')

    def test_load_default_config(self):
        """Checking all table:rows"""
        nms_api.load_config('default_config.txt')
        self.check_next_table('access', row=1)
        self.check_next_table('alert')
        self.check_next_table('bal_controller')
        self.check_next_table('camera')
        self.check_next_table('controller')
        self.check_next_table('dashboard')
        self.check_next_table('device')
        self.check_next_table('group', row=1)
        self.check_next_table('network')
        self.check_next_table('policy')
        self.check_next_table('polrule')
        self.check_next_table('port_map')
        self.check_next_table('profile_set')
        self.check_next_table('rip_router')
        self.check_next_table('route')
        self.check_next_table('server')
        self.check_next_table('service')
        self.check_next_table('qos')
        self.check_next_table('shaper')
        self.check_next_table('sr_controller')
        self.check_next_table('sr_license')
        self.check_next_table('sr_teleport')
        self.check_next_table('station')
        self.check_next_table('sw_upload')
        self.check_next_table('teleport')
        self.check_next_table('user', row=1)
        self.check_next_table('vno')
        self.check_next_table('scheduler')
        self.check_next_table('sch_range')
        self.check_next_table('sch_service')
        self.check_next_table('sch_task')
