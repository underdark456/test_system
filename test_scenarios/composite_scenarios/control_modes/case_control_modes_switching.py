from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes, ControlModes, ControlModesStr
from src.exceptions import InvalidOptionsException, NmsControlledModeException
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.nms import Nms
from src.nms_entities.basic_entities.teleport import Teleport
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.composite_scenarios.control_modes'
backup_name = 'default_config.txt'


class ControlModesSwitchingCase(CustomTestCase):
    """Switch controller control modes several times"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.20'
    __execution_time__ = 860  # approximate case execution time in seconds
    __express__ = False

    @classmethod
    def set_up_class(cls):
        cls.uhp_controller = OptionsProvider.get_uhp_by_model('UHP200', 'UHP200X', number=1)[0]

        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)

        cls.options = OptionsProvider.get_options(options_path)

        cls.nms = Nms(cls.driver, 0, 0)
        cls.net = Network.create(cls.driver, 0, {'name': 'test_name'})

        cls.tp = Teleport.create(cls.driver, 0, {'name': 'test_tp', 'tx_lo': 0, 'rx1_lo': 0, 'rx2_lo': 0})
        cls.ctrl = Controller.create(cls.driver, 0, {
            'name': 'test_ctrl',
            'up_timeout': 10,
            'teleport': f'teleport:{cls.tp.get_id()}',
            'mode': ControllerModes.MF_HUB,
            'control': ControlModes.NO_ACCESS,
            'device_ip': cls.uhp_controller.get('device_ip'),
            'device_vlan': cls.uhp_controller.get('device_vlan'),
            'device_gateway': cls.uhp_controller.get('device_gateway'),
            'uhp_model': cls.uhp_controller.get('model'),
        })

        cls.uhp1_driver = cls.uhp_controller.get('web_driver')
        cls.uhp1_driver.set_nms_permission(password=cls.net.read_param('dev_password'))

        if not cls.ctrl.wait_not_states(['Unknown', 'Unreachable', ]):
            raise NmsControlledModeException(f'Controller state is {cls.ctrl.read_param("state")}')

    def test_control_modes(self):
        """Four control modes are tested in random cycle several times"""
        for i in range(self.options.get('number_of_cycles')):
            modes = [
                ControlModesStr.FULL,
                ControlModesStr.UNCONFIGURED,
                ControlModesStr.STATS_ONLY,
                ControlModesStr.NO_ACCESS
            ]
            # # Getting random ControlModes list
            # random.shuffle(modes)
            for mode in modes:
                self.ctrl.send_param('control', mode)
                applied_mode = self.ctrl.get_param('control')
                self.assertEqual(mode, applied_mode, msg=f'Sent control mode={mode}, applied mode={applied_mode}')
                self.nms.wait_ticks(3)
                if mode == ControlModesStr.FULL:
                    self.full()
                elif mode == ControlModesStr.NO_ACCESS:
                    self.no_access()
                elif mode == ControlModesStr.STATS_ONLY:
                    self.stats_only()
                elif mode == ControlModesStr.UNCONFIGURED:
                    self.unconfigured()
                else:
                    raise InvalidOptionsException(f'Unexpected Control mode {mode}')

    def full(self):
        self.assertTrue(self.uhp1_driver.wait_nms_controlled_mode(), msg=f'UHP is not under NMS control'
                                                                         f' in Full control mode')
        ctrl_state = self.ctrl.get_param('state')
        self.assertEqual('Down', ctrl_state, msg=f'Controller state {ctrl_state}. Should be `Down` in Full mode')
        active_pro_name = self.uhp1_driver.get_active_profile_name()
        self.assertEqual('MF hub', active_pro_name, msg=f'UHP active profile name {active_pro_name}. '
                                                        f'Should be `MF hub` in Full Control mode')

    def stats_only(self):
        nms_controlled_mode = self.uhp1_driver.get_nms_controlled_mode()
        self.assertFalse(nms_controlled_mode, msg=f'NMS controlled mode is {nms_controlled_mode}. '
                                                  f'Should be False in Stats_only mode')
        # Stats only mode should not apply changes to UHP controller
        self.ctrl.send_param('up_timeout', 60)
        self.nms.wait_ticks(2)
        uhp_timeout = self.uhp1_driver.get_basic_form().get('timeout')
        self.assertNotEqual('60', uhp_timeout, msg=f'New value is applied to controller in Stats_only mode')
        self.ctrl.send_param('up_timeout', 10)

    def unconfigured(self):
        nms_controlled_mode = self.uhp1_driver.get_nms_controlled_mode()
        self.assertFalse(nms_controlled_mode, msg=f'NMS controlled mode is {nms_controlled_mode}. '
                                                  f'Should be False in Unconfigured mode')
        ctrl_state = self.ctrl.get_param('state')
        self.assertEqual('Idle', ctrl_state, msg=f'Controller state {ctrl_state}. '
                                                 f'Should be `Idle` in Unconfigured mode')
        active_pro_name = self.uhp1_driver.get_active_profile_name()
        self.assertEqual('none', active_pro_name, msg=f'UHP active profile name {active_pro_name}. '
                                                      f'Should be `none` in Unconfigured Control mode')
        for i in range(1, 9):
            profile_mode = self.uhp1_driver.get_basic_form(profile_number=i).get('mode')
            self.assertEqual('0', profile_mode, msg=f'UHP profile number {i} mode {profile_mode}. '
                                                    f'Should be `0` in Unconfigured Control mode')

    def no_access(self):
        nms_controlled_mode = self.uhp1_driver.get_nms_controlled_mode()
        self.assertFalse(nms_controlled_mode, msg=f'NMS controlled mode is {nms_controlled_mode}. '
                                                  f'Should be False in No_access mode')
        ctrl_state = self.ctrl.get_param('state')
        self.assertEqual('Off', ctrl_state, msg=f'Controller state {ctrl_state}. Should be `Off` in No_access mode')
        # No_access mode should not apply changes to UHP controller
        self.ctrl.send_param('up_timeout', 60)
        self.nms.wait_ticks(2)
        uhp_timeout = self.uhp1_driver.get_basic_form().get('timeout')
        self.assertNotEqual('60', uhp_timeout, msg=f'New value is applied to controller in No_access mode')
        self.ctrl.send_param('up_timeout', 10)
