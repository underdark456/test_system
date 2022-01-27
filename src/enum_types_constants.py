# enum_types_constants.py - the module features enumeration classes using in the test system.
# Examples:
#       AlertModes.OFF >>> "Off"
#       "Specify" in AlertModes() >>> True
#       [*AlertModes()] >>> ["Inherit", "Off", "Specify"]
#
# Regular classes, such as `AlertModes` features numeric values, while `AlertModesStr` features string values


class _Contains:
    """
    Base class that is used for building enumeration classes.
    The built-in methods allow to check if an item is in the container,
    and getting the next item of the container.
    """
    _container = None

    def __init__(self):
        self._i = None

    def __contains__(self, item):
        return item in self._container

    def __iter__(self):
        self._i = 0
        return self

    def __next__(self):
        if self._i >= len(self._container):
            raise StopIteration
        val = self._container[self._i]
        self._i += 1
        return str(val)


class AlertModes(_Contains):
    INHERIT = 0  # "Inherit"
    OFF = 1  # "Off"
    SPECIFY = 2  # "Specify"
    _container = [INHERIT, OFF, SPECIFY, ]


class AlertModesStr(_Contains):
    INHERIT = 'Inherit'
    OFF = 'Off'
    SPECIFY = 'Specify'
    _container = [INHERIT, OFF, SPECIFY, ]


class AlertPriority(_Contains):
    LOW = 0  # "Low"
    MEDIUM = 1  # "Medium"
    HIGH = 2  # 'High'
    _container = [LOW, MEDIUM, HIGH, ]


class AlertPriorityStr(_Contains):
    LOW = 'Low'
    MEDIUM = 'Medium'
    HIGH = 'High'
    _container = [LOW, MEDIUM, HIGH, ]


class BindingModes(_Contains):
    STATIC = 0  # "Static"
    REDUNDANT_STATIC = 1  # "Redundant_static"
    SMART = 2  # "Smart"
    _container = [STATIC, REDUNDANT_STATIC, SMART, ]


class BindingModesStr(_Contains):
    STATIC = 'Static'
    REDUNDANT_STATIC = 'Redundant_static'
    SMART = 'Smart'
    _container = [STATIC, REDUNDANT_STATIC, SMART, ]


class ControllerModes(_Contains):
    NONE = 0  # "None"
    MF_HUB = 1  # "MF_hub"
    OUTROUTE = 2  # "Outroute"
    DAMA_HUB = 3  # "DAMA_hub"
    HUBLESS_MASTER = 4  # "Hubless_master"
    INROUTE = 5  # "Inroute"
    DAMA_INROUTE = 6  # "DAMA_inroute"
    MF_INROUTE = 7  # "MF_inroute"
    GATEWAY = 8  # "Gateway"
    _container = [
        NONE,
        MF_HUB,
        OUTROUTE,
        DAMA_HUB,
        HUBLESS_MASTER,
        INROUTE,
        DAMA_INROUTE,
        MF_INROUTE,
        GATEWAY,
    ]


class ControllerModesStr(_Contains):
    NONE = 'None'
    MF_HUB = 'MF_hub'
    OUTROUTE = 'Outroute'
    DAMA_HUB = 'DAMA_hub'
    HUBLESS_MASTER = 'Hubless_master'
    INROUTE = 'Inroute'
    DAMA_INROUTE = 'DAMA_inroute'
    MF_INROUTE = 'MF_inroute'
    GATEWAY = 'Gateway'
    _container = [
        NONE,
        MF_HUB,
        OUTROUTE,
        DAMA_HUB,
        HUBLESS_MASTER,
        INROUTE,
        DAMA_INROUTE,
        MF_INROUTE,
        GATEWAY,
    ]


class ControlModes(_Contains):
    FULL = 0  # 'Full'
    STATS_ONLY = 1  # 'Stats_only'
    NO_ACCESS = 2  # 'No_access'
    UNCONFIGURED = 3  # 'Unconfigured'
    _container = [FULL, STATS_ONLY, NO_ACCESS, UNCONFIGURED, ]


class ControlModesStr(_Contains):
    FULL = 'Full'
    STATS_ONLY = 'Stats_only'
    NO_ACCESS = 'No_access'
    UNCONFIGURED = 'Unconfigured'
    _container = [FULL, STATS_ONLY, NO_ACCESS, UNCONFIGURED, ]


class DemodulatorInputModes(_Contains):
    OFF = 0
    RX1 = 1
    RX2 = 2
    _container = [OFF, RX1, RX2]


class DemodulatorInputModesStr(_Contains):
    OFF = 'OFF'
    RX1 = 'RX1'
    RX2 = 'RX2'
    _container = [OFF, RX1, RX2]


class SnmpModes(_Contains):
    OFF = 0  # 'Off'
    V1_V2C = 1  # 'V1_V2C'
    V3 = 2  # 'V3'
    _container = [
        OFF,
        V1_V2C,
        V3,
    ]


class SnmpModesStr(_Contains):
    OFF = 'Off'
    V1_V2C = 'V1_V2C'
    V3 = 'V3'
    _container = [
        OFF,
        V1_V2C,
        V3,
    ]


class SnmpAuth(_Contains):
    NO_AUTH = 0  # 'No_auth'
    AUTH_NO_PRIV = 1  # 'Auth_no_priv'
    AUTH_PRIV = 2  # 'Auth_priv'
    _container = [
        NO_AUTH,
        AUTH_NO_PRIV,
        AUTH_PRIV,
    ]


class SnmpAuthStr(_Contains):
    NO_AUTH = 'No_auth'
    AUTH_NO_PRIV = 'Auth_no_priv'
    AUTH_PRIV = 'Auth_priv'
    _container = [
        NO_AUTH,
        AUTH_NO_PRIV,
        AUTH_PRIV,
    ]


class RipModes(_Contains):
    OFF = 0  # 'Off'
    ON = 1  # 'On'
    TX_ONLY = 2  # 'TX_only'
    _container = [
        OFF,
        ON,
        TX_ONLY,
    ]


class RipModesStr(_Contains):
    OFF = 'Off'
    ON = 'On'
    TX_ONLY = 'TX_only'
    _container = [
        OFF,
        ON,
        TX_ONLY,
    ]


class DhcpModes(_Contains):
    OFF = 0  # "Off"
    ON = 1  # "On"
    RELAY = 2  # "Relay"
    _container = [OFF, ON, RELAY, ]


class DhcpModesStr(_Contains):
    OFF = 'Off'
    ON = 'On'
    RELAY = 'Relay'
    _container = [OFF, ON, RELAY, ]


class ExtGatewayModes(_Contains):
    OFF = 0  # "Off"
    GATEWAY_1 = 1  # "Gateway_1"
    GATEWAY_2 = 2  # "Gateway_2"
    GATEWAY_3 = 3  # "Gateway_3"
    _container = [
        OFF,
        GATEWAY_1,
        GATEWAY_2,
        GATEWAY_3,
    ]


