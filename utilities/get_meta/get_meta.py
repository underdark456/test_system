import json
import os
import re

import requests
from bs4 import BeautifulSoup

from src.backup_manager.backup_manager import BackupManager
from src.constants import NO_ERROR
from src.drivers.drivers_provider import DriversProvider
from src.drivers.uhp.constants import TDM_TX_MODCOD_ATTR_NAME, TDMA_RF_MODCOD_ATTR_NAME
from src.drivers.uhp.uhp_requests_driver import UhpRequestsDriver
from src.drivers.uhp.uhp_telnet_driver import UhpTelnetDriver
from src.exceptions import InvalidOptionsException
from src.nms_entities.basic_entities.nms import Nms
from src.options_providers.options_provider import OptionsProvider, API_CONNECT

options_path = 'utilities.get_meta'


def get_driver():
    connection_options = OptionsProvider.get_connection('global_options', API_CONNECT)
    api = DriversProvider.get_driver_instance(connection_options)
    return api


def get_meta():
    backup = BackupManager()
    backup.apply_backup('each_entity.txt')
    api = get_driver()
    nms = Nms(api, 0, 0)
    nms_version = nms.get_param('version').split()[1].replace('.', '_')
    options = OptionsProvider.get_options(options_path)
    path = 'api/form/edit/{}=0'
    resulting_json = {}
    for entity in options.get('entities'):
        meta_path = path.format(entity)
        reply, error, error_code = api.custom_get(meta_path)
        if error_code != NO_ERROR or error != '' or reply == '' or reply is None:
            raise Exception(f'Cannot get {entity} meta')
        resulting_json[entity] = reply

    with open(f'{os.path.dirname(os.path.abspath(__file__))}{os.sep}meta_{nms_version}.txt', 'w') as file:
        json.dump(resulting_json, file, indent=4, sort_keys=True)


# TODO: get modcodes from UHP instead of NMS
def get_modcodes():
    res = requests.get('http://10.56.24.40:8000/static/js/16.js')
    if res:
        js_code = res.text

        modcodes = {}

        start = js_code.find('[{"name":"SF QPSK 1/4"')
        end = js_code.find('},"27":{"input":"select","format":"modcod","values"')
        if end > start:
            result = ''
            for i in range(start, end):
                result += js_code[i]
            modcodes['tx_modcod'] = json.loads(result)

        start = js_code.find('[{"name":"BPSK 1/2","value":0}')
        end = js_code.find('},"32":{"input":"select"')
        if end > start:
            result = ''
            for i in range(start, end):
                result += js_code[i]
            modcodes['tdma_mc'] = json.loads(result)

        api = get_driver()
        nms = Nms(api, 0, 0)
        nms_version = nms.get_param('version').split()[1].replace('.', '_')

        with open(f'{os.path.dirname(os.path.abspath(__file__))}{os.sep}modcodes_{nms_version}.txt', 'w') as file:
            json.dump(modcodes, file, indent=4, sort_keys=True)


def get_modcodes_from_uhp(uhp_ip):
    if uhp_ip is None:
        raise InvalidOptionsException('Cannot get UHP IP address from options')
    uhp = UhpRequestsDriver(uhp_ip)
    uhp_telnet = UhpTelnetDriver(uhp_ip)
    uhp_telnet.get_raw_result('pro 8 type manual scpc')
    uhp_hw_ver = uhp.get_support_info_value(regex=re.compile(r'\(h/w\suhp-[0-9]+[a-z]*')).replace('-', '_')
    res = uhp.get_request(f'http://{uhp_ip}/ct3?da=8')
    modcodes = {'tx_modcod': [], 'tdma_mc': []}
    error = False
    if res:
        soup = BeautifulSoup(res.content, 'html.parser')
        tags = soup.find_all('select')
        for tag in tags:
            name = tag.get('name', None)
            value = tag.get('value', None)
            if name != TDM_TX_MODCOD_ATTR_NAME:
                continue
            options = tag.find_all('option')
            for option in options:
                modcodes.get('tx_modcod').append({'name': option.text, 'value': int(option.get('value'))})
    else:
        print('Cannot get TDM modcodes')
        error = True
    uhp_telnet.get_raw_result('pro 8 type manual master')
    res = uhp.get_request(f'http://{uhp_ip}/cd3?da=8')
    if res:
        soup = BeautifulSoup(res.content, 'html.parser')
        tags = soup.find_all('select')
        for tag in tags:
            name = tag.get('name', None)
            value = tag.get('value', None)
            if name != TDMA_RF_MODCOD_ATTR_NAME:
                continue
            options = tag.find_all('option')
            for option in options:
                modcodes.get('tdma_mc').append(
                    {'name': option.text.replace('\t', '').lstrip().replace('-', ' '), 'value': int(option.get('value'))})
    else:
        print('Cannot get TDMA modcodes')
        error = True
    if not error:
        with open(f'{os.path.dirname(os.path.abspath(__file__))}{os.sep}modcodes_{uhp_hw_ver}.txt', 'w') as file:
            json.dump(modcodes, file, indent=4, sort_keys=True)


if __name__ == '__main__':
    options = OptionsProvider.get_system_options('global_options')
    get_meta()
    # get_modcodes()
    # uhp_ip = options.get('uhp2_ip')
    # get_modcodes_from_uhp(uhp_ip)
