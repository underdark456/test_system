from unittest import skip

from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.drivers.uhp.uhp_requests_driver import UhpRequestsDriver
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.service import Service
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider, API_CONNECT

options_path = 'test_scenarios.composite_scenarios.subtests.multifrequency'
backup_name = 'default_config.txt'


@skip('Should be implemented new UHP getter')
class MfNetworkInstallCase(CustomTestCase):
    """Creation complicated MF network"""
    # MF hub, two inroutes, MF inroute,
    # tree real stations, 200 fake stations)

    backup = None
    system_options = None

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(options_path, API_CONNECT)
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)
        cls.system_options = OptionsProvider.get_system_options(options_path)

        cls.uhp11_ip = cls.system_options.get('uhp11_ip')
        cls.uhp12_ip = cls.system_options.get('uhp12_ip')
        cls.uhp13_ip = cls.system_options.get('uhp13_ip')
        cls.uhp14_ip = cls.system_options.get('uhp14_ip')
        cls.uhp15_ip = cls.system_options.get('uhp15_ip')
        cls.uhp16_ip = cls.system_options.get('uhp16_ip')
        cls.uhp17_ip = cls.system_options.get('uhp17_ip')
        cls.uhp11_vlan = cls.system_options.get('uhp11_vlan')
        cls.uhp12_vlan = cls.system_options.get('uhp12_vlan')
        cls.uhp13_vlan = cls.system_options.get('uhp13_vlan')
        cls.uhp14_vlan = cls.system_options.get('uhp14_vlan')
        cls.uhp15_vlan = cls.system_options.get('uhp15_vlan')
        cls.uhp16_vlan = cls.system_options.get('uhp16_vlan')
        cls.uhp17_vlan = cls.system_options.get('uhp17_vlan')
        cls.uhp11_gw = cls.system_options.get('uhp11_gw')
        cls.uhp12_gw = cls.system_options.get('uhp12_gw')
        cls.uhp13_gw = cls.system_options.get('uhp13_gw')
        cls.uhp14_gw = cls.system_options.get('uhp14_gw')
        cls.uhp15_gw = cls.system_options.get('uhp15_gw')
        cls.uhp16_gw = cls.system_options.get('uhp16_gw')
        cls.uhp17_gw = cls.system_options.get('uhp17_gw')
        cls.net_id = cls.system_options.get('net_id')

        # настриваем модем контроллера MF hub
        cls.uhp11_driver = UhpRequestsDriver(cls.uhp11_ip)
        cls.uhp11_driver.set_nms_permission(password='', vlan=cls.uhp11_vlan)

        # TODO добыть серийники всех станций сразу циклом
        # добываем с модема станции 01 серийный номер

        stations = {
           'station1': {
               'ip': cls.uhp12_ip,
            },
           'station2': {
               'ip': cls.uhp13_ip,
           },
           'station3': {
               'ip': cls.uhp17_ip,
           }
       }
        for i in range(1, 4):
            stations[f'station{i}']['driver'] = UhpRequestsDriver(stations[f'station{i}']['ip'])
            stations[f'station{i}']['serial'] = stations[f'station{i}']['driver'].get_serial_number()

        print(stations)

        cls.uhp2_driver = UhpRequestsDriver(cls.uhp12_ip)
        cls.station_sn = cls.uhp12_driver.get_serial_number()

        # добываем с модема станции 02 серийный номер
        cls.uhp3_driver = UhpRequestsDriver(cls.uhp13_ip)
        cls.station_sn = cls.uhp13_driver.get_serial_number()

        # добываем с модема станции 03 серийный номер
        cls.uhp7_driver = UhpRequestsDriver(cls.uhp17_ip)
        cls.station_sn = cls.uhp17_driver.get_serial_number()

    def test_mf_network_install(self):
        # создаем mf сеть
        mf_network_options = OptionsProvider.get_options(options_path, 'mf_network')
        mf_network = Network.create(
            self.driver,
            mf_network_options['nms_id'],
            mf_network_options['values']
        )
        self.assertIsNotNone(mf_network.get_id())

        # создаем телепорт
        mf_teleport_01_options = OptionsProvider.get_options(options_path, 'mf_teleport_01')
        mf_teleport = Teleport.create(
            self.driver,
            mf_teleport_01_options['network_id'],
            mf_teleport_01_options['values']
        )
        self.assertIsNotNone(mf_teleport.get_id())

        # создаем VNO
        vno_01_options = OptionsProvider.get_options(options_path, 'vno-01')
        vno_01 = Vno.create(
            self.driver,
            vno_01_options['network_id'],
            vno_01_options['values']
        )
        self.assertIsNotNone(vno_01.get_id())

        # создаем сервис
        service_01 = Service.create(
            self.driver,
            mf_network.get_id(),
            {'name': 'service-01',
             'hub_vlan': self.uhp11_vlan,
             'stn_vlan': self.uhp12_vlan
             }
        )

        # создаем MF хаб
        mf_hub_01_options = OptionsProvider.get_options(options_path, 'mf_hub_01')
        mf_hub_01 = Controller.create(
            self.driver,
            mf_hub_01_options['network_id'],
            mf_hub_01_options['values']
        )
        self.assertIsNotNone(mf_hub_01.get_id())
        mf_hub_01.send_params({
            'device_ip': self.uhp11_ip,
            'device_vlan': self.uhp11_vlan,
            'device_gateway': self.uhp11_gw,
            'net_id': self.net_id,
        })

        # создаем Inroute-01
        inroute_01_options = OptionsProvider.get_options(options_path, 'inroute_01')
        inroute_01 = Controller.create(
            self.driver,
            inroute_01_options['network_id'],
            inroute_01_options['values']
        )
        self.assertIsNotNone(inroute_01.get_id())

        inroute_01.send_params({
            'device_ip': self.uhp14_ip,
            'device_vlan': self.uhp14_vlan,
            'device_gateway': self.uhp14_gw,
            'net_id': self.net_id,
        })

        # создаем Inroute-02
        inroute_02_options = OptionsProvider.get_options(options_path, 'inroute_02')
        inroute_02 = Controller.create(
            self.driver,
            inroute_02_options['network_id'],
            inroute_02_options['values']
        )
        self.assertIsNotNone(inroute_02.get_id())

        inroute_02.send_params({
            'device_ip': self.uhp15_ip,
            'device_vlan': self.uhp15_vlan,
            'device_gateway': self.uhp15_gw,
            'net_id': self.net_id,
        })

        # создаем MF inroute-01
        mf_inroute_01_options = OptionsProvider.get_options(options_path, 'mf_inroute_01')
        mf_inroute_01 = Controller.create(
            self.driver,
            mf_inroute_01_options['network_id'],
            mf_inroute_01_options['values']
        )
        self.assertIsNotNone(mf_inroute_01.get_id())

        mf_inroute_01.send_params({
            'device_ip': self.uhp16_ip,
            'device_vlan': self.uhp16_vlan,
            'device_gateway': self.uhp16_gw,
            'net_id': self.net_id,
        })

        # TODO убрать создание станций в цикл
        # создаем в NMS станцию 01
        station_01_options = OptionsProvider.get_options(options_path, 'station_01')
        station_01_options['values']['serial'] = self.station_sn
        station_01 = Station.create(
            self.driver,
            station_01_options['vno_id'],
            station_01_options['values'],
        )

        # создаем в NMS станцию 02
        station_02_options = OptionsProvider.get_options(options_path, 'station_02')
        station_02_options['values']['serial'] = self.station_sn
        station_02 = Station.create(
            self.driver,
            station_02_options['vno_id'],
            station_02_options['values'],
        )
        
        # создаем в NMS станцию 03
        station_03_options = OptionsProvider.get_options(options_path, 'station_03')
        station_03_options['values']['serial'] = self.station_sn
        station_03 = Station.create(
            self.driver,
            station_03_options['vno_id'],
            station_03_options['values'],
        )