class ExtGatewayModesStr(_Contains):
    OFF = 'Off'
    GATEWAY_1 = 'Gateway_1'
    GATEWAY_2 = 'Gateway_2'
    GATEWAY_3 = 'Gateway_3'
    _container = [
        OFF,
        GATEWAY_1,
        GATEWAY_2,
        GATEWAY_3,
    ]


class IpScreeningModes(_Contains):
    AUTO = 0  # "Auto"
    ON = 1  # "On"
    OFF = 2  # "Off"
    _container = [AUTO, ON, OFF, ]


class IpScreeningModesStr(_Contains):
    AUTO = 'Auto'
    ON = 'On'
    OFF = 'Off'
    _container = [AUTO, ON, OFF, ]


class LanCheckModes(_Contains):
    OFF = 0  # "Off"
    HIGHER = 1  # "Higher"
    LOWER = 2  # "Lower"
    _container = [OFF, HIGHER, LOWER, ]


class LanCheckModesStr(_Contains):
    OFF = 'Off'
    HIGHER = 'Higher'
    LOWER = 'Lower'
    _container = [OFF, HIGHER, LOWER, ]


class LatitudeModes(_Contains):
    NORTH = 0  # "North"
    SOUTH = 1  # "South"
    _container = [NORTH, SOUTH, ]


class LatitudeModesStr(_Contains):
    NORTH = 'North'
    SOUTH = 'South'
    _container = [NORTH, SOUTH, ]


class LoadTypeModes(_Contains):
    TRAFFIC = 0  # "Traffic"
    TDMA_TOTAL = 1  # "TDMA_Total"
    TDMA_CIR = 2  # "TDMA_CIR"
    _container = [TRAFFIC, TDMA_TOTAL, TDMA_CIR, ]


class LoadTypeModesStr(_Contains):
    TRAFFIC = 'Traffic'
    TDMA_TOTAL = 'TDMA_Total'
    TDMA_CIR = 'TDMA_CIR'
    _container = [TRAFFIC, TDMA_TOTAL, TDMA_CIR, ]


class LongitudeModes(_Contains):
    EAST = 0  # "East"
    WEST = 1  # "West"
    _container = [EAST, WEST, ]


class LongitudeModesStr(_Contains):
    EAST = 'East'
    WEST = 'West'
    _container = [EAST, WEST, ]


class RollofModes(_Contains):
    R20 = 0  # "R20"
    R5 = 1  # "R5"
    _container = [R20, R5, ]


class RollofModesStr(_Contains):
    R20 = 'R20'
    R5 = 'R5'
    _container = [R20, R5, ]


class SntpModes(_Contains):
    OFF = 0  # "Off"
    CLIENT = 1  # "Client"
    SERVER = 2  # "Server"
    BOTH = 3  # "Both"
    _container = [OFF, CLIENT, SERVER, BOTH, ]


class SntpModesStr(_Contains):
    OFF = 'Off'
    CLIENT = 'Client'
    SERVER = 'Server'
    BOTH = 'Both'
    _container = [OFF, CLIENT, SERVER, BOTH, ]


class McastModes(_Contains):
    OFF = 0  # "Off"
    STATIC = 1  # "Static"
    IGMP = 2  # "IGMP"
    _container = [OFF, STATIC, IGMP, ]


class McastModesStr(_Contains):
    OFF = 'Off'
    STATIC = 'Static'
    IGMP = 'IGMP'
    _container = [OFF, STATIC, IGMP, ]


class StationModes(_Contains):
    STAR = 0  # "Star"
    MESH = 1  # "Mesh"
    DAMA = 2  # "DAMA"
    # Changed in NMS 4.0.0.14
    HUBLESS = 3
    RX_ONLY = 4  # "RX_only"
    # ROAMING = 4  # "Roaming"
    # ROAMING_MESH = 5  # "Roam_mesh"
    _container = [
        STAR,
        DAMA,
        MESH,
        HUBLESS,
        RX_ONLY,
        # ROAMING,
        # ROAMING_MESH,
    ]


class StationModesStr(_Contains):
    STAR = 'Star'
    MESH = 'Mesh'
    DAMA = 'DAMA'
    # Changed in NMS 4.0.0.14
    HUBLESS = 'Hubless'
    RX_ONLY = 'RX_only'
    # ROAMING = 'Roaming'
    # ROAMING_MESH = 'Roam_mesh'
    _container = [
        STAR,
        DAMA,
        MESH,
        HUBLESS,
        RX_ONLY,
        # ROAMING,
        # ROAMING_MESH,
    ]


class RouteTypes(_Contains):
    NONE = 0  # "None"
    IP_ADDRESS = 1  # "Ip_address"
    STATIC_ROUTE = 2  # "Static_route"
    ROUTE_TO_HUB = 3  # "Route_to_hub"
    NETWORK_TX = 4  # "Network_tx"
    NETWORK_RX = 5  # "Network_rx"
    L2_BRIDGE = 6  # "L2_bridge"
    IPV6_ADDRESS = 7  # "Ipv6_address"
    IPV6_ROUTE = 8  # "Ipv6_route"
    IPV6_TO_HUB = 9  # "Ipv6_to_hub"
    IPV6_NET_TX = 10  # "Ipv6_net_tx"
    IPV6_NET_RX = 11  # "Ipv6_net_rx"
    _container = [
        IP_ADDRESS,
        STATIC_ROUTE,
        ROUTE_TO_HUB,
        NETWORK_TX,
        NETWORK_RX,
        L2_BRIDGE,
        IPV6_ADDRESS,
        IPV6_ROUTE,
        IPV6_TO_HUB,
        IPV6_NET_TX,
        IPV6_NET_RX,
    ]


class RouteTypesStr(_Contains):
    NONE = 'None'
    IP_ADDRESS = 'IP_address'
    STATIC_ROUTE = 'Static_route'
    ROUTE_TO_HUB = 'Route_to_hub'
    NETWORK_TX = 'Network_tx'
    NETWORK_RX = 'Network_rx'
    L2_BRIDGE = 'L2_bridge'
    IPV6_ADDRESS = 'Ipv6_address'
    IPV6_ROUTE = 'Ipv6_route'
    IPV6_TO_HUB = 'Ipv6_to_hub'
    IPV6_NET_TX = 'Ipv6_net_tx'
    IPV6_NET_RX = 'Ipv6_net_rx'
    _container = [
        IP_ADDRESS,
        STATIC_ROUTE,
        ROUTE_TO_HUB,
        NETWORK_TX,
        NETWORK_RX,
        L2_BRIDGE,
        IPV6_ADDRESS,
        IPV6_ROUTE,
        IPV6_TO_HUB,
        IPV6_NET_TX,
        IPV6_NET_RX,
    ]


