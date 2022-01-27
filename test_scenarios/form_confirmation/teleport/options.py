from src.enum_types_constants import LatitudeModes, LongitudeModes, TdmaSearchModes, LongitudeModesStr, \
    LatitudeModesStr, TdmaSearchModesStr

options = {
    'teleport': {
        # settings section
        'name': 'MSK',
        # satellite_data section
        'sat_name': 'Eutelsat16A',
        'sat_lon_deg': '15',
        'sat_lon_min': '48',
        # teleport_location section
        'lat_deg': '55',
        'lat_min': '50',
        'lat_south': LatitudeModesStr.NORTH,
        'lon_deg': '37',
        'lon_min': '51',
        'lon_west': LongitudeModesStr.EAST,
        'time_zone': '3',
        # tx_rf_setup section
        'tx_lo': '12800000',
        'tx_offset': '1820',
        'tx_spi': '1',
        # rx1_rf_setup section
        'rx1_lo': '10750000',
        'rx1_offset': '1057',
        'rx1_spi': '1',
        # rx2_rf_setup section
        'rx2_lo': '9750000',
        'rx2_offset': '2323',
        'rx2_spi': '1',
        # rx_search_bw section
        'dvb_search': '2399',
        'tdma_search': TdmaSearchModesStr.BW24,
    }
}