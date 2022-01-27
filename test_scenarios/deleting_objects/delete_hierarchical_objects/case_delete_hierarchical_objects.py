import time

from src import test_api, nms_api
from src.custom_test_case import CustomTestCase
from src.exceptions import NmsErrorResponseException

options_path = 'test_scenarios.deleting_objects.delete_hierarchical_objects'
backup_name = 'case_database_performance.txt'


class DeleteHierarchicalObjectsCase(CustomTestCase):
    """Delete stand alone objects and parent objects containing child objects"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.21'
    __execution_time__ = None  # approximate test case execution time in seconds
    __express__ = False

    @classmethod
    def set_up_class(cls):
        nms_options = test_api.get_nms(options_path)
        nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))
        cls.options = test_api.get_options(options_path)

    def set_up(self):
        nms_api.set_timeout(3)

    def check_table(self, del_name, check_name, row=0):
        for i in range(row, self.options.get(f'number_of_{check_name}')):
            with self.assertRaises(
                    NmsErrorResponseException,
                    msg=f'{check_name}:{i} is in place after deleting {del_name}'
            ):
                nms_api.get_param(f'{check_name}:{i}', '%row')

    def test_delete_vno(self):
        """Delete vno containing all child objects: sub-vnos, stations etc."""
        # ~1100 seconds
        nms_api.set_timeout(120)
        nms_api.load_config('vno_with_all_objects.txt')
        time.sleep(5)
        nms_api.delete('vno:0')
        self.check_table('vno', 'vno')
        self.check_table('vno', 'dashboard')
        self.check_table('vno', 'station')
        self.check_table('vno', 'sch_task')
        self.check_table('vno', 'rip_router')
        self.check_table('vno', 'port_map')
        self.check_table('vno', 'route')

    def test_delete_controller_route(self):
        """Delete controller route"""
        nms_api.load_config('controller_with_all_objects.txt')
        num = self.options.get('number_of_route')
        for i in (0, num // 2, num - 1):
            nms_api.delete(f'route:{i}')
            with self.assertRaises(NmsErrorResponseException, msg=f'route:{i} is in place after its deletion'):
                nms_api.get_param(f'route:{i}', 'type')

    def test_delete_controller_rip_router(self):
        """Delete controller rip_router"""
        nms_api.load_config('controller_with_all_objects.txt')
        num = self.options.get('number_of_rip_router')
        for i in (0, num // 2, num - 1):
            nms_api.delete(f'rip_router:{i}')
            with self.assertRaises(NmsErrorResponseException, msg=f'rip_router:{i} is in place after its deletion'):
                nms_api.get_param(f'rip_router:{i}', 'service')

    def test_delete_controller_port_map(self):
        """Delete controller port_map"""
        nms_api.load_config('controller_with_all_objects.txt')
        num = self.options.get('number_of_port_map')
        for i in (0, num // 2, num - 1):
            nms_api.delete(f'port_map:{i}')
            with self.assertRaises(NmsErrorResponseException, msg=f'port_map:{i} is in place after its deletion'):
                nms_api.get_param(f'port:{i}', 'service')

    def test_delete_controller_access(self):
        """Delete controller access"""
        nms_api.load_config('controller_with_all_objects.txt')
        for i in (1, 255, 512):
            nms_api.delete(f'access:{i}')
            with self.assertRaises(NmsErrorResponseException, msg=f'access:{i} is in place after its deletion'):
                nms_api.get_param(f'access:{i}', 'group')

    def test_delete_controller(self):
        """Delete controller containing all route, rip_router, port_map, and access"""
        nms_api.load_config('controller_with_all_objects.txt')
        nms_api.set_timeout(10)
        nms_api.delete('controller:0')
        self.check_table('controller', 'route')
        self.check_table('controller', 'rip_router')
        self.check_table('controller', 'port_map')
        self.check_table('controller', 'access', row=1)

    def test_delete_station_route(self):
        """Delete station route"""
        nms_api.load_config('station_with_all_objects.txt')
        num = self.options.get('number_of_route')
        for i in (0, num // 2, num - 1):
            nms_api.delete(f'route:{i}')
            with self.assertRaises(NmsErrorResponseException, msg=f'route:{i} is in place after its deletion'):
                nms_api.get_param(f'route:{i}', 'type')

    def test_delete_station_rip_router(self):
        """Delete station rip_router"""
        nms_api.load_config('station_with_all_objects.txt')
        num = self.options.get('number_of_rip_router')
        for i in (0, num // 2, num - 1):
            nms_api.delete(f'rip_router:{i}')
            with self.assertRaises(NmsErrorResponseException, msg=f'rip_router:{i} is in place after its deletion'):
                nms_api.get_param(f'rip_router:{i}', 'service')

    def test_delete_station_port_map(self):
        """Delete station port_map"""
        nms_api.load_config('station_with_all_objects.txt')
        num = self.options.get('number_of_port_map')
        for i in (0, num // 2, num - 1):
            nms_api.delete(f'port_map:{i}')
            with self.assertRaises(NmsErrorResponseException, msg=f'port_map:{i} is in place after its deletion'):
                nms_api.get_param(f'port:{i}', 'service')

    def test_delete_station_sch_task(self):
        """Delete station sch_task"""
        nms_api.load_config('station_with_all_objects.txt')
        time.sleep(5)
        num = self.options.get('number_of_sch_task')
        for i in (0, num // 2, num - 1):
            nms_api.delete(f'sch_task:{i}')
            with self.assertRaises(NmsErrorResponseException, msg=f'sch_task:{i} is in place after its deletion'):
                nms_api.get_param(f'sch_task:{i}', 'name')

    def test_delete_station(self):
        """Delete station containing all sch_task, route, rip_router, port_map"""
        nms_api.load_config('station_with_all_objects.txt')
        nms_api.set_timeout(10)
        nms_api.delete('station:0')
        self.check_table('station', 'route')
        self.check_table('station', 'rip_router')
        self.check_table('station', 'port_map')
        self.check_table('station', 'sch_task')

    def test_delete_network(self):
        """Delete network containing all objects"""
        # Duration 560 seconds
        nms_api.load_config('network_with_all_objects.txt')
        nms_api.set_timeout(120)  # timeout is set to a higher value in order to let NMS delete all child objects
        nms_api.delete('network:0')
        time.sleep(20)
        self.check_table('network', 'teleport')
        self.check_table('network', 'controller')
        self.check_table('network', 'vno')
        self.check_table('network', 'service')
        self.check_table('network', 'shaper')
        self.check_table('network', 'policy')
        self.check_table('network', 'polrule')
        self.check_table('network', 'group', row=1)
        self.check_table('network', 'user', row=1)
        self.check_table('network', 'access', row=1)
        self.check_table('network', 'sr_controller')
        self.check_table('network', 'sr_teleport')
        self.check_table('network', 'device')
        self.check_table('network', 'sr_license')
        self.check_table('network', 'bal_controller')
        self.check_table('network', 'profile_set')
        self.check_table('network', 'sw_upload')
        self.check_table('network', 'camera')
        self.check_table('network', 'dashboard')
        self.check_table('network', 'scheduler')
        self.check_table('network', 'sch_service')
        self.check_table('network', 'sch_range')
        self.check_table('network', 'sch_task')
        self.check_table('network', 'station')
        self.check_table('network', 'rip_router')
        self.check_table('network', 'port_map')
        self.check_table('network', 'route')