class RouteIds(_Contains):
    NORMAL = 0  # 'Normal'
    GATEWAY = 1  # 'Gateway'
    MESH = 2  # 'Mesh'
    PRIVATE = 3  # 'Private'
    _container = [NORMAL, GATEWAY, MESH, PRIVATE, ]


class RouteIdsStr(_Contains):
    NORMAL = 'Normal'
    GATEWAY = 'Gateway'
    MESH = 'Mesh'
    PRIVATE = 'Private'
    _container = [NORMAL, GATEWAY, MESH, PRIVATE, ]


class TdmaAcmModes(_Contains):
    OFF = 0
    LEGACY = 1
    TWELVE_MODCODS = 2
    SIXTEEN_MODCODS = 3
    _container = [OFF, LEGACY, TWELVE_MODCODS, SIXTEEN_MODCODS, ]


class TdmaAcmModesStr(_Contains):
    OFF = 'OFF'
    LEGACY = 'Legacy'
    TWELVE_MODCODS = '12modcods'
    SIXTEEN_MODCODS = '16modcods'
    _container = [OFF, LEGACY, TWELVE_MODCODS, SIXTEEN_MODCODS, ]


class TdmaInputModes(_Contains):
    RX1 = 0  # "RX1"
    RX2 = 1  # "RX2"
    _container = [RX1, RX2, ]


class TdmaInputModesStr(_Contains):
    RX1 = 'RX1'
    RX2 = 'RX2'
    _container = [RX1, RX2, ]


class TdmaSearchModes(_Contains):
    BW6 = 0  # "bw6"
    BW12 = 1  # "bw12"
    BW24 = 2  # "bw24"
    BW40 = 3  # "bw40"
    _container = [BW6, BW12, BW24, BW40, ]


class TdmaSearchModesStr(_Contains):
    BW6 = 'bw6'
    BW12 = 'bw12'
    BW24 = 'bw24'
    BW40 = 'bw40'
    _container = [BW6, BW12, BW24, BW40, ]


class TtsModes(_Contains):
    MEASURE = 0  # "Measure"
    VALUE = 1  # "Value"
    LOCATION = 2  # "Location"
    _container = [MEASURE, VALUE, LOCATION, ]


class TtsModesStr(_Contains):
    MEASURE = 'Measure'
    VALUE = 'Value'
    LOCATION = 'Location'
    _container = [MEASURE, VALUE, LOCATION, ]


class WbmModes(_Contains):
    OFF = 0  # 'Off',
    WB_MODULATOR = 1  # 'WB_modulator'
    SLICE_CONTROLLER = 2  # 'Slice_controller'
    WBM_AND_SC = 3  # 'WBM_and_SC'
    _container = [OFF, WB_MODULATOR, SLICE_CONTROLLER, WBM_AND_SC, ]


class WbmModesStr(_Contains):
    OFF = 'Off',
    WB_MODULATOR = 'WB_modulator'
    SLICE_CONTROLLER = 'Slice_controller'
    WBM_AND_SC = 'WBM_and_SC'
    _container = [OFF, WB_MODULATOR, SLICE_CONTROLLER, WBM_AND_SC, ]


