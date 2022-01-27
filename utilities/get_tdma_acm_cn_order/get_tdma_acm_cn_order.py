import json
import time
import requests
from src.drivers.uhp.constants import TDM_ACM_MODCOD2_ATTR_NAME
from src.drivers.uhp.uhp_requests_driver import UhpRequestsDriver
from bs4 import BeautifulSoup


def get_tdma_acm_cn_order(ip):
    """
    Getting UHP TDMA ACM modcods list sorted by C/N values from lowest to highest
    The results are saved into `tdma_acm_cn_order_uhp200x.txt`

    :param str ip: UHP IP address to get data from
    :returns None: this function returns None

    """
    uhp = UhpRequestsDriver(ip)
    uhp_hw = uhp.get_hw()
    uhp.set_nms_permission(control=False, monitoring=False)
    uhp.set_profile_basic(profile_number=1, params={'mode': 10})
    uhp.set_profile_modulator(profile_number=1)
    uhp.run_profile(profile_number=1)
    uhp.set_profile_tdma_rf(profile_number=1, params={'tdma_mc': 0})
    # Getting available modcods
    modcods = []
    uhp.set_profile_tdma_acm(profile_number=1, params={
        'acm_enable': 1,
        'mode': 1,
        'bpsk1_2': 1,
        'bpsk2_3': 1,
        'bpsk3_4': 1,
        'bpsk5_6': 1,
        'qpsk1_2': 1,
        'qpsk2_3': 1,
        'qpsk3_4': 1,
        'qpsk5_6': 1,
        'epsk1_2': 1,
        'epsk2_3': 1,
        'epsk3_4': 1,
        'epsk5_6': 1,
        'apsk1_2': 1,
        'apsk2_3': 1,
        'apsk3_4': 1,
        'apsk5_6': 1,
    })
    # Getting C/N thresholds for all available modcods
    modcods = [
        {'value': '0', 'name': 'BPSK 1/2'},
        {'value': '1', 'name': 'BPSK 2/3'},
        {'value': '2', 'name': 'BPSK 3/4'},
        {'value': '3', 'name': 'BPSK 5/6'},
        {'value': '4', 'name': 'QPSK 1/2'},
        {'value': '5', 'name': 'QPSK 2/3'},
        {'value': '6', 'name': 'QPSK 3/4'},
        {'value': '7', 'name': 'QPSK 5/6'},
        {'value': '8', 'name': '8PSK 1/2'},
        {'value': '9', 'name': '8PSK 2/3'},
        {'value': '10', 'name': '8PSK 3/4'},
        {'value': '11', 'name': '8PSK 5/6'},
        {'value': '12', 'name': '16APSK 1/2'},
        {'value': '13', 'name': '16APSK 2/3'},
        {'value': '14', 'name': '16APSK 3/4'},
        {'value': '15', 'name': '16APSK 5/6'},
    ]
    time.sleep(5)
    for m in modcods:
        # Getting default C/N threshold for current modcod
        res = requests.get(f'http://{ip}/ss40')
        if res:
            soup = BeautifulSoup(res.content, 'lxml')
            tables = soup.find_all('table')
            rows = tables[-2].find_all('tr')
            for i in range(1, len(rows)):
                row_data = rows[i].find_all('td')
                data = [td.text for td in row_data]
                if ' '.join(data[1].split('-')).lstrip() == m.get('name'):
                    m['acm_thr'] = data[2]
                    break
    # Sorting modcods in the ascending acm_thr order
    modcods.sort(key=lambda x: float(x.get('acm_thr')))

    with open(f'tdma_acm_cn_order_uhp200x.txt', 'w') as file:
        json.dump(modcods, file, indent=4, sort_keys=False)


if __name__ == '__main__':
    # modcods = [
    #     {'value': '5', 'name': 'SF QPSK 3/5', 'acm_thr': '3.9'},
    #     {'value': '108', 'name': 'SX QPSK 11/45', 'acm_thr': '1.2'}
    # ]
    # modcods.sort(key=lambda x: float(x.get('acm_thr')))
    # with open(f'test_tdm_cn_order.txt', 'w') as file:
    #     json.dump(modcods, file, indent=4, sort_keys=False)
    # # print(modcods)
    get_tdma_acm_cn_order('10.56.24.13')
