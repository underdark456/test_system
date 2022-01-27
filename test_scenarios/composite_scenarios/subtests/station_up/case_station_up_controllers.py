import time
from unittest import skip

from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.drivers.uhp.uhp_requests_driver import UhpRequestsDriver
from src.drivers.uhp.uhp_telnet_driver import UhpTelnetDriver
from src.enum_types_constants import ControllerModes, CheckboxStr, StationModes, RouteTypes, StationModesStr, \
    TdmaModcodStr, TdmaModcod, ControllerModesStr, RouteIds
from src.exceptions import InvalidOptionsException
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.nms import Nms
from src.nms_entities.basic_entities.service import Service
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.station_route import StationRoute
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider, API_CONNECT

__author__ = 'dkudryashov'
__version__ = '0.1'
options_path = 'test_scenarios.composite_scenarios.subtests.station_up'
backup_name = 'default_config.txt'


@skip('Skipped due to DAMA inroute issue')
class StationUpControllersCase(CustomTestCase):
    """Check if station is in UP state after switching to different controllers"""

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(options_path, API_CONNECT)
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)

        cls.nms = Nms(cls.driver, 0, 0)
        cls.class_logger.info(f'NMS version {cls.nms.get_version()}')

        cls.system_options = OptionsProvider.get_system_options(options_path)
        cls.options = OptionsProvider.get_options(options_path)
        cls.hub_ip = cls.system_options.get('uhp1_ip')
        cls.inr_ip = cls.system_options.get('uhp2_ip')
        cls.station_ip = cls.system_options.get('uhp3_ip')
        print(cls.hub_ip, cls.inr_ip, cls.station_ip)

        cls.hub_requests = UhpRequestsDriver(cls.hub_ip)
        cls.hub_requests.set_nms_permission(password='')
        cls.stn_requests = UhpRequestsDriver(cls.station_ip)
        cls.stn_telnet = UhpTelnetDriver(cls.station_ip)
        cls.stn_serial = cls.stn_requests.get_serial_number()
        cls.class_logger.info(f'UHP station at {cls.station_ip} '
                        f'SW {cls.stn_requests.get_software_version()}, serial={cls.stn_serial}')

        cls.net = Network.create(cls.driver, 0, {'name': 'test_net'})
        cls.tp = Teleport.create(
            cls.driver,
            cls.net.get_id(),
            {'name': 'test_tp', 'tx_lo': 0, 'rx1_lo': 0, 'rx2_lo': 0}
        )
        cls.service = Service.create(cls.driver, cls.net.get_id(), {'name': 'test_service'})
        cls.vno = Vno.create(cls.driver, cls.net.get_id(), {'name': 'test_vno'})

        cls.mf_hub_ctrl = Controller.create(cls.driver, cls.net.get_id(), {
            'name': 'mf_hub',
            'mode': ControllerModes.MF_HUB,
            'teleport': f'teleport:{cls.tp.get_id()}',
            'tx_on': CheckboxStr.ON,
            'tx_level': 20,
            'own_cn_high': 50,
        })

        cls.hubless_ctrl = Controller.create(cls.driver, cls.net.get_id(), {
            'name': 'hubless',
            'mode': ControllerModes.HUBLESS_MASTER,
            'teleport': f'teleport:{cls.tp.get_id()}',
            'tx_on': CheckboxStr.ON,
            'tx_level': 20,
            'own_cn_high': 50,
        })

        cls.dama_hub = Controller.create(cls.driver, cls.net.get_id(), {
            'name': 'dama_hub',
            'mode': ControllerModes.DAMA_HUB,
            'teleport': f'teleport:{cls.tp.get_id()}',
            'tx_on': CheckboxStr.ON,
            'tx_level': 20,
            'own_cn_high': 50,
            'a_dama_tx': CheckboxStr.ON,
            'a_dama_level': 20,
        })

        cls.dama_inr = Controller.create(cls.driver, cls.net.get_id(), {
            'name': 'dama_inr',
            'mode': ControllerModes.DAMA_INROUTE,
            'teleport': f'teleport:{cls.tp.get_id()}',
            'tx_controller': f'controller:{cls.dama_hub.get_id()}',
            'a_dama_tx': CheckboxStr.ON,
            'a_dama_level': 20,
        })
        # cls.inroute = Controller.create(cls.driver, cls.net.get_id(), {
        #     'name': 'test_inroute_ctrl',
        #     'mode': ControllerModes.INROUTE,
        #     'teleport': f'teleport:{cls.tp.get_id()}',
        # })

        cls.stn = Station.create(cls.driver, cls.vno.get_id(), {
            'name': 'test_stn',
            'enable': CheckboxStr.ON,
            'serial': cls.stn_serial,
            'mode': StationModes.RX_ONLY,
            # 'rx_controller': f'controller:{cls.mf_hub_ctrl.get_id()}'
        })
        # Leaving station IP untouched
        cls.stn_route = StationRoute.create(cls.driver, cls.stn.get_id(), {
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:{cls.service.get_id()}',
            'ip': cls.station_ip,
            'id': RouteIds.PRIVATE,
        })

    def test_station_up(self):
        st_time = time.perf_counter()
        number_of_cycles = self.options.get('number_of_cycles')
        for i in range(number_of_cycles):

            self.dama_hub.send_param('device_ip', self.hub_ip)
            self.dama_inr.send_param('device_ip', self.inr_ip)
            # Controller DAMA_inroute -> Station valid modes: DAMA
            for stn_mode in self.options.get(f'{self.dama_inr.get_param("mode").lower()}_valid_station_modes'):
                self.info(f'Testing controller DAMA_inroute, station {stn_mode}')
                self.stn.send_params({'mode': stn_mode, 'rx_controller': f'controller:{self.dama_inr.get_id()}'})
                # Make sure that the params are applied
                self.assertEqual(
                    stn_mode,
                    self.stn.get_param('mode'),
                    msg=f'{stn_mode} is not applied'
                )
                self.assertEqual(
                    f'controller:{self.dama_inr.get_id()} {self.dama_inr.get_param("name")}',
                    self.stn.get_param('rx_controller'),
                    msg=f'rx controller {self.dama_inr.get_param("mode")} is not applied'),
                # Testing station UP in DAMA mode
                if stn_mode == StationModesStr.DAMA:
                    self.dama_station(self.dama_inr)
                else:
                    raise InvalidOptionsException(f'{stn_mode} is not tested in DAMA_inroute controller mode')
            self.dama_hub.send_param('device_ip', '127.0.0.1')
            self.dama_inr.send_param('device_ip', '127.0.0.2')

            self.dama_hub.send_param('device_ip', self.hub_ip)
            # Controller DAMA_hub -> Station valid modes: DAMA
            for stn_mode in self.options.get(f'{self.dama_hub.get_param("mode").lower()}_valid_station_modes'):
                self.info(f'Testing controller DAMA_hub, station {stn_mode}')
                self.stn.send_params({'mode': stn_mode, 'rx_controller': f'controller:{self.dama_hub.get_id()}'})
                # Make sure that the params are applied
                self.assertEqual(
                    stn_mode,
                    self.stn.get_param('mode'),
                    msg=f'{stn_mode} is not applied'
                )
                self.assertEqual(
                    f'controller:{self.dama_hub.get_id()} {self.dama_hub.get_param("name")}',
                    self.stn.get_param('rx_controller'),
                    msg=f'rx controller {self.dama_hub.get_param("mode")} is not applied'),
                # Testing station UP in HUBLESS mode
                if stn_mode == StationModesStr.DAMA:
                    self.dama_station(self.dama_hub)
                elif stn_mode == StationModesStr.RX_ONLY:
                    self.rx_only_station(self.dama_hub)
                else:
                    raise InvalidOptionsException(f'{stn_mode} is not tested in DAMA_hub controller mode')
            self.dama_hub.send_param('device_ip', '127.0.0.1')

            # Controller MF HUB -> Station valid modes: STAR, Mesh, Hubless?
            self.mf_hub_ctrl.send_param('device_ip', self.hub_ip)
            for stn_mode in self.options.get(f'{self.mf_hub_ctrl.get_param("mode").lower()}_valid_station_modes'):
                self.info(f'Testing controller MF_Hub, station {stn_mode}')
                self.stn.send_params({'mode': stn_mode, 'rx_controller': f'controller:{self.mf_hub_ctrl.get_id()}'})
                # Make sure that the params are applied
                self.assertEqual(
                    stn_mode,
                    self.stn.get_param('mode'),
                    msg=f'{stn_mode} is not applied'
                )
                self.assertEqual(
                    f'controller:{self.mf_hub_ctrl.get_id()} {self.mf_hub_ctrl.get_param("name")}',
                    self.stn.get_param('rx_controller'),
                    msg=f'rx controller {self.mf_hub_ctrl.get_param("mode")} is not applied'),
                # Testing station UP in STAR mode
                if stn_mode == StationModesStr.STAR:
                    self.star_station(self.mf_hub_ctrl)
                # Testing station UP in MESH mode
                elif stn_mode == StationModesStr.MESH:
                    self.mesh_station(self.mf_hub_ctrl)
                else:
                    self.info('Not testing RX only station with MF hub controller now')
                    # self.rx_only_station(self.mf_hub_ctrl)
            self.mf_hub_ctrl.send_param('device_ip', '127.0.0.3')

            self.hubless_ctrl.send_param('device_ip', self.hub_ip)
            # Controller Hubless Master -> Station valid modes: Hubless
            for stn_mode in self.options.get(f'{self.hubless_ctrl.get_param("mode").lower()}_valid_station_modes'):
                self.info(f'Testing controller Hubless master, station {stn_mode}')
                self.stn.send_params({'mode': stn_mode, 'rx_controller': f'controller:{self.hubless_ctrl.get_id()}'})
                # Make sure that the params are applied
                self.assertEqual(
                    stn_mode,
                    self.stn.get_param('mode'),
                    msg=f'{stn_mode} is not applied'
                )
                self.assertEqual(
                    f'controller:{self.hubless_ctrl.get_id()} {self.hubless_ctrl.get_param("name")}',
                    self.stn.get_param('rx_controller'),
                    msg=f'rx controller {self.hubless_ctrl.get_param("mode")} is not applied'),
                # Testing station UP in HUBLESS mode
                if stn_mode == StationModesStr.HUBLESS:
                    self.hubless_station(self.hubless_ctrl)
                else:
                    raise InvalidOptionsException(f'{stn_mode} is not tested in Hubless mode')
            self.hubless_ctrl.send_param('device_ip', '127.0.0.4')

        self.info(f'Test execution time (number of cycles={number_of_cycles}) '
                  f'is {time.perf_counter() - st_time} seconds')

    def dama_station(self, ctrl):
        ctrl_mode = ctrl.get_param("mode")
        self.stn_telnet.send('pro 1 type manual damarem')
        if ctrl_mode == ControllerModesStr.DAMA_INROUTE:
            self.stn_telnet.send(f'pro 1 rx {self.dama_hub.get_param("tx_frq")} {self.dama_hub.get_param("tx_sr")}')
        else:
            self.stn_telnet.send(f'pro 1 rx {ctrl.get_param("tx_frq")} '
                                 f'{ctrl.get_param("tx_sr")}')
        self.stn_telnet.send('pro 1 autorun on')
        self.stn_telnet.send('pro 1 run')
        self.assertTrue(ctrl.wait_up(), msg=f'controller {ctrl_mode} is not in UP state')
        self.assertTrue(self.stn.wait_up(), msg=f'controller {ctrl_mode}, '
                                                f'station DAMA is not in UP state')

    def star_station(self, ctrl):
        self.stn_telnet.send('pro 1 type manual starrem')
        self.stn_telnet.send(f'pro 1 rx {ctrl.get_param("tx_frq")} '
                             f'{ctrl.get_param("tx_sr")}')
        self.stn_telnet.send('pro 1 mod on 200')
        self.stn_telnet.send('pro 1 autorun on')
        self.stn_telnet.send('pro 1 dtts source value')
        self.stn_telnet.send('pro 1 run')
        self.assertTrue(ctrl.wait_up(), msg=f'controller {ctrl.get_param("mode")} is not in UP state')
        self.assertTrue(self.stn.wait_up(), msg=f'controller {ctrl.get_param("mode")}, '
                                                f'station Star is not in UP state')

    def mesh_station(self, ctrl):
        self.stn_telnet.send('pro 1 type manual hmesh')
        self.stn_telnet.send(f'pro 1 rx {ctrl.get_param("tx_frq")} '
                             f'{ctrl.get_param("tx_sr")}')
        self.stn_telnet.send('pro 1 mod on 200')
        self.stn_telnet.send('pro 1 autorun on')
        self.stn_telnet.send('pro 1 dtts source value')
        self.stn_telnet.send('pro 1 run')

        self.assertTrue(ctrl.wait_up(), msg=f'controller {ctrl.get_param("mode")} is not in UP state')
        self.assertTrue(self.stn.wait_up(), msg=f'controller {ctrl.get_param("mode")}, '
                                                f'station Mesh is not in UP state')

    def hubless_station(self, ctrl):
        self.stn_telnet.send('pro 1 type manual slave')
        self.stn_telnet.send(f'pro 1 hubless tdma {ctrl.get_param("frame_length")} '
                             f'{ctrl.get_param("slot_length")} {ctrl.get_param("stn_number")}')
        i = [*TdmaModcodStr()].index(ctrl.get_param("tdma_mc"))
        if i is None:
            raise Exception('Cannot transform string TDMA modcod to the numeric value')
        self.stn_telnet.send(f'pro 1 hubless rf {ctrl.get_param("mf1_tx")} {ctrl.get_param("mf1_rx")} '
                             f'{ctrl.get_param("mf1_rx")} {ctrl.get_param("tdma_sr")} {int([*TdmaModcod()][i]) + 1}')
        self.stn_telnet.send('pro 1 mod on 200')
        self.stn_telnet.send('pro 1 autorun on')
        self.stn_telnet.send('pro 1 dtts source value')
        self.stn_telnet.send('pro 1 run')

        self.assertTrue(ctrl.wait_up(), msg=f'controller {ctrl.get_param("mode")} is not in UP state')
        self.assertTrue(self.stn.wait_up(), msg=f'controller {ctrl.get_param("mode")}, '
                                                f'station Hubless is not in UP state')

    def rx_only_station(self, ctrl):
        ctrl_mode = ctrl.get_param("mode")
        if ctrl_mode == 'MF_hub':
            self.stn_telnet.send('pro 1 type manual starrem')
            self.stn_telnet.send(f'pro 1 rx {ctrl.get_param("tx_frq")} '
                                 f'{ctrl.get_param("tx_sr")}')
        elif ctrl_mode == 'DAMA_hub':
            self.stn_telnet.send('pro 1 type manual damarem')
            self.stn_telnet.send(f'pro 1 rx {ctrl.get_param("tx_frq")} '
                                 f'{ctrl.get_param("tx_sr")}')
        elif ctrl_mode == 'Outroute':
            self.info('Outroute is not tested now')
            return
        # self.stn_telnet.send('pro 1 mod on 200')
        self.stn_telnet.send('pro 1 autorun on')
        self.stn_telnet.send('pro 1 dtts source value')
        self.stn_telnet.send('pro 1 run')

        self.assertTrue(ctrl.wait_up(), msg=f'controller {ctrl_mode} is not in UP state')
        self.assertTrue(self.stn.wait_up(), msg=f'controller {ctrl_mode}, '
                                                f'station RX_only is not in UP state')
