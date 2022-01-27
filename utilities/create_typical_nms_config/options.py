from src.enum_types_constants import StationModes

options = {
    'starblazer': {

        'network_names': ['Dmitrov AM7', 'AM8C', 'Dmitrov Yamal 401', 'Khimki-ROSTEX-AM8', 'Khabarovsk AM5'],

        'AM7_vnos': [
            '40-REAL_IP-StarBlazer',
            'AM7-FNSKUT(113)',
            'AM7-BSPC(14)',
            'AM7-CB-Redund',
            'AM7-CNTA(15)',
            'AM7-INET (10)',
            'AM7-MARS(20)',
            'AM7-MORF(405)',
            'AM7-REA (590)',
            'AM7-StarBlazer',
            'AM7-Telecom365',
            'AM7-TessCom',
        ],

        'AM8C_vnos': ['AM8C-Af', 'AM8C-Eu'],

        'Yamal 401_vnos': [
            '300K-StarBlazer',
            '300K-Telekonika',
            '401-CB-Redund',
            '401-REAL_IP-StarBlazer',
            'Halliburton (918)',
            'PH-Бурение (443)',
            'Губкинский',
            'Нижневартовск',
            'Оренбург',
            'Резервные каналы',
            'Ханты-Мансийск',
        ],

        'AM8_vnos': ['AF', 'AM', 'EU'],

        'AM5_vnos': [
            'AM5-CB-Redund',
            'AM5-FNSKUT (113)',
            'AM5-REAL_IP-StarBlazer',
            'AM5-StarBlazer',
            'AM5-Telekonika'
        ],

        'AM7-REA_sub_vnos': ['AM7-ref'],
        'AM7-FNSKUT_sub_vnos': ['AM7-GAZ(18)'],
        '401-REAL_IP-StarBlazer_sub_vnos': ['CNTA (15)', 'DEUTAG', 'FNSKUT (113)', 'GAZ (18)'],
        'Halliburton_sub_vnos': ['INET (10)'],
        'Губкинский_sub_vnos': ['Иркутск'],
        'Ханты-Мансийск_sub_vnos': ['REA (590)', 'ya401-ref', 'Усинск'],
        'AM5-REAL_IP-StarBlazer_sub_vnos': ['AM5-Ref'],

        'station': {
            'vno_id': 34,
            'values': {
                'name': "station_07",
                'mode': StationModes.STAR,
                'serial': 123,
                'rx_controller': 'controller:8',
                'enable': 1
            },

        },
    },

}
