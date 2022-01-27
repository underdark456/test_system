import random
from src.custom_test_case import CustomTestCase
from src.drivers.snmp.snmp_executor import SnmpExecutor
from src.drivers.snmp.snmp_executor_v3 import SnmpExecutorV3
from src.drivers.uhp.uhp_requests_driver import UhpRequestsDriver
from src.enum_types_constants import SnmpModes, SnmpAuth
from src.options_providers.options_provider import OptionsProvider

__author__ = 'dkudryashov'
__version__ = '0.1'
options_path = 'test_scenarios.uhp_ip_protocols.subtests.snmp'
backup_name = 'default_config.txt'


class UhpSnmpV3ModesCase(CustomTestCase):
    """UHP SNMPv3 capabilities case. Correct/incorrect credentials. Correct/incorrect modes"""

    @classmethod
    def set_up_class(cls):
        cls.uhp1_ip = OptionsProvider.get_system_options(options_path).get('uhp1_ip')
        cls.uhp = UhpRequestsDriver(cls.uhp1_ip)
        cls.oid_executor = SnmpExecutorV3()
        cls.oid_executor_v2 = SnmpExecutor()
        cls.test_oid = '.1.3.6.1.4.1.8000.22.1.5.0'

    def test_snmpv3_no_auth_no_priv(self):
        """No_Auth,No_Priv mode test. Random username. Correct and incorrect requests modes and credentials"""
        for u in (1, 8, 16):
            username = UhpSnmpV3ModesCase._generate_random_string(u)
            self.uhp.set_snmp({
                'snmp_mode': SnmpModes.V3,
                'access1_ip': '255.255.255.255',
                'snmp_user': username,
                'snmp_auth': SnmpAuth.NO_AUTH,
            })
            result = self.oid_executor.get(
                self.uhp1_ip,
                161,
                username,
                self.test_oid,
            )
            with self.subTest(f'mode=No_auth,No_priv, correct username={username}'):
                self.assertIsNotNone(result)

            # SNMPv2
            result = self.oid_executor_v2.get(
                self.uhp1_ip,
                161,
                username,
                self.test_oid,
            )
            with self.subTest(f'mode=SNMPv2c'):
                self.assertIsNone(result)

            # Incorrect username
            result = self.oid_executor.get(
                self.uhp1_ip,
                161,
                'qwerty',
                self.test_oid,
            )
            with self.subTest(f'mode=No_auth,No_priv, incorrect username=qwerty'):
                self.assertIsNone(result)

            # use Auth,No_Priv
            result = self.oid_executor.get(
                self.uhp1_ip,
                161,
                username,
                '.1.3.6.1.4.1.8000.22.1.5.0',
                authKey='12345678'
            )
            with self.subTest(f'mode=Auth,No_Priv, correct username={username} auth=12345678'):
                self.assertIsNone(result)

            # use Auth,Priv
            result = self.oid_executor.get(
                self.uhp1_ip,
                161,
                username,
                self.test_oid,
                authKey='12345678',
                privKey='87654321',
            )
            with self.subTest(f'mode=Auth,Priv, correct username={username}, auth=12345678, priv=87654321'):
                self.assertIsNone(result)

    def test_snmpv3_auth_no_priv(self):
        """Auth,No_Priv mode test. Random username, auth password, of minimum and maximum lengths"""
        # Wrong modes and credentials are also tested - expected to get no response
        for u in (1, 8, 16):
            username = UhpSnmpV3ModesCase._generate_random_string(u)
            for a in range(8, 17):
                auth_key = UhpSnmpV3ModesCase._generate_random_string(a)
                self.uhp.set_snmp({
                    'snmp_mode': SnmpModes.V3,
                    'access1_ip': '255.255.255.255',
                    'snmp_user': username,
                    'snmp_auth': SnmpAuth.AUTH_NO_PRIV,
                    'snmp_read': auth_key,
                })
                result = self.oid_executor.get(
                    self.uhp1_ip,
                    161,
                    username,
                    self.test_oid,
                    authKey=auth_key,
                )
                with self.subTest(f'mode=Auth,No_priv, correct username={username}, correct auth={auth_key}'):
                    self.assertIsNotNone(result)

                # SNMPv2
                result = self.oid_executor_v2.get(
                    self.uhp1_ip,
                    161,
                    username,
                    self.test_oid,
                )
                with self.subTest(f'mode=SNMPv2c'):
                    self.assertIsNone(result)

                # Incorrect username
                result = self.oid_executor.get(
                    self.uhp1_ip,
                    161,
                    'user1',
                    self.test_oid,
                    authKey=auth_key,
                )
                with self.subTest(f'mode=Auth,No_priv, incorrect username=user1, correct auth={auth_key}'):
                    self.assertIsNone(result)
                # Incorrect auth_key
                result = self.oid_executor.get(
                    self.uhp1_ip,
                    161,
                    username,
                    self.test_oid,
                    authKey='qwerty123',
                )
                with self.subTest(f'mode=Auth,No_priv, correct username={username}, incorrect auth=qwerty123'):
                    self.assertIsNone(result)

                # use No_Auth,No_Priv
                result = self.oid_executor.get(
                    self.uhp1_ip,
                    161,
                    username,
                    self.test_oid,
                )
                with self.subTest(f'mode=No_Auth,No_Priv, correct username={username}'):
                    self.assertIsNone(result)

                # use Auth,Priv
                result = self.oid_executor.get(
                    self.uhp1_ip,
                    161,
                    username,
                    self.test_oid,
                    authKey=auth_key,
                    privKey='12345678',
                )
                with self.subTest(f'mode=Auth,Priv, correct username={username}, auth={auth_key}, priv=12345678'):
                    self.assertIsNone(result)

    def test_snmpv3_auth_priv(self):
        """Auth,Priv mode test. Random username, auth password, and privacy password of minimum and maximum lengths"""
        # Wrong modes and credentials are also tested - expected to get no response
        # username length
        for u in (1, 8, 16):
            username = UhpSnmpV3ModesCase._generate_random_string(u)
            # auth password length
            for a in (8, 16):
                auth_key = UhpSnmpV3ModesCase._generate_random_string(a)
                # priv password length
                for p in (8, 16):
                    priv_key = UhpSnmpV3ModesCase._generate_random_string(p)
                    self.uhp.set_snmp({
                        'snmp_mode': SnmpModes.V3,
                        'access1_ip': '255.255.255.255',
                        'snmp_user': username,
                        'snmp_auth': SnmpAuth.AUTH_PRIV,
                        'snmp_read': auth_key,
                        'snmp_write': priv_key,
                    })
                    result = self.oid_executor.get(
                        self.uhp1_ip,
                        161,
                        username,
                        self.test_oid,
                        authKey=auth_key,
                        privKey=priv_key,
                    )
                    with self.subTest(f'mode=Auth,Priv, correct username={username}, correct auth={auth_key}, '
                                      f'correct priv={priv_key}'):
                        self.assertIsNotNone(result)

                    # SNMPv2
                    result = self.oid_executor_v2.get(
                        self.uhp1_ip,
                        161,
                        username,
                        self.test_oid,
                    )
                    with self.subTest(f'mode=SNMPv2c'):
                        self.assertIsNone(result)

                    # incorrect username
                    result = self.oid_executor.get(
                        self.uhp1_ip,
                        161,
                        'user',
                        self.test_oid,
                        authKey=auth_key,
                        privKey=priv_key,
                    )
                    with self.subTest(f'mode=Auth,Priv, incorrect username=user, correct auth={auth_key}, '
                                      f'correct priv={priv_key}'):
                        self.assertIsNone(result)
                    # incorrect auth key
                    result = self.oid_executor.get(
                        self.uhp1_ip,
                        161,
                        username,
                        self.test_oid,
                        authKey='12345678',
                        privKey=priv_key,
                    )
                    with self.subTest(f'mode=Auth,Priv, correct username={username}, incorrect auth=12345678, '
                                      f'correct priv={priv_key}'):
                        self.assertIsNone(result)

                    # incorrect priv key
                    result = self.oid_executor.get(
                        self.uhp1_ip,
                        161,
                        username,
                        self.test_oid,
                        authKey=auth_key,
                        privKey='12345678',
                    )
                    with self.subTest(f'mode=Auth,Priv, correct username={username}, correct auth={auth_key}, '
                                      f'incorrect priv=12345678'):
                        self.assertIsNone(result)

                    # use No_Auth,No_Priv
                    result = self.oid_executor.get(
                        self.uhp1_ip,
                        161,
                        username,
                        self.test_oid,
                    )
                    with self.subTest(f'mode=No_Auth,No_Priv, correct username={username}'):
                        self.assertIsNone(result)

                    # use Auth,No_Priv
                    result = self.oid_executor.get(
                        self.uhp1_ip,
                        161,
                        username,
                        self.test_oid,
                        authKey=auth_key,
                    )
                    with self.subTest(f'mode=Auth,No_Priv, correct username={username}, correct auth={auth_key}'):
                        self.assertIsNone(result)

    @staticmethod
    def _generate_random_string(length=8):
        whitespace = r' \t\n\r\v\f'
        ascii_lowercase = 'abcdefghijklmnopqrstuvwxyz'
        ascii_uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        ascii_letters = ascii_lowercase + ascii_uppercase
        digits = '0123456789'
        # Some characters are not accepted by UHP: quotes, ampersands, slash, plus, greater, less
        punctuation = r"""!#$%()*,-.:;=?@[\]^_`{|}~"""
        printable = digits + ascii_letters + punctuation + whitespace
        random_string = ''
        for _ in range(length):
            # Keep appending random characters using chr(x)
            random_string += printable[random.randint(0, len(printable) - 1)]
        return random_string

