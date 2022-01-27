options = {
    'realtime': {
        # Interfaces section
        'lan': {'command': 'show int eth', 'startswith': 'Ethernet interface is'},
        'modulator': {'command': 'show int mod', 'startswith': 'Modulator interface is'},
        'demod 1': {'command': 'show in dem', 'startswith': 'Demodulator-1 interface'},
        'demod 2': {'command': 'show int 2dem', 'startswith': 'Demodulator-2 interface'},

        # Network section
        'network': {'command': 'show net', 'startswith': '--------------------------- Unit state'},
        'stations': {'command': 'show stat', 'startswith': 'Stn | Bytes Rcvd CRC_errs |'},
        'stations rf': {'command': 'show st rf 0', 'startswith': 'Stn | CRC_errs | All | RF HbRX'},
        'stations tr': {'command': 'show st tr 0', 'startswith': 'Stn   SN     Shap Acc |'},
        'mf tdma': {'command': 'show mf_tdma', 'startswith': 'Ch    SN      Flags'},
        'nms': {'command': 'show nms', 'startswith': 'NMS state'},

        # System section
        'system': {'command': 'show system', 'startswith': 'UHP-'},
        'profiles': {'command': 'show prof', 'startswith': 'Active profile:'},
        'errors': {'command': 'show err', 'startswith': 'No SW errors'},
        'bluescreen': {'command': 'bl', 'startswith': 'Counters cleared:'},
        'options': {'command': 'unit key', 'startswith': 'Keys information upon start-up:'},
        'boot mode': {'command': 'show boot', 'startswith': 'Main:    Flash bank'},
        'log': {'command': 'show log', 'startswith': ''},
        'redundancy': {'command': 'show backup', 'startswith': 'Mode:'},

        # Protocols section
        'routing': {'command': 'show ip  ', 'startswith': 'IP Scr:'},
        'rip': {'command': 'show rip', 'startswith': 'RIPv2:'},
        'vlans': {'command': 'show vlans', 'startswith': 'VLAN    RX packets    RX bytes'},
        'svlans': {'command': 'show svlans', 'startswith': 'SVLAN   RX VLAN   RX packets'},
        'mac tbl': {'command': 'show mac', 'startswith': 'Eth'},
        'rtp': {'command': 'show rtp', 'startswith': 'Transmit ---------------'},
        'arp': {'command': 'show arp', 'startswith': 'Free entries:'},
        'snmp': {'command': 'show snmp', 'startswith': 'Version - SNMPv'},
        'tcpa': {'command': 'show acc all', 'startswith': '--------------------------------- TCPA Settings'},
        'dhcp': {'command': 'show dhcp', 'startswith': 'Mode: '},
        'nat': {'command': 'show nat', 'startswith': 'NAT-ed sessions:'},
        'multicast': {'command': 'show mult', 'startswith': ' Multicast IP     Source IP'},
        'shapers': {'command': 'show shapers', 'startswith': 'Tables load(cfg/rntm(%)):'},
        'tuning': {'command': 'show serv tun', 'startswith': '------------------Enable-----Current------Fixed'},
        'cotm': {'command': 'show serv cotm', 'startswith': '--------------------------------- COTM general'},
        'acm': {'command': 'show modcods', 'startswith': '----------------------------- TDM ACM'},
    },
    'realtime_set': {
        'save conf': {'command': 'conf save'},
        'clr cntrs': {'command': 'cle co all'},
        'reboot': {'command': 'ds 1'},
        'clr faults': {'command': 'cf'},
        'exit teln': {'command': 'exit'},
        'run prof 1': {'command': 'prof 1 run'},
    }
}
