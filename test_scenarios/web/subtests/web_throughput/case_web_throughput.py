import math
import random
import time
import requests
import matplotlib.pyplot as plt
from multiprocessing import Process, Queue


from requests.adapters import HTTPAdapter

from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.abstract_http_driver import API
from src.drivers.drivers_provider import DriversProvider
from src.exceptions import InvalidOptionsException
from src.options_providers.options_provider import OptionsProvider, API_CONNECT

__author__ = 'dkudryashov'
__version__ = '0.1'
options_path = 'test_scenarios.web.subtests.web_throughput'
backup_name = 'case_web_throughput.txt'


class WebThroughputCase(CustomTestCase):
    """NMS WEB server throughput case"""

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(options_path)
        )
        cls.backup = BackupManager(OptionsProvider.get_connection(options_path))
        cls.backup.apply_backup(backup_name)

        cls.options = OptionsProvider.get_options(options_path)
        cls.number_of_get_requests = cls.options.get('number_of_get_requests')
        cls.number_of_post_requests = cls.options.get('number_of_post_requests')
        cls.number_of_users = cls.options.get('number_of_users')
        cls.ramp_up_period = cls.options.get('ramp_up_period')
        cls.get_urls = cls.options.get('get_urls')
        cls.post_urls = cls.options.get('post_urls')
        cls.static_urls = cls.options.get('static_urls')
        cls.system_options = OptionsProvider.get_system_options(options_path)

        cls.nms_address_port = cls.system_options.get(API_CONNECT).get('address')

    @staticmethod
    def process_results(results: list):
        # print(results)
        average_resp_times = []
        total_req_numbers = []
        number_of_users = []

        # Getting the begin and end time to plot from the first user
        for user in results:
            if list(user.keys())[0] == 'user-1':
                user1_requests_number = user.get('user-1').get('requests_number')
                user1_st_time = list(user1_requests_number[0].keys())
                user1_end_time = list(user1_requests_number[len(user1_requests_number) - 1])
                begin_time = user1_st_time[0]
                end_time = user1_end_time[0]
                break
        else:
            raise Exception('Cannot find user-1 results')

        x_pos = []
        i = 0
        while begin_time <= end_time:
            x_pos.append(i)
            total_resp_times = 0
            total_req_num = 0
            num_of_usrs = 0
            for user in results:
                username = list(user.keys())[0]

                for req_num in user.get(username).get('requests_number'):
                    key = list(req_num.keys())[0]
                    if key == begin_time:
                        total_req_num += req_num.get(key)
                        num_of_usrs += 1
                        break

                for resp_time in user.get(username).get('resp_times'):
                    key = list(resp_time.keys())[0]
                    if key == begin_time:
                        total_resp_times += resp_time.get(key)
                        break
            avr_resp_time = total_resp_times / num_of_usrs
            average_resp_times.append(avr_resp_time * 10000)

            number_of_users.append(num_of_usrs * 50)

            total_req_numbers.append(total_req_num)
            begin_time += 1
            i += 1

        # Getting the absolute maximum response time, its corresponding url
        max_resp_time = 0
        max_resp_time_url = None
        max_resp_time_user = None
        for user in results:
            username = list(user.keys())[0]
            if user.get(username).get('max_resp_time') > max_resp_time:
                max_resp_time = user.get(username).get('max_resp_time')
                max_resp_time_user = username
                max_resp_time_url = user.get(username).get('max_resp_time_url')
        return x_pos, total_req_numbers, average_resp_times, number_of_users, max_resp_time, max_resp_time_url

    def show_result(self, method, x_pos, total_req_numbers, average_resp_times, number_of_users):

        plt.xlabel('seconds')
        plt.ylabel('response time / num of requests')
        plt.title(f'{method} requests throughput with maximum {self.number_of_users} users')
        plt.plot(x_pos, total_req_numbers, label='total requests number per second')
        plt.plot(x_pos, average_resp_times, label='average response time, ms * 10')
        plt.plot(x_pos, number_of_users, label='number_of_users * 50')
        plt.legend(loc="upper left")
        # saving plot
        plt.savefig(f'web_throughput_{method.lower()}_{self.number_of_users}_users.png', dpi=300, bbox_inches='tight')
        # !!!! Blocking action
        # plt.show()

    def test_web_get_throughput(self):
        """WEB server throughput for GET requests test"""
        queue = Queue(maxsize=0)
        processes = []
        results = []
        for i in range(1, self.number_of_users + 1):
            processes.append(Process(
                target=self.handler,
                args=(queue, 'GET', i)
            ))
        # Adding new users according to ramp up period
        delay = self.ramp_up_period / self.number_of_users - 1
        if delay < 0:
            delay = 0.2
        i = 1
        for process in processes:
            process.start()
            print(f'Process {i} started')
            time.sleep(delay)
            i += 1

        for process in processes:
            while True:
                if not queue.empty():
                    print('Getting info from queue')
                    results.append(queue.get())
                if not process.is_alive():
                    process.join()
                    print(f'{process.pid} finished')
                    break

        for user in results:
            username = list(user.keys())[0]
            errors = user.get(username).get('errors')
            # Make sure that all requests are without errors
            if len(errors) == 1:
                errors = errors[0]
                self.assertEqual(0, len(errors), f'{username} errors={errors}')
            else:
                self.assertEqual(0, len(errors), f'{username} errors={len(errors)}')


        x_pos, \
        total_req_numbers, \
        average_resp_times, \
        number_of_users, \
        max_resp_time, \
        max_resp_time_url = self.process_results(results)

        self.show_result('GET', x_pos, total_req_numbers, average_resp_times, number_of_users)

        # Checking maximum response time among all the users and requests
        self.assertTrue(max_resp_time < 1.5, msg=f'{max_resp_time_url} response time {max_resp_time} seconds')

    # def test_web_post_throughput(self):
    #     """WEB server throughput for POST requests test"""
    #     queue = Queue()
    #     processes = []
    #     results = []
    #     for i in range(1, self.number_of_users + 1):
    #         processes.append(Process(
    #             target=self.handler,
    #             args=(queue, 'POST', i)
    #         ))
    #     for process in processes:
    #         process.start()
    #     for process in processes:
    #         process.join()
    #         results.append(queue.get())
    #         # Getting all the items from the queue
    #         if not queue.empty():
    #             results.append(queue.get())
    #
    #     for user in results:
    #         username = list(user.keys())[0]
    #         errors = user.get(username).get('errors')
    #         # Make sure that all requests are without errors
    #         self.assertEqual(0, len(errors), f'{username} errors={len(errors)}')
    #
    #     x_pos, \
    #     total_req_numbers, \
    #     average_resp_times, \
    #     number_of_users, \
    #     max_resp_time, \
    #     max_resp_time_url = self.process_results(results)
    #
    #     self.show_result('GET', x_pos, total_req_numbers, average_resp_times, number_of_users)
    #
    #     print(max_resp_time, max_resp_time_url)
    #     self.assertTrue(max_resp_time < 1.0, msg=f'{max_resp_time_url} response time {max_resp_time} seconds')

    def handler(self, queue: Queue, method, user_id):
        username = f'user-{user_id}'

        min_resp_time = math.inf
        max_resp_time = 0
        max_resp_time_url = None
        resp_times = []
        errors = []

        try:
            driver = DriversProvider.get_driver_instance(
                {
                    'type': API,
                    'address': self.nms_address_port,
                    'username': username,
                    'password': '12345',
                    'auto_login': True,
                }
            )
        except requests.exceptions.ConnectTimeout:
            if queue.full():
                raise Exception('Queue is full!!!')
            results = {
                username: {
                    'min_resp_time': 0,
                    'max_resp_time': 0,
                    'max_resp_time_url': 0,
                    'errors': [f'user {user_id} login timeout'],
                    'requests_number': 0,
                    'resp_times': 0,
                }
            }
            queue.put(results)
            return

        if method == 'GET':
            number_of_requests = self.number_of_get_requests
        elif method == 'POST':
            number_of_requests = self.number_of_post_requests
        else:
            raise InvalidOptionsException(f'Method {method} is not supported')

        # session = requests.Session()
        # session.mount('http://', HTTPAdapter(max_retries=3))
        # cookies = driver.get_cookies()

        for i in range(number_of_requests):
            if method == 'GET':
                path = random.choice(self.get_urls)
                st_time = time.perf_counter()
                try:
                    reply, error, error_code = driver.custom_get(path, timeout=10)
                except requests.exceptions.ConnectTimeout:
                    results = {
                        username: {
                            'min_resp_time': 0,
                            'max_resp_time': 0,
                            'max_resp_time_url': 0,
                            'errors': [f'user {user_id} request timeout (10 seconds) path={path}'],
                            'requests_number': 0,
                            'resp_times': 0,
                        }
                    }
                    queue.put(results)
                    return

                    # resp = session.get(f'{self.nms_address_port}{path}', timeout=3, cookies=cookies)
                # reply = None
                # error_code = None
                # try:
                #     result_obj = json.loads(resp.content)
                #     reply = result_obj.get('reply', None)
                #     error_code = result_obj.get('error_code', None)
                #     error = result_obj.get('error_log', None)
                # except JSONDecodeError:
                #     error = 'Invalid json in response'5

            elif method == 'POST':
                path = random.choice(list(self.post_urls.keys()))
                post = self.post_urls.get(path)
                st_time = time.perf_counter()
                try:
                    reply, error, error_code = driver.custom_post(path, payload=post)
                except requests.exceptions.ConnectTimeout:
                    results = {
                        username: {
                            'min_resp_time': 0,
                            'max_resp_time': 0,
                            'max_resp_time_url': 0,
                            'errors': [f'user {user_id} request timeout (10 seconds) path={path}'],
                            'requests_number': 0,
                            'resp_times': 0,
                        }
                    }
                    queue.put(results)
                    return
            else:
                raise InvalidOptionsException(f'Method {method} is not supported')

            if error_code is None:
                errors.append(path)

            resp_time = time.perf_counter() - st_time
            if resp_time < min_resp_time:
                min_resp_time = resp_time
            if resp_time > max_resp_time:
                max_resp_time = resp_time
                max_resp_time_url = path
            resp_times.append({'st_time': st_time, 'resp_time': resp_time})

        avr_resp_times = []
        # Start counting responses from a whole second
        begin = int(resp_times[0].get('st_time')) + 1
        next_ = begin + 1
        interval_resp_times = []
        interval_requests_number = []
        number_of_requests = 0

        for resp_time in resp_times:
            st_time = resp_time.get('st_time')
            # print(begin, next_, st_time)
            if st_time < begin:
                continue
            elif next_ > st_time > begin:
                avr_resp_times.append(resp_time.get('resp_time'))
                number_of_requests += 1
            elif st_time > next_:
                ts = 0
                for t in avr_resp_times:
                    ts += t
                if len(avr_resp_times) > 0:
                    interval_resp_times.append({next_ - 1: ts / len(avr_resp_times)})
                    interval_requests_number.append({next_ - 1: number_of_requests})
                avr_resp_times = [resp_time.get('resp_time')]
                next_ += 1
                number_of_requests = 0
            else:
                raise Exception('Unexpected condition')

        # session.close()

        # We don't need the final interval as it is not full
        if len(interval_requests_number) > 0:
            interval_requests_number.pop()
        if len(interval_resp_times) > 0:
            interval_resp_times.pop()

        results = {
            username: {
                'min_resp_time': min_resp_time,
                'max_resp_time': max_resp_time,
                'max_resp_time_url': max_resp_time_url,
                'errors': errors,
                'requests_number': interval_requests_number,
                'resp_times': interval_resp_times,
            }
        }

        if queue.full():
            raise Exception('Queue is full!!!')
        print(f'user {user_id} finished, putting in queue')
        queue.put(results, block=False)
