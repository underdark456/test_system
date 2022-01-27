from src import nms_api, test_api
from src.enum_types_constants import RouteTypes, PriorityTypes, StationModes
from utilities.network_up.mf_hub_1stn_up import MfHub1StnUp

options_path = 'test_scenarios.form_confirmation.shaper'
backup_name = 'default_config.txt'


class ShaperConfirmationCase(MfHub1StnUp):
    """"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.25'
    __execution_time__ = None  # approximate case execution time in seconds
    mf_hub_uhp = None
    stn1_uhp = None

    @classmethod
    def set_up_class(cls):
        super().set_up_class()
        test_options = test_api.get_options(options_path)
        # Creating and applying shaper to VNO
        shp = nms_api.create('network:0', 'shaper', test_options.get('vno_stn_shaper'))
        nms_api.update('vno:0', {'stn_shaper': shp})
        # Creating a shaper to individually assign to station
        shp = nms_api.create('network:0', 'shaper', test_options.get('stn_shaper'))
        # Adding 8 dummy stations
        for i in range(1, 9):
            stn = nms_api.create('vno:0', 'station', {
                'name': f'dummy{i}',
                'serial': 10000 + i,
                'enable': True,
                'rx_controller': 'controller:0',
                'mode': StationModes.STAR,
            })
            # Assigning individual stn_shaper to every even station
            if i % 2 == 0:
                nms_api.update(stn, {'stn_shaper': shp})

    def test_sample(self):
        pass