import re
import ipaddress
from typing import Dict

from src.exceptions import ParameterNotPassedException


class UhpParser:


    @classmethod
    def get_ip_screening(cls, reply=None):
        if reply is None:
            raise ParameterNotPassedException('IP screening reply must be passed to the method')
        uhp_values = {}
        value = re.compile(r'ip scr:[\s]*[a-z]+').search(reply.lower())
        if value is not None:
            uhp_values['ip_screening'] = value.group().split()[-1]
        print(uhp_values)
        return uhp_values

    @classmethod
    def get_snmp(cls, reply=None):
        if reply is None:
            raise ParameterNotPassedException('SNMP reply must be passed to the method')
        uhp_values = {}
        comm_read = re.compile(r'read community[\s]*-[\s]*[^\s]+').search(reply.lower())
        if comm_read is not None:
            uhp_values['comm_read'] = comm_read.group().split('-')[-1].strip()
        comm_write = re.compile(r'wrt\. community[\s]*-[\s]*[^\s]+').search(reply.lower())
        if comm_write is not None:
            uhp_values['comm_write'] = comm_write.group()[len('wrt. community - '):]
        access_ip1 = re.compile(r'ip permitted 1 - [0-9]+\.[0-9]+\.[0-9]+\.[0-9]+').search(reply.lower())
        if access_ip1 is not None:
            uhp_values['access1_ip'] = access_ip1.group()[len('ip permitted 1 - '):]
        access_ip2 = re.compile(r'ip permitted 2 - [0-9]+\.[0-9]+\.[0-9]+\.[0-9]+').search(reply.lower())
        if access_ip2 is not None:
            uhp_values['access2_ip'] = access_ip2.group()[len('ip permitted 2 - '):]
        return uhp_values

    @classmethod
    def get_dhcp(cls, reply=None):
        if reply is None:
            raise ParameterNotPassedException('DHCP reply must be passed to the method')
        uhp_values: Dict[str, str] = {}
        mode_re = re.compile(r'mode:\s*[a-z]+').search(reply.lower())
        if mode_re is not None:
            uhp_values['dhcp_mode'] = mode_re.group().split()[-1]
        vlan_re = re.compile(r'vlan:\s*[0-9]+').search(reply.lower())
        if vlan_re is not None:
            uhp_values['dhcp_vlan'] = vlan_re.group().split()[-1]
        ip_start_re = re.compile(r'range:\s*[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+').search(reply.lower())
        if ip_start_re is not None:
            uhp_values['dhcp_ip_start'] = ip_start_re.group()[len('range: '):].split()[-1]
        ip_end_re = re.compile(r'[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+-[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+').search(reply.lower())
        if ip_end_re is not None:
            uhp_values['dhcp_ip_end'] = ip_end_re.group().split('-')[-1]
        mask_re = re.compile(r'mask:\s*[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+').search(reply.lower())
        if mask_re is not None:
            # Converting netmask into the prefix format
            uhp_values['dhcp_mask'] = f'/{cls._mask_to_prefix(mask_re.group().split()[-1])}'
        gateway_re = re.compile(r'gateway\(local relay ip\):\s*[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+').search(reply.lower())
        if gateway_re is not None:
            uhp_values['dhcp_gateway'] = gateway_re.group().split()[-1]
        dns_re = re.compile(r'dns\(relay\):\s*[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+').search(reply.lower())
        if dns_re is not None:
            uhp_values['dhcp_dns'] = dns_re.group().split()[-1]
        timeout_re = re.compile(r'lease:\s*[0-9]+').search(reply.lower())
        if timeout_re is not None:
            uhp_values['dhcp_timeout'] = timeout_re.group().split()[-1]
        return uhp_values


    @classmethod
    def get_arp(cls, reply=None):
        if reply is None:
            raise ParameterNotPassedException('ARP reply must be passed to the method')
        uhp_values: Dict[str, str] = {}
        arp_timeout_re = re.compile(r'purge interval[\s]*[:]*[0-9]+').search(reply.lower())
        if arp_timeout_re is not None:
            uhp_values['arp_timeout'] = arp_timeout_re.group().split()[-1].strip()
        # TODO: proxy ARP
        return uhp_values

    @classmethod
    def get_multicast(cls, reply=None):
        pass

    @classmethod
    def _mask_to_prefix(cls, mask=None):
        try:
            prefix = ipaddress.IPv4Network(f'0.0.0.0/{mask}').prefixlen
            return prefix
        except Exception:
            return None


