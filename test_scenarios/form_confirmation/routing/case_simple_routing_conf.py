from src import nms_api, test_api
from src.enum_types_constants import RouteTypes, PriorityTypes
from utilities.network_up.mf_hub_1stn_up import MfHub1StnUp

options_path = 'test_scenarios.form_confirmation.routing'
backup_name = 'default_config.txt'


class RoutingExpectedUhpRecordsCase(MfHub1StnUp):
    """Test if each route type creates the expected routing records in UHP for hub and station"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.25'
    __execution_time__ = None  # approximate case execution time in seconds
    mf_hub_uhp = None
    stn1_uhp = None

    @classmethod
    def set_up_class(cls):
        # The following order of routes creation is used to know policies and shapers numbers in UHP:
        # bridge, network_rx, network_tx,
        super().set_up_class()
        # nms_options = test_api.get_nms()
        # nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))
        cls.test_options = test_api.get_options(options_path)
        # Configuring L2 bridge
        cls.bridge_service = nms_api.create('network:0', 'service', cls.test_options.get('bridge_service'))
        cls.bridge_policy = nms_api.create('network:0', 'policy', cls.test_options.get('bridge_policy'))
        cls.bridge_polrule = nms_api.create(cls.bridge_policy, 'polrule', cls.test_options.get('bridge_polrule'))
        cls.bridge_shaper = nms_api.create('network:0', 'shaper', cls.test_options.get('bridge_shaper'))
        cls.bridge_qos = nms_api.create('network:0', 'qos', {
            'name': 'bridge',
            'priority': PriorityTypes.POLICY,
            'policy': cls.bridge_policy,
            'shaper': cls.bridge_shaper,
        })
        cls.mf_hub_bridge = nms_api.create('controller:0', 'route', {
            'type': RouteTypes.L2_BRIDGE,
            'service': cls.bridge_service,
            'forward_qos': cls.bridge_qos
        })
        cls.stn_bridge = nms_api.create('station:0', 'route', {
            'type': RouteTypes.L2_BRIDGE,
            'service': cls.bridge_service,
            'return_qos': cls.bridge_qos
        })
        # Configuring Network RX
        cls.network_rx_service = nms_api.create('network:0', 'service', cls.test_options.get('network_rx_service'))
        cls.network_rx_policy = nms_api.create('network:0', 'policy', cls.test_options.get('network_rx_policy'))
        cls.network_rx_polrule = nms_api.create(
            cls.network_rx_policy,
            'polrule',
            cls.test_options.get('network_rx_polrule')
        )
        cls.network_rx_shaper = nms_api.create('network:0', 'shaper', cls.test_options.get('network_rx_shaper'))
        cls.network_rx_qos = nms_api.create('network:0', 'qos', {
            'name': 'network_rx',
            'priority': PriorityTypes.POLICY,
            'policy': cls.network_rx_policy,
            'shaper': cls.network_rx_shaper,
        })
        cls.mf_hub_network_rx = nms_api.create('controller:0', 'route', {
            'type': RouteTypes.NETWORK_RX,
            'service': cls.network_rx_service,
            'forward_qos': cls.network_rx_qos,
        })
        cls.stn_network_rx = nms_api.create('station:0', 'route', {
            'type': RouteTypes.NETWORK_RX,
            'service': cls.network_rx_service,
            'return_qos': cls.network_rx_qos,
        })
        # Configuring Network TX
        cls.network_tx_service = nms_api.create('network:0', 'service', cls.test_options.get('network_tx_service'))
        cls.network_tx_policy = nms_api.create('network:0', 'policy', cls.test_options.get('network_tx_policy'))
        cls.network_tx_polrule = nms_api.create(cls.network_tx_policy, 'polrule', cls.test_options.get('network_tx_polrule'))
        cls.network_tx_shaper = nms_api.create('network:0', 'shaper', cls.test_options.get('network_tx_shaper'))
        cls.network_tx_qos = nms_api.create('network:0', 'qos', {
            'name': 'network_tx',
            'priority': PriorityTypes.POLICY,
            'policy': cls.network_tx_policy,
            'shaper': cls.network_tx_shaper,
        })
        cls.mf_hub_network_tx = nms_api.create('controller:0', 'route', {
            'type': RouteTypes.NETWORK_TX,
            'service': cls.network_tx_service,
            'forward_qos': cls.network_tx_qos,
            'ip': '172.30.0.0',
            'mask': '/16',
        })
        cls.stn_network_tx = nms_api.create('station:0', 'route', {
            'type': RouteTypes.NETWORK_TX,
            'service': cls.network_tx_service,
            'return_qos': cls.network_tx_qos,
            'ip': '172.40.0.0',
            'mask': '/16',
        })
        # Configuring Route to hub
        cls.rth_service = nms_api.create('network:0', 'service', cls.test_options.get('rth_service'))
        cls.rth_policy = nms_api.create('network:0', 'policy', cls.test_options.get('rth_policy'))
        cls.rth_polrule = nms_api.create(cls.rth_policy, 'polrule', cls.test_options.get('rth_polrule'))
        cls.rth_shaper = nms_api.create('network:0', 'shaper', cls.test_options.get('rth_shaper'))
        cls.rth_qos = nms_api.create('network:0', 'qos', {
            'name': 'rth',
            'priority': PriorityTypes.POLICY,
            'policy': cls.rth_policy,
            'shaper': cls.rth_shaper,
        })
        cls.stn_rth = nms_api.create('station:0', 'route', {
            'type': RouteTypes.ROUTE_TO_HUB,
            'service': cls.rth_service,
            'return_qos': cls.rth_qos,
            'ip': '172.50.0.0',
            'mask': '/16',
        })
        # Configuring Static_route
        cls.static_service = nms_api.create('network:0', 'service', cls.test_options.get('static_service'))
        cls.static_policy = nms_api.create('network:0', 'policy', cls.test_options.get('static_policy'))
        cls.static_polrule = nms_api.create(cls.static_policy, 'polrule', cls.test_options.get('static_polrule'))
        cls.static_shaper = nms_api.create('network:0', 'shaper', cls.test_options.get('static_shaper'))
        cls.static_qos = nms_api.create('network:0', 'qos', {
            'name': 'static',
            'priority': PriorityTypes.POLICY,
            'policy': cls.static_policy,
            'shaper': cls.static_shaper,
        })
        cls.mf_hub_static = nms_api.create('controller:0', 'route', {
            'type': RouteTypes.STATIC_ROUTE,
            'service': cls.static_service,
            'forward_qos': cls.static_qos,
            'return_qos': cls.static_qos,
            'ip': '172.60.0.0',
            'mask': '/16',
            'gateway': '192.168.1.1'
        })
        cls.stn_static = nms_api.create('station:0', 'route', {
            'type': RouteTypes.STATIC_ROUTE,
            'service': cls.static_service,
            'forward_qos': cls.static_qos,
            'return_qos': cls.static_qos,
            'ip': '172.70.0.0',
            'mask': '/16',
            'gateway': '192.168.2.1'
        })
        nms_api.wait_ticks(3)
        cls.mf_hub_routing_table = cls.mf_hub_uhp.get_ip_routing_static()
        cls.stn1_routing_table = cls.stn1_uhp.get_ip_routing_static()

    def test_l2_bridge(self):
        """One line string describing the test method"""
        hub_bridge_records = self.mf_hub_routing_table.get('l2_bridge')
        stn_bridge_records = self.stn1_routing_table.get('l2_bridge')
        hub_network_rx_records = self.mf_hub_routing_table.get('network_rx')
        stn_network_rx_records = self.stn1_routing_table.get('network_rx')
        self.assertEqual(1, len(hub_bridge_records), msg=f'MF hub l2 bridge records {len(hub_bridge_records)}')
        self.assertEqual(1, len(stn_bridge_records), msg=f'Station l2 bridge records {len(stn_bridge_records)}')

        for record in hub_network_rx_records:
            if record.get('vlan') == self.test_options.get('bridge_service').get('hub_vlan') \
                    and record.get('svlan') == str(int(self.test_options.get('bridge_service').get('hub_vlan')) + 30000):
                break
        else:
            self.fail('MF hub Network RX (SVLAN RX) is not found for bridge')

        for record in stn_network_rx_records:
            if record.get('vlan') == self.test_options.get('bridge_service').get('stn_vlan') \
                    and record.get('svlan') == str(int(self.test_options.get('bridge_service').get('hub_vlan')) + 30000):
                break
        else:
            self.fail('Station Network RX (SVLAN RX) is not found for bridge')

        self.assertEqual(
            self.test_options.get('bridge_service').get('hub_vlan'),
            hub_bridge_records[0].get('vlan'),
            msg=f'MF hub bridge vlan is not {self.test_options.get("bridge_service").get("hub_vlan")}'
        )
        self.assertEqual(
            'Pol-1',
            hub_bridge_records[0].get('prio/pol'),
            msg=f'MF hub bridge prio/pol is not Pol-1'
        )
        self.assertEqual(
            '1',
            hub_bridge_records[0].get('shaper'),
            msg=f'MF hub bridge shaper is not 1'
        )
        self.assertEqual(
            self.test_options.get('bridge_service').get('stn_vlan'),
            stn_bridge_records[0].get('vlan'),
            msg=f'Station bridge vlan is not {self.test_options.get("bridge_service").get("stn_vlan")}'
        )
        self.assertEqual(
            'Pol-1',
            stn_bridge_records[0].get('prio/pol'),
            msg=f'Station bridge prio/pol is not Pol-1'
        )
        self.assertEqual(
            '1',
            stn_bridge_records[0].get('shaper'),
            msg=f'Station bridge shaper is not 1'
        )

    def test_network_rx(self):
        """Network_RX routing records should create SVLAN RX in MF hub and station with proper parameters"""
        hub_vlan = self.test_options.get('network_rx_service').get('hub_vlan')
        stn_vlan = self.test_options.get('network_rx_service').get('stn_vlan')
        svlan = str(int(hub_vlan) + 25000)  # looks like svlan for network rx is created based on the given numbering
        title = self.test_options.get('network_rx_service').get('name')
        hub_net_rx = self.mf_hub_routing_table.get('network_rx')
        stn_net_rx = self.stn1_routing_table.get('network_rx')
        for rec in hub_net_rx:  # trying to find the expected SVLAN RX record in hub
            if rec.get('vlan') == hub_vlan and rec.get('svlan') == svlan and rec.get('title') == title:
                break
        else:
            self.fail(f'UHP MF hub cannot find SVLAN RX record with vlan={hub_vlan}, svlan={svlan}, title={title}')
        for rec in stn_net_rx:  # trying to find the expected SVLAN RX record in station
            if rec.get('vlan') == stn_vlan and rec.get('svlan') == svlan and rec.get('title') == title:
                break
        else:
            self.fail(f'UHP station cannot find SVLAN RX record with vlan={stn_vlan}, svlan={svlan}, title={title}')

    def test_network_tx(self):
        """Network_TX routing records should create TX Map in MF hub and station with proper parameters"""
        hub_vlan = self.test_options.get('network_tx_service').get('hub_vlan')
        stn_vlan = self.test_options.get('network_tx_service').get('stn_vlan')
        svlan = str(int(hub_vlan) + 25000)  # looks like svlan for network rx is created based on the given numbering
        hub_net_tx = self.mf_hub_routing_table.get('network_tx')
        stn_net_tx = self.stn1_routing_table.get('network_tx')
        for r in hub_net_tx:
            if r.get('vlan') == hub_vlan and r.get('svlan') == svlan and r.get('prio/pol') == 'Pol-2' \
                    and r.get('shaper') == '2' and r.get('ip') == '172.30.0.0' and r.get('mask') == '/16':
                break
        else:
            self.fail(f'UHP hub cannot locate TX Map with vlan={hub_vlan}, svlan={svlan}, '
                      f'prio/pol=Pol-2, shaper=2, ip=172.30.0.0/16')

        for r in stn_net_tx:
            if r.get('vlan') == stn_vlan and r.get('svlan') == svlan and r.get('prio/pol') == 'Pol-2' \
                    and r.get('shaper') == '2' and r.get('ip') == '172.40.0.0' and r.get('mask') == '/16':
                break
        else:
            self.fail(f'UHP station cannot locate TX Map with vlan={stn_vlan}, svlan={svlan}, '
                      f'prio/pol=Pol-2, shaper=2, ip=172.40.0.0/16')

    def test_route_to_hub(self):
        """Route_to_hub routing record should create TX Map in station and SVLAN RX in hub with proper parameters"""
        hub_vlan = self.test_options.get('rth_service').get('hub_vlan')
        stn_vlan = self.test_options.get('rth_service').get('stn_vlan')
        svlan = str(int(hub_vlan) + 10000)  # looks like svlan for route_to_hub is created based on the given numbering
        hub_rth = self.mf_hub_routing_table.get('network_rx')
        stn_rth = self.stn1_routing_table.get('network_tx')
        for r in hub_rth:
            if r.get('vlan') == hub_vlan and r.get('svlan') == svlan:
                break
        else:
            self.fail(f'UHP hub cannot locate SVLAN RX with vlan={hub_vlan}, svlan={svlan}')
        for r in stn_rth:
            if r.get('vlan') == stn_vlan and r.get('svlan') == svlan and r.get('prio/pol') == 'Pol-3' \
                    and r.get('shaper') == '3' and r.get('ip') == '172.50.0.0' and r.get('mask') == '/16':
                break
        else:
            self.fail(f'UHP station cannot locate TX Map with vlan={stn_vlan}, svlan={svlan}, '
                      f'prio/pol=Pol-3, shaper=3, ip=172.50.0.0/16')

    def test_static_route(self):
        """Static_route record in hub creates TX Map in hub, static_route in station creates TX Map; SVLAN RX in hub"""
        hub_vlan = self.test_options.get('static_service').get('hub_vlan')
        stn_vlan = self.test_options.get('static_service').get('stn_vlan')
        svlan = str(int(hub_vlan) + 10000)  # looks like svlan for route_to_hub is created based on the given numbering
        hub_static = self.mf_hub_routing_table.get('static_route')
        hub_tx = self.mf_hub_routing_table.get('network_tx')
        hub_rx = self.mf_hub_routing_table.get('network_rx')
        stn_static = self.stn1_routing_table.get('static_route')
        stn_tx = self.stn1_routing_table.get('network_tx')
        stn_rx = self.stn1_routing_table.get('network_rx')
        for r in hub_static:  # checking hub Static
            if r.get('vlan') == hub_vlan and r.get('ip') == '172.60.0.0' and r.get('mask') == '/16' \
                    and r.get('gateway') == '192.168.1.1':
                break
        else:
            self.fail(f'UHP hub cannot locate Static route with vlan={hub_vlan}, ip=172.60.0.0/16, gateway=192.168.1.1')
        for r in stn_static:  # checking station Static
            if r.get('vlan') == stn_vlan and r.get('ip') == '172.70.0.0' and r.get('mask') == '/16' \
                    and r.get('gateway') == '192.168.2.1':
                break
        else:
            self.fail(f'UHP stn cannot locate Static route with vlan={stn_vlan}, ip=172.70.0.0/16, gateway=192.168.1.1')
        for r in hub_tx:  # checking hub TX Map to station
            if r.get('vlan') == hub_vlan and r.get('ip') == '172.70.0.0' and r.get('mask') == '/16' \
                    and r.get('svlan') == svlan and r.get('destination') == 'Station - 2' \
                    and r.get('prio/pol') == 'Pol-3' and r.get('shaper') == '3':
                break
        else:
            self.fail(f'UHP hub cannot locate TX Map to stn with vlan={hub_vlan}, svlan={svlan}, ip=172.70.0.0/16')
        for r in stn_tx:  # checking stn TX Map to hub
            if r.get('vlan') == stn_vlan and r.get('ip') == '172.60.0.0' and r.get('mask') == '/16' \
                    and r.get('svlan') == svlan and r.get('prio/pol') == 'Pol-4' and r.get('shaper') == '4':
                break
        else:
            self.fail(f'UHP stn cannot locate TX Map to hub with vlan={hub_vlan}, svlan={svlan}, ip=172.60.0.0/16')
        for r in hub_rx:
            if r.get('vlan') == hub_vlan and r.get('svlan') == svlan:
                break
        else:
            self.fail(f'UHP hub cannot locate SVLAN RX with vlan={hub_vlan}, svlan={svlan}')
        for r in stn_rx:
            if r.get('vlan') == stn_vlan and r.get('svlan') == svlan:
                break
        else:
            self.fail(f'UHP stn cannot locate SVLAN RX with vlan={stn_vlan}, svlan={svlan}')
