import json
import time

from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import Checkbox, StationModes, ControllerModes, RouteTypes, RouteIds, LanCheckModes
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.service import Service
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.station_route import StationRoute
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.statistics.faults'
backup_name = 'default_config.txt'


# TODO: make the rest test methods
class ObjectFaultsCase(CustomTestCase):
    """Trigger most UHP and NMS faults for controller and station"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.27'
    __execution_time__ = 750
    __express__ = True

    @classmethod
    def set_up_class(cls):
        cls.controllers, cls.stations = OptionsProvider.get_uhp_controllers_stations(1, ['UHP200', ], 1, ['ANY', ])
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(options_path), driver_id='case_object_faults'
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)
        cls.options = OptionsProvider.get_options(options_path)

        # UHPs configuration
        cls.mf_hub_uhp = cls.controllers[0].get('web_driver')
        cls.mf_hub_uhp.set_nms_permission(vlan=cls.controllers[0].get('device_vlan'), password='')

        cls.stn1_uhp = cls.stations[0].get('web_driver')
        cls.stn1_uhp.star_station(params={
            'rx1_frq': 970_000,
            'rx1_sr': 3000,
            'tx_level': cls.options.get('tx_level'),
        })

        # NMS configuration
        cls.network = Network.create(cls.driver, 0, {'name': 'net', 'dev_password': ''})
        cls.teleport = Teleport.create(cls.driver, cls.network.get_id(), {
            'name': 'teleport',
            'rx1_lo': 0,
            'rx2_lo': 0,
            'tx_lo': 0
        })
        cls.mf_hub = Controller.create(cls.driver, cls.network.get_id(), {
            'name': 'mf_hub',
            'mode': ControllerModes.MF_HUB,
            'teleport': f'teleport:{cls.teleport.get_id()}',
            'uhp_model': cls.controllers[0].get('model'),
            'device_ip': cls.controllers[0].get('device_ip'),
            'device_vlan': cls.controllers[0].get('device_vlan'),
            'device_gateway': cls.controllers[0].get('device_gateway'),
            'rx1_frq': 970_000,
            'rx1_sr': 3000,
            'tx_frq': 970_000,
            'tx_sr': 3000,
            'tx_on': Checkbox.ON,
            'tx_level': cls.options.get('tx_level'),
        })
        cls.local_ser = Service.create(cls.driver, cls.network.get_id(), {
                'name': 'local_ser',
                'hub_vlan': cls.controllers[0].get('device_vlan'),
                'stn_vlan': cls.stations[0].get('device_vlan')
        })
        cls.vno = Vno.create(cls.driver, cls.network.get_id(), {'name': 'vno'})
        cls.stn1 = Station.create(cls.driver, cls.vno.get_id(), {
            'name': 'stn1',
            'serial': cls.stations[0].get('serial'),
            'enable': Checkbox.OFF,
            'mode': StationModes.STAR,
            'rx_controller': f'controller:{cls.mf_hub.get_id()}',
        })
        StationRoute.create(cls.driver, cls.stn1.get_id(), {
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:{cls.local_ser.get_id()}',
            'ip': cls.stations[0].get('device_ip'),
            'id': RouteIds.PRIVATE,
        })
        StationRoute.create(cls.driver, cls.stn1.get_id(), {
            'type': RouteTypes.STATIC_ROUTE,
            'service': f'service:{cls.local_ser.get_id()}',
            'ip': '0.0.0.0',
            'mask': '/0',
            'gateway': cls.stations[0].get('device_gateway'),
            'id': RouteIds.PRIVATE,
        })
        cls.stn1.send_param('enable', Checkbox.ON)
        cls.backup.create_backup('temp.txt', local=False)

    def set_up(self):
        self.assertTrue(self.stn1_uhp.set_site_setup({'dvb_search': 800}), msg='Cannot set UHP Station dvb_search=800')
        self.assertTrue(
            self.stn1_uhp.set_profile_tdm_rx(
                params={'rx1_frq': 970_000, 'rx1_sr': 3000}
            ),
            msg=f'Cannot set UHP Station rx1_frq=970000, rx1_sr=3000'
        )
        self.assertTrue(
            self.stn1_uhp.set_profile_tlc(
                params={'tlc_enable': Checkbox.OFF}
            ),
            msg=f'Cannot set UHP station tlc_enable=0'
        )
        self.backup.apply_backup('temp.txt', local=False)
        self.assertTrue(self.mf_hub.wait_up(timeout=60), msg=f'MF hub is not Up within timeout, '
                                                             f'state is {self.mf_hub.read_param("state")}')
        self.assertTrue(self.stn1.wait_up(timeout=60), msg=f'Station 1 is not up within timeout, '
                                                           f'state is {self.stn1.read_param("state")}')

    def test_demod1(self):
        """DEMOD1 fault indication in MF Hub and Star station"""
        self.teleport.send_param('dvb_search', 100)
        self.mf_hub.send_param('rx1_frq', 970_000 + 100)
        self.stn1_uhp.set_site_setup({'dvb_search': 100})
        self.stn1_uhp.set_profile_tdm_rx(params={
            'rx1_frq': 970_000 + 100,
            'rx1_sr': 3000,
        })
        self.assertTrue(
            self.mf_hub.wait_state(Controller.FAULT, timeout=60),
            msg=f'MF Hub is not in Fault after setting DVB search'
        )
        self.assertTrue(self.mf_hub.wait_faults([Controller.RX1_FAULT]), msg=f'MF Hub RX1 fault is not shown')
        self.assertTrue(self.stn1.wait_state(Station.FAULT), msg=f'Station is not in Fault after setting DVB search')
        self.assertTrue(self.stn1.wait_faults([Station.RX1_FAULT]), msg=f'Station RX1 fault is not shown')

    def test_tx(self):
        """TX fault indication in MF Hub and Star Station"""
        self.mf_hub.send_params({'tlc_enable': Checkbox.ON, 'tlc_max_lvl': self.options.get('tx_level') + 1})
        self.stn1_uhp.set_profile_tlc(
            params={'tlc_enable': Checkbox.ON, 'tlc_max_lvl': self.options.get('tx_level') + 1}
        )
        self.assertTrue(
            self.mf_hub.wait_state(Controller.FAULT, timeout=60),
            msg=f'MF Hub is not in Fault after setting TLC'
        )
        self.assertTrue(self.mf_hub.wait_faults([Controller.TX_FAULT]), msg=f'MF Hub TX fault is not shown')
        self.assertTrue(self.stn1.wait_state(Station.FAULT), msg=f'Station is not in Fault after setting TLC')
        self.assertTrue(self.stn1.wait_faults([Station.TX_FAULT]), msg=f'Station TX fault is not shown')

    def test_net(self):
        """NETWORK fault indication in MF Hub and Star Station"""
        # TODO: finalize when Question 8531 is answered
        pass

    def test_qos(self):
        """QOS fault indication in MF Hub and Star Station"""
        self.mf_hub.send_params({'sm_enable': Checkbox.ON, 'lan_rx_check': LanCheckModes.LOWER, 'rx_check_rate': 1000})
        self.stn1.send_params({'sm_enable': Checkbox.ON, 'lan_rx_check': LanCheckModes.LOWER, 'rx_check_rate': 1000})
        self.assertTrue(self.mf_hub.wait_state(Controller.FAULT), msg=f'MF Hub is not in Fault after setting SM')
        self.assertTrue(self.mf_hub.wait_faults([Controller.QOS_FAULT]), msg=f'MF Hub QOS fault is not shown')
        self.assertTrue(self.stn1.wait_state(Station.FAULT), msg=f'Station is not in Fault after setting SM')
        self.assertTrue(self.stn1.wait_faults([Station.QOS_FAULT]), msg=f'Station QOS fault is not shown')

    def test_system(self):
        """SYSTEM fault indication in MF Hub and Star Station"""
        self.mf_hub_uhp.network_script('co sa 0')
        time.sleep(5)
        self.mf_hub_uhp.reboot()
        self.stn1_uhp.network_script('co sa 0')
        time.sleep(20)
        self.stn1_uhp.reboot()
        self.mf_hub_uhp.set_nms_permission(vlan=self.controllers[0].get('device_vlan'), password='')

        self.assertTrue(
            self.mf_hub.wait_state(Controller.FAULT, timeout=60),
            msg=f'MF Hub is not in either Fault or Down state after reboot, '
                f'state is {self.mf_hub.read_param("state")}'
        )
        self.assertTrue(
            self.mf_hub.wait_faults(Controller.SYSTEM_FAULT, strict=False),
            msg=f'MF Hub, SYSTEM fault is not shown'
        )
        self.assertTrue(
            self.stn1.wait_state(Station.FAULT, timeout=60),
            msg=f'Station is not in Fault state after reboot, state is {self.stn1.read_param("state")}'
        )
        self.assertTrue(
            self.stn1.wait_faults(Station.SYSTEM_FAULT, strict=False),
            msg=f'Station, SYSTEM fault is not shown'
        )

    def test_down(self):
        """DOWN fault indication in MF Hub"""
        params = {'rx1_frq': self.mf_hub.read_param('rx1_frq') + 5000, 'own_cn_low': 0}
        self.mf_hub.send_params(params)
        self.assertTrue(self.mf_hub.wait_state(Controller.DOWN), msg=f'MF Hub is not in fault state '
                                                                     f'after setting {json.dumps(params)}')
        faults = self.mf_hub.get_faults()
        self.assertEqual(
            Controller.DOWN_FAULT,
            faults,
            msg=f'MF Hub, expected {Controller.DOWN}, actual {faults}'
        )

    def test_hub_low(self):
        """C/N on hub is low fault indication in MF Hub and Star Station"""
        hub_params = {'own_cn_low': 50, 'own_cn_high': 50}
        stn_params = {'hub_low_cn': 25.5, 'hub_high_cn': 25.5}
        self.next_hub_stn_fault(Controller.HUB_CN_LOW_FAULT, hub_params, stn_params)

    def test_hub_high(self):
        """C/N on hub is high fault indication in MF Hub and Star Station"""
        hub_params = {'own_cn_low': 0, 'own_cn_high': 0}
        stn_params = {'hub_low_cn': 0, 'hub_high_cn': 0}
        self.next_hub_stn_fault(Controller.HUB_CN_HIGH_FAULT, hub_params, stn_params)

    def test_stn_low(self):
        """C/N on station is low fault indication in Star Station"""
        self.stn1.send_params({'station_low_cn': 25.5, 'station_high_cn': 25.5})
        self.assertTrue(self.stn1.wait_state(Station.FAULT), msg=f'Station 1 is not in fault state '
                                                                 f'after setting station_low_cn=25.5')
        faults = self.stn1.get_faults()
        self.assertEqual(
            Station.STN_CN_LOW_FAULT,
            faults,
            msg=f'Station, expected {Station.STN_CN_LOW_FAULT}, actual {faults}'
        )

    def test_stn_high(self):
        """C/N on station is high fault indication in Star Station"""
        self.stn1.send_params({'station_low_cn': 0, 'station_high_cn': 0})
        self.assertTrue(self.stn1.wait_state(Station.FAULT), msg=f'Station 1 is not in fault state '
                                                                 f'after setting station_high_cn=0')
        faults = self.stn1.get_faults()
        self.assertEqual(
            Station.STN_CN_HIGH_FAULT,
            faults,
            msg=f'Station, expected {Station.STN_CN_HIGH_FAULT}, actual {faults}'
        )

    def test_multiple_faults(self):
        """Multiple faults indication in station: DEMOD1, TX, QOS, SYSTEM, HUB C/N HIGH, STN C/N HIGH"""
        # HUB C/N HIGH PREPARATION
        self.stn1.send_params({'hub_low_cn': 0, 'hub_high_cn': 0})
        # STN C/N HIGH PREPARATION
        self.stn1.send_params({'station_low_cn': 0, 'station_high_cn': 0})
        # SYSTEM PREPARATION
        self.stn1_uhp.network_script('co sa 0')
        time.sleep(5)
        self.stn1_uhp.reboot()
        time.sleep(20)
        # QOS PREPARATION
        self.stn1.send_params({'sm_enable': Checkbox.ON, 'lan_rx_check': LanCheckModes.LOWER, 'rx_check_rate': 1000})
        # DEMOD1 fault preparation
        self.stn1_uhp.set_site_setup({'dvb_search': 100})
        self.stn1_uhp.set_profile_tdm_rx(params={
            'rx1_frq': 970_000 + 100,
            'rx1_sr': 3000,
        })
        # TX fault preparation
        self.stn1_uhp.set_profile_tlc(
            params={'tlc_enable': Checkbox.ON, 'tlc_max_lvl': self.options.get('tx_level') + 1}
        )
        exp_faults = [
                        Station.RX1_FAULT,
                        Station.TX_FAULT,
                        Station.QOS_FAULT,
                        Station.SYSTEM_FAULT,
                        Station.HUB_CN_HIGH_FAULT,
                        Station.STN_CN_HIGH_FAULT,
                    ]
        self.assertTrue(
            self.stn1.wait_faults(
                exp_faults,
                timeout=90
            ),
            msg=f'Station faults: {self.stn1.get_faults()}, expected {" ".join([str(f) for f in exp_faults])}'
        )

    def next_hub_stn_fault(self, exp_fault, hub_params, stn_params):
        self.mf_hub.send_params(hub_params)
        self.stn1.send_params(stn_params)
        self.assertTrue(self.mf_hub.wait_state(Controller.FAULT), msg=f'MF Hub is not in fault state '
                                                                      f'after setting {json.dumps(hub_params)}')
        faults = self.mf_hub.get_faults()
        self.assertEqual(
            exp_fault,
            faults,
            msg=f'MF Hub, expected {exp_fault}, actual {faults}'
        )
        self.assertTrue(self.stn1.wait_state(Station.FAULT), msg=f'Station 1 is not in fault state '
                                                                 f'after setting {json.dumps(stn_params)}')
        faults = self.stn1.get_faults()
        self.assertEqual(
            exp_fault,
            faults,
            msg=f'Station, expected {exp_fault}, actual {faults}'
        )