class ModcodModes(_Contains):
    SF_QPSK_1_4 = 1
    SF_QPSK_1_3 = 2
    SF_QPSK_2_5 = 3
    SF_QPSK_1_2 = 4
    SF_QPSK_3_5 = 5
    SF_QPSK_2_3 = 6
    SF_QPSK_3_4 = 7
    SF_QPSK_4_5 = 8
    SF_QPSK_5_6 = 9
    SF_QPSK_8_9 = 10
    SF_8PSK_3_5 = 12
    SF_8PSK_2_3 = 13
    SF_8PSK_3_4 = 14
    SF_8PSK_5_6 = 15
    SF_8PSK_8_9 = 16
    SF_16APSK_2_3 = 18
    SF_16APSK_3_4 = 19
    SF_16APSK_4_5 = 20
    SF_16APSK_5_6 = 21
    SF_16APSK_8_9 = 22
    SF_32APSK_3_4 = 24
    SF_32APSK_4_5 = 25
    SF_32APSK_5_6 = 26
    SF_32APSK_8_9 = 27
    LF_QPSK_1_3 = 34
    LF_QPSK_2_5 = 35
    LF_QPSK_1_2 = 36
    LF_QPSK_3_5 = 37
    LF_QPSK_2_3 = 38
    LF_QPSK_3_4 = 39
    LF_QPSK_4_5 = 40
    LF_QPSK_5_6 = 41
    LF_QPSK_8_9 = 42
    LF_QPSK_9_10 = 43
    LF_8PSK_3_5 = 44
    LF_8PSK_2_3 = 45
    LF_8PSK_3_4 = 46
    LF_8PSK_5_6 = 47
    LF_8PSK_8_9 = 48
    LF_8PSK_9_10 = 49
    LF_16APSK_2_3 = 50
    LF_16APSK_3_4 = 51
    LF_16APSK_4_5 = 52
    LF_16APSK_5_6 = 53
    LF_16APSK_8_9 = 54
    LF_16APSK_9_10 = 55
    LF_32APSK_3_4 = 56
    LF_32APSK_4_5 = 57
    LF_32APSK_5_6 = 58
    LF_32APSK_8_9 = 59
    LF_32APSK_9_10 = 60
    LX_QPSK_9_20 = 67
    LX_QPSK_11_20 = 68
    LX_8APSK_100_180 = 69
    LX_8APSK_104_180 = 70
    LX_8PSK_23_36 = 71
    LX_8PSK_25_36 = 72
    LX_8PSK_13_18 = 73
    LX_16APSK_96_180 = 75
    LX_16APSK_100_180 = 76
    LX_16APSK_26_45 = 77
    LX_16APSK_3_5 = 78
    LX_16APSK_18_30 = 79
    LX_16APSK_28_45 = 80
    LX_16APSK_23_36 = 81
    LX_16APSK_20_30 = 82
    LX_16APSK_25_36 = 83
    LX_16APSK_13_18 = 84
    LX_16APSK_140_180 = 85
    LX_16APSK_154_180 = 86
    LX_32APSK_2_3 = 87
    LX_32APSK_128_180 = 89
    LX_32APSK_132_180 = 90
    LX_32APSK_140_180 = 91
    LX_64APSK_128_180 = 92
    LX_64APSK_132_180 = 93
    LX_64APSK_7_9 = 95
    LX_64APSK_4_5 = 97
    LX_64APSK_5_6 = 99
    LX_128APSK_135_180 = 100
    LX_128APSK_140_180 = 101
    LX_256APSK_116_180 = 102
    LX_256APSK_124_180 = 104
    LX_256APSK_128_180 = 105
    LX_256APSK_135_180 = 107
    SX_QPSK_11_45 = 108
    SX_QPSK_4_15 = 109
    SX_QPSK_14_45 = 110
    SX_QPSK_7_15 = 111
    SX_QPSK_8_15 = 112
    SX_QPSK_32_45 = 113
    SX_8PSK_7_15 = 114
    SX_8PSK_8_15 = 115
    SX_8PSK_26_45 = 116
    SX_8PSK_32_45 = 117
    SX_16APSK_7_15 = 118
    SX_16APSK_8_15 = 119
    SX_16APSK_26_45 = 120
    SX_16APSK_3_5 = 121
    SX_16APSK_32_45 = 122
    SX_32APSK_2_3 = 123
    SX_32APSK_32_45 = 124
    _container = [
        SF_QPSK_1_4,
        SF_QPSK_1_3,
        SF_QPSK_2_5,
        SF_QPSK_1_2,
        SF_QPSK_3_5,
        SF_QPSK_2_3,
        SF_QPSK_3_4,
        SF_QPSK_4_5,
        SF_QPSK_5_6,
        SF_QPSK_8_9,
        SF_8PSK_3_5,
        SF_8PSK_2_3,
        SF_8PSK_3_4,
        SF_8PSK_5_6,
        SF_8PSK_8_9,
        SF_16APSK_2_3,
        SF_16APSK_3_4,
        SF_16APSK_4_5,
        SF_16APSK_5_6,
        SF_16APSK_8_9,
        SF_32APSK_3_4,
        SF_32APSK_4_5,
        SF_32APSK_5_6,
        SF_32APSK_8_9,
        LF_QPSK_1_3,
        LF_QPSK_2_5,
        LF_QPSK_1_2,
        LF_QPSK_3_5,
        LF_QPSK_2_3,
        LF_QPSK_3_4,
        LF_QPSK_4_5,
        LF_QPSK_5_6,
        LF_QPSK_8_9,
        LF_QPSK_9_10,
        LF_8PSK_3_5,
        LF_8PSK_2_3,
        LF_8PSK_3_4,
        LF_8PSK_5_6,
        LF_8PSK_8_9,
        LF_8PSK_9_10,
        LF_16APSK_2_3,
        LF_16APSK_3_4,
        LF_16APSK_4_5,
        LF_16APSK_5_6,
        LF_16APSK_8_9,
        LF_16APSK_9_10,
        LF_32APSK_3_4,
        LF_32APSK_4_5,
        LF_32APSK_5_6,
        LF_32APSK_8_9,
        LF_32APSK_9_10,
        LX_QPSK_9_20,
        LX_QPSK_11_20,
        LX_8APSK_100_180,
        LX_8APSK_104_180,
        LX_8PSK_23_36,
        LX_8PSK_25_36,
        LX_8PSK_13_18,
        LX_16APSK_96_180,
        LX_16APSK_100_180,
        LX_16APSK_26_45,
        LX_16APSK_3_5,
        LX_16APSK_18_30,
        LX_16APSK_28_45,
        LX_16APSK_23_36,
        LX_16APSK_20_30,
        LX_16APSK_25_36,
        LX_16APSK_13_18,
        LX_16APSK_140_180,
        LX_16APSK_154_180,
        LX_32APSK_2_3,
        LX_32APSK_128_180,
        LX_32APSK_132_180,
        LX_32APSK_140_180,
        LX_64APSK_128_180,
        LX_64APSK_132_180,
        LX_64APSK_7_9,
        LX_64APSK_4_5,
        LX_64APSK_5_6,
        LX_128APSK_135_180,
        LX_128APSK_140_180,
        LX_256APSK_116_180,
        LX_256APSK_124_180,
        LX_256APSK_128_180,
        LX_256APSK_135_180,
        SX_QPSK_11_45,
        SX_QPSK_4_15,
        SX_QPSK_14_45,
        SX_QPSK_7_15,
        SX_QPSK_8_15,
        SX_QPSK_32_45,
        SX_8PSK_7_15,
        SX_8PSK_8_15,
        SX_8PSK_26_45,
        SX_8PSK_32_45,
        SX_16APSK_7_15,
        SX_16APSK_8_15,
        SX_16APSK_26_45,
        SX_16APSK_3_5,
        SX_16APSK_32_45,
        SX_32APSK_2_3,
        SX_32APSK_32_45,
    ]


