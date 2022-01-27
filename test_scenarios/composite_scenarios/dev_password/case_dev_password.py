from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.nms import Nms
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.has_up_state_object import HasUpState
from src.options_providers.options_provider import OptionsProvider
from utilities.utils import get_random_string

options_path = 'test_scenarios.composite_scenarios.dev_password'
backup_name = 'default_config.txt'


class DevPasswordCase(CustomTestCase):
    """NMS controlled mode with password"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.26'
    __execution_time__ = 245  # approximate test case execution time
    __express__ = True

    @classmethod
    def set_up_class(cls):
        cls.uhp_options = OptionsProvider.get_uhp(number=4)
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)

        cls.nms = Nms(cls.driver, 0, 0)
        cls.net = Network.create(cls.driver, 0, {'name': 'test_net', 'dev_password': 'lafkjh'})
        cls.tp = Teleport.create(cls.driver, cls.net.get_id(), {'name': 'test_tp'})
        cls.ctrl = Controller.create(cls.driver, cls.net.get_id(), {
            'name': 'test_ctrl',
            'mode': ControllerModes.MF_HUB,
            'teleport': f'teleport:{cls.tp.get_id()}',
            'device_ip': cls.uhp_options[0].get('device_ip'),
            'device_vlan': cls.uhp_options[0].get('device_vlan'),
            'device_gateway': cls.uhp_options[0].get('device_gateway'),
        })
        cls.uhp_driver = cls.uhp_options[0].get('web_driver')
        cls.uhp2_driver = cls.uhp_options[1].get('web_driver')
        cls.uhp3_driver = cls.uhp_options[2].get('web_driver')
        cls.uhp4_driver = cls.uhp_options[3].get('web_driver')

    def test_dev_password_length(self):
        """dev_password various length test case (up to 10 characters including)"""
        for i in range(11):
            if i == 0:
                random_pass = ''
            else:
                random_pass = get_random_string(length=i, punctuation=False)

            self.net.send_param('dev_password', random_pass)
            self.nms.wait_ticks(2)
            if not self.ctrl.wait_state(HasUpState.UNREACHABLE):
                self.fail(f'Controller state {self.ctrl.read_param("state")}, should be Unreachable'
                          f' after changing dev_password to newly generated {random_pass}')

            self.uhp_driver.set_nms_permission(vlan=self.uhp_options[0].get('device_vlan'), password=random_pass)
            self.nms.wait_ticks(2)
            if not self.ctrl.wait_not_states([HasUpState.UNKNOWN, HasUpState.UNREACHABLE]):
                self.fail(f'Password {random_pass} of length {len(random_pass)} is set to NMS and UHP,'
                          f' but controller state is {self.ctrl.read_param("state")}')

    def test_dev_password_several_nets(self):
        """NMS controlled mode in 4 networks with different dev_password"""
        self.net.send_param('dev_password', 'indeed')
        self.net2 = Network.create(self.driver, 0, {'name': 'test_net2', 'dev_password': 'kawabanga'})
        self.net3 = Network.create(self.driver, 0, {'name': 'test_net3', 'dev_password': 'bazinga'})
        self.net4 = Network.create(self.driver, 0, {'name': 'test_net4', 'dev_password': ''})

        self.tp2 = Teleport.create(self.driver, self.net2.get_id(), {'name': 'test_tp2'})
        self.ctrl2 = Controller.create(self.driver, self.net2.get_id(), {
            'name': 'test_ctrl2',
            'mode': ControllerModes.MF_HUB,
            'teleport': f'teleport:{self.tp2.get_id()}',
            'device_ip': self.uhp_options[1].get('device_ip'),
            'device_vlan': self.uhp_options[1].get('device_vlan'),
            'device_gateway': self.uhp_options[1].get('device_gateway'),
        })

        self.tp3 = Teleport.create(self.driver, self.net3.get_id(), {'name': 'test_tp3'})
        self.ctrl3 = Controller.create(self.driver, self.net3.get_id(), {
            'name': 'test_ctrl3',
            'mode': ControllerModes.MF_HUB,
            'teleport': f'teleport:{self.tp3.get_id()}',
            'device_ip': self.uhp_options[2].get('device_ip'),
            'device_vlan': self.uhp_options[2].get('device_vlan'),
            'device_gateway': self.uhp_options[2].get('device_gateway'),
        })

        self.tp4 = Teleport.create(self.driver, self.net4.get_id(), {'name': 'test_tp4'})
        self.ctrl4 = Controller.create(self.driver, self.net4.get_id(), {
            'name': 'test_ctrl4',
            'mode': ControllerModes.MF_HUB,
            'teleport': f'teleport:{self.tp4.get_id()}',
            'device_ip': self.uhp_options[3].get('device_ip'),
            'device_vlan': self.uhp_options[3].get('device_vlan'),
            'device_gateway': self.uhp_options[3].get('device_gateway'),
        })

        net_pass = self.net.read_param('dev_password')
        self.uhp_driver.set_nms_permission(vlan=self.uhp_options[0].get('device_vlan'), password=net_pass)
        if not self.ctrl.wait_not_states([HasUpState.UNKNOWN, HasUpState.UNREACHABLE]):
            self.fail(f'Network 1: password {net_pass} of length {len(net_pass)} is set to NMS and UHP,'
                      f' but controller state is {self.ctrl.read_param("state")}')

        net_pass2 = self.net2.read_param('dev_password')
        self.uhp2_driver.set_nms_permission(vlan=self.uhp_options[1].get('device_vlan'), password=net_pass2)
        if not self.ctrl2.wait_not_states([HasUpState.UNKNOWN, HasUpState.UNREACHABLE]):
            self.fail(f'Network 2: password {net_pass2} of length {len(net_pass2)} is set to NMS and UHP,'
                      f' but controller state is {self.ctrl2.read_param("state")}')

        net_pass3 = self.net3.read_param('dev_password')
        self.uhp3_driver.set_nms_permission(vlan=self.uhp_options[2].get('device_vlan'), password=net_pass3)
        if not self.ctrl3.wait_not_states([HasUpState.UNKNOWN, HasUpState.UNREACHABLE]):
            self.fail(f'Network 3: password {net_pass3} of length {len(net_pass3)} is set to NMS and UHP,'
                      f' but controller state is {self.ctrl3.read_param("state")}')

        net_pass4 = self.net4.read_param('dev_password')
        self.uhp4_driver.set_nms_permission(vlan=self.uhp_options[3].get('device_vlan'), password=net_pass4)
        if not self.ctrl4.wait_not_states([HasUpState.UNKNOWN, HasUpState.UNREACHABLE]):
            self.fail(f'Network 4: password {net_pass4} of length {len(net_pass4)} is set to NMS and UHP,'
                      f' but controller state is {self.ctrl4.read_param("state")}')
