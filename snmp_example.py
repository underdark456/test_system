from src.drivers.snmp.snmp_executor import SnmpExecutor
from src.drivers.snmp.uhp_snmp_driver import UhpSnmpDriver

requests_delay = 1
ip = '10.0.2.228'
public = 'public'
private = 'private'


def delay_control():
    ex = SnmpExecutor(requests_delay)
    dr = UhpSnmpDriver(ex, ip, public, private)

    avg_cn_50_steps = dr.tdma().rem_table().carrier_to_noise(0).get(dr.GET_AVG, 50)

    ex.set_delay(0.1)
    fast_avg_cn_50_steps = dr.tdma().rem_table().carrier_to_noise(0).get(dr.GET_AVG, 50)


def get_value():
    dr = UhpSnmpDriver(SnmpExecutor(requests_delay), ip, public, private)
    cn_reader = dr.tdma().rem_table().carrier_to_noise(0)

    current_cn = cn_reader.get()
    min_cn = cn_reader.get(dr.GET_MIN)
    avg_cn = cn_reader.get(dr.GET_AVG)
    avg_cn_50_steps = cn_reader.get(dr.GET_AVG, 50)
    max_cn = cn_reader.get(dr.GET_MAX)
    cn_min, cn_avg, cn_max = cn_reader.get(dr.GET_MIN_AVG_MAX, 20)

    p1_speed = dr.tdma().rem_table().p1_bytes(0).get(dr.GET_AS_SPEED)
    wtf = dr.shaper().stream_speed(0).get()


def set_value():
    dr = UhpSnmpDriver(SnmpExecutor(requests_delay), ip, public, private)

    dr.mobile().tx_control().set(1)

    dr.control().save_config(1)


if __name__ == '__main__':
    get_value()
