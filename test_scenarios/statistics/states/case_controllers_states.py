import time

from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControlModes, DemodulatorInputModes
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.nms import Nms
from src.nms_entities.basic_entities.teleport import Teleport
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.statistics.states'
backup_name = 'default_config.txt'


class ControllersStatesCase(CustomTestCase):
    """Controllers states in Network dashboard"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.22'
    __express__ = True
    __execution_time__ = 150

    @classmethod
    def set_up_class(cls):
        cls.controllers = OptionsProvider.get_uhp_by_model('UHP200', 'UHP200X', number=4)
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.system_options = OptionsProvider.get_system_options(options_path)
        cls.options = OptionsProvider.get_options(options_path)
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)

        cls.uhp1 = cls.controllers[0].get('web_driver')
        cls.uhp2 = cls.controllers[1].get('web_driver')
        cls.uhp3 = cls.controllers[2].get('web_driver')
        # UHP4 is a dummy controller with no device and IP address
        cls.uhp1.set_nms_permission(password=cls.options.get('network').get('dev_password'))
        cls.uhp2.set_nms_permission(password=cls.options.get('network').get('dev_password'))
        cls.uhp3.set_nms_permission(password=cls.options.get('network').get('dev_password'))
        cls.nms = Nms(cls.driver, 0, 0)

        cls.net = Network.create(cls.driver, 0, cls.options.get('network'))
        cls.tp1 = Teleport.create(cls.driver, cls.net.get_id(), cls.options.get('teleport1'))
        cls.tp2 = Teleport.create(cls.driver, cls.net.get_id(), cls.options.get('teleport2'))
        cls.tp3 = Teleport.create(cls.driver, cls.net.get_id(), cls.options.get('teleport3'))
        cls.tp4 = Teleport.create(cls.driver, cls.net.get_id(), cls.options.get('teleport4'))

        ctrl1_options = cls.options.get('controller1')
        ctrl1_options.update({
            'device_ip': cls.controllers[0].get('device_ip'),
            'device_vlan': cls.controllers[0].get('device_vlan'),
            'device_gateway': cls.controllers[0].get('device_gateway'),
            'uhp_model': cls.controllers[0].get('model'),
            'tx_level': cls.options.get('tx_level'),
        })
        ctrl2_options = cls.options.get('controller2')
        ctrl2_options.update({
            'device_ip': cls.controllers[1].get('device_ip'),
            'device_vlan': cls.controllers[1].get('device_vlan'),
            'device_gateway': cls.controllers[1].get('device_gateway'),
            'uhp_model': cls.controllers[1].get('model'),
            'tx_level': cls.options.get('tx_level'),
        })
        ctrl3_options = cls.options.get('controller3')
        ctrl3_options.update({
            'device_ip': cls.controllers[2].get('device_ip'),
            'device_vlan': cls.controllers[2].get('device_vlan'),
            'device_gateway': cls.controllers[2].get('device_gateway'),
            'uhp_model': cls.controllers[2].get('model'),
            'tx_level': cls.options.get('tx_level'),
        })
        ctrl4_options = cls.options.get('controller4')
        cls.ctrl1 = Controller.create(cls.driver, cls.net.get_id(), ctrl1_options)
        cls.ctrl2 = Controller.create(cls.driver, cls.net.get_id(), ctrl2_options)
        cls.ctrl3 = Controller.create(cls.driver, cls.net.get_id(), ctrl3_options)
        cls.ctrl4 = Controller.create(cls.driver, cls.net.get_id(), ctrl4_options)

    def test_controller_states_network_dash(self):
        """4 controllers with various states in network dash case"""
        # Initially 4 controllers are OFF
        self.nms.wait_next_tick()
        with self.subTest('4 controllers are OFF'):
            net_state = self.net.get_state()
            self.assertEqual(0, net_state.get('down_controllers'))
            self.assertEqual(0, net_state.get('up_controllers'))
            self.assertEqual(0, net_state.get('fault_controllers'))
            self.assertEqual(4, net_state.get('off_controllers'))

        with self.subTest('2 controllers are DOWN, 1 is IDLE, 1 is OFF'):
            self.ctrl1.send_param('control', ControlModes.FULL)
            self.ctrl2.send_param('control', ControlModes.UNCONFIGURED)
            self.ctrl3.send_param('control', ControlModes.FULL)
            self.nms.wait_ticks(3)
            net_state = self.net.get_state()
            self.assertEqual(2, net_state.get('down_controllers'), 'Down controllers should be 2')
            self.assertEqual(0, net_state.get('up_controllers'), 'Up controllers should be 0')
            self.assertEqual(0, net_state.get('fault_controllers'), 'Fault controllers should be 0')
            self.assertEqual(1, 4 - net_state.get('off_controllers') - net_state.get('down_controllers'))
            self.assertEqual(1, self.net.get_state().get('off_controllers'), 'Off controllers should be 1')

        with self.subTest('2 controllers are UP with FAULT, 1 is DOWN with FAULT, 1 is OFF'):
            self.ctrl1.send_params({
                'control': ControlModes.FULL,
                'rx1_frq': 1100000,
                'own_cn_low': 50,
                'rx1_input': DemodulatorInputModes.RX1,
            })
            self.ctrl2.send_params({
                'control': ControlModes.FULL,
                'rx1_frq': 1200000,
                'own_cn_low': 50,
            })
            self.ctrl3.send_params({
                'control': ControlModes.FULL,
                'rx1_frq': 1300000,
                'own_cn_low': 50,
                'rx1_input': DemodulatorInputModes.RX1,
            })
            time.sleep(50)
            net_state = self.net.get_state()
            self.assertEqual(1, net_state.get('down_controllers'), 'Down controllers should be 1')
            self.assertEqual(2, net_state.get('up_controllers'), 'Up controllers should be 2')
            self.assertEqual(2, net_state.get('fault_controllers'), 'Fault controllers should be 2')
            self.assertEqual(1, net_state.get('off_controllers'), 'Off controllers should be 1')

        with self.subTest('3 controllers are UP with NO FAULT, 1 is OFF'):
            self.tp2.send_params({'tx_lo': 0, 'rx1_lo': 0, 'rx2_lo': 0})
            self.ctrl1.send_param('own_cn_low', 2)
            self.ctrl2.send_params({'own_cn_low': 2, 'rx1_input': DemodulatorInputModes.RX1})
            self.ctrl3.send_param('own_cn_low', 2)

            time.sleep(50)
            net_state = self.net.get_state()
            self.assertEqual(0, net_state.get('down_controllers'))
            self.assertEqual(3, net_state.get('up_controllers'))
            self.assertEqual(0, net_state.get('fault_controllers'))
            self.assertEqual(1, net_state.get('off_controllers'))
