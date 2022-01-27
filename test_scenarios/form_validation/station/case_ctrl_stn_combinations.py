from src.backup_manager.backup_manager import BackupManager
from src.constants import NEW_OBJECT_ID
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes, StationModesStr, CheckboxStr
from src.exceptions import ObjectNotCreatedException
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.form_validation.station'
backup_name = 'default_config.txt'


class ControllerStationCombinationsCase(CustomTestCase):
    """Station's controller validation case"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.21'
    __execution_time__ = 3  # approximate test case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)

        cls.options = OptionsProvider.get_options(options_path)

        cls.net = Network.create(cls.driver, 0, {'name': 'test_net'})
        cls.tp = Teleport.create(cls.driver, 0, {'name': 'test_tp'})

        cls.mf_hub = Controller.create(cls.driver, 0, {
            'name': 'mf_hub',
            'mode': ControllerModes.MF_HUB,
            'teleport': 'teleport:0',
        })
        cls.outroute = Controller.create(cls.driver, 0, {
            'name': 'outroute',
            'mode': ControllerModes.OUTROUTE,
            'teleport': 'teleport:0',
        })
        cls.dama_hub = Controller.create(cls.driver, 0, {
            'name': 'dama_hub',
            'mode': ControllerModes.DAMA_HUB,
            'teleport': 'teleport:0',
        })

        cls.inroute = Controller.create(cls.driver, 0, {
            'name': 'inroute',
            'mode': ControllerModes.INROUTE,
            'teleport': 'teleport:0',
            'tx_controller': f'controller:{cls.mf_hub.get_id()}',
            'inroute': 2,
        })
        cls.dama_inroute = Controller.create(cls.driver, 0, {
            'name': 'dama_inr',
            'mode': ControllerModes.DAMA_INROUTE,
            'teleport': 'teleport:0',
            'tx_controller': f'controller:{cls.dama_hub.get_id()}',
        })
        cls.mf_inroute = Controller.create(cls.driver, 0, {
                'name': 'mf_inr',
                'mode': ControllerModes.MF_INROUTE,
                'teleport': 'teleport:0',
        })

        cls.hubless = Controller.create(cls.driver, 0, {
            'name': 'hubless',
            'mode': ControllerModes.HUBLESS_MASTER,
            'teleport': 'teleport:0',
        })
        cls.gateway_mf_hub = Controller.create(cls.driver, 0, {
                'name': 'gateway_mf_hub',
                'mode': ControllerModes.GATEWAY,
                'tx_controller': f'controller:{cls.mf_hub.get_id()}',
                'teleport': 'teleport:0',
        })
        cls.gateway_dama_hub = Controller.create(cls.driver, 0, {
                'name': 'gateway_dama_hub',
                'mode': ControllerModes.GATEWAY,
                'tx_controller': f'controller:{cls.dama_hub.get_id()}',
                'teleport': 'teleport:0',
        })
        cls.gateway_outroute = Controller.create(cls.driver, 0, {
                'name': 'gateway_outroute',
                'mode': ControllerModes.GATEWAY,
                'tx_controller': f'controller:{cls.outroute.get_id()}',
                'teleport': 'teleport:0',
        })

        cls.controllers = (
            cls.mf_hub,
            cls.outroute,
            cls.dama_hub,
            cls.hubless,
            cls.inroute,
            cls.dama_inroute,
            cls.mf_inroute,
            cls.gateway_mf_hub,
            cls.gateway_dama_hub,
            cls.gateway_outroute,
        )

        cls.vno = Vno.create(cls.driver, 0, {'name': 'test_vno'})

        cls.next_serial = 1

    def test_rx_controllers(self):
        """Star, Mesh, Hubless, Dama stations valid RX controllers"""
        for stn_mode in (StationModesStr.STAR, StationModesStr.MESH, StationModesStr.HUBLESS):
            for ctrl in self.controllers:
                ctrl_mode = ctrl.read_param('mode')
                with self.subTest(f'rx_controller={ctrl_mode}, station={stn_mode}'):
                    self.next_serial += 1
                    stn = Station(self.driver, self.vno.get_id(), NEW_OBJECT_ID, {
                        'name': f'stn-{self.next_serial}',
                        'serial': self.next_serial,
                        'mode': stn_mode,
                        'enable': CheckboxStr.ON,
                        'rx_controller': f'controller:{ctrl.get_id()}',
                    })
                    if ctrl_mode not in self.options.get(f'{stn_mode.lower()}_valid_ctrl_modes'):
                        with self.assertRaises(ObjectNotCreatedException, msg='Station created'):
                            stn.save()
                    else:
                        stn.save()
                        self.assertIsNotNone(stn.get_id(), msg=f'Station is not created')

    def test_rx_controllers_dama(self):
        next_dama_ab = 0
        for ctrl in self.controllers:
            ctrl_mode = ctrl.read_param('mode')
            with self.subTest(f'rx_controller={ctrl_mode}, station=dama'):
                self.next_serial += 1
                stn = Station(self.driver, self.vno.get_id(), NEW_OBJECT_ID, {
                    'name': f'stn-{self.next_serial}',
                    'serial': self.next_serial,
                    'mode': StationModesStr.DAMA,
                    'enable': CheckboxStr.ON,
                    'dama_ab': next_dama_ab,
                    'rx_controller': f'controller:{ctrl.get_id()}',
                })
                if ctrl_mode not in self.options.get('dama_valid_ctrl_modes'):
                    with self.assertRaises(ObjectNotCreatedException, msg='Station created'):
                        stn.save()
                else:
                    stn.save()
                    self.assertIsNotNone(stn.get_id(), msg=f'Station is not created')
                    next_dama_ab += 1

    def test_tx_controllers(self):
        """RX_only station valid TX controllers"""
        stn_mode = StationModesStr.RX_ONLY
        for ctrl in self.controllers:
            ctrl_mode = ctrl.read_param('mode')
            with self.subTest(f'tx_controller={ctrl_mode}, station={stn_mode}'):
                self.next_serial += 1
                stn = Station(self.driver, self.vno.get_id(), NEW_OBJECT_ID, {
                    'name': f'stn_rx_only-{self.next_serial}',
                    'serial': self.next_serial,
                    'mode': stn_mode,
                    'enable': CheckboxStr.ON,
                    'tx_controller': f'controller:{ctrl.get_id()}',
                })
                if ctrl_mode not in self.options.get(f'{stn_mode.lower()}_valid_ctrl_modes'):
                    with self.assertRaises(ObjectNotCreatedException, msg='Station created'):
                        stn.save()
                else:
                    stn.save()
                    self.assertIsNotNone(stn.get_id(), msg=f'Station is not created')

    def test_ext_gateway(self):
        """Star, Mesh stations valid RX controllers and External Gateway"""
        for stn_mode in (StationModesStr.STAR, StationModesStr.MESH):
            for ctrl in (self.mf_hub, self.dama_hub, self.outroute):
                ctrl_mode = ctrl.read_param('mode')
                for gateway in (self.gateway_mf_hub, self.gateway_dama_hub, self.gateway_outroute):
                    gateway_tx_ctrl_mode = gateway.read_param('tx_controller').split()[-1]
                    with self.subTest(f'Station={stn_mode}, rx_controller={ctrl_mode},'
                                      f' ext_gateway mode={gateway_tx_ctrl_mode}'):
                        stn = Station(self.driver, self.vno.get_id(), NEW_OBJECT_ID, {
                            'name': f'stn_with_gw-{self.next_serial}',
                            'serial': self.next_serial,
                            'mode': stn_mode,
                            'enable': CheckboxStr.ON,
                            'rx_controller': f'controller:{ctrl.get_id()}',
                            'ext_gateway': f'controller:{gateway.get_id()}',
                        })
                        self.next_serial += 1
                        if ctrl_mode.lower() != gateway_tx_ctrl_mode.lower():
                            with self.assertRaises(ObjectNotCreatedException, msg='station created'):
                                stn.save()
                        elif ctrl_mode not in self.options.get(f'{stn_mode.lower()}_valid_ctrl_modes'):
                            with self.assertRaises(ObjectNotCreatedException, msg='station created2'):
                                stn.save()
                        else:
                            stn.save()
                            self.assertIsNotNone(stn.get_id(), msg=f'station is not created')
