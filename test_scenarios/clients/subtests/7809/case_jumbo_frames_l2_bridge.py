import multiprocessing
import os
import threading
import time
from scapy.layers.inet import IP, UDP
from scapy.layers.l2 import Ether, Dot1Q
from scapy.sendrecv import sniff, sendp

from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.drivers.uhp.uhp_requests_driver import UhpRequestsDriver
from src.drivers.uhp.uhp_telnet_driver import UhpTelnetDriver
from src.enum_types_constants import TdmaModcod, RxVoltage
from src.exceptions import UhpUpStateException
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.station_route import StationRoute
from src.options_providers.options_provider import OptionsProvider

__author__ = 'dkudryashov'  # place your name in here
__version__ = '0.1'
options_path = 'test_scenarios.clients.subtests.7809'
backup_name = 'case_jumbo_frames_l2_bridge.txt'


class JumboFramesL2BridgeCase(CustomTestCase):
    # TODO: Preconfiguration is too long! Figure out methods to preconfigure stations for tests
    """
    Ticket 7809. L2 Network MTU>1500 not working
    """

    @classmethod
    def set_up_class(cls):
        # TODO: current MTU size check
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)
        cls.options = OptionsProvider.get_options(options_path)
        cls.MTU = cls.options.get('MTU')
        cls.NUMBER_OF_PACKETS = cls.options.get('NUMBER_OF_PACKETS')
        cls.PPS = cls.options.get('PPS')
        cls.master_options = cls.options.get('hubless_master')
        cls.station_options = cls.options.get('hubless_station')

        cls.net = Network(cls.driver, 0, 0)
        cls.ctrl = Controller(cls.driver, cls.net.get_id(), 0)
        cls.stn = Station(cls.driver, 0, 0)  # Getting station 0 as the only station in the config

        # Setting station IP address in order to make it available
        stn_ip = StationRoute(cls.driver, 0, 0)
        stn_ip.send_params({
            'ip': cls.station_options.get('device_ip'),
            'mask': cls.station_options.get('device_mask'),
        })

        cls.dev_password = cls.net.get_param('dev_password')  # Network `dev_password`
        cls.ctrl.send_params({
            'device_ip': cls.master_options.get('device_ip'),
            'device_mask': cls.master_options.get('device_mask'),
            'device_vlan': cls.master_options.get('device_vlan'),
            'tdma_mc': TdmaModcod._16APSK_2_3
        })
        cls.uhp_master = UhpRequestsDriver(cls.master_options.get('device_ip'))
        cls.uhp_master.set_nms_permission(vlan=cls.master_options.get('device_vlan'), password=cls.dev_password)
        if not cls.ctrl.wait_up():
            raise UhpUpStateException('Timeout! Hubless master is not in UP state')
        cls.uhp_station = UhpRequestsDriver(cls.station_options.get('device_ip'))
        cls.stn.send_param('serial', cls.uhp_station.get_serial_number())
        cls.uhp_station_telnet = UhpTelnetDriver(cls.station_options.get('device_ip'))
        cls.station_default_config()
        cls.station_preconfigure()
        # TODO: Telnet?
        if not cls.stn.wait_up():
            raise UhpUpStateException('Timeout! Hubless station is not in UP state')
        cls.uhp_master.clear_all_stats_log()

    def test_jumbo_frames(self):
        """Test jumbo frames in a L2 hubless network. Traffic is generated from both a Hub LAN and a station LAN"""

        self.received_packets1 = 0
        self.received_packets2 = 0
        pkt1 = Ether(src='2c:2B:1A:4E:2A:5B', dst='2C:1A:2B:3C:4E:5E', type=0x8100)
        pkt1 /= Dot1Q(vlan=1006)
        pkt1 /= IP(src='172.16.1.8', dst='172.16.34.1')
        pkt1 /= UDP(sport=12122, dport=54300)
        pkt1 /= os.urandom(self.MTU - len(pkt1) + 14)

        pkt2 = Ether(src='2c:2B:1A:4E:2A:5C', dst='2C:1A:2B:3C:4E:5F', type=0x8100)
        pkt2 /= Dot1Q(vlan=4006)
        pkt2 /= IP(src='172.16.1.9', dst='172.16.34.1')
        pkt2 /= UDP(sport=12123, dport=54301)
        pkt2 /= os.urandom(self.MTU - len(pkt1) + 14)

        sniff_thread = threading.Thread(target=self.sniff_pkts)
        sniff_thread.daemon = True
        sniff_thread.start()
        time.sleep(5)

        traffic_process1 = multiprocessing.Process(target=self.send_packet, args=(pkt1,))
        traffic_process2 = multiprocessing.Process(target=self.send_packet, args=(pkt2,))
        traffic_process1.start()
        traffic_process2.start()

        st_time = time.perf_counter()
        traffic_process1.join()
        traffic_process2.join()
        end_time = time.perf_counter()
        self.dbg(f'Average pps={self.NUMBER_OF_PACKETS // (end_time - st_time)}')
        time.sleep(5)

        uhp1_out_pkt = int(self.uhp_master.get_modulator_stats().get('p1_packets'))
        uhp2_out_pkt = int(self.uhp_station.get_modulator_stats().get('p1_packets'))
        uhp1_drops_pkt = int(self.uhp_master.get_modulator_stats().get('p1_drops'))
        uhp2_drops_pkt = int(self.uhp_station.get_modulator_stats().get('p1_drops'))
        uhp1_sum = uhp1_out_pkt + uhp1_drops_pkt
        uhp2_sum = uhp2_out_pkt + uhp2_drops_pkt
        with self.subTest(f'Master sent packets: outPktsP1={uhp1_out_pkt}, dropsP1={uhp1_drops_pkt}'):
            self.assertEqual(uhp1_sum, self.NUMBER_OF_PACKETS)
        with self.subTest(f'Station sent packets: outPktsP1={uhp2_out_pkt}, dropsP1={uhp2_drops_pkt}'):
            self.assertEqual(uhp2_sum, self.NUMBER_OF_PACKETS)
        with self.subTest('Packets received and sent to LAN by Master'):
            self.assertEqual(uhp1_out_pkt, self.received_packets1)
        with self.subTest('Packets received and sent to LAN by Station'):
            self.assertEqual(uhp2_out_pkt, self.received_packets2)

    def sniff_pkts(self):
        sniff(filter=f"udp",
              prn=self.handle_udp,
              store=0
              )

    def send_packet(self, pkt):
        sendp(pkt, count=self.NUMBER_OF_PACKETS, inter=1 / self.PPS, verbose=False)

    def handle_udp(self, pkt):
        if Dot1Q not in pkt:
            return
        if pkt[UDP].dport == 54300 and pkt[Dot1Q].vlan == 206:
            self.received_packets1 += 1
        elif pkt[UDP].dport == 54301 and pkt[Dot1Q].vlan == 306:
            self.received_packets2 += 1

    def tear_down(self) -> None:
        pass

    @classmethod
    def tear_down_class(cls) -> None:
        pass

    @classmethod
    def station_default_config(cls):
        if cls.uhp_station.get_state() != 'off':
            cls.uhp_station_telnet.get_raw_result('ip update off')
            cls.uhp_station_telnet.get_raw_result('config load default all')
            cls.uhp_station.set_snmp({
                'access1_ip': '255.255.255.0',
                'access2_ip': '0.0.0.0',
                'snmp_read': 'public',
                'snmp_write': 'private',
            })
            cls.uhp_station_telnet.get_raw_result('lic clear')
            cls.uhp_station_telnet.get_raw_result('cl in eth')
            time.sleep(3)
            cls.uhp_station_telnet.get_raw_result('rf lo 0 0 0')
            cls.uhp_station_telnet.get_raw_result(f'ip address {cls.station_options.get("device_ip")} /24')
            cls.uhp_station_telnet.get_raw_result('conf save')
            cls.uhp_station.wait_reboot()
            time.sleep(5)
            cls.uhp_station_telnet = UhpTelnetDriver(cls.station_options.get('device_ip'))

    @classmethod
    def station_preconfigure(cls):
        cls.uhp_station_telnet.get_raw_result('pro 1 type auto slave')
        cls.uhp_station_telnet.get_raw_result('pro 1 hubless tdma')
        cls.uhp_station_telnet.get_raw_result('pro 1 mod on 200')
        # Cannot set correctly via telnet so far
        cls.uhp_station.set_profile_tdma_rf(profile_number=1, params={
            'tdma_sr': cls.ctrl.get_param('tdma_sr'),
            'tdma_mc': TdmaModcod._16APSK_2_3,
            'mf1_tx': cls.ctrl.get_param('mf1_tx'),
            'mf1_rx': cls.ctrl.get_param('mf1_rx'),
        })
        cls.uhp_station.set_profile_tdma_prot(profile_number=1, params={
            'frame_length': cls.ctrl.get_param('frame_length'),
            'slot_length': cls.ctrl.get_param('slot_length'),
        })
        cls.uhp_station_telnet.get_raw_result('pro 1 run')
