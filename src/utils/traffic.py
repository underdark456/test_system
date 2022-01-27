import ipaddress
import os

from scapy.arch import get_if_raw_hwaddr, get_if_addr
from scapy.config import conf
from scapy.layers.inet import IP, ICMP
from scapy.layers.l2 import Ether, Dot1Q, ARP
from scapy.sendrecv import sendp, srp

from src.exceptions import InvalidOptionsException


class TrafficGenerator:

    _pkt: None

    def __init__(self, uhp_ip=None):
        self._src_ip = get_if_addr(conf.iface)
        if uhp_ip is None:
            raise InvalidOptionsException('UHP IP-address must be provided to use traffic generator')
        if not self.is_ipv4(uhp_ip):
            raise InvalidOptionsException('Provided UHP IP-address is not valid')
        self._uhp_ip = uhp_ip
        _, self._src_mac = get_if_raw_hwaddr(conf.iface)
        self._uhp_mac = self.get_mac_by_ip(src_mac=self._src_mac, ip_address=self._uhp_ip)
        self._mtu = 1500
        self._pkt = None

    def set_mtu(self, mtu):
        if isinstance(mtu, int):
            if mtu not in range(68, 2000):
                raise InvalidOptionsException('MTU must be in range 68-2000')
            self._mtu = mtu
        else:
            raise InvalidOptionsException('MTU must be an integer')

    def send_arp(self, **kwargs):
        """
        Send an ARP packet. If no options provided the packet has all defaults:
            - source MAC-address - default interface MAC-address;
            - destination MAC-address - UHP MAC-address resolved from passed UHP IP-address upon initialization;
            - no DOT1Q layer;
            - ARP source MAC-address - default interface MAC-address;
            - ARP destination MAC-address - 'd4:3d:7e:44:55:66';
            - ARP source IP-address - default interface IP-address;
            - ARP destination IP-address - localhost;
            - ARP type - 2 REPLY.
        Options are passed as a dictionary.
        """
        self._pkt = None  # just in case
        self._form_base_packet('arp', **kwargs)
        if Dot1Q not in self._pkt:
            # noinspection PyUnresolvedReferences
            self._pkt[Ether].type = 0x0806
        else:
            # noinspection PyUnresolvedReferences
            self._pkt[Ether].type = 0x8100
            # noinspection PyUnresolvedReferences
            self._pkt[Dot1Q].type = 0x0806
        self._pkt /= ARP()
        hwsrc = kwargs.get('arp_hwsrc', None)
        if hwsrc is not None:
            self._pkt.hwsrc = hwsrc
        hwdst = kwargs.get('arp_hwdst', None)
        if hwdst is not None:
            self._pkt.hwdst = hwdst
        psrc = kwargs.get('arp_ipsrc', None)
        if psrc is not None:
            self._pkt.psrc = psrc
        pdst = kwargs.get('arp_ipdst', None)
        if pdst is not None:
            self._pkt.pdst = pdst
        arp_type = kwargs.get('arp_type', None)
        if arp_type is not None:
            if arp_type not in range(26):
                raise InvalidOptionsException('Provided ARP type is invalid')
            else:
                self._pkt.op = arp_type
        # TODO: Handle rest types
        if arp_type == 1:
            pass
        else:
            self._pkt.dst = 'FF:FF:FF:FF:FF:FF'
        self._send_packet(**kwargs)

    def send_icmp(self, **kwargs):
        """
        Send an ICMP packet. If no options provided the packet has all defaults:
            - source MAC-address - default interface MAC-address;
            - destination MAC-address - UHP MAC-address resolved from passed UHP IP-address upon initialization;
            - no DOT1Q layer;
            - source IP-address - default interface IP-address;
            - destination IP-address - localhost;
            - IPv4 type of service - 0;
        """
        self._pkt = None  # just in case
        icmp_type = kwargs.get('icmp_type', 8)
        if icmp_type is not None and icmp_type not in range(19):
            raise InvalidOptionsException('ICMP: Provided ICMP type is invalid')
        self._form_base_packet('icmp', **kwargs)
        # noinspection PyUnresolvedReferences
        self._pkt[IP].proto = 1  # just in case
        self._pkt /= ICMP(type=icmp_type)
        self._send_packet(**kwargs)
        self._pkt = None

    def _form_base_packet(self, packet_type, **kwargs):
        # Forming Ethernet layer of the packet
        # noinspection PyTypeChecker
        self._pkt = Ether()
        src_mac = kwargs.get('src_mac', None)
        if src_mac is None:
            src_mac = self._src_mac
        uhp_mac = kwargs.get('uhp_mac', None)
        if uhp_mac is None:
            uhp_mac = self._uhp_mac
        self._pkt.src = src_mac
        self._pkt.dst = uhp_mac

        # Forming Dot1Q layer of the packet
        vlan = kwargs.get('vlan', None)
        if vlan is not None and isinstance(vlan, int):
            if vlan not in range(4096):
                raise InvalidOptionsException('Provided VLAN ID is invalid')
            else:
                # noinspection PyUnresolvedReferences
                self._pkt[Ether].type = 0x8100
                self._pkt /= Dot1Q(vlan=vlan)
        pcp = kwargs.get('pcp', None)
        if pcp is not None and isinstance(pcp, int):
            if pcp not in range(8):
                raise InvalidOptionsException('Provided 802.1Q priority is invalid')
            else:
                if Dot1Q not in self._pkt:
                    # noinspection PyUnresolvedReferences
                    self._pkt[Ether].type = 0x8100
                    self._pkt /= Dot1Q(vlan=0, prio=pcp)
                else:
                    # noinspection PyUnresolvedReferences
                    self._pkt[Dot1Q].prio = pcp
        if packet_type == 'ARP':
            return

        # Forming Layer 3 of the packet
        self._pkt /= IP()
        src_ip = kwargs.get('src_ip', None)
        if src_ip is not None:
            if not self.is_ipv4(src_ip):
                raise InvalidOptionsException('Provided source IP address is not a valid IPv4 address')
        else:
            src_ip = self._src_ip
        # noinspection PyUnresolvedReferences
        self._pkt[IP].src = src_ip
        dst_ip = kwargs.get('dst_ip', None)
        if dst_ip is not None:
            if not self.is_ipv4(dst_ip):
                raise InvalidOptionsException('Provided destination IP address is not a valid IPv4 address')
        else:
            dst_ip = '127.0.0.1'
        # noinspection PyUnresolvedReferences
        self._pkt[IP].dst = dst_ip
        tos = kwargs.get('tos', None)
        if tos is not None:
            if tos not in range(256):
                raise InvalidOptionsException('Provided TOS not in valid range')
        else:
            tos = 0
        # noinspection PyUnresolvedReferences
        self._pkt[IP].tos = tos
        protocol = kwargs.get('protocol')
        if protocol is not None:
            if protocol not in range(256):
                raise InvalidOptionsException('Provided IPv4 protocol type is invalid')
        else:
            protocol = 0
        # noinspection PyUnresolvedReferences
        self._pkt[IP].proto = protocol

    def _send_packet(self, **kwargs):
        payload_size = kwargs.get('payload_size', None)
        if payload_size is not None and isinstance(payload_size, int) and payload_size in range(40, 2000):
            self._add_dummy_payload(payload_size)

        pps = kwargs.get('pps', None)
        if pps is not None and isinstance(pps, int):
            inter = 1 / pps
        else:
            inter = 0
        verbose = kwargs.get('verbose', None)
        if verbose:
            verbose = True
        else:
            verbose = False
        if kwargs.get('count', None) is not None and isinstance(kwargs.get('count'), int):
            count = kwargs.get('count')
        else:
            count = 1
        if self._pkt is not None:
            sendp(
                self._pkt,
                verbose=verbose,
                count=count,
                inter=inter,
            )
        self._pkt = None

    def _add_dummy_payload(self, payload_size):
        if Dot1Q in self._pkt:
            max_layer2_payload = self._mtu - len(self._pkt) + 14
        else:
            max_layer2_payload = self._mtu - len(self._pkt) + 10
        if payload_size < max_layer2_payload:
            payload = os.urandom(payload_size)
        else:
            payload = os.urandom(max_layer2_payload)
        self._pkt /= payload

    @staticmethod
    def is_ipv4(ip_address):
        try:
            ipaddress.IPv4Address(ip_address)
            return True
        except ipaddress.AddressValueError:
            return False

    @staticmethod
    def is_ipv6(ip_address):
        try:
            ipaddress.IPv6Address(ip_address)
            return True
        except ipaddress.AddressValueError:
            return False

    @staticmethod
    def get_mac_by_ip(**kwargs):
        ip_address = kwargs.get('ip_address', '127.0.0.1')
        pkt = Ether(src=kwargs.get('src_mac', '127.0.0.1'), dst='ff:ff:ff:ff:ff:ff')
        pkt /= ARP(pdst=ip_address)
        ans, _ = srp(pkt, timeout=2, verbose=False)
        if len(ans) == 0:
            return None
        for sent, received in ans:
            target_mac = received.sprintf("%Ether.src%")
            return target_mac


if __name__ == '__main__':
    t = TrafficGenerator(uhp_ip='10.0.2.156')
    t.send_arp(
        vlan=206
    )
