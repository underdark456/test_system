import json
import time
import requests
from src.drivers.uhp.constants import TDM_ACM_MODCOD2_ATTR_NAME
from src.drivers.uhp.uhp_requests_driver import UhpRequestsDriver
from bs4 import BeautifulSoup


def get_tdm_acm_cn_order(ip):
    """
    Getting UHP TDM ACM modcods list sorted by C/N values from lowest to highest
    The results for short frames and long frames are saved into two files for UHP200X:
        `sf_tdm_acm_cn_order_uhp200x.txt` and `lf_tdm_acm_cn_order_uhp200x.txt`
    The results for UHP200 are saved into `sf_tdm_acm_cn_order_uhp200.txt`

    :param str ip: UHP IP address to get data from
    :returns None: this function returns None

    """
    uhp = UhpRequestsDriver(ip)
    uhp_hw = uhp.get_hw()
    uhp.set_nms_permission(control=False, monitoring=False)
    uhp.set_profile_basic(profile_number=1, params={'mode': 10})
    uhp.set_profile_modulator(profile_number=1)
    uhp.run_profile(profile_number=1)
    for frame_type in ('sf', 'lf'):
        if uhp_hw == 'uhp200' and frame_type == 'lf':  # No long frames for UHP200
            continue
        if uhp_hw == 'uhp200x':
            if frame_type == 'sf':
                uhp.set_profile_tdm_tx(profile_number=1, params={'tx_modcod': 1})
            else:
                uhp.set_profile_tdm_tx(profile_number=1, params={'tx_modcod': 34})
        else:
            uhp.set_profile_tdm_tx(profile_number=1, params={'tx_modcod': 2})
        # Getting available modcods
        modcods = []
        req = requests.get(f'http://{ip}/ca3?da=1')
        if req:
            soup = BeautifulSoup(req.content, 'html.parser')
            tags = soup.find_all('select')
            for tag in tags:
                name = tag.get('name')
                if name is None:
                    continue
                elif name == TDM_ACM_MODCOD2_ATTR_NAME:
                    options = tag.find_all('option')
                    for option in options:
                        modcods.append({'value': option.get('value'), 'name': option.contents[0]})
        # Getting C/N thresholds for all available modcods
        for m in modcods:
            uhp.set_profile_tdm_acm(profile_number=1, params={'acm_enable': 1, 'acm_thr': 0.0, 'acm_mc2': m.get('value')})
            time.sleep(2)
            # Getting default C/N threshold for current modcod
            res = requests.get(f'http://{ip}/ss40')
            if res:
                soup = BeautifulSoup(res.content, 'lxml')
                tables = soup.find_all('table')
                rows = tables[-2].find_all('tr')
                for i in range(1, len(rows)):
                    row_data = rows[i].find_all('td')
                    data = [td.text for td in row_data]
                    if data[0] == '2':
                        m['acm_thr'] = data[2]
                        break
        # Sorting modcods in the ascending acm_thr order
        modcods.sort(key=lambda x: float(x.get('acm_thr')))
        with open(f'{frame_type}_tdm_acm_cn_order_{uhp_hw}.txt', 'w') as file:
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
    get_tdm_acm_cn_order('10.56.24.11')
