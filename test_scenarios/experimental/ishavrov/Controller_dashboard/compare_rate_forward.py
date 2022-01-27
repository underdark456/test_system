from src import nms_api, test_api
from src.drivers.uhp.uhp_requests_driver import UhpRequestsDriver
import time

nms_options = test_api.get_nms()
nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))

UHP1 = UhpRequestsDriver('10.56.33.30')
# print(UHP1.get_modulator_stats())
def forward_rate_all():
     forward_rate_ctrl_uhp = []
     forward_rate_all_nms = nms_api.get_param('controller:0', 'forward_rate_all')
     # nms_api.wait_next_tick()
     forward_rate_all_uhp = UHP1.get_modulator_stats().get('rate')
     for i in range(1, 3):
          forward_rate_ctrl_uhp.append(UHP1.get_modulator_stats().get('outBytesC'))
          time.sleep(5)
     ctrl_map = list(map(int,forward_rate_ctrl_uhp))
     total_ctrl = ((ctrl_map[1] - ctrl_map[0]) * 8) / 5
     print(f'CTRL: {total_ctrl}')
     print(f'NMS_Rate: {forward_rate_all_nms}')
     print(f'UHP_Rate: {int(forward_rate_all_uhp) / 1000}')

# forward_rate_all()

def forward_p():
     p1_nms = nms_api.get_param('controller:0', 'forward_rate1')
     p2_nms = nms_api.get_param('controller:0', 'forward_rate2')
     p1_uhp = []
     p2_uhp = []
     for i in range(1, 3):
          p1_uhp.append(UHP1.get_modulator_stats().get('outBytesP1'))
          time.sleep(5)
     for i in range(1, 3):
          p2_uhp.append(UHP1.get_modulator_stats().get('outBytesP2'))
          time.sleep(5)
     p1_map = list(map(int, p1_uhp))
     p2_map = list(map(int, p2_uhp))
     print(p1_map)
     print(p2_map)
forward_p()
     # nms_api.wait_next_tick()
     # forward_rate_all_nms.append(nms_api.get_param('controller:0','forward_rate_all'))
     # p1_nms.append(nms_api.get_param('controller:0', 'forward_rate1'))
     #
     # time.sleep(5)
     # forward_rate_all_uhp.append(UHP1.get_modulator_stats().get('rate'))
     # forward_rate_ctrl_uhp.append(UHP1.get_modulator_stats().get('outBytesC'))
     # p1_uhp.append(UHP1.get_modulator_stats().get('outBytesP1'))

# print(f"NMS_Rate:{forward_rate_all_nms}")
# print(f"UHP_Rate:{forward_rate_all_uhp}")
# print(f"UHP_CTRL:{forward_rate_ctrl_uhp}")
# print(f"UHP_P1:{p1_uhp}")
# print(f"NMS_P1:{p1_nms}")