class ModcodModesStr(_Contains):
    SF_QPSK_1_4 = 'SF QPSK 1/4'
    SF_QPSK_1_3 = 'SF QPSK 1/3'
    SF_QPSK_2_5 = 'SF QPSK 2/5'
    SF_QPSK_1_2 = 'SF QPSK 1/2'
    SF_QPSK_3_5 = 'SF QPSK 3/5'
    SF_QPSK_2_3 = 'SF QPSK 2/3'
    SF_QPSK_3_4 = 'SF QPSK 3/4'
    SF_QPSK_4_5 = 'SF QPSK 4/5'
    SF_QPSK_5_6 = 'SF QPSK 5/6'
    SF_QPSK_8_9 = 'SF QPSK 8/9'
    SF_8PSK_3_5 = 'SF 8PSK 3/5'
    SF_8PSK_2_3 = 'SF 8PSK 2/3'
    SF_8PSK_3_4 = 'SF 8PSK 3/4'
    SF_8PSK_5_6 = 'SF 8PSK 5/6'
    SF_8PSK_8_9 = 'SF 8PSK 8/9'
    SF_16APSK_2_3 = 'SF 16APSK 2/3'
    SF_16APSK_3_4 = 'SF 16APSK 3/4'
    SF_16APSK_4_5 = 'SF 16APSK 4/5'
    SF_16APSK_5_6 = 'SF 16APSK 5/6'
    SF_16APSK_8_9 = 'SF 16APSK 8/9'
    SF_32APSK_3_4 = 'SF 32APSK 3/4'
    SF_32APSK_4_5 = 'SF 32APSK 4/5'
    SF_32APSK_5_6 = 'SF 32APSK 5/6'
    SF_32APSK_8_9 = 'SF 32APSK 8/9'
    LF_QPSK_1_3 = 'LF QPSK 1/3'
    LF_QPSK_2_5 = 'LF QPSK 2/5'
    LF_QPSK_1_2 = 'LF QPSK 1/2'
    LF_QPSK_3_5 = 'LF QPSK 3/5'
    LF_QPSK_2_3 = 'LF QPSK 2/3'
    LF_QPSK_3_4 = 'LF QPSK 3/4'
    LF_QPSK_4_5 = 'LF QPSK 4/5'
    LF_QPSK_5_6 = 'LF QPSK 5/6'
    LF_QPSK_8_9 = 'LF QPSK 8/9'
    LF_QPSK_9_10 = 'LF QPSK 9/10'
    LF_8PSK_3_5 = 'LF 8PSK 3/5'
    LF_8PSK_2_3 = 'LF 8PSK 2/3'
    LF_8PSK_3_4 = 'LF 8PSK 3/4'
    LF_8PSK_5_6 = 'LF 8PSK 5/6'
    LF_8PSK_8_9 = 'LF 8PSK 8/9'
    LF_8PSK_9_10 = 'LF 8PSK 9/10'
    LF_16APSK_2_3 = 'LF 16APSK 2/3'
    LF_16APSK_3_4 = 'LF 16APSK 3/4'
    LF_16APSK_4_5 = 'LF 16APSK 4/5'
    LF_16APSK_5_6 = 'LF 16APSK 5/6'
    LF_16APSK_8_9 = 'LF 16APSK 8/9'
    LF_16APSK_9_10 = 'LF 16APSK 9/10'
    LF_32APSK_3_4 = 'LF 32APSK 3/4'
    LF_32APSK_4_5 = 'LF 32APSK 4/5'
    LF_32APSK_5_6 = 'LF 32APSK 5/6'
    LF_32APSK_8_9 = 'LF 32APSK 8/9'
    LF_32APSK_9_10 = 'LF 32APSK 9/10'
    LX_QPSK_9_20 = 'LX QPSK 9/20'
    LX_QPSK_11_20 = 'LX QPSK 11/20'
    LX_8APSK_100_180 = 'LX 8APSK 100/180'
    LX_8APSK_104_180 = 'LX 8APSK 104/180'
    LX_8PSK_23_36 = 'LX 8PSK 23/36'
    LX_8PSK_25_36 = 'LX 8PSK 25/36'
    LX_8PSK_13_18 = 'LX 8PSK 13/18'
    LX_16APSK_96_180 = 'LX 16APSK 96/180'
    LX_16APSK_100_180 = 'LX 16APSK 100/180'
    LX_16APSK_26_45 = 'LX 16APSK 26/45'
    LX_16APSK_3_5 = 'LX 16APSK 3/5'
    LX_16APSK_18_30 = 'LX 16APSK 18/30'
    LX_16APSK_28_45 = 'LX 16APSK 28/45'
    LX_16APSK_23_36 = 'LX 16APSK 23/36'
    LX_16APSK_20_30 = 'LX 16APSK 20/30'
    LX_16APSK_25_36 = 'LX 16APSK 25/36'
    LX_16APSK_13_18 = 'LX 16APSK 13/18'
    LX_16APSK_140_180 = 'LX 16APSK 140/180'
    LX_16APSK_154_180 = 'LX 16APSK 154/180'
    LX_32APSK_2_3 = 'LX 32APSK 2/3'
    LX_32APSK_128_180 = 'LX 32APSK 128/180'
    LX_32APSK_132_180 = 'LX 32APSK 132/180'
    LX_32APSK_140_180 = 'LX 32APSK 140/180'
    LX_64APSK_128_180 = 'LX 64APSK 128/180'
    LX_64APSK_132_180 = 'LX 64APSK 132/180'
    LX_64APSK_7_9 = 'LX 64APSK 7/9'
    LX_64APSK_4_5 = 'LX 64APSK 4/5'
    LX_64APSK_5_6 = 'LX 64APSK 5/6'
    LX_128APSK_135_180 = 'LX 128APSK 135/180'
    LX_128APSK_140_180 = 'LX 128APSK 140/180'
    LX_256APSK_116_180 = 'LX 256APSK 116/180'
    LX_256APSK_124_180 = 'LX 256APSK 124/180'
    LX_256APSK_128_180 = 'LX 256APSK 128/180'
    LX_256APSK_135_180 = 'LX 256APSK 135/180'
    SX_QPSK_11_45 = 'SX QPSK 11/45'
    SX_QPSK_4_15 = 'SX QPSK 4/15'
    SX_QPSK_14_45 = 'SX QPSK 14/45'
    SX_QPSK_7_15 = 'SX QPSK 7/15'
    SX_QPSK_8_15 = 'SX QPSK 8/15'
    SX_QPSK_32_45 = 'SX QPSK 32/45'
    SX_8PSK_7_15 = 'SX 8PSK 7/15'
    SX_8PSK_8_15 = 'SX 8PSK 8/15'
    SX_8PSK_26_45 = 'SX 8PSK 26/45'
    SX_8PSK_32_45 = 'SX 8PSK 32/45'
    SX_16APSK_7_15 = 'SX 16APSK 7/15'
    SX_16APSK_8_15 = 'SX 16APSK 8/15'
    SX_16APSK_26_45 = 'SX 16APSK 26/45'
    SX_16APSK_3_5 = 'SX 16APSK 3/5'
    SX_16APSK_32_45 = 'SX 16APSK 32/45'
    SX_32APSK_2_3 = 'SX 32APSK 2/3'
    SX_32APSK_32_45 = 'SX 32APSK 32/45'
    _container = [
        SF_QPSK_1_4,
        SF_QPSK_1_3,
        SF_QPSK_2_5,
        SF_QPSK_1_2,
        SF_QPSK_3_5,
        SF_QPSK_2_3,
        SF_QPSK_3_4,
        SF_QPSK_4_5,
        SF_QPSK_5_6,
        SF_QPSK_8_9,
        SF_8PSK_3_5,
        SF_8PSK_2_3,
        SF_8PSK_3_4,
        SF_8PSK_5_6,
        SF_8PSK_8_9,
        SF_16APSK_2_3,
        SF_16APSK_3_4,
        SF_16APSK_4_5,
        SF_16APSK_5_6,
        SF_16APSK_8_9,
        SF_32APSK_3_4,
        SF_32APSK_4_5,
        SF_32APSK_5_6,
        SF_32APSK_8_9,
        LF_QPSK_1_3,
        LF_QPSK_2_5,
        LF_QPSK_1_2,
        LF_QPSK_3_5,
        LF_QPSK_2_3,
        LF_QPSK_3_4,
        LF_QPSK_4_5,
        LF_QPSK_5_6,
        LF_QPSK_8_9,
        LF_QPSK_9_10,
        LF_8PSK_3_5,
        LF_8PSK_2_3,
        LF_8PSK_3_4,
        LF_8PSK_5_6,
        LF_8PSK_8_9,
        LF_8PSK_9_10,
        LF_16APSK_2_3,
        LF_16APSK_3_4,
        LF_16APSK_4_5,
        LF_16APSK_5_6,
        LF_16APSK_8_9,
        LF_16APSK_9_10,
        LF_32APSK_3_4,
        LF_32APSK_4_5,
        LF_32APSK_5_6,
        LF_32APSK_8_9,
        LF_32APSK_9_10,
        LX_QPSK_9_20,
        LX_QPSK_11_20,
        LX_8APSK_100_180,
        LX_8APSK_104_180,
        LX_8PSK_23_36,
        LX_8PSK_25_36,
        LX_8PSK_13_18,
        LX_16APSK_96_180,
        LX_16APSK_100_180,
        LX_16APSK_26_45,
        LX_16APSK_3_5,
        LX_16APSK_18_30,
        LX_16APSK_28_45,
        LX_16APSK_23_36,
        LX_16APSK_20_30,
        LX_16APSK_25_36,
        LX_16APSK_13_18,
        LX_16APSK_140_180,
        LX_16APSK_154_180,
        LX_32APSK_2_3,
        LX_32APSK_128_180,
        LX_32APSK_132_180,
        LX_32APSK_140_180,
        LX_64APSK_128_180,
        LX_64APSK_132_180,
        LX_64APSK_7_9,
        LX_64APSK_4_5,
        LX_64APSK_5_6,
        LX_128APSK_135_180,
        LX_128APSK_140_180,
        LX_256APSK_116_180,
        LX_256APSK_124_180,
        LX_256APSK_128_180,
        LX_256APSK_135_180,
        SX_QPSK_11_45,
        SX_QPSK_4_15,
        SX_QPSK_14_45,
        SX_QPSK_7_15,
        SX_QPSK_8_15,
        SX_QPSK_32_45,
        SX_8PSK_7_15,
        SX_8PSK_8_15,
        SX_8PSK_26_45,
        SX_8PSK_32_45,
        SX_16APSK_7_15,
        SX_16APSK_8_15,
        SX_16APSK_26_45,
        SX_16APSK_3_5,
        SX_16APSK_32_45,
        SX_32APSK_2_3,
        SX_32APSK_32_45,
    ]


