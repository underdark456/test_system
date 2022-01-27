import time
from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes, Checkbox, StationModes
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.profile import Profile
from src.nms_entities.basic_entities.scheduler import Scheduler
from src.nms_entities.basic_entities.shaper import Shaper
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.vno import Vno
from src.nms_entities.paths_manager import PathsManager
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.api.tools'
backup_name = 'default_config.txt'


class ApiStationsToolCase(CustomTestCase):
    """Test cases for station tool"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.25'
    __execution_time__ = 25  # approximate case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()

        cls.system_options = OptionsProvider.get_system_options(options_path)
        cls.options = OptionsProvider.get_options(options_path)

    def test_stations_tool_all_frontend_vars_1_stn(self):
        """Test station tool response upon requesting all vars that can be selected in frontend for 1 station"""
        self.backup.apply_backup('default_config.txt')
        self.net = Network.create(self.driver, 0, {'name': 'test_net'})
        self.tp = Teleport.create(
            self.driver,
            self.net.get_id(),
            {'name': 'test_tp', 'tx_lo': 0, 'rx1_lo': 0, 'rx2_lo': 0}
        )
        self.vno = Vno.create(self.driver, self.net.get_id(), {'name': 'test_vno'})
        self.hub_shp = Shaper.create(self.driver, self.net.get_id(), {'name': 'test_hub_shp'})
        self.stn_shp = Shaper.create(self.driver, self.net.get_id(), {'name': 'test_stn_shp'})
        self.pro_set = Profile.create(self.driver, self.net.get_id(), {'name': 'test_pro_set'})
        self.sch = Scheduler.create(self.driver, self.net.get_id(), {'name': 'test_scheduler'})

        self.mf_hub = Controller.create(self.driver, self.net.get_id(), {
            'name': 'test_ctrl',
            'mode': ControllerModes.MF_HUB,
            'teleport': f'teleport:{self.tp.get_id()}',
        })

        self.ext_gw = Controller.create(self.driver, self.net.get_id(), {
            'name': 'test_ext_gw',
            'mode': ControllerModes.GATEWAY,
            'tx_controller': f'controller:{self.mf_hub.get_id()}',
            'device_ip': '127.0.0.1',
            'teleport': f'teleport:{self.tp.get_id()}',
            'inroute': 24,
        })

        self.stn = Station.create(self.driver, self.vno.get_id(), {
            'name': 'test_stn',
            'enable': Checkbox.ON,
            'serial': 12345,
            'mode': StationModes.STAR,
            'rx_controller': f'controller:{self.mf_hub.get_id()}',
            'red_serial': 763543,
            'ext_gateway': f'controller:{self.ext_gw.get_id()}',
            'profile_set': f'profile_set:{self.pro_set.get_id()}',
            'scheduler': f'scheduler:{self.sch.get_id()}',
            'sw_load_id': 15,
            'hub_shaper': f'shaper:{self.hub_shp.get_id()}',
            'stn_shaper': f'shaper:{self.stn_shp.get_id()}',
            'hub_low_cn': 2.3,
            'hub_high_cn': 25.4,
            'station_low_cn': 2.2,
            'station_high_cn': 25.3,
        })
        path = PathsManager._API_STATION_LIST.format('network', 0)
        _vars = self.options.get('station_tool_vars_frontend')
        reply, error, error_code = self.driver.custom_post(
            path,
            payload={'vars': ','.join(_vars) + ','}
        )
        reply_list = reply.get('list')[0]
        self.assertEqual(
            len(_vars),
            len(reply_list),
            msg=f'Number of vars requested {len(_vars)}, '
                f'number of values returned {len(reply_list)}'
        )
        for i in range(len(_vars)):
            self.assertEqual(
                _vars[i],
                reply.get('vars')[i],
                msg=f'{i} var requested {_vars[i]}, {i} var in response {reply.get("vars")[i]}'
            )

    def test_stations_tool_32768_stations(self):
        """Stations tool response 32768 stations"""
        self.backup.apply_backup('32768_stations_1_vno.txt')
        path = PathsManager._API_STATION_LIST.format('network', 0)
        reply, error, error_code = self.driver.custom_post(
            path,
            payload={'vars': 'name,state,faults,cn_on_hub,station_cn,tx_margin,rx_errors,down_times,fault_times,'}
        )
        reply_list = reply.get('list')
        self.assertEqual(32768, len(reply_list), msg=f'Number of stations in reply {len(reply_list)}, expected 32768')
        for stn in reply_list:
            self.assertEqual(9, len(stn), msg=f'Number of returned vars for one of the stations {len(stn)}, expected 9')

        path = PathsManager._API_STATION_LIST.format('vno', 0)
        reply, error, error_code = self.driver.custom_post(
            path,
            payload={'vars': 'name,state,faults,cn_on_hub,station_cn,tx_margin,rx_errors,down_times,fault_times,'}
        )
        reply_list = reply.get('list')
        self.assertEqual(32768, len(reply_list), msg=f'Number of stations in reply {len(reply_list)}, expected 32768')
        for stn in reply_list:
            self.assertEqual(9, len(stn), msg=f'Number of returned vars for one of the stations {len(stn)}, expected 9')

        path = PathsManager._API_STATION_LIST.format('controller', 0)
        reply, error, error_code = self.driver.custom_post(
            path,
            payload={'vars': 'name,state,faults,cn_on_hub,station_cn,tx_margin,rx_errors,down_times,fault_times,'}
        )
        reply_list = reply.get('list')
        self.assertEqual(32768, len(reply_list), msg=f'Number of stations in reply {len(reply_list)}, expected 32768')
        for stn in reply_list:
            self.assertEqual(9, len(stn), msg=f'Number of returned vars for one of the stations {len(stn)}, expected 9')

    def test_stations_tool_all_frontend_vars_10000_stn(self):
        """Test station tool response upon requesting all vars that can be selected in frontend for 10000 stations"""
        self.backup.apply_backup('10000_stations_in_1_network.txt')
        _vars = self.options.get('station_tool_vars_frontend')
        path = PathsManager._API_STATION_LIST.format('network', 0)
        st_time = time.perf_counter()
        reply, error, error_code = self.driver.custom_post(
            path,
            payload={'vars': ','.join(_vars) + ','}
        )
        self.info(f'Response time {round(time.perf_counter() - st_time, 3)} seconds')
        self.assertEqual(
            len(_vars),
            len(reply.get('vars')),
            msg=f'{len(_vars)} vars requested, {len(reply.get("list")[0])} vars returned'
        )
        self.assertEqual(
            10000,
            len(reply.get('list')),
            msg=f'10000 stations, returned vars for {len(reply.get("list"))}'
        )

    def test_stations_tool_all_frontend_vars_32768_stn(self):
        """Test station tool response upon requesting all vars that can be selected in frontend for 32768 stations"""
        self.backup.apply_backup('32768_stations_1_vno.txt')
        _vars = self.options.get('station_tool_vars_frontend')
        path = PathsManager._API_STATION_LIST.format('network', 0)
        st_time = time.perf_counter()
        reply, error, error_code = self.driver.custom_post(
            path,
            payload={'vars': ','.join(_vars) + ','}
        )
        self.info(f'Response time {round(time.perf_counter() - st_time, 3) } seconds')
        self.assertEqual(
            len(_vars),
            len(reply.get('vars')),
            msg=f'{len(_vars)} vars requested, {len(reply.get("list")[0])} vars returned'
        )
        self.assertEqual(
            32768,
            len(reply.get('list')),
            msg=f'10000 stations, returned vars for {len(reply.get("list"))}'
        )
