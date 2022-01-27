from src import nms_api, test_api


nms_options = test_api.get_nms()
nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))
test_api.get_uhp()