class TdmaModcod(_Contains):
    # Have to use the underscore as variables cannot start with digits
    _BPSK_1_2 = 0
    _BPSK_2_3 = 1
    _BPSK_3_4 = 2
    _BPSK_5_6 = 3
    _QPSK_1_2 = 4
    _QPSK_2_3 = 5
    _QPSK_3_4 = 6
    _QPSK_5_6 = 7
    _8PSK_1_2 = 8
    _8PSK_2_3 = 9
    _8PSK_3_4 = 10
    _8PSK_5_6 = 11
    _16APSK_1_2 = 12
    _16APSK_2_3 = 13
    _16APSK_3_4 = 14
    _16APSK_5_6 = 15
    _container = [
        _BPSK_1_2,
        _BPSK_2_3,
        _BPSK_3_4,
        _BPSK_5_6,
        _QPSK_1_2,
        _QPSK_2_3,
        _QPSK_3_4,
        _QPSK_5_6,
        _8PSK_1_2,
        _8PSK_2_3,
        _8PSK_3_4,
        _8PSK_5_6,
        _16APSK_1_2,
        _16APSK_2_3,
        _16APSK_3_4,
        _16APSK_5_6,
    ]


class TdmaModcodStr(_Contains):
    # Have to use the underscore as variables cannot start with digits
    _BPSK_1_2 = 'BPSK 1/2'
    _BPSK_2_3 = 'BPSK 2/3'
    _BPSK_3_4 = 'BPSK 3/4'
    _BPSK_5_6 = 'BPSK 5/6'
    _QPSK_1_2 = 'QPSK 1/2'
    _QPSK_2_3 = 'QPSK 2/3'
    _QPSK_3_4 = 'QPSK 3/4'
    _QPSK_5_6 = 'QPSK 5/6'
    _8PSK_1_2 = '8PSK 1/2'
    _8PSK_2_3 = '8PSK 2/3'
    _8PSK_3_4 = '8PSK 3/4'
    _8PSK_5_6 = '8PSK 5/6'
    _16APSK_1_2 = '16APSK 1/2'
    _16APSK_2_3 = '16APSK 2/3'
    _16APSK_3_4 = '16APSK 3/4'
    _16APSK_5_6 = '16APSK 5/6'
    _container = [
        _BPSK_1_2,
        _BPSK_2_3,
        _BPSK_3_4,
        _BPSK_5_6,
        _QPSK_1_2,
        _QPSK_2_3,
        _QPSK_3_4,
        _QPSK_5_6,
        _8PSK_1_2,
        _8PSK_2_3,
        _8PSK_3_4,
        _8PSK_5_6,
        _16APSK_1_2,
        _16APSK_2_3,
        _16APSK_3_4,
        _16APSK_5_6,
    ]


class RxVoltage(_Contains):
    DC13V = 0  # 'DC13V'
    DC18V = 1  # 'DC18V'
    _container = [DC13V, DC18V, ]


class RxVoltageStr(_Contains):
    DC13V = 'DC13V'
    DC18V = 'DC18V'
    _container = [DC13V, DC18V, ]


class TcpaVersion(_Contains):
    V3_5 = 0  # 'V3_5'
    V3_4 = 1  # 'V3_4'
    _container = [V3_5, V3_4, ]


class TcpaVersionStr(_Contains):
    V3_5 = 'V3_5'
    V3_4 = 'V3_4'
    _container = [V3_5, V3_4, ]


# Policy rules type
class RuleTypes(_Contains):
    CHECK = 0  # 'Check'
    ACTION = 1  # 'Action'
    _container = [CHECK, ACTION, ]


# Policy rules type
class RuleTypesStr(_Contains):
    CHECK = 'Check'
    ACTION = 'Action'
    _container = [CHECK, ACTION, ]


# Policy rules of type check
class CheckTypes(_Contains):
    PRIORITY_802_1Q = 0  # 'priority_802_1q'
    VLAN = 1  # 'VLAN'
    TOS = 2  # 'TOS'
    DSCP = 3  # 'DSCP'
    PROTOCOL = 4  # 'Protocol'
    SRC_NET = 5  # 'SRC_NET'
    DST_NET = 6  # 'DST_NET'
    SRC_TCP_PORT = 7  # 'SRC_TCP_port'
    DST_TCP_PORT = 8  # 'DST_TCP_port'
    SRC_UDP_PORT = 9  # 'SRC_UDP_port'
    DST_UDP_PORT = 10  # 'DST_UDP_port'
    ICMP_TYPE = 11  # 'ICMP_type'
    _container = [
        PRIORITY_802_1Q,
        VLAN,
        TOS,
        DSCP,
        PROTOCOL,
        SRC_NET,
        DST_NET,
        SRC_TCP_PORT,
        DST_TCP_PORT,
        SRC_UDP_PORT,
        DST_UDP_PORT,
        ICMP_TYPE,
    ]


