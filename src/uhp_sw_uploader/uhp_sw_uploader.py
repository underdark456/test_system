import os
import socket
import telnetlib
import threading
import time
from typing import Union

import requests
from http import HTTPStatus
from bs4 import BeautifulSoup
from src.exceptions import InvalidOptionsException
from src.options_providers.options_provider import OptionsProvider


class UhpSwUploader(object):

    def __init__(self):
        self._remote_sw_dir = None
        self._load_older = False

    # TODO: finalize load_older
    def upload(self, uhps: list, load_older=False):
        """
        Upload software to UHPs

        :uhps list: list of dictionaries containing UHP parameters, i.e {'device_ip': '127.0.0.1', 'model': 'UHP200' ...
        :load_older bool: if False do not upload older software to UHP
        """
        st_time = time.perf_counter()
        self._load_older = load_older
        if not isinstance(uhps, list):
            raise InvalidOptionsException(f'UHPs must be passed as list of dictionaries obtained from OptionsProvider')
        self._get_remote_sw_dir()
        _threads = []
        for uhp in uhps:
            _sw_filename = self._get_sw_filename(uhp.get('model'))
            if _sw_filename is None:
                print(f'Cannot determine software filename for {uhp.get("device_ip")}')
            else:
                _sw_full_path = self._remote_sw_dir + os.sep + _sw_filename
                if not os.path.isfile(_sw_full_path):
                    print(f'{_sw_full_path} does not exist, skipping {uhp.get("device_ip")} sw upload')
                    continue
                if not self._load_to_ram(uhp, _sw_full_path):
                    continue
                _t = threading.Thread(target=self._image_write, args=(uhp, ), kwargs={'bank': 1})
                _t.start()
                _threads.append(_t)
        for t in _threads:
            t.join()
        # Waiting for responses after reboot
        # TODO: async?
        for uhp in uhps:
            sw = uhp.get('web_driver').get_software_version(timeout=45)
            if sw:
                print(f'UHP {uhp.get("device_ip")} rebooted, current SW={sw}')
        print(f'Total uploading time {round(time.perf_counter() - st_time, 1)} seconds')

    @staticmethod
    def _get_sw_filename(model: str) -> Union[str, None]:
        """
        Get software filename based on UHP model

        :param str model: UHP model
        :returns Union[str, None] sw_filename: software version filename, or None if cannot be determined
        """
        if model == 'UHP200X':
            sw_filename = 'uhp-200.S2X'
        elif model == 'UHP200':
            sw_filename = 'uhp-soft.240'
        elif model in ('UHP100', 'UHP100X'):
            sw_filename = 'uhp-soft.100'
        else:
            sw_filename = None
        return sw_filename

    @staticmethod
    def _load_to_ram(uhp_dict, sw_filename_full_path):
        print(uhp_dict.get('device_ip'), sw_filename_full_path)
        _uhp_ip = uhp_dict.get("device_ip")
        _uhp_web_driver = uhp_dict.get('web_driver')
        with open(sw_filename_full_path, 'rb') as file:
            files = {'upfile': file}
            # TODO: implement POST in UhpRequestsDriver
            res = requests.post(f'http://{_uhp_ip}/cc41', files=files, timeout=3)
            if res.status_code != HTTPStatus.OK:
                return False

        # Must be called once prior to checking if it is possible to write to RAM
        _uhp_web_driver.get_request(f'http://{_uhp_ip}/cc41')

        # Waiting for software in RAM
        res = _uhp_web_driver.get_request(f'http://{_uhp_ip}/cc41')
        if not res:
            return False
        soup = BeautifulSoup(res.content, 'html.parser')
        tags = soup.find_all('input')
        for tag in tags:
            if tag.get('id') == 'write':
                if tag.get('disabled') is not None:
                    print('Software CANNOT be written, probably wrong version')
                else:
                    print('Software CAN be written')
                    return True
        time.sleep(1)
        return False

    # TODO: get rid of print statements
    @staticmethod
    def _image_write(uhp_dict, bank=1):
        # closing telnet connection by sending exit command via network script
        if not uhp_dict.get('web_driver').exit_telnet():
            return False
        _ip = uhp_dict.get('device_ip')
        print(f'Connecting via telnet to {_ip}...')
        try:
            tn = telnetlib.Telnet(_ip, timeout=3)
        except socket.timeout:
            print(f'Cannot connect to {_ip} via telnet: socket timeout')
            return False
        print(f'{_ip} telnet connection OK')
        time.sleep(2)

        tn.write(f'image write\r\n'.encode('UTF-8'))
        response = tn.read_until(b"Default load bank", 150)
        if not response.count(b"Default load bank"):
            print(f'{_ip} Default load bank output is not seen: {response}')
            return False
        print(f'{_ip} Writing image to bank {bank}')
        time.sleep(3)
        tn.write(f'{bank}\r\n'.encode('UTF-8'))
        time.sleep(2)
        tn.write('y\r\n'.encode('UTF-8'))
        response = tn.read_until(b"Default load bank", 150)
        if not response.count(b"Default load bank"):
            print(f'{_ip} Default load bank is not seen after writing to flash: {response}')
            return False
        print(f'{_ip} Image has been written, rebooting...')
        tn.write('reboot\r\n'.encode('UTF-8'))
        time.sleep(1)
        tn.write('y\r\n'.encode('UTF-8'))
        tn.close()
        time.sleep(1)
        return True

    def _get_remote_sw_dir(self):
        self._remote_sw_dir = OptionsProvider.get_system_options('global_options').get('uhp_sw_dir')


if __name__ == '__main__':
    _uhps = OptionsProvider.get_uhp(default=False)
    uploader = UhpSwUploader()
    uploader.upload(_uhps)
