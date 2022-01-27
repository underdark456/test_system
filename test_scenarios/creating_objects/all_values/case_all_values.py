from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes, ModcodModes, ModcodModesStr, TdmaModcod, \
    TdmaModcodStr
from src.nms_entities.basic_entities.access import Access
from src.nms_entities.basic_entities.alert import Alert
from src.nms_entities.basic_entities.bal_controller import BalController
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.dashboard import Dashboard
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.server import Server
from src.nms_entities.basic_entities.shaper import Shaper
from src.nms_entities.basic_entities.sr_controller import SrController
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.user_group import UserGroup
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.creating_objects.all_values'
backup_name = 'default_config.txt'


class AllValuesCase(CustomTestCase):
    """Create objects by passing all parameters"""
    # The current class contains tests that create objects using API and passing all the existing values for an object.

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.23'
    __execution_time__ = 75  # approximate test case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()
        cls.options = OptionsProvider.get_options(options_path)

    def set_up(self) -> None:
        self.backup.apply_backup(backup_name)

    def test_server(self):
        """Create server by passing all parameters"""
        ser = Server.create(self.driver, 0, params=self.options.get('server'))
        self.assertIsNotNone(ser.get_id(), msg='server is not created')
        for key, value in self.options.get('server').items():
            self.assertEqual(value, ser.read_param(key).strip())

    def test_user_group(self):
        """Create user group by passing all parameters"""
        gr = UserGroup.create(self.driver, 0, params=self.options.get('user_group'))
        self.assertIsNotNone(gr.get_id(), msg='user group is not created')
        for key, value in self.options.get('user_group').items():
            self.assertEqual(value, gr.read_param(key).strip())

    def test_alert(self):
        """Create alert by passing all parameters"""
        al = Alert.create(self.driver, 0, params=self.options.get('alert'))
        self.assertIsNotNone(al.get_id(), msg='alert is not created')
        for key, value in self.options.get('alert').items():
            self.assertEqual(value, al.read_param(key).strip())

    def test_access(self):
        """Create access by passing all parameters"""
        UserGroup.create(self.driver, 0, params={'name': 'test_gr'})
        access = Access.create(self.driver, 0, params=self.options.get('access'))
        self.assertIsNotNone(access.get_id(), msg='access is not created')
        for key, value in self.options.get('access').items():
            if key == 'group':
                self.assertEqual(value, access.read_param(key).split()[0])
            else:
                self.assertEqual(value, access.read_param(key).strip())

    def test_dashboard(self):
        """Create dashboard by passing all parameters"""
        dash = Dashboard.create(self.driver, 0, params={'name': 'sample_dash'})
        self.assertIsNotNone(dash.get_id(), msg='dashboard is not created')
        self.assertEqual('sample_dash', dash.read_param('name'))

    def test_network(self):
        """Create network by passing all parameters"""
        Alert.create(self.driver, 0, params={'name': 'al_net', 'popup': True})
        net = Network.create(self.driver, 0, params=self.options.get('network'))
        self.assertIsNotNone(net.get_id(), msg='network is not created')
        for key, value in self.options.get('network').items():
            if key == 'set_alert':
                self.assertEqual(value, net.read_param(key).split()[0])
            else:
                self.assertEqual(str(value), str(net.read_param(key)).strip())

    def test_teleport(self):
        """Create teleport by passing all parameters"""
        net = Network.create(self.driver, 0, params={'name': 'sample_net'})
        tp = Teleport.create(self.driver, net.get_id(), params=self.options.get('teleport'))
        self.assertIsNotNone(tp.get_id(), msg='teleport is not created')
        for key, value in self.options.get('teleport').items():
            self.assertEqual(str(value), str(tp.read_param(key)).strip())

    def test_mf_hub(self):
        """Create MF hub by passing all parameters"""
        net = Network.create(self.driver, 0, params={'name': 'sample_net'})
        Alert.create(self.driver, 0, params={'name': 'al_net', 'popup': True})
        SrController.create(self.driver, 0, params={'name': 'sample_sr_ctrl'})
        BalController.create(self.driver, 0, params={'name': 'sample_ba_ctrl'})
        Teleport.create(self.driver, 0, params={'name': 'sample_tp', 'sat_name': 'sat'})
        hub = Controller.create(self.driver, net.get_id(), params=self.options.get('mf_hub'))
        self.assertIsNotNone(hub.get_id(), msg='MF HUB is not created')
        for key, value in self.options.get('mf_hub').items():
            if key in ('set_alert', 'teleport', 'bal_controller'):
                self.assertEqual(
                    value,
                    hub.read_param(key).split()[0],
                    msg=f'MF hub set {key}={value}, got {key}={hub.read_param(key).split()[0]}'
                )
            elif key in ('tx_level_adj', 'acm_thr', 'tlc_cn_stn', 'tx_level', 'tlc_max_lvl', 'own_cn_low',
                         'own_cn_high', 'tlc_cn_hub', 'tdma_leg_thr', 'tdma_thr_acm', 'lowest_cn', 'relative_cn'):
                self.assertEqual(
                    str(float(value)),
                    str(hub.read_param(key)).strip(),
                    msg=f'MF hub set {key}={value}, got {key}={str(hub.read_param(key)).strip()}'
                )
            elif key == 'tx_modcod' or key.startswith('acm_mc'):
                i = [*ModcodModes()].index(str(value))
                self.assertEqual(
                    [*ModcodModesStr()][i],
                    hub.read_param(key),
                    msg=f'MF hub set {key}={[*ModcodModesStr()][i]}, got {key}={hub.read_param(key)}'
                )
            elif key in ('tdma_mc', 'mesh_mc'):
                i = [*TdmaModcod()].index(str(value))
                self.assertEqual(
                    [*TdmaModcodStr()][i],
                    hub.read_param(key),
                    msg=f'MF hub set {key}={[*TdmaModcodStr()][i]}, got {key}={hub.read_param(key)}'
                )
            else:
                self.assertEqual(
                    str(value),
                    str(hub.read_param(key)).strip(),
                    msg=f'MF hub set {key}={value}, got {key}={str(hub.read_param(key)).strip()}'
                )

    def test_outroute(self):
        """Create Outroute by passing all parameters"""
        net = Network.create(self.driver, 0, params={'name': 'sample_net'})
        Alert.create(self.driver, 0, params={'name': 'al_net', 'popup': True})
        SrController.create(self.driver, 0, params={'name': 'sample_sr_ctrl'})
        Teleport.create(self.driver, 0, params={'name': 'sample_tp', 'sat_name': 'sat'})
        outroute = Controller.create(self.driver, net.get_id(), params=self.options.get('outroute'))
        self.assertIsNotNone(outroute.get_id())
        for key, value in self.options.get('outroute').items():
            if key in ('set_alert', 'teleport', 'bal_controller'):
                self.assertEqual(
                    value,
                    outroute.read_param(key).split()[0],
                    msg=f'Outroute set {key}={value}, got {key}={outroute.read_param(key).split()[0]}'
                )
            elif key in ('tx_level_adj', 'acm_thr', 'tlc_cn_stn', 'tx_level', 'tlc_max_lvl', 'own_cn_low',
                         'own_cn_high', 'tlc_cn_hub', 'tdma_leg_thr', 'tdma_thr_acm', 'lowest_cn', 'relative_cn'):
                self.assertEqual(
                    str(float(value)),
                    str(outroute.read_param(key)).strip(),
                    msg=f'Outroute set {key}={float(value)}, got {key}={str(outroute.read_param(key)).strip()}'
                )
            elif key == 'tx_modcod' or key.startswith('acm_mc'):
                i = [*ModcodModes()].index(str(value))
                self.assertEqual(
                    [*ModcodModesStr()][i],
                    outroute.read_param(key),
                    msg=f'Outroute set {key}={[*ModcodModesStr()][i]}, got {key}={outroute.read_param(key)}'
                )
            elif key == 'tdma_mc':
                i = [*TdmaModcod()].index(str(value))
                self.assertEqual(
                    [*TdmaModcodStr()][i],
                    outroute.read_param(key),
                    msg=f'Outroute set {key}={[*TdmaModcodStr()][i]}, got {key}={outroute.read_param(key)}'
                )
            else:
                self.assertEqual(
                    str(value),
                    str(outroute.read_param(key)).strip(),
                    msg=f'Outroute set {key}={str(value)}, got {key}={str(outroute.read_param(key)).strip()}'
                )

    def test_dama_hub(self):
        """Create DAMA hub by passing all parameters"""
        net = Network.create(self.driver, 0, params={'name': 'sample_net'})
        Alert.create(self.driver, 0, params={'name': 'al_net', 'popup': True})
        SrController.create(self.driver, 0, params={'name': 'sample_sr_ctrl'})
        Teleport.create(self.driver, 0, params={'name': 'sample_tp', 'sat_name': 'sat'})
        dama_hub = Controller.create(self.driver, net.get_id(), params=self.options.get('dama_hub'))
        self.assertIsNotNone(dama_hub.get_id())
        for key, value in self.options.get('dama_hub').items():
            if key in ('set_alert', 'teleport', 'bal_controller', 'sr_controller'):
                self.assertEqual(
                    value,
                    dama_hub.read_param(key).split()[0],
                    msg=f'DAMA hub set {key}={value}, got {key}={dama_hub.read_param(key).split()[0]}'
                )
            elif key in ('a_dama_level', 'b_dama_level', 'acm_thr', 'tx_level', 'tlc_max_lvl', 'tlc_cn_stn',
                         'a_dama_cn_hub', 'b_dama_cn_hub'):
                self.assertEqual(
                    str(float(value)),
                    str(dama_hub.read_param(key)).strip(),
                    msg=f'DAMA hub set {key}={float(value)}, got {key}={str(dama_hub.read_param(key)).strip()}'
                )
            elif key in ('tx_modcod', 'a_dama_modcod', 'b_dama_modcod') or key.startswith('acm_mc'):
                i = [*ModcodModes()].index(str(value))
                self.assertEqual(
                    [*ModcodModesStr()][i],
                    dama_hub.read_param(key),
                    msg=f'DAMA hub set {key}={[*ModcodModesStr()][i]}, got {key}={dama_hub.read_param(key)}'
                )
            elif key == 'tdma_mc':
                i = [*TdmaModcod()].index(str(value))
                self.assertEqual(
                    [*TdmaModcodStr()][i],
                    dama_hub.read_param(key),
                    msg=f'DAMA hub set {key}={[*TdmaModcodStr()][i]}, got {key}={dama_hub.read_param(key)}'
                )
            else:
                self.assertEqual(
                    str(value),
                    str(dama_hub.read_param(key)).strip(),
                    msg=f'DAMA hub set {key}={str(value)}, got {key}={str(dama_hub.read_param(key)).strip()}'
                )

    def test_hubless_master(self):
        """Create Hubless master by passing all parameters"""
        net = Network.create(self.driver, 0, params={'name': 'sample_net'})
        Alert.create(self.driver, 0, params={'name': 'al_net', 'popup': True})
        SrController.create(self.driver, 0, params={'name': 'sample_sr_ctrl'})
        Teleport.create(self.driver, 0, params={'name': 'sample_tp', 'sat_name': 'sat'})
        Shaper.create(self.driver, 0, params={'name': 'sample_shaper'})
        hubless = Controller.create(self.driver, net.get_id(), params=self.options.get('hubless_master'))
        self.assertIsNotNone(hubless.get_id())
        for key, value in self.options.get('hubless_master').items():
            if key in ('set_alert', 'teleport', 'bal_controller', 'hub_shaper'):
                self.assertEqual(
                    value,
                    hubless.read_param(key).split()[0],
                    msg=f'Hubless set {key}={value}, got {key}={hubless.read_param(key).split()[0]}'
                )
            elif key in ('tx_level', 'tlc_max_lvl', 'tlc_cn_stn', 'own_cn_low', 'own_cn_high', 'tlc_cn_hub'):
                self.assertEqual(
                    str(float(value)),
                    str(hubless.read_param(key)).strip(),
                    msg=f'Hubless set {key}={float(value)}, got {key}={str(hubless.read_param(key)).strip()}'
                )
            elif key == 'tdma_mc':
                i = [*TdmaModcod()].index(str(value))
                self.assertEqual(
                    [*TdmaModcodStr()][i],
                    hubless.read_param(key),
                    msg=f'Hubless set {key}={[*TdmaModcodStr()][i]}, got {key}={hubless.read_param(key)}'
                )
            else:
                self.assertEqual(
                    str(value),
                    str(hubless.read_param(key)).strip(),
                    msg=f'Hubless set {key}={str(value)}, got {key}={str(hubless.read_param(key)).strip()}'
                )

    def test_inroute(self):
        """Create Inroute by passing all parameters"""
        net = Network.create(self.driver, 0, params={'name': 'sample_net'})
        Alert.create(self.driver, 0, params={'name': 'al_net', 'popup': True})
        Teleport.create(self.driver, 0, params={'name': 'sample_tp', 'sat_name': 'sat'})
        Controller.create(self.driver, 0, params={
            'name': 'sample_ctrl',
            'mode': ControllerModes.OUTROUTE,
            'teleport': 'teleport:0'
        })
        SrController.create(self.driver, 0, params={'name': 'sample_sr_ctrl'})
        BalController.create(self.driver, 0, params={'name': 'sample_ba_ctrl'})
        inroute = Controller.create(self.driver, net.get_id(), params=self.options.get('inroute'))
        self.assertIsNotNone(inroute.get_id())
        for key, value in self.options.get('inroute').items():
            if key in ('set_alert', 'teleport', 'bal_controller', 'hub_shaper', 'tx_controller'):
                self.assertEqual(
                    value,
                    inroute.read_param(key).split()[0],
                    msg=f'Inroute set {key}={value}, got {key}={inroute.read_param(key).split()[0]}'
                )
            elif key in ('tx_level', 'own_cn_low', 'own_cn_high', 'tlc_cn_hub', 'tx_level_adj', 'tdma_thr_acm',
                         'lowest_cn', 'relative_cn'):
                self.assertEqual(
                    str(float(value)),
                    str(inroute.read_param(key)).strip(),
                    msg=f'Inroute set {key}={float(value)}, got {key}={str(inroute.read_param(key)).strip()}'
                )
            elif key == 'tdma_mc':
                i = [*TdmaModcod()].index(str(value))
                self.assertEqual(
                    [*TdmaModcodStr()][i],
                    inroute.read_param(key),
                    msg=f'Inroute set {key}={[*TdmaModcodStr()][i]}, got {key}={inroute.read_param(key)}'
                )
            else:
                self.assertEqual(
                    str(value),
                    str(inroute.read_param(key)).strip(),
                    msg=f'Inroute set {key}={str(value)}, got {key}={str(inroute.read_param(key)).strip()}'
                )

    def test_dama_inroute(self):
        """Create DAMA inroute by passing all parameters"""
        net = Network.create(self.driver, 0, params={'name': 'sample_net'})
        Alert.create(self.driver, 0, params={'name': 'al_net', 'popup': True})
        Teleport.create(self.driver, 0, params={'name': 'sample_tp', 'sat_name': 'sat'})
        Controller.create(self.driver, 0, params={
            'name': 'sample_ctrl',
            'mode': ControllerModes.DAMA_HUB,
            'teleport': 'teleport:0',
        })
        SrController.create(self.driver, 0, params={'name': 'sample_sr_ctrl'})

        dama_inroute = Controller.create(self.driver, net.get_id(), params=self.options.get('dama_inroute'))
        self.assertIsNotNone(dama_inroute.get_id())
        for key, value in self.options.get('dama_inroute').items():
            if key in ('set_alert', 'teleport', 'bal_controller', 'hub_shaper', 'tx_controller'):
                self.assertEqual(
                    value,
                    dama_inroute.read_param(key).split()[0],
                    msg=f'DAMA inroute set {key}={value}, got {key}={dama_inroute.read_param(key).split()[0]}'
                )
            elif key in ('tx_level', 'own_cn_low', 'own_cn_high', 'tlc_cn_hub', 'tx_level_adj', 'tdma_thr_acm',
                         'a_dama_cn_hub', 'b_dama_cn_hub', 'a_dama_level', 'b_dama_level'):
                self.assertEqual(
                    str(float(value)),
                    str(dama_inroute.read_param(key)).strip(),
                    msg=f'DAMA inroute set {key}={float(value)}, got {key}={str(dama_inroute.read_param(key)).strip()}'
                )
            elif key in ('tx_modcod', 'a_dama_modcod', 'b_dama_modcod') or key.startswith('acm_mc'):
                i = [*ModcodModes()].index(str(value))
                self.assertEqual(
                    [*ModcodModesStr()][i],
                    dama_inroute.read_param(key),
                    msg=f'DAMA hub set {key}={[*ModcodModesStr()][i]}, got {key}={dama_inroute.read_param(key)}'
                )
            else:
                self.assertEqual(
                    str(value),
                    str(dama_inroute.read_param(key)).strip(),
                    msg=f'DAMA inroute set {key}={str(value)}, got {key}={str(dama_inroute.read_param(key)).strip()}'
                )

    def test_mf_inroute(self):
        """Create MF inroute by passing all parameters"""
        net = Network.create(self.driver, 0, params={'name': 'sample_net'})
        Alert.create(self.driver, 0, params={'name': 'al_net', 'popup': True})
        SrController.create(self.driver, 0, params={'name': 'sample_sr_ctrl'})
        Teleport.create(self.driver, 0, params={'name': 'sample_tp', 'sat_name': 'sat'})
        mf_inroute = Controller.create(self.driver, net.get_id(), params=self.options.get('mf_inroute'))
        self.assertIsNotNone(mf_inroute.get_id())

    def test_gateway(self):
        """Create Gateway by passing all parameters"""
        net = Network.create(self.driver, 0, params={'name': 'sample_net'})
        Alert.create(self.driver, 0, params={'name': 'al_net', 'popup': True})
        Teleport.create(self.driver, 0, params={'name': 'sample_tp', 'sat_name': 'sat'})
        Controller.create(self.driver, 0, params={
            'name': 'sample_ctrl',
            'mode': ControllerModes.MF_HUB,
            'teleport': 'teleport:0',
        })
        SrController.create(self.driver, 0, params={'name': 'sample_sr_ctrl'})

        gateway = Controller.create(self.driver, net.get_id(), params=self.options.get('gateway'))
        self.assertIsNotNone(gateway.get_id())