# Policy rules of type check
class CheckTypesStr(_Contains):
    PRIORITY_802_1Q = 'priority_802_1q'
    VLAN = 'VLAN'
    TOS = 'TOS'
    DSCP = 'DSCP'
    PROTOCOL = 'Protocol'
    SRC_NET = 'SRC_Net'
    DST_NET = 'DST_Net'
    SRC_TCP_PORT = 'SRC_TCP_port'
    DST_TCP_PORT = 'DST_TCP_port'
    SRC_UDP_PORT = 'SRC_UDP_port'
    DST_UDP_PORT = 'DST_UDP_port'
    ICMP_TYPE = 'ICMP_type'
    _container = [
        PRIORITY_802_1Q,
        VLAN,
        TOS,
        DSCP,
        PROTOCOL,
        SRC_NET,
        DST_NET,
        SRC_TCP_PORT,
        DST_TCP_PORT,
        SRC_UDP_PORT,
        DST_UDP_PORT,
        ICMP_TYPE,
    ]


# Policy rules of type action
class ActionTypes(_Contains):
    DROP = 0  # 'Drop'
    SET_QUEUE = 1  # 'Set_queue'
    SET_TS_CH = 2  # 'Set_TS_ch'
    NO_TCPA = 3  # 'No_TCPA'
    COMPRESS_RTP = 4  # 'Compress_RTP'
    NO_SCREENING = 5  # 'No_screening'
    SET_ACM_CHANNEL = 6  # 'Set_ACM_channel'
    DROP_IF_STATION_DOWN = 8  # 'Drop_if_station_down'
    ENCRYPT = 9  # 'Encrypt'
    SET_TOS = 10  # 'Set_TOS'
    SET_DSCP = 11  # 'Set_DSCP'
    GOTO_POLICY = 12  # 'GOTO_policy'
    CALL_POLICY = 13  # 'CALL_policy'
    COMPRESS_GTP = 14  # 'Compress_GTP'
    _container = [
        DROP,
        SET_QUEUE,
        SET_TS_CH,
        NO_TCPA,
        COMPRESS_RTP,
        NO_SCREENING,
        SET_ACM_CHANNEL,
        DROP_IF_STATION_DOWN,
        ENCRYPT,
        SET_TOS,
        SET_DSCP,
        GOTO_POLICY,
        CALL_POLICY,
        COMPRESS_GTP,
    ]


# Policy rules of type action
class ActionTypesStr(_Contains):
    DROP = 'Drop'
    SET_QUEUE = 'Set_queue'
    SET_TS_CH = 'Set_TS_ch'
    NO_TCPA = 'No_TCPA'
    COMPRESS_RTP = 'Compress_RTP'
    NO_SCREENING = 'No_screening'
    SET_ACM_CHANNEL = 'Set_ACM_channel'
    DROP_IF_STATION_DOWN = 'Drop_if_station_down'
    ENCRYPT = 'Encrypt'
    SET_TOS = 'Set_TOS'
    SET_DSCP = 'Set_DSCP'
    GOTO_POLICY = 'GOTO_policy'
    CALL_POLICY = 'CALL_policy'
    COMPRESS_GTP = 'Compress_GTP'
    _container = [
        DROP,
        SET_QUEUE,
        SET_TS_CH,
        NO_TCPA,
        COMPRESS_RTP,
        NO_SCREENING,
        SET_ACM_CHANNEL,
        DROP_IF_STATION_DOWN,
        ENCRYPT,
        SET_TOS,
        SET_DSCP,
        GOTO_POLICY,
        CALL_POLICY,
        COMPRESS_GTP,
    ]


class QueueTypes(_Contains):
    LOW = 0  # 'Low'
    P2 = 1  # 'P2'
    P3 = 2  # 'P3'
    MEDIUM = 3  # 'Medium'
    P5 = 4  # 'P5'
    P6 = 5  # 'P6'
    HIGH = 6  # 'High'
    _container = [
        LOW,
        P2,
        P3,
        MEDIUM,
        P5,
        P6,
        HIGH,
    ]


class QueueTypesStr(_Contains):
    LOW = 'Low'
    P2 = 'P2'
    P3 = 'P3'
    MEDIUM = 'Medium'
    P5 = 'P5'
    P6 = 'P6'
    HIGH = 'High'
    _container = [
        LOW,
        P2,
        P3,
        MEDIUM,
        P5,
        P6,
        HIGH,
    ]


class PriorityTypes(_Contains):
    LOW = 0  # 'Low'
    P2 = 1  # 'P2'
    P3 = 2  # 'P3'
    MEDIUM = 3  # 'Medium'
    P5 = 4  # 'P5'
    P6 = 5  # 'P6'
    HIGH = 6  # 'High'
    POLICY = 7  # 'Policy'
    _container = [
        LOW,
        P2,
        P3,
        MEDIUM,
        P5,
        P6,
        HIGH,
        POLICY,
    ]


class PriorityTypesStr(_Contains):
    LOW = 'Low'
    P2 = 'P2'
    P3 = 'P3'
    MEDIUM = 'Medium'
    P5 = 'P5'
    P6 = 'P6'
    HIGH = 'High'
    POLICY = 'Policy'
    _container = [
        LOW,
        P2,
        P3,
        MEDIUM,
        P5,
        P6,
        HIGH,
        POLICY,
    ]


class ShaperUpQueue(_Contains):
    Q1 = 0  # 'Q1'
    Q2 = 1  # 'Q2'
    Q3 = 2  # 'Q3'
    Q4 = 3  # 'Q4'
    Q5 = 4  # 'Q5'
    Q6 = 5  # 'Q6'
    Q7 = 6  # 'Q7'
    Q_TO_Q = 7  # 'QtoQ'
    _container = [
        Q1,
        Q2,
        Q3,
        Q4,
        Q5,
        Q6,
        Q7,
        Q_TO_Q,
    ]


class ShaperUpQueueStr(_Contains):
    Q1 = 'Q1'
    Q2 = 'Q2'
    Q3 = 'Q3'
    Q4 = 'Q4'
    Q5 = 'Q5'
    Q6 = 'Q6'
    Q7 = 'Q7'
    Q_TO_Q = 'QtoQ'
    _container = [
        Q1,
        Q2,
        Q3,
        Q4,
        Q5,
        Q6,
        Q7,
        Q_TO_Q,
    ]


class MeshRouting(_Contains):
    NONE = 0  # 'None'
    TO_MESH_ROUTES = 1  # 'To_mesh_routes'
    TO_GW_ROUTES = 2  # 'To_gw_routes'
    _container = [NONE, TO_MESH_ROUTES, TO_GW_ROUTES, ]


class MeshRoutingStr(_Contains):
    NONE = 'None'
    TO_MESH_ROUTES = 'To_mesh_routes'
    TO_GW_ROUTES = 'To_gw_routes'
    _container = [NONE, TO_MESH_ROUTES, TO_GW_ROUTES, ]


class SrTeleportModes(_Contains):
    IN_SERVICE = 0  # 'In_service'
    DISABLED = 1  # 'Disabled'
    _container = [IN_SERVICE, DISABLED, ]


