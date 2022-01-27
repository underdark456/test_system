import random
import time
from src.constants import API_FORCE_CONFIG_CONTROLLER_COMMAND
from src.custom_test_case import CustomTestCase
from src import nms_api, test_api
from src.enum_types_constants import ControllerModes, Checkbox, StationModes
from src.exceptions import NmsControlledModeException

options_path = 'test_scenarios.composite_scenarios.nms_control'
backup_name = 'default_config.txt'


class NmsControlUhp(CustomTestCase):
    """UHP under NMS control in appropriate mode"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.26'
    __execution_time__ = 1520  # approximate test case execution time in seconds

    @classmethod
    def set_up_class(cls):
        cls.uhp_option = test_api.get_uhp(number=1)[0]
        nms_options = test_api.get_nms()
        nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))
        cls.uhp_driver = cls.uhp_option.get('web_driver')

    def set_up(self):
        nms_api.load_config(backup_name)
        self.net = nms_api.create('nms:0', 'network', {'name': 'test_net'})
        self.tp = nms_api.create(self.net, 'teleport', {'name': 'test_tp', 'tx_lo': 0, 'rx1_lo': 0, 'rx2_lo': 0})

    def test_delete_create_controller_cycle(self):
        """Delete MF hub controller in NMS, create again and make sure that UHP in MF hub profile mode"""
        # ~1000 seconds
        self.mf_hub = nms_api.create(self.net, 'controller', {
            'name': 'mf_hub',
            'mode': ControllerModes.MF_HUB,
            'teleport': self.tp,
            'device_ip': self.uhp_option.get('device_ip'),
            'device_vlan': self.uhp_option.get('device_vlan'),
            'device_gateway': self.uhp_option.get('device_gateway'),
            'uhp_model': self.uhp_option.get('model'),
            'allow_local': Checkbox.OFF,
        })
        self.uhp_driver.set_nms_permission(vlan=self.uhp_option.get('device_vlan'), password='')
        number_of_iterations = 100
        for i in range(number_of_iterations):
            self.info(f'Iteration {i + 1} out of {number_of_iterations}')
            nms_api.delete(self.mf_hub)
            res = self.uhp_driver.star_station()
            self.assertTrue(res, msg=f'Cannot apply Star station profile to the UHP under test')

            self.mf_hub = nms_api.create(self.net, 'controller', {
                'name': 'mf_hub',
                'mode': ControllerModes.MF_HUB,
                'teleport': self.tp,
                'device_ip': self.uhp_option.get('device_ip'),
                'device_vlan': self.uhp_option.get('device_vlan'),
                'device_gateway': self.uhp_option.get('device_gateway'),
                'uhp_model': self.uhp_option.get('model'),
                'allow_local': Checkbox.OFF,
            })

            if not nms_api.wait_state(self.mf_hub, 'Down'):
                self.fail(f'MF hub expected state Down, current {nms_api.get_param(self.mf_hub, "state")}')
            nms_api.wait_next_tick()
            nms_api.wait_next_tick()
            nms_api.wait_next_tick()
            self.assertEqual('MF hub', self.uhp_driver.get_active_profile_name())

    def test_controlled_mode_change_permission(self):
        """UHP runs correct profile after changing permissions' password"""
        self.mf_hub = nms_api.create(self.net, 'controller', {
            'name': 'mf_hub',
            'mode': ControllerModes.MF_HUB,
            'teleport': self.tp,
            'device_ip': self.uhp_option.get('device_ip'),
            'device_vlan': self.uhp_option.get('device_vlan'),
            'device_gateway': self.uhp_option.get('device_gateway'),
            'uhp_model': self.uhp_option.get('model'),
            'allow_local': Checkbox.OFF,
        })
        for i in range(1, 6):
            timeout = 60
            self.uhp_driver.set_nms_permission(password='ljfdsaad')
            self.uhp_driver.star_station()
            if not nms_api.wait_state('controller:0', 'Unreachable'):
                test_api.fail(self, f'Controller state is not Unreachable after setting invalid NMS permissions')

            nms_api.wait_next_tick()
            nms_api.wait_next_tick()
            self.uhp_driver.set_nms_permission(
                vlan=self.uhp_option.get('device_vlan'),
                password=nms_api.get_param('network:0', 'dev_password')
            )
            if not nms_api.wait_states('controller:0', ['Up', 'Fault', 'Down', ], timeout=timeout):
                test_api.fail(self, f'Controller is neither in UP nor in Fault nor in Down state '
                                    f'after setting again NMS permissions timeout={timeout} seconds')
            uhp_act_pro_mode = self.uhp_driver.get_active_profile_name()
            self.assertEqual('MF hub', uhp_act_pro_mode, msg=f'UHP active profile mode {uhp_act_pro_mode}, '
                                                             f'should be MF hub')

    def test_force_config_controller(self):
        """Force config applies config to controller if it has another profile running"""
        self.mf_hub = nms_api.create(self.net, 'controller', {
            'name': 'mf_hub',
            'mode': ControllerModes.MF_HUB,
            'teleport': self.tp,
            'device_ip': self.uhp_option.get('device_ip'),
            'device_vlan': self.uhp_option.get('device_vlan'),
            'device_gateway': self.uhp_option.get('device_gateway'),
            'uhp_model': self.uhp_option.get('model'),
            'allow_local': Checkbox.OFF,
        })
        for i in range(1, 10):
            self.uhp_driver.set_nms_permission(
                vlan=self.uhp_option.get('device_vlan'),
                password=nms_api.get_param('network:0', 'dev_password')
            )
            timeout = 60
            if not nms_api.wait_states('controller:0', ['Up', 'Fault', 'Down', ], timeout=timeout):
                test_api.fail(self, f'Controller is neither in UP nor Fault nor Down state '
                                    f'after setting NMS permissions timeout={timeout} seconds')
            # Imitating UHP reboot by setting OFF NMS permissions and running another profile
            self.uhp_driver.set_nms_permission(password='ljfdsaad')
            self.uhp_driver.star_station()
            if not nms_api.wait_state('controller:0', 'Unreachable'):
                test_api.fail(self, f'Controller state is not Unreachable after setting invalid NMS permissions')

            self.uhp_driver.set_nms_permission(
                vlan=self.uhp_option.get('device_vlan'),
                password=nms_api.get_param('network:0', 'dev_password')
            )
            if not nms_api.wait_not_state('controller:0', 'Unreachable'):
                test_api.fail(self, f'Controller state is Unreachable after setting correct NMS permissions')
            nms_api.wait_ticks(3)

            uhp_act_pro_mode = self.uhp_driver.get_active_profile_name()
            if uhp_act_pro_mode != 'MF hub':
                self.info('Running profile is not MF hub after setting correct NMS permissions, trying force...')
                nms_api.update('controller:0', {'command': API_FORCE_CONFIG_CONTROLLER_COMMAND})
                nms_api.wait_ticks(4)
                uhp_act_pro_mode = self.uhp_driver.get_active_profile_name()
                self.assertEqual('MF hub', uhp_act_pro_mode, msg=f'UHP profile mode is not MF hub after force config')

    def test_uhp_reboot(self):
        """UHP NMS controlled mode after UHP reboot (5 iterations)"""
        self.mf_hub = nms_api.create(self.net, 'controller', {
            'name': 'mf_hub',
            'mode': ControllerModes.MF_HUB,
            'teleport': self.tp,
            'device_ip': self.uhp_option.get('device_ip'),
            'device_vlan': self.uhp_option.get('device_vlan'),
            'device_gateway': self.uhp_option.get('device_gateway'),
            'uhp_model': self.uhp_option.get('model'),
            'allow_local': Checkbox.OFF,
        })
        # 600 seconds
        for i in range(1, 20):
            self.uhp_driver.reboot()
            time.sleep(20)
            res = self.uhp_driver.set_nms_permission(
                vlan=self.uhp_option.get('device_vlan'),
                password=nms_api.get_param('network:0', 'dev_password')
            )
            self.assertTrue(res, msg=f'Cannot set NMS permissions to UHP after {i} reboot')
            nms_api.wait_next_tick()
            nms_api.wait_next_tick()
            uhp_act_pro_mode = self.uhp_driver.get_active_profile_name()
            self.assertEqual(
                'MF hub',
                uhp_act_pro_mode,
                msg=f'UHP is not in MF hub profile, active profile {uhp_act_pro_mode}'
            )

    def test_uhp_reboot_with_active_profile(self):
        """UHP NMS controlled mode after UHP reboot and running Star station profile (5 iterations)"""
        # 600 seconds
        self.mf_hub = nms_api.create(self.net, 'controller', {
            'name': 'mf_hub',
            'mode': ControllerModes.MF_HUB,
            'teleport': self.tp,
            'device_ip': self.uhp_option.get('device_ip'),
            'device_vlan': self.uhp_option.get('device_vlan'),
            'device_gateway': self.uhp_option.get('device_gateway'),
            'uhp_model': self.uhp_option.get('model'),
            'allow_local': Checkbox.OFF,
        })
        for i in range(1, 20):
            self.uhp_driver.reboot()
            time.sleep(20)
            res = self.uhp_driver.star_station()
            self.assertTrue(res, msg=f'Cannot set UHP Star station profile after {i} reboot')
            res = self.uhp_driver.set_nms_permission(
                vlan=self.uhp_option.get('device_vlan'),
                password=nms_api.get_param('network:0', 'dev_password')
            )
            self.assertTrue(res, msg=f'Cannot set NMS permissions to UHP after {i} reboot')
            nms_api.wait_ticks(3)
            uhp_act_pro_mode = self.uhp_driver.get_active_profile_name()
            self.assertEqual(
                'MF hub',
                uhp_act_pro_mode,
                msg=f'Iteration {i}: UHP is not in MF hub profile, active profile {uhp_act_pro_mode}'
            )

    def test_uhp_default_nms_control(self):
        """Getting available UHPs (default is called) make sure that NMS sends config to controller (100 iterations)"""
        modes = {'MF_hub': 'MF hub', 'DAMA_hub': 'DAMA hub', 'Hubless_master': 'Hubless master', 'DAMA_inroute': 'DAMA inroute'}
        ctrl_to_stn = {'MF_hub': 'Star', 'DAMA_hub': 'DAMA', 'Hubless_master': 'Hubless', 'DAMA_inroute': 'DAMA'}
        for i in range(1, 251):
            uhp_option = test_api.get_uhp(number=1)[0]
            uhp_driver = uhp_option.get('web_driver')
            print(f'Iteration {i}, ip={uhp_option.get("device_ip")}')

            nms_api.load_config(backup_name)

            net = nms_api.create('nms:0', 'network', {'name': 'test_net'})
            tp = nms_api.create(net, 'teleport', {'name': 'test_tp', 'tx_lo': 0, 'rx1_lo': 0, 'rx2_lo': 0})
            nms_api.create(net, 'shaper', {'name': 'shp'})
            vno = nms_api.create(net, 'vno', {'name': 'vno'})

            nms_api.update(net, {'name': 'new_name'})
            nms_api.update(tp, {'name': 'new_tp'})

            ctrl = nms_api.create(net, 'controller', {
                'name': 'test_ctrl',
                'mode': random.choice(
                    [ControllerModes.MF_HUB, ControllerModes.DAMA_HUB, ControllerModes.HUBLESS_MASTER]
                ),
                'teleport': tp,
                'device_ip': uhp_option.get('device_ip'),
                'device_vlan': uhp_option.get('device_vlan'),
                'device_gateway': uhp_option.get('device_gateway'),
                'uhp_model': uhp_option.get('model'),
                # 'allow_local': Checkbox.OFF,
            })
            _ctrl_mode = nms_api.get_param(ctrl, 'mode')
            if _ctrl_mode not in ('DAMA_hub', 'DAMA_inroute'):
                for j in range(5):
                    nms_api.create(vno, 'station', {
                        'name': f'stn{j}',
                        'mode': ctrl_to_stn.get(_ctrl_mode),
                        'serial': 10000 + j,
                        'rx_controller': ctrl,
                        'enable': True
                    })
            else:
                nms_api.create(vno, 'station', {
                    'name': f'stn1',
                    'mode': ctrl_to_stn.get(_ctrl_mode),
                    'serial': 12345,
                    'rx_controller': ctrl,
                    'enable': True
                })
            uhp_driver.set_nms_permission(vlan=self.uhp_option.get('device_vlan'), password='')
            if not nms_api.wait_states(ctrl, ['Up', 'Down', 'Fault']):
                raise NmsControlledModeException('Controller is not in either Up, Down. Fault states')
            nms_api.wait_ticks(2)
            for _ in range(3):
                _uhp_profile = uhp_driver.get_active_profile_name()
                # Figure out Read timeout UHP!
                if _uhp_profile is None:
                    print('Probably read timeout, trying again!')
                    time.sleep(5)
                    continue
                else:
                    self.assertEqual(modes.get(_ctrl_mode), uhp_driver.get_active_profile_name())
