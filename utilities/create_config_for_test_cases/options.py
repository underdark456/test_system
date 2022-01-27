from src.enum_types_constants import ControllerModes, StationModes, DamaAB, RouteTypes

system = {

}

options = {
    'network': {
        'name': 'DAMA_net',
        'dev_password': 'nms40'
    },
    'teleport': {
        'name': 'TELEPORTNAME',
        'sat_name': 'test_sat',
        'tx_lo': 0,
        'rx1_lo': 0,
        'rx2_lo': 0
    },
    'vno': {
        'name': 'vno_name'
    },
    'dama_hub': {
        'name': 'DAMA_HUB',
        'mode': ControllerModes.DAMA_HUB,
        'net_id': 192,
        'teleport': 'teleport:0',
        'tx_frq': 1_500_000,
        'tx_sr': 5500,
        'tx_level': 25,
        'a_dama_tx_frq': 1_510_000,
        'a_dama_rx_frq': 1_510_000,
        'a_dama_level': 25,
        'a_dama_tx': 1,
        'b_dama_tx_frq': 1_513_000,
        'b_dama_rx_frq': 1_513_000,
        'b_dama_level': 25,
        'b_dama_tx': 1,

    },
    'dama_inroute': {
        'name': 'DAMA_Inr',
        'mode': ControllerModes.DAMA_INROUTE,
        'tx_controller': 'controller:0',
        'net_id': 192,
        'teleport': 'teleport:0',
        'a_dama_tx_frq': 1_520_000,
        'a_dama_rx_frq': 1_520_000,
        'a_dama_tx': 1,
        'a_dama_level': 25,
        'b_dama_tx_frq': 1_523_000,
        'b_dama_rx_frq': 1_523_000,
        'b_dama_tx': 1,
        'b_dama_level': 25,
    },
    'dama_station_01': {
        'name': 'dama_station_01',
        'enable': True,
        'serial': 111,
        'mode': StationModes.DAMA,
        'rx_controller': 'controller:0',
        'dama_ab': DamaAB.CHANNEL_A,
    },

    'dama_station_02': {
        'name': 'dama_station_02',
        'enable': True,
        'serial': 222,
        'mode': StationModes.DAMA,
        'rx_controller': 'controller:1',
        'dama_ab': DamaAB.CHANNEL_B,
    },
    'service': {
        'name': 'station_ips',
    },
    'service_traffic-01': {
        'name': 'service-01_Tr',
        'hub_vlan': '100',
        'stn_vlan': '110',
        'stn_normal': True,
    },
    'hub_traffic_ip': {
        'type': RouteTypes.IP_ADDRESS,
        'service': 'service:1',
        'ip': '101.0.0.11'
    },
    'station01_ip': {
        'type': RouteTypes.IP_ADDRESS,
        'service': 'service:0',
        'ip': '111.111.111.111'
    },
    'station01_traffic_ip': {
        'type': RouteTypes.IP_ADDRESS,
        'service': 'service:1',
        'ip': '101.1.1.11'
    },
    'station02_ip': {
        'type': RouteTypes.IP_ADDRESS,
        'service': 'service:0',
        'ip': '222.222.222.222'
    },
    'station01_gw': {
        'type': RouteTypes.STATIC_ROUTE,
        'service': 'service:0',
        'mask': '/0',
        'gateway': '111.111.111.1',
    },
    'station02_gw': {
        'type': RouteTypes.STATIC_ROUTE,
        'service': 'service:0',
        'mask': '/0',
        'gateway': '222.222.222.1',
    },
    'number_of_access': 1024,
    'number_of_access_net0': 512,  # have to split into two
    'number_of_access_net1': 511,
    'number_of_alert': 2048,
    'number_of_bal_controller': 32,
    'number_of_camera': 64,
    'number_of_controller': 512,
    'number_of_dashboard': 256,
    'number_of_device': 2048,
    'number_of_group': 512,
    'number_of_network': 128,
    'number_of_policy': 512,
    'number_of_polrule': 10000,
    'number_of_port_map': 16000,
    'number_of_profile_set': 128,
    'number_of_qos': 1024,
    'number_of_rip_router': 256,
    'number_of_route': 65000,
    'number_of_sch_range': 64,
    'number_of_sch_service': 128,
    'number_of_sch_task': 512,
    'number_of_scheduler': 64,
    'number_of_server': 64,
    'number_of_service': 512,
    'number_of_shaper': 2048,
    'number_of_sr_controller': 32,
    'number_of_sr_license': 256,
    'number_of_sr_teleport': 128,
    'number_of_station': 32768,
    'number_of_sw_upload': 32,
    'number_of_teleport': 128,
    'number_of_user': 512,
    'number_of_vno': 512,
    'names': {
        'alert': '',
        'bal_controller': '',
        'camera': '',
        'controller': '',
        'dashboard': '',
        'device': '',
        'group': '',
        'network': '',
        'policy': '',
        'profile_set': '',
        'qos': '',
        'sch_range': '',
        'sch_service': '',
        'sch_task': '',
        'scheduler': '',
        'server': '',
        'service': '',
        'shaper': '',
        'sr_controller': '',
        'sr_license': '',
        'sr_teleport': '',
        'station': '',
        'sw_upload': '',
        'teleport': '',
        'user': '',
        'vno': '',
    },
}