class SrTeleportModesStr(_Contains):
    IN_SERVICE = 'In_service'
    DISABLED = 'Disabled'
    _container = [IN_SERVICE, DISABLED, ]


class DeviceModes(_Contains):
    NO_ACCESS = 0  # 'no_access'
    STANDBY = 1  # 'standby'
    USED = 2  # 'used'
    _container = [NO_ACCESS, STANDBY, USED, ]


class DeviceModesStr(_Contains):
    NO_ACCESS = 'no_access'
    STANDBY = 'standby'
    USED = 'used'
    _container = [NO_ACCESS, STANDBY, USED, ]


class DeviceModConnect(_Contains):
    TELEPORT_TX = 0  # 'Teleport_TX'
    WB_MODULATOR = 1  # 'WB_modulator'
    DISCONNECTED = 2  # 'Disconnected'
    _container = [TELEPORT_TX, WB_MODULATOR, DISCONNECTED, ]


class DeviceModConnectStr(_Contains):
    TELEPORT_TX = 'Teleport_TX'
    WB_MODULATOR = 'WB_modulator'
    DISCONNECTED = 'Disconnected'
    _container = [TELEPORT_TX, WB_MODULATOR, DISCONNECTED, ]


class DeviceDemConnect(_Contains):
    TELEPORT_RX = 0  # 'Teleport_RX'
    OUTROUTE_SYNC = 1  # 'Outroute_sync'
    DISCONNECTED = 2  # 'Disconnected'
    _container = [TELEPORT_RX, OUTROUTE_SYNC, DISCONNECTED, ]


class DeviceDemConnectStr(_Contains):
    TELEPORT_RX = 'Teleport_RX'
    OUTROUTE_SYNC = 'Outroute_sync'
    DISCONNECTED = 'Disconnected'
    _container = [TELEPORT_RX, OUTROUTE_SYNC, DISCONNECTED, ]


class ProfileSetModes(_Contains):
    NO_CHANGE = 0  # 'No_change'
    NONE = 1  # 'None'
    STAR_STATION = 2  # 'Star_station'
    MESH_STATION = 3  # 'Mesh_station'
    DAMA_STATION = 4  # 'DAMA_station'
    HUBLESS_STATION = 5  # 'Hubless_station'
    CROSSPOL_TEST = 6  # 'CrossPol_test'
    _container = [NO_CHANGE, NONE, STAR_STATION, MESH_STATION, DAMA_STATION, HUBLESS_STATION, CROSSPOL_TEST, ]


class ProfileSetModesStr(_Contains):
    NO_CHANGE = 'No_change'
    NONE = 'None'
    STAR_STATION = 'Star_station'
    MESH_STATION = 'Mesh_station'
    DAMA_STATION = 'DAMA_station'
    HUBLESS_STATION = 'Hubless_station'
    CROSSPOL_TEST = 'CrossPol_test'
    _container = [NO_CHANGE, NONE, STAR_STATION, MESH_STATION, DAMA_STATION, HUBLESS_STATION, CROSSPOL_TEST, ]


class ModelTypes(_Contains):
    UHP200X = 0  # 'UHP100
    UHP232 = 1  # 'UHP100X
    UHP200 = 2  # 'UHP200
    UHP100X = 3  # UHP200X
    UHP100 = 4  # UHP232
    _container = [UHP200X, UHP232, UHP200, UHP100X, UHP100, ]


class ModelTypesStr(_Contains):
    UHP100 = 'UHP100'
    UHP100X = 'UHP100X'
    UHP200 = 'UHP200'
    UHP200X = 'UHP200X'
    UHP232 = 'UHP232'
    _container = [UHP200X, UHP232, UHP200, UHP100X, UHP100, ]


class LanguageTypes(_Contains):
    ENGLISH = 0
    RUSSIAN = 1
    _container = [ENGLISH, RUSSIAN, ]


class LanguageTypesStr(_Contains):
    ENGLISH = 'English'
    RUSSIAN = 'Russian'
    _container = [ENGLISH, RUSSIAN, ]


class Checkbox(_Contains):
    ON = 1
    OFF = 0
    _container = [ON, OFF, ]


class CheckboxStr(_Contains):
    ON = 'ON'
    OFF = 'OFF'
    _container = [ON, OFF, ]


class DamaAB(_Contains):
    CHANNEL_A = 0
    CHANNEL_B = 1
    _container = [CHANNEL_A, CHANNEL_B, ]


class DamaABStr(_Contains):
    CHANNEL_A = 'Channel_A'
    CHANNEL_B = 'Channel_B'
    _container = [CHANNEL_A, CHANNEL_B, ]


class DamaTx(_Contains):
    OFF = 0
    ON = 1
    PURE = 2
    _container = [OFF, ON, PURE, ]


class DamaTxStr(_Contains):
    OFF = 'Off'
    ON = 'On'
    PURE = 'Pure'
    _container = [OFF, ON, PURE, ]


class Licensing(_Contains):
    DEMO_MODE = 0
    LOCAL_KEY = 1
    UHP_KEYS = 2
    _container = [DEMO_MODE, LOCAL_KEY, UHP_KEYS, ]


class LicensingStr(_Contains):
    DEMO_MODE = 'Demo_mode'
    LOCAL_KEY = 'Local_key'
    UHP_KEYS = 'UHP_keys'
    _container = [DEMO_MODE, LOCAL_KEY, UHP_KEYS, ]


class MapSource(_Contains):
    STADIAMAPS = 0
    LOCAL = 1
    USER = 2
    _container = [STADIAMAPS, LOCAL, USER, ]


class MapSourceStr(_Contains):
    STADIAMAPS = 'Stadiamaps'
    LOCAL = 'Local'
    USER = 'User'
    _container = [STADIAMAPS, LOCAL, USER, ]


class SwUploadStates(_Contains):
    STOPPED = 0
    RUNNING = 1
    _container = [STOPPED, RUNNING]


class SwUploadStatesStr(_Contains):
    STOPPED = 'Stopped'
    RUNNING = 'Running'
    _container = [STOPPED, RUNNING]


# TODO: redefine when 4.0.0.27 is released
class FaultCodes(_Contains):  # Fault codes reporting by NMS
    LAN = 1
    RX1 = 2  # to be specified
    RX2 = 4  # to be specified
    TX = 8  # checked
    NETWORK = 16  # checked
    QOS = 32  # checked
    SYSTEM = 64  # checked
    DOWN = 128  # checked
    HUB_CN_LOW = 256  # checked
    HUB_CN_HIGH = 512  # checked
    STN_CN_LOW = 1024  # checked
    STN_CN_HIGH = 2048  # checked
    _container = [RX1, RX2, TX, NETWORK, QOS, SYSTEM, DOWN, HUB_CN_LOW, HUB_CN_HIGH, STN_CN_LOW, STN_CN_HIGH, ]
