import ipaddress
from src import nms_api
from src.enum_types_constants import DhcpModesStr
from utilities.network_up.mf_hub_1stn_up import MfHub1StnUp


class DhcpConfirmationCase(MfHub1StnUp):
    """MF hub and 1 station DHCP confirmation"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.25'
    __execution_time__ = 350  # approximate test case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        super().set_up_class()

    def test_dhcp_on(self):
        """DHCP mode ON MF hub and station confirmation"""
        for i in range(6):
            dhcp_params = {
                'dhcp_mode': DhcpModesStr.ON,
                'dhcp_vlan': str(819 * i),  # from 0 to 4095 with step 819
                'dhcp_ip_start': str(ipaddress.IPv4Address('10.0.0.0') + 10_000 * i),
                'dhcp_ip_end': str(ipaddress.IPv4Address('10.0.0.0') + 11_000 * i),
                'dhcp_mask': f'/{2 + i * 6}',
                'dhcp_gateway': str(ipaddress.IPv4Address('4.4.4.4') + 200_000_000 * i),
                'dhcp_dns': str(ipaddress.IPv4Address('8.8.8.8') + 200_000_000 * i),
                'dhcp_timeout': str(30 + 17274 * i),  # from 30 to 86400 with step 17274
            }
            nms_api.update(self.mf_hub, dhcp_params)
            nms_api.update(self.stn1, dhcp_params)
            nms_api.wait_ticks(4)
            hub_dhcp = self.mf_hub_uhp.get_dhcp_stats()
            stn_dhcp = self.stn1_uhp.get_dhcp_stats()
            for key, value in dhcp_params.items():
                self.assertEqual(
                    str(value).lower(),
                    hub_dhcp.get(key),
                    msg=f'NMS {key}={value}, UHP Hub {key}={ hub_dhcp.get(key)}'
                )
                self.assertEqual(
                    str(value).lower(),
                    stn_dhcp.get(key),
                    msg=f'NMS {key}={value}, UHP Stn {key}={stn_dhcp.get(key)}'
                )
        nms_api.update(self.mf_hub, {'dhcp_mode': DhcpModesStr.OFF})
        nms_api.update(self.stn1, {'dhcp_mode': DhcpModesStr.OFF})
        nms_api.wait_ticks(4)
        hub_dhcp = self.mf_hub_uhp.get_dhcp_stats()
        stn_dhcp = self.stn1_uhp.get_dhcp_stats()
        self.assertEqual(DhcpModesStr.OFF.lower(), hub_dhcp.get('dhcp_mode'), msg=f'UHP MF hub DHCP is not OFF')
        self.assertEqual(DhcpModesStr.OFF.lower(), stn_dhcp.get('dhcp_mode'), msg=f'UHP stn DHCP is not OFF')

    def test_dhcp_relay(self):
        """DHCP mode Relay MF hub and station confirmation"""
        for i in range(6):
            dhcp_params = {
                'dhcp_mode': DhcpModesStr.RELAY,
                'dhcp_vlan': str(819 * i),
                'dhcp_helper': str(ipaddress.IPv4Address('4.4.4.4') + 200_000_000 * i),
                'dhcp_local_ip': str(ipaddress.IPv4Address('8.8.8.8') + 200_000_000 * i),
            }
            nms_api.update(self.mf_hub, dhcp_params)
            nms_api.update(self.stn1, dhcp_params)
            nms_api.wait_ticks(4)
            hub_dhcp = self.mf_hub_uhp.get_dhcp_stats()
            stn_dhcp = self.stn1_uhp.get_dhcp_stats()
            for key, value in dhcp_params.items():
                if key in ('dhcp_mode', 'dhcp_vlan'):
                    self.assertEqual(
                        str(value).lower(),
                        hub_dhcp.get(key),
                        msg=f'NMS {key}={value}, UHP Hub {key}={hub_dhcp.get(key)}'
                    )
                    self.assertEqual(
                        str(value).lower(),
                        stn_dhcp.get(key),
                        msg=f'NMS {key}={value}, UHP Stn {key}={stn_dhcp.get(key)}'
                    )
                elif key == 'dhcp_helper':
                    self.assertEqual(
                        str(value).lower(),
                        hub_dhcp.get('dhcp_dns'),
                        msg=f'NMS {key}={value}, UHP Hub {key}={hub_dhcp.get("dhcp_dns")}'
                    )
                    self.assertEqual(
                        str(value).lower(),
                        stn_dhcp.get('dhcp_dns'),
                        msg=f'NMS {key}={value}, UHP Stn {key}={stn_dhcp.get("dhcp_dns")}'
                    )
                elif key == 'dhcp_local_ip':
                    self.assertEqual(
                        str(value).lower(),
                        hub_dhcp.get('dhcp_gateway'),
                        msg=f'NMS {key}={value}, UHP Hub {key}={hub_dhcp.get("dhcp_gateway")}'
                    )
                    self.assertEqual(
                        str(value).lower(),
                        stn_dhcp.get('dhcp_gateway'),
                        msg=f'NMS {key}={value}, UHP Stn {key}={stn_dhcp.get("dhcp_gateway")}'
                    )

        nms_api.update(self.mf_hub, {'dhcp_mode': DhcpModesStr.OFF})
        nms_api.update(self.stn1, {'dhcp_mode': DhcpModesStr.OFF})
        nms_api.wait_ticks(4)
        hub_dhcp = self.mf_hub_uhp.get_dhcp_stats()
        stn_dhcp = self.stn1_uhp.get_dhcp_stats()
        self.assertEqual(DhcpModesStr.OFF.lower(), hub_dhcp.get('dhcp_mode'), msg=f'UHP MF hub DHCP is not OFF')
        self.assertEqual(DhcpModesStr.OFF.lower(), stn_dhcp.get('dhcp_mode'), msg=f'UHP stn DHCP is not OFF')
