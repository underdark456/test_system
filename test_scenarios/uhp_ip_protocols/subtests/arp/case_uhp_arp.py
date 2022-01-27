import ipaddress
from time import sleep

from scapy.all import *
from scapy.layers.l2 import ARP, Dot1Q, Ether

from src.custom_logger import DEBUG
from src.custom_test_case import CustomTestCase
from src.drivers.uhp.uhp_requests_driver import UhpRequestsDriver
from src.drivers.uhp.uhp_telnet_driver import UhpTelnetDriver
from src.exceptions import InvalidOptionsException, UhpResponseException
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.uhp_ip_protocols.subtests.arp'
backup_name = 'default_config.txt'


class UhpArpCase(CustomTestCase):
    # TODO: add ARP table MAC-addresses and IP-addresses; ICMP echo requests should not trigger ARP requests
    """ARP capabilities of UHP routers case"""

    router_address = None
    uhp_telnet = None
    sniffer = None

    @classmethod
    def set_up_class(cls):
        # cls.driver = DriversProvider.get_driver_instance(
        #     OptionsProvider.get_connection()
        # )
        cls.options = OptionsProvider.get_options(options_path)
        cls.router_address = cls.options.get('device_ip', None)
        cls.test_vlan = cls.options.get('device_vlan', 206)
        if cls.router_address is None:
            raise InvalidOptionsException('UHP IP address is not in the provided options')
        cls.uhp_mac = cls._get_uhp_mac()
        _, cls.hw = get_if_raw_hwaddr(conf.iface)
        cls.src_ip = get_if_addr(conf.iface)
        cls.uhp_telnet = UhpTelnetDriver(cls.router_address)
        cls.uhp_driver = UhpRequestsDriver(cls.router_address)
        cls.clear_timeout = cls.options.get('clear_timeout')
        cls.uhp_driver.set_arp_form(params={'arp_timeout': cls.clear_timeout})

    def set_up(self) -> None:
        self.logger.setLevel(DEBUG)

    def test_total_number_of_arp_entries(self):
        """Get maximum number of ARP entries"""
        self.uhp_telnet.clear_arp()
        free_entries = self.uhp_telnet.show_arp().get('free_entries', None)
        self.assertNotEqual(None, free_entries)
        self.info(f'Number of free ARP entries {free_entries}')

    def test_make_full_arp_table(self):
        """Fill up ARP table completely. Test clear timeout as well"""
        fake_network = self.options.get('fake_network', None)
        if fake_network is None:
            raise InvalidOptionsException('Options are not provided for filling up ARP table test')
        fake_network = ipaddress.IPv4Network(fake_network)
        self.hosts = list(fake_network.hosts())
        self.uhp_telnet.clear_arp()
        initial_free_entries = self.uhp_telnet.show_arp().get('free_entries', 0)
        self.logger.info(f'Number of free entries at the beginning of filling up ARP table: {initial_free_entries}')

        pkt = Ether(dst=self.uhp_mac)
        pkt /= Dot1Q(vlan=self.test_vlan)
        pkt /= ARP(op=2, hwdst=self.uhp_mac, pdst=self.router_address)
        for i in range(int(initial_free_entries)):
            fake_mac = self._generate_random_mac()
            pkt[Ether].src = fake_mac
            pkt[ARP].hwsrc = fake_mac
            pkt[ARP].psrc = f'{str(self.hosts[i + 2])}'
            sleep(1/4)  # the timeout is needed to let the router handle the requests.
            sendp(pkt, verbose=False)
        free_entries = self.uhp_telnet.show_arp().get('free_entries', None)
        with self.subTest(f'ARP entries after filling up ARP table'):
            self.assertEqual(0, int(free_entries))
        time.sleep(self.clear_timeout * 60)
        free_entries = self.uhp_telnet.show_arp().get('free_entries')
        with self.subTest(f'ARP entries after clear timeout'):
            self.assertEqual(int(initial_free_entries), int(free_entries))

    def test_clear_arp_table_command(self):
        """Test clear arp command"""
        fake_network = self.options.get('fake_network', None)
        if fake_network is None:
            raise InvalidOptionsException('Options are not provided for filling up ARP table test')
        fake_network = ipaddress.IPv4Network(fake_network)
        self.hosts = list(fake_network.hosts())
        self.uhp_telnet.clear_arp()
        initial_free_entries = self.uhp_telnet.show_arp().get('free_entries', 0)
        self.logger.info(f'Number of free entries at the beginning of filling up ARP table: {initial_free_entries}')

        pkt = Ether(dst=self.uhp_mac)
        pkt /= Dot1Q(vlan=self.test_vlan)
        pkt /= ARP(op=2, hwdst=self.uhp_mac, pdst=self.router_address)
        for i in range(int(initial_free_entries)):
            fake_mac = self._generate_random_mac()
            pkt[Ether].src = fake_mac
            pkt[ARP].hwsrc = fake_mac
            pkt[ARP].psrc = f'{str(self.hosts[i + 2])}'
            sleep(1/4)  # the timeout is needed to let the router handle the requests.
            sendp(pkt, verbose=False)
        free_entries = self.uhp_telnet.show_arp().get('free_entries', None)
        with self.subTest(f'ARP entries after filling up ARP table'):
            self.assertEqual(0, int(free_entries))
        self.logger.info('Issuing clear arp command')
        self.uhp_telnet.clear_arp()
        free_entries = self.uhp_telnet.show_arp().get('free_entries', None)
        with self.subTest(f'ARP entries after clear arp command'):
            self.assertEqual(initial_free_entries, free_entries)

    def tear_down(self) -> None:
        pass

    @classmethod
    def tear_down_class(cls) -> None:
        if cls.uhp_telnet is not None:
            cls.uhp_telnet.close()

    @classmethod
    def _get_uhp_mac(cls):
        # Getting MAC-address of HUB.
        ans, _ = srp(
            Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=cls.router_address),
            timeout=2,
            verbose=False
        )
        if len(ans) == 0:
            raise UhpResponseException(f'Cannot get MAC address of UHP {cls.router_address}')
        for sent, received in ans:
            cls.uhp_mac = received.sprintf("%Ether.src%")
            return cls.uhp_mac

    @staticmethod
    def _generate_random_mac():
        """The method generates a random MAC-address"""
        mac_address = RandMAC()
        mac_address = str(mac_address)
        mac_address = 'd4:3d:7e' + mac_address[8:]
        return mac_address


