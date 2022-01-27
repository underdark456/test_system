from src.drivers.abstract_http_driver import API


class PathsManager:
    _OBJECT_CREATE = "form/new/{}={}/new_item={}"
    _OBJECT_EDIT = "form/edit/{}={}"
    _OBJECTS_LIST = "list/edit/{}={}/list_items={}"
    _OBJECT_STATUS = "object/dashboard/{}={}"
    _OBJECT_DASHBOARD = "object/dashboard/{}={}"  # alias for _OBJECT_STATUS
    _OBJECT_LOG = "logs/get/{}={}"
    _REALTIME = 'realtime/get/{}={}'
    _OBJECT_MAP = 'map/get/{}={}'
    _OBJECT_GRAPH = 'graph/get/{}={}'
    _OBJECT_STATION = 'station/list/{}={}'
    _OBJECT_INVESTIGATOR = 'investigator/get/{}={}'

    _NMS = 'nms'
    _NETWORK = 'network'
    _CONTROLLER = 'controller'
    _SERVICE = 'service'
    _VNO = 'vno'
    _TELEPORT = 'teleport'
    _POLICY = 'policy'
    _RULE = 'polrule'
    _STATION = 'station'
    _PROFILE = 'profile_set'
    _SHAPER = 'shaper'
    _ALERT = 'alert'
    _USER = 'user'
    _GROUP = 'group'
    _ROUTE = 'route'
    _DASHBOARD = 'dashboard'
    _BAL_CONTROLLER = 'bal_controller'
    _SR_CONTROLLER = 'sr_controller'
    _SR_LICENSE = 'sr_license'
    _SR_TELEPORT = 'sr_teleport'
    _DEVICE = 'device'
    _SERVER = 'server'
    _ACCESS = 'access'
    _CAMERA = 'camera'
    _PORT_MAP = 'port_map'
    _SW_UPLOAD = 'sw_upload'
    _RIP = 'rip_router'
    _SCHEDULER = 'scheduler'
    _SCH_RANGE = 'sch_range'
    _SCH_SERVICE = 'sch_service'
    _SCH_TASK = 'sch_task'
    _QOS = 'qos'

    _API_OBJECT_CREATE = 'api/object/write/{}={}/new_item={}'
    _API_OBJECT_READ = 'api/object/get/{}={}'
    _API_OBJECT_UPDATE = 'api/object/write/{}={}'
    _API_OBJECT_DELETE = 'api/object/delete/{}={}'
    _API_OBJECT_LOG = 'api/log/get/{}={}'
    _API_REALTIME = 'api/realtime/get/{}={}'
    _API_LIST_ITEMS = 'api/list/get/{}={}/list_items={}'
    _API_LIST_SKIP = 'list_skip={}'
    _API_LIST_MAX = 'list_max={}'
    _API_LIST_VARS = 'list_vars={}'
    _API_OBJECT_MAP = 'api/map/list/{}={}'
    _API_OBJECT_DASHBOARD = 'api/object/dashboard/{}={}'
    _API_OBJECT_GRAPH = 'api/graph/get/{}={}'
    _API_STATION_LIST = 'api/station/list/{}={}'
    _API_FILE_GET = 'api/fs/content/nms=0/path={}'
    _API_FILE_DELETE = 'api/fs/delete/nms=0/path={}'
    _API_FILE_DOWNLOAD = 'api/fs/download/nms=0/path={}'
    _API_OBJECT_TREE = 'api/tree/get/{}={}'
    _API_SEARCH_TOOL = 'api/search/get/{}={}'

    # POLICY RULE SECTION
    @classmethod
    def policy_rule_create(cls, driver_type, policy_id):
        if API == driver_type:
            return cls._API_OBJECT_CREATE.format(cls._POLICY, policy_id, cls._RULE)
        else:
            return cls._OBJECT_CREATE.format(cls._POLICY, policy_id, cls._RULE)

    @classmethod
    def policy_rule_read(cls, driver_type, rule_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._RULE, rule_id)
        else:
            return cls._OBJECT_EDIT.format(cls._RULE, rule_id)

    @classmethod
    def policy_rule_update(cls, driver_type, rule_id):
        if API == driver_type:
            return cls._API_OBJECT_UPDATE.format(cls._RULE, rule_id)
        else:
            return cls._OBJECT_EDIT.format(cls._RULE, rule_id)

    @classmethod
    def policy_rule_delete(cls, driver_type, rule_id):
        if API == driver_type:
            return cls._API_OBJECT_DELETE.format(cls._RULE, rule_id)
        else:
            return cls._OBJECT_EDIT.format(cls._RULE, rule_id)

    @classmethod
    def policy_rule_list(cls, driver_type, policy_id, skip=None, max_=None, vars_=None):
        if API == driver_type:
            command = cls._API_LIST_ITEMS.format(cls._POLICY, policy_id, cls._RULE)
            if skip is not None:
                command += f'/{cls._API_LIST_SKIP.format(skip)}'
            if max_ is not None:
                command += f'/{cls._API_LIST_MAX.format(max_)}'
            if vars_ is not None:
                command += f'/{cls._API_LIST_VARS.format(",".join(vars_))}'
            return command
        else:
            return cls._OBJECTS_LIST.format(cls._POLICY, policy_id, cls._RULE)

    # POLICY SECTION
    @classmethod
    def policy_create(cls, driver_type, network_id):
        if API == driver_type:
            return cls._API_OBJECT_CREATE.format(cls._NETWORK, network_id, cls._POLICY)
        else:
            return cls._OBJECT_CREATE.format(cls._NETWORK, network_id, cls._POLICY)

    @classmethod
    def policy_read(cls, driver_type, policy_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._POLICY, policy_id)
        else:
            return cls._OBJECT_EDIT.format(cls._POLICY, policy_id)

    @classmethod
    def policy_update(cls, driver_type, policy_id):
        if API == driver_type:
            return cls._API_OBJECT_UPDATE.format(cls._POLICY, policy_id)
        else:
            return cls._OBJECT_EDIT.format(cls._POLICY, policy_id)

    @classmethod
    def policy_delete(cls, driver_type, policy_id):
        if API == driver_type:
            return cls._API_OBJECT_DELETE.format(cls._POLICY, policy_id)
        else:
            return cls._OBJECT_EDIT.format(cls._POLICY, policy_id)

    @classmethod
    def policy_list(cls, driver_type, network_id, skip=None, max_=None, vars_=None):
        if API == driver_type:
            command = cls._API_LIST_ITEMS.format(cls._NETWORK, network_id, cls._POLICY)
            if skip is not None:
                command += f'/{cls._API_LIST_SKIP.format(skip)}'
            if max_ is not None:
                command += f'/{cls._API_LIST_MAX.format(max_)}'
            if vars_ is not None:
                command += f'/{cls._API_LIST_VARS.format(",".join(vars_))}'
            return command
        else:
            return cls._OBJECTS_LIST.format(cls._NETWORK, network_id, cls._POLICY)

    # SERVICE SECTION
    @classmethod
    def service_create(cls, driver_type, network_id):
        if API == driver_type:
            return cls._API_OBJECT_CREATE.format(cls._NETWORK, network_id, cls._SERVICE)
        else:
            return cls._OBJECT_CREATE.format(cls._NETWORK, network_id, cls._SERVICE)

    @classmethod
    def service_read(cls, driver_type, service_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._SERVICE, service_id)
        else:
            return cls._OBJECT_EDIT.format(cls._SERVICE, service_id)

    @classmethod
    def service_update(cls, driver_type, service_id):
        if API == driver_type:
            return cls._API_OBJECT_UPDATE.format(cls._SERVICE, service_id)
        else:
            return cls._OBJECT_EDIT.format(cls._SERVICE, service_id)

    @classmethod
    def service_delete(cls, driver_type, service_id):
        if API == driver_type:
            return cls._API_OBJECT_DELETE.format(cls._SERVICE, service_id)
        else:
            return cls._OBJECT_EDIT.format(cls._SERVICE, service_id)

    @classmethod
    def service_list(cls, driver_type, network_id, skip=None, max_=None, vars_=None):
        if API == driver_type:
            command = cls._API_LIST_ITEMS.format(cls._NETWORK, network_id, cls._SERVICE)
            if skip is not None:
                command += f'/{cls._API_LIST_SKIP.format(skip)}'
            if max_ is not None:
                command += f'/{cls._API_LIST_MAX.format(max_)}'
            if vars_ is not None:
                command += f'/{cls._API_LIST_VARS.format(",".join(vars_))}'
            return command
        else:
            return cls._OBJECTS_LIST.format(cls._NETWORK, network_id, cls._SERVICE)

    # CONTROLLER ROUTE SECTIONS
    @classmethod
    def controller_route_create(cls, driver_type, controller_id):
        if API == driver_type:
            return cls._API_OBJECT_CREATE.format(cls._CONTROLLER, controller_id, cls._ROUTE)
        else:
            return cls._OBJECT_CREATE.format(cls._CONTROLLER, controller_id, cls._ROUTE)

    @classmethod
    def controller_route_read(cls, driver_type, route_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._ROUTE, route_id)
        else:
            return cls._OBJECT_EDIT.format(cls._ROUTE, route_id)

    @classmethod
    def controller_route_update(cls, driver_type, route_id):
        if API == driver_type:
            return cls._API_OBJECT_UPDATE.format(cls._ROUTE, route_id)
        else:
            return cls._OBJECT_EDIT.format(cls._ROUTE, route_id)

    @classmethod
    def controller_route_delete(cls, driver_type, route_id):
        if API == driver_type:
            return cls._API_OBJECT_DELETE.format(cls._ROUTE, route_id)
        else:
            return cls._OBJECT_EDIT.format(cls._ROUTE, route_id)

    @classmethod
    def controller_route_list(cls, driver_type, controller_id, skip=None, max_=None, vars_=None):
        if API == driver_type:
            command = cls._API_LIST_ITEMS.format(cls._CONTROLLER, controller_id, cls._ROUTE)
            if skip is not None:
                command += f'/{cls._API_LIST_SKIP.format(skip)}'
            if max_ is not None:
                command += f'/{cls._API_LIST_MAX.format(max_)}'
            if vars_ is not None:
                command += f'/{cls._API_LIST_VARS.format(",".join(vars_))}'
            return command
        else:
            return cls._OBJECTS_LIST.format(cls._CONTROLLER, controller_id, cls._ROUTE)

    # STATION ROUTE SECTIONS
    @classmethod
    def station_route_create(cls, driver_type, station_id):
        if API == driver_type:
            return cls._API_OBJECT_CREATE.format(cls._STATION, station_id, cls._ROUTE)
        else:
            return cls._OBJECT_CREATE.format(cls._STATION, station_id, cls._ROUTE)

    @classmethod
    def station_route_read(cls, driver_type, route_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._ROUTE, route_id)
        else:
            return cls._OBJECT_EDIT.format(cls._ROUTE, route_id)

    @classmethod
    def station_route_update(cls, driver_type, route_id):
        if API == driver_type:
            return cls._API_OBJECT_UPDATE.format(cls._ROUTE, route_id)
        else:
            return cls._OBJECT_EDIT.format(cls._ROUTE, route_id)

    @classmethod
    def station_route_delete(cls, driver_type, route_id):
        if API == driver_type:
            return cls._API_OBJECT_DELETE.format(cls._ROUTE, route_id)
        else:
            return cls._OBJECT_EDIT.format(cls._ROUTE, route_id)

    @classmethod
    def station_route_list(cls, driver_type, station_id, skip=None, max_=None, vars_=None):
        if API == driver_type:
            command = cls._API_LIST_ITEMS.format(cls._STATION, station_id, cls._ROUTE)
            if skip is not None:
                command += f'/{cls._API_LIST_SKIP.format(skip)}'
            if max_ is not None:
                command += f'/{cls._API_LIST_MAX.format(max_)}'
            if vars_ is not None:
                command += f'/{cls._API_LIST_VARS.format(",".join(vars_))}'
            return command
        else:
            return cls._OBJECTS_LIST.format(cls._STATION, station_id, cls._ROUTE)

    # GROUP SECTIONS
    @classmethod
    def group_create(cls, driver_type, parent_id, parent_type=None):
        if parent_type is None:
            parent_type = cls._NMS
        if API == driver_type:
            return cls._API_OBJECT_CREATE.format(parent_type, parent_id, cls._GROUP)
        else:
            return cls._OBJECT_CREATE.format(parent_type, parent_id, cls._GROUP)

    @classmethod
    def group_read(cls, driver_type, parent_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._GROUP, parent_id)
        else:
            return cls._OBJECT_EDIT.format(cls._GROUP, parent_id)

    @classmethod
    def group_update(cls, driver_type, parent_id):
        if API == driver_type:
            return cls._API_OBJECT_UPDATE.format(cls._GROUP, parent_id)
        else:
            return cls._OBJECT_EDIT.format(cls._GROUP, parent_id)

    @classmethod
    def group_delete(cls, driver_type, parent_id):
        if API == driver_type:
            return cls._API_OBJECT_DELETE.format(cls._GROUP, parent_id)
        else:
            return cls._OBJECT_EDIT.format(cls._GROUP, parent_id)

    @classmethod
    def group_list(cls, driver_type, parent_id, parent_type=None, skip=None, max_=None, vars_=None):
        if parent_type is None:
            parent_type = cls._NMS
        if API == driver_type:
            command = cls._API_LIST_ITEMS.format(parent_type, parent_id, cls._GROUP)
            if skip is not None:
                command += f'/{cls._API_LIST_SKIP.format(skip)}'
            if max_ is not None:
                command += f'/{cls._API_LIST_MAX.format(max_)}'
            if vars_ is not None:
                command += f'/{cls._API_LIST_VARS.format(",".join(vars_))}'
            return command
        else:
            return cls._OBJECTS_LIST.format(parent_type, parent_id, cls._GROUP)

    # USER SECTIONS
    @classmethod
    def user_create(cls, driver_type, group_id):
        if API == driver_type:
            return cls._API_OBJECT_CREATE.format(cls._GROUP, group_id, cls._USER)
        else:
            return cls._OBJECT_CREATE.format(cls._GROUP, group_id, cls._USER)

    @classmethod
    def user_read(cls, driver_type, user_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._USER, user_id)
        else:
            return cls._OBJECT_EDIT.format(cls._USER, user_id)

    @classmethod
    def user_update(cls, driver_type, user_id):
        if API == driver_type:
            return cls._API_OBJECT_UPDATE.format(cls._USER, user_id)
        else:
            return cls._OBJECT_EDIT.format(cls._USER, user_id)

    @classmethod
    def user_delete(cls, driver_type, user_id):
        if API == driver_type:
            return cls._API_OBJECT_DELETE.format(cls._USER, user_id)
        else:
            return cls._OBJECT_EDIT.format(cls._USER, user_id)

    @classmethod
    def user_list(cls, driver_type, user_group_id, skip=None, max_=None, vars_=None):
        if API == driver_type:
            command = cls._API_LIST_ITEMS.format(cls._GROUP, user_group_id, cls._USER)
            if skip is not None:
                command += f'/{cls._API_LIST_SKIP.format(skip)}'
            if max_ is not None:
                command += f'/{cls._API_LIST_MAX.format(max_)}'
            if vars_ is not None:
                command += f'/{cls._API_LIST_VARS.format(",".join(vars_))}'
            return command
        else:
            return cls._OBJECTS_LIST.format(cls._GROUP, user_group_id, cls._USER)

    # CONTROLLERS SECTIONS
    @classmethod
    def controller_create(cls, driver_type, network_id):
        if API == driver_type:
            return cls._API_OBJECT_CREATE.format(cls._NETWORK, network_id, cls._CONTROLLER)
        else:
            return cls._OBJECT_CREATE.format(cls._NETWORK, network_id, cls._CONTROLLER)

    @classmethod
    def controller_read(cls, driver_type, controller_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._CONTROLLER, controller_id)
        else:
            return cls._OBJECT_EDIT.format(cls._CONTROLLER, controller_id)

    @classmethod
    def controller_update(cls, driver_type, controller_id):
        if API == driver_type:
            return cls._API_OBJECT_UPDATE.format(cls._CONTROLLER, controller_id)
        else:
            return cls._OBJECT_EDIT.format(cls._CONTROLLER, controller_id)

    @classmethod
    def controller_delete(cls, driver_type, controller_id):
        if API == driver_type:
            return cls._API_OBJECT_DELETE.format(cls._CONTROLLER, controller_id)
        else:
            return cls._OBJECT_EDIT.format(cls._CONTROLLER, controller_id)

    @classmethod
    def controller_status(cls, driver_type, controller_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._CONTROLLER, controller_id)
        else:
            return cls._OBJECT_STATUS.format(cls._CONTROLLER, controller_id)

    @classmethod
    def controller_log(cls, driver_type, controller_id):
        if API == driver_type:
            return cls._API_OBJECT_LOG.format(cls._CONTROLLER, controller_id)
        else:
            return cls._OBJECT_LOG.format(cls._CONTROLLER, controller_id)

    @classmethod
    def controller_graph(cls, driver_type, controller_id):
        if API == driver_type:
            return cls._API_OBJECT_GRAPH.format(cls._CONTROLLER, controller_id)
        else:
            return cls._OBJECT_GRAPH.format(cls._CONTROLLER, controller_id)

    @classmethod
    def controller_list(cls, driver_type, network_id, skip=None, max_=None, vars_=None):
        if API == driver_type:
            command = cls._API_LIST_ITEMS.format(cls._NETWORK, network_id, cls._CONTROLLER)
            if skip is not None:
                command += f'/{cls._API_LIST_SKIP.format(skip)}'
            if max_ is not None:
                command += f'/{cls._API_LIST_MAX.format(max_)}'
            if vars_ is not None:
                command += f'/{cls._API_LIST_VARS.format(",".join(vars_))}'
            return command
        else:
            return cls._OBJECTS_LIST.format(cls._NETWORK, network_id, cls._CONTROLLER)

    @classmethod
    def controller_map(cls, driver_type, controller_id):
        if API == driver_type:
            return cls._API_OBJECT_MAP.format(cls._CONTROLLER, controller_id)
        else:
            return cls._OBJECT_MAP.format(cls._CONTROLLER, controller_id)

    # NETWORKS SECTIONS
    @classmethod
    def network_create(cls, driver_type, nms_id):
        if API == driver_type:
            return cls._API_OBJECT_CREATE.format(cls._NMS, nms_id, cls._NETWORK)
        else:
            return cls._OBJECT_CREATE.format(cls._NMS, nms_id, cls._NETWORK)

    @classmethod
    def network_read(cls, driver_type, network_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._NETWORK, network_id)
        else:
            return cls._OBJECT_EDIT.format(cls._NETWORK, network_id)

    @classmethod
    def network_update(cls, driver_type, network_id):
        if API == driver_type:
            return cls._API_OBJECT_UPDATE.format(cls._NETWORK, network_id)
        else:
            return cls._OBJECT_EDIT.format(cls._NETWORK, network_id)

    @classmethod
    def network_delete(cls, driver_type, network_id):
        if API == driver_type:
            return cls._API_OBJECT_DELETE.format(cls._NETWORK, network_id)
        else:
            return cls._OBJECT_EDIT.format(cls._NETWORK, network_id)

    @classmethod
    def network_status(cls, driver_type, network_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._NETWORK, network_id)
        else:
            return cls._OBJECT_STATUS.format(cls._NETWORK, network_id)

    @classmethod
    def network_log(cls, driver_type, network_id):
        if API == driver_type:
            return cls._API_OBJECT_LOG.format(cls._NETWORK, network_id)
        else:
            return cls._OBJECT_LOG.format(cls._NETWORK, network_id)

    @classmethod
    def network_list(cls, driver_type, nms_id, skip=None, max_=None, vars_=None):
        if API == driver_type:
            command = cls._API_LIST_ITEMS.format(cls._NMS, nms_id, cls._NETWORK)
            if skip is not None:
                command += f'/{cls._API_LIST_SKIP.format(skip)}'
            if max_ is not None:
                command += f'/{cls._API_LIST_MAX.format(max_)}'
            if vars_ is not None:
                command += f'/{cls._API_LIST_VARS.format(",".join(vars_))}'
            return command
        else:
            return cls._OBJECTS_LIST.format(cls._NMS, nms_id, cls._NETWORK)

    @classmethod
    def network_map(cls, driver_type, network_id):
        if API == driver_type:
            return cls._API_OBJECT_MAP.format(cls._NETWORK, network_id)
        else:
            return cls._OBJECT_MAP.format(cls._NETWORK, network_id)

    @classmethod
    def network_graph(cls, driver_type, network_id):
        if API == driver_type:
            return cls._API_OBJECT_GRAPH.format(cls._NETWORK, network_id)
        else:
            return cls._OBJECT_GRAPH.format(cls._NETWORK, network_id)

    # STATION SECTION
    @classmethod
    def station_create(cls, driver_type, vno_id):
        if API == driver_type:
            return cls._API_OBJECT_CREATE.format(cls._VNO, vno_id, cls._STATION)
        else:
            return cls._OBJECT_CREATE.format(cls._VNO, vno_id, cls._STATION)

    @classmethod
    def station_read(cls, driver_type, station_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._STATION, station_id)
        else:
            return cls._OBJECT_EDIT.format(cls._STATION, station_id)

    @classmethod
    def station_update(cls, driver_type, station_id):
        if API == driver_type:
            return cls._API_OBJECT_UPDATE.format(cls._STATION, station_id)
        else:
            return cls._OBJECT_EDIT.format(cls._STATION, station_id)

    @classmethod
    def station_delete(cls, driver_type, station_id):
        if API == driver_type:
            return cls._API_OBJECT_DELETE.format(cls._STATION, station_id)
        else:
            return cls._OBJECT_EDIT.format(cls._STATION, station_id)

    @classmethod
    def station_status(cls, driver_type, station_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._STATION, station_id)
        else:
            return cls._OBJECT_STATUS.format(cls._STATION, station_id)

    @classmethod
    def station_log(cls, driver_type, station_id):
        if API == driver_type:
            return cls._API_OBJECT_LOG.format(cls._STATION, station_id)
        else:
            return cls._OBJECT_LOG.format(cls._STATION, station_id)

    @classmethod
    def station_graph(cls, driver_type, station_id):
        if API == driver_type:
            return cls._API_OBJECT_GRAPH.format(cls._STATION, station_id)
        else:
            return cls._OBJECT_GRAPH.format(cls._STATION, station_id)

    @classmethod
    def station_list(cls, driver_type, vno_id, skip=None, max_=None, vars_=None):
        if API == driver_type:
            command = cls._API_LIST_ITEMS.format(cls._VNO, vno_id, cls._STATION)
            if skip is not None:
                command += f'/{cls._API_LIST_SKIP.format(skip)}'
            if max_ is not None:
                command += f'/{cls._API_LIST_MAX.format(max_)}'
            if vars_ is not None:
                command += f'/{cls._API_LIST_VARS.format(",".join(vars_))}'
            return command
        else:
            return cls._OBJECTS_LIST.format(cls._VNO, vno_id, cls._STATION)

    @classmethod
    def station_map(cls, driver_type, station_id):
        if API == driver_type:
            return cls._API_OBJECT_MAP.format(cls._STATION, station_id)
        else:
            return cls._OBJECT_MAP.format(cls._STATION, station_id)

    # VNO SECTION
    @classmethod
    def vno_create(cls, driver_type, parent_id, parent_type=None):
        if parent_type is None:
            parent_type = cls._NETWORK
        if API == driver_type:
            return cls._API_OBJECT_CREATE.format(parent_type, parent_id, cls._VNO)
        else:
            return cls._OBJECT_CREATE.format(parent_type, parent_id, cls._VNO)

    @classmethod
    def vno_read(cls, driver_type, vno_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._VNO, vno_id)
        else:
            return cls._OBJECT_EDIT.format(cls._VNO, vno_id)

    @classmethod
    def vno_update(cls, driver_type, vno_id):
        if API == driver_type:
            return cls._API_OBJECT_UPDATE.format(cls._VNO, vno_id)
        else:
            return cls._OBJECT_EDIT.format(cls._VNO, vno_id)

    @classmethod
    def vno_delete(cls, driver_type, vno_id):
        if API == driver_type:
            return cls._API_OBJECT_DELETE.format(cls._VNO, vno_id)
        else:
            return cls._OBJECT_EDIT.format(cls._VNO, vno_id)

    @classmethod
    def vno_log(cls, driver_type, vno_id):
        if API == driver_type:
            return cls._API_OBJECT_LOG.format(cls._VNO, vno_id)
        else:
            return cls._OBJECT_LOG.format(cls._VNO, vno_id)

    @classmethod
    def vno_graph(cls, driver_type, vno_id):
        if API == driver_type:
            return cls._API_OBJECT_GRAPH.format(cls._VNO, vno_id)
        else:
            return cls._OBJECT_GRAPH.format(cls._VNO, vno_id)

    @classmethod
    def vno_status(cls, driver_type, vno_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._VNO, vno_id)
        else:
            return cls._OBJECT_STATUS.format(cls._VNO, vno_id)

    @classmethod
    def vno_list(cls, driver_type, parent_id, parent_type=None, skip=None, max_=None, vars_=None):
        if parent_type is None:
            parent_type = cls._NETWORK
        if API == driver_type:
            command = cls._API_LIST_ITEMS.format(parent_type, parent_id, cls._VNO)
            if skip is not None:
                command += f'/{cls._API_LIST_SKIP.format(skip)}'
            if max_ is not None:
                command += f'/{cls._API_LIST_MAX.format(max_)}'
            if vars_ is not None:
                command += f'/{cls._API_LIST_VARS.format(",".join(vars_))}'
            return command
        else:
            return cls._OBJECTS_LIST.format(parent_type, parent_id, cls._VNO)

    @classmethod
    def vno_map(cls, driver_type, vno_id):
        if API == driver_type:
            return cls._API_OBJECT_MAP.format(cls._VNO, vno_id)
        else:
            return cls._OBJECT_MAP.format(cls._VNO, vno_id)

    # Sub-VNO SECTION
    @classmethod
    def sub_vno_create(cls, driver_type, vno_id):
        if API == driver_type:
            return cls._API_OBJECT_CREATE.format(cls._VNO, vno_id, cls._VNO)
        else:
            return cls._OBJECT_CREATE.format(cls._VNO, vno_id, cls._VNO)

    @classmethod
    def sub_vno_read(cls, driver_type, vno_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._VNO, vno_id)
        else:
            return cls._OBJECT_EDIT.format(cls._VNO, vno_id)

    @classmethod
    def sub_vno_update(cls, driver_type, vno_id):
        if API == driver_type:
            return cls._API_OBJECT_UPDATE.format(cls._VNO, vno_id)
        else:
            return cls._OBJECT_EDIT.format(cls._VNO, vno_id)

    @classmethod
    def sub_vno_delete(cls, driver_type, vno_id):
        if API == driver_type:
            return cls._API_OBJECT_DELETE.format(cls._VNO, vno_id)
        else:
            return cls._OBJECT_EDIT.format(cls._VNO, vno_id)

    @classmethod
    def sub_vno_log(cls, driver_type, vno_id):
        if API == driver_type:
            return cls._API_OBJECT_LOG.format(cls._VNO, vno_id)
        else:
            return cls._OBJECT_LOG.format(cls._VNO, vno_id)

    @classmethod
    def sub_vno_status(cls, driver_type, vno_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._VNO, vno_id)
        else:
            return cls._OBJECT_STATUS.format(cls._VNO, vno_id)

    @classmethod
    def sub_vno_list(cls, driver_type, vno_id):
        if API == driver_type:
            return ""
        else:
            return cls._OBJECTS_LIST.format(cls._VNO, vno_id, cls._VNO)

    @classmethod
    def sub_vno_map(cls, driver_type, vno_id):
        if API == driver_type:
            return cls._API_OBJECT_MAP.format(cls._VNO, vno_id)
        else:
            return cls._OBJECT_MAP.format(cls._VNO, vno_id)

    # TELEPORT SECTION
    @classmethod
    def teleport_create(cls, driver_type, network_id):
        if API == driver_type:
            return cls._API_OBJECT_CREATE.format(cls._NETWORK, network_id, cls._TELEPORT)
        else:
            return cls._OBJECT_CREATE.format(cls._NETWORK, network_id, cls._TELEPORT)

    @classmethod
    def teleport_read(cls, driver_type, teleport_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._TELEPORT, teleport_id)
        else:
            return cls._OBJECT_EDIT.format(cls._TELEPORT, teleport_id)

    @classmethod
    def teleport_update(cls, driver_type, teleport_id):
        if API == driver_type:
            return cls._API_OBJECT_UPDATE.format(cls._TELEPORT, teleport_id)
        else:
            return cls._OBJECT_EDIT.format(cls._TELEPORT, teleport_id)

    @classmethod
    def teleport_delete(cls, driver_type, teleport_id):
        if API == driver_type:
            return cls._API_OBJECT_DELETE.format(cls._TELEPORT, teleport_id)
        else:
            return cls._OBJECT_EDIT.format(cls._TELEPORT, teleport_id)

    @classmethod
    def teleport_list(cls, driver_type, network_id, skip=None, max_=None, vars_=None):
        if API == driver_type:
            command = cls._API_LIST_ITEMS.format(cls._NETWORK, network_id, cls._TELEPORT)
            if skip is not None:
                command += f'/{cls._API_LIST_SKIP.format(skip)}'
            if max_ is not None:
                command += f'/{cls._API_LIST_MAX.format(max_)}'
            if vars_ is not None:
                command += f'/{cls._API_LIST_VARS.format(",".join(vars_))}'
            return command
        else:
            return cls._OBJECTS_LIST.format(cls._NETWORK, network_id, cls._TELEPORT)

    # PROFILE SECTION
    @classmethod
    def profile_create(cls, driver_type, network_id):
        if API == driver_type:
            return cls._API_OBJECT_CREATE.format(cls._NETWORK, network_id, cls._PROFILE)
        else:
            return cls._OBJECT_CREATE.format(cls._NETWORK, network_id, cls._PROFILE)

    @classmethod
    def profile_read(cls, driver_type, profile_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._PROFILE, profile_id)
        else:
            return cls._OBJECT_EDIT.format(cls._PROFILE, profile_id)

    @classmethod
    def profile_update(cls, driver_type, profile_id):
        if API == driver_type:
            return cls._API_OBJECT_UPDATE.format(cls._PROFILE, profile_id)
        else:
            return cls._OBJECT_EDIT.format(cls._PROFILE, profile_id)

    @classmethod
    def profile_delete(cls, driver_type, profile_id):
        if API == driver_type:
            return cls._API_OBJECT_DELETE.format(cls._PROFILE, profile_id)
        else:
            return cls._OBJECT_EDIT.format(cls._PROFILE, profile_id)

    @classmethod
    def profile_list(cls, driver_type, network_id, skip=None, max_=None, vars_=None):
        if API == driver_type:
            command = cls._API_LIST_ITEMS.format(cls._NETWORK, network_id, cls._PROFILE)
            if skip is not None:
                command += f'/{cls._API_LIST_SKIP.format(skip)}'
            if max_ is not None:
                command += f'/{cls._API_LIST_MAX.format(max_)}'
            if vars_ is not None:
                command += f'/{cls._API_LIST_VARS.format(",".join(vars_))}'
            return command
        else:
            return cls._OBJECTS_LIST.format(cls._NETWORK, network_id, cls._PROFILE)

    # SHAPER SECTION
    @classmethod
    def shaper_create(cls, driver_type, parent_id, parent_type):
        if parent_type is None:
            parent_type = cls._NETWORK
        if API == driver_type:
            return cls._API_OBJECT_CREATE.format(parent_type, parent_id, cls._SHAPER)
        else:
            return cls._OBJECT_CREATE.format(parent_type, parent_id, cls._SHAPER)

    @classmethod
    def shaper_read(cls, driver_type, shaper_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._SHAPER, shaper_id)
        else:
            return cls._OBJECT_EDIT.format(cls._SHAPER, shaper_id)

    @classmethod
    def shaper_update(cls, driver_type, shaper_id):
        if API == driver_type:
            return cls._API_OBJECT_UPDATE.format(cls._SHAPER, shaper_id)
        else:
            return cls._OBJECT_EDIT.format(cls._SHAPER, shaper_id)

    @classmethod
    def shaper_delete(cls, driver_type, shaper_id):
        if API == driver_type:
            return cls._API_OBJECT_DELETE.format(cls._SHAPER, shaper_id)
        else:
            return cls._OBJECT_EDIT.format(cls._SHAPER, shaper_id)

    @classmethod
    def shaper_list(cls, driver_type, network_id, skip=None, max_=None, vars_=None):
        if API == driver_type:
            command = cls._API_LIST_ITEMS.format(cls._NETWORK, network_id, cls._SHAPER)
            if skip is not None:
                command += f'/{cls._API_LIST_SKIP.format(skip)}'
            if max_ is not None:
                command += f'/{cls._API_LIST_MAX.format(max_)}'
            if vars_ is not None:
                command += f'/{cls._API_LIST_VARS.format(",".join(vars_))}'
            return command
        else:
            return cls._OBJECTS_LIST.format(cls._NETWORK, network_id, cls._SHAPER)

    # ALERT SECTION
    @classmethod
    def alert_create(cls, driver_type, nms_id):
        if API == driver_type:
            return cls._API_OBJECT_CREATE.format(cls._NMS, nms_id, cls._ALERT)
        else:
            return cls._OBJECT_CREATE.format(cls._NMS, nms_id, cls._ALERT)

    @classmethod
    def alert_read(cls, driver_type, alert_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._ALERT, alert_id)
        else:
            return cls._OBJECT_EDIT.format(cls._ALERT, alert_id)

    @classmethod
    def alert_update(cls, driver_type, alert_id):
        if API == driver_type:
            return cls._API_OBJECT_UPDATE.format(cls._ALERT, alert_id)
        else:
            return cls._OBJECT_EDIT.format(cls._ALERT, alert_id)

    @classmethod
    def alert_delete(cls, driver_type, alert_id):
        if API == driver_type:
            return cls._API_OBJECT_DELETE.format(cls._ALERT, alert_id)
        else:
            return cls._OBJECT_EDIT.format(cls._ALERT, alert_id)

    @classmethod
    def alert_list(cls, driver_type, nms_id, skip=None, max_=None, vars_=None):
        if API == driver_type:
            command = cls._API_LIST_ITEMS.format(cls._NMS, nms_id, cls._ALERT)
            if skip is not None:
                command += f'/{cls._API_LIST_SKIP.format(skip)}'
            if max_ is not None:
                command += f'/{cls._API_LIST_MAX.format(max_)}'
            if vars_ is not None:
                command += f'/{cls._API_LIST_VARS.format(",".join(vars_))}'
            return command
        else:
            return cls._OBJECTS_LIST.format(cls._NMS, nms_id, cls._ALERT)

    # NMS GLOBAL SETTINGS SECTION
    @classmethod
    def nms_update(cls, driver_type, nms_id):
        if API == driver_type:
            return cls._API_OBJECT_UPDATE.format(cls._NMS, nms_id)
        else:
            return cls._OBJECT_EDIT.format(cls._NMS, nms_id)

    @classmethod
    def nms_read(cls, driver_type, nms_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._NMS, nms_id)
        else:
            return cls._OBJECT_EDIT.format(cls._NMS, nms_id)

    @classmethod
    def nms_log(cls, driver_type, nms_id):
        if API == driver_type:
            return cls._API_OBJECT_LOG.format(cls._NMS, nms_id)
        else:
            return cls._OBJECT_LOG.format(cls._NMS, nms_id)

    @classmethod
    def nms_status(cls, driver_type, nms_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._NMS, nms_id)
        else:
            return cls._OBJECT_STATUS.format(cls._NMS, nms_id)

    @classmethod
    def realtime(cls, driver_type, entity: str, entity_id):
        """Returns a path corresponding to the Realtime monitor of a specific entity"""
        if API == driver_type:
            return cls._API_REALTIME.format(entity, entity_id)
        else:
            return cls._REALTIME.format(entity, entity_id)

    @classmethod
    def nms_investigator(cls, driver_type, nms_id):
        if API == driver_type:
            return None
        else:
            return cls._OBJECT_INVESTIGATOR.format(cls._NMS, nms_id)

    # DASHBOARD SECTION
    @classmethod
    def dashboard_create(cls, driver_type, nms_id, parent_type=None):
        if parent_type is None:
            parent_type = cls._NMS
        if API == driver_type:
            return cls._API_OBJECT_CREATE.format(parent_type, nms_id, cls._DASHBOARD)
        else:
            return cls._OBJECT_CREATE.format(parent_type, nms_id, cls._DASHBOARD)

    @classmethod
    def dashboard_read(cls, driver_type, dashboard_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._DASHBOARD, dashboard_id)
        else:
            return cls._OBJECT_EDIT.format(cls._DASHBOARD, dashboard_id)

    @classmethod
    def dashboard_update(cls, driver_type, dashboard_id):
        if API == driver_type:
            return cls._API_OBJECT_UPDATE.format(cls._DASHBOARD, dashboard_id)
        else:
            return cls._OBJECT_EDIT.format(cls._DASHBOARD, dashboard_id)

    @classmethod
    def dashboard_delete(cls, driver_type, dashboard_id):
        if API == driver_type:
            return cls._API_OBJECT_DELETE.format(cls._DASHBOARD, dashboard_id)
        else:
            return cls._OBJECT_EDIT.format(cls._DASHBOARD, dashboard_id)

    @classmethod
    def dashboard_list(cls, driver_type, parent_id, parent_type=None, skip=None, max_=None, vars_=None):
        if parent_type is None:
            parent_type = cls._NMS
        if API == driver_type:
            command = cls._API_LIST_ITEMS.format(parent_type, parent_id, cls._DASHBOARD)
            if skip is not None:
                command += f'/{cls._API_LIST_SKIP.format(skip)}'
            if max_ is not None:
                command += f'/{cls._API_LIST_MAX.format(max_)}'
            if vars_ is not None:
                command += f'/{cls._API_LIST_VARS.format(",".join(vars_))}'
            return command
        else:
            return cls._OBJECTS_LIST.format(parent_type, parent_id, cls._DASHBOARD)

    # BALANCE CONTROLLER SECTIONS
    @classmethod
    def bal_controller_create(cls, driver_type, network_id):
        if API == driver_type:
            return cls._API_OBJECT_CREATE.format(cls._NETWORK, network_id, cls._BAL_CONTROLLER)
        else:
            return cls._OBJECT_CREATE.format(cls._NETWORK, network_id, cls._BAL_CONTROLLER)

    @classmethod
    def bal_controller_read(cls, driver_type, bal_controller_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._BAL_CONTROLLER, bal_controller_id)
        else:
            return cls._OBJECT_EDIT.format(cls._BAL_CONTROLLER, bal_controller_id)

    @classmethod
    def bal_controller_update(cls, driver_type, bal_controller_id):
        if API == driver_type:
            return cls._API_OBJECT_UPDATE.format(cls._BAL_CONTROLLER, bal_controller_id)
        else:
            return cls._OBJECT_EDIT.format(cls._BAL_CONTROLLER, bal_controller_id)

    @classmethod
    def bal_controller_delete(cls, driver_type, bal_controller_id):
        if API == driver_type:
            return cls._API_OBJECT_DELETE.format(cls._BAL_CONTROLLER, bal_controller_id)
        else:
            return cls._OBJECT_EDIT.format(cls._BAL_CONTROLLER, bal_controller_id)

    @classmethod
    def bal_controller_status(cls, driver_type, bal_controller_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._BAL_CONTROLLER, bal_controller_id)
        else:
            return cls._OBJECT_STATUS.format(cls._BAL_CONTROLLER, bal_controller_id)

    @classmethod
    def bal_controller_log(cls, driver_type, bal_controller_id):
        if API == driver_type:
            return cls._API_OBJECT_LOG.format(cls._BAL_CONTROLLER, bal_controller_id)
        else:
            return cls._OBJECT_LOG.format(cls._BAL_CONTROLLER, bal_controller_id)

    @classmethod
    def bal_controller_list(cls, driver_type, network_id, skip=None, max_=None, vars_=None):
        if API == driver_type:
            command = cls._API_LIST_ITEMS.format(cls._NETWORK, network_id, cls._BAL_CONTROLLER)
            if skip is not None:
                command += f'/{cls._API_LIST_SKIP.format(skip)}'
            if max_ is not None:
                command += f'/{cls._API_LIST_MAX.format(max_)}'
            if vars_ is not None:
                command += f'/{cls._API_LIST_VARS.format(",".join(vars_))}'
            return command
        else:
            return cls._OBJECTS_LIST.format(cls._NETWORK, network_id, cls._BAL_CONTROLLER)

    # SMART REDUNDANCY CONTROLLER SECTIONS
    @classmethod
    def sr_controller_create(cls, driver_type, network_id):
        if API == driver_type:
            return cls._API_OBJECT_CREATE.format(cls._NETWORK, network_id, cls._SR_CONTROLLER)
        else:
            return cls._OBJECT_CREATE.format(cls._NETWORK, network_id, cls._SR_CONTROLLER)

    @classmethod
    def sr_controller_read(cls, driver_type, sr_controller_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._SR_CONTROLLER, sr_controller_id)
        else:
            return cls._OBJECT_EDIT.format(cls._SR_CONTROLLER, sr_controller_id)

    @classmethod
    def sr_controller_update(cls, driver_type, sr_controller_id):
        if API == driver_type:
            return cls._API_OBJECT_UPDATE.format(cls._SR_CONTROLLER, sr_controller_id)
        else:
            return cls._OBJECT_EDIT.format(cls._SR_CONTROLLER, sr_controller_id)

    @classmethod
    def sr_controller_delete(cls, driver_type, sr_controller_id):
        if API == driver_type:
            return cls._API_OBJECT_DELETE.format(cls._SR_CONTROLLER, sr_controller_id)
        else:
            return cls._OBJECT_EDIT.format(cls._SR_CONTROLLER, sr_controller_id)

    @classmethod
    def sr_controller_status(cls, driver_type, sr_controller_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._SR_CONTROLLER, sr_controller_id)
        else:
            return cls._OBJECT_STATUS.format(cls._SR_CONTROLLER, sr_controller_id)

    @classmethod
    def sr_controller_log(cls, driver_type, sr_controller_id):
        if API == driver_type:
            return cls._API_OBJECT_LOG.format(cls._SR_CONTROLLER, sr_controller_id)
        else:
            return cls._OBJECT_LOG.format(cls._SR_CONTROLLER, sr_controller_id)

    @classmethod
    def sr_controller_list(cls, driver_type, net_id, skip=None, max_=None, vars_=None):
        if API == driver_type:
            command = cls._API_LIST_ITEMS.format(cls._NETWORK, net_id, cls._SR_CONTROLLER)
            if skip is not None:
                command += f'/{cls._API_LIST_SKIP.format(skip)}'
            if max_ is not None:
                command += f'/{cls._API_LIST_MAX.format(max_)}'
            if vars_ is not None:
                command += f'/{cls._API_LIST_VARS.format(",".join(vars_))}'
            return command
        else:
            return cls._OBJECTS_LIST.format(cls._NETWORK, net_id, cls._SR_CONTROLLER)

    # SERVER SECTION
    @classmethod
    def server_create(cls, driver_type, nms_id):
        if API == driver_type:
            return cls._API_OBJECT_CREATE.format(cls._NMS, nms_id, cls._SERVER)
        else:
            return cls._OBJECT_CREATE.format(cls._NMS, nms_id, cls._SERVER)

    @classmethod
    def server_read(cls, driver_type, server_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._SERVER, server_id)
        else:
            return cls._OBJECT_EDIT.format(cls._SERVER, server_id)

    @classmethod
    def server_update(cls, driver_type, server_id):
        if API == driver_type:
            return cls._API_OBJECT_UPDATE.format(cls._SERVER, server_id)
        else:
            return cls._OBJECT_EDIT.format(cls._SERVER, server_id)

    @classmethod
    def server_delete(cls, driver_type, server_id):
        if API == driver_type:
            return cls._API_OBJECT_DELETE.format(cls._SERVER, server_id)
        else:
            return cls._OBJECT_EDIT.format(cls._SERVER, server_id)

    @classmethod
    def server_list(cls, driver_type, nms_id, skip=None, max_=None, vars_=None):
        if API == driver_type:
            command = cls._API_LIST_ITEMS.format(cls._NMS, nms_id, cls._SERVER)
            if skip is not None:
                command += f'/{cls._API_LIST_SKIP.format(skip)}'
            if max_ is not None:
                command += f'/{cls._API_LIST_MAX.format(max_)}'
            if vars_ is not None:
                command += f'/{cls._API_LIST_VARS.format(",".join(vars_))}'
            return command
        else:
            return cls._OBJECTS_LIST.format(cls._NMS, nms_id, cls._SERVER)

    # ACCESS SECTION
    @classmethod
    def access_create(cls, driver_type, parent_id, parent_type=None):
        if parent_type is None:
            parent_type = cls._NMS
        if API == driver_type:
            return cls._API_OBJECT_CREATE.format(parent_type, parent_id, cls._ACCESS)
        else:
            return cls._OBJECT_CREATE.format(parent_type, parent_id, cls._ACCESS)

    @classmethod
    def access_read(cls, driver_type, access_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._ACCESS, access_id)
        else:
            return cls._OBJECT_EDIT.format(cls._ACCESS, access_id)

    @classmethod
    def access_update(cls, driver_type, access_id):
        if API == driver_type:
            return cls._API_OBJECT_UPDATE.format(cls._ACCESS, access_id)
        else:
            return cls._OBJECT_EDIT.format(cls._ACCESS, access_id)

    @classmethod
    def access_delete(cls, driver_type, access_id):
        if API == driver_type:
            return cls._API_OBJECT_DELETE.format(cls._ACCESS, access_id)
        else:
            return cls._OBJECT_EDIT.format(cls._ACCESS, access_id)

    @classmethod
    def access_list(cls, driver_type, parent_id, parent_type=None, skip=None, max_=None, vars_=None):
        if parent_type is None:
            parent_type = cls._NMS
        if API == driver_type:
            command = cls._API_LIST_ITEMS.format(parent_type, parent_id, cls._ACCESS)
            if skip is not None:
                command += f'/{cls._API_LIST_SKIP.format(skip)}'
            if max_ is not None:
                command += f'/{cls._API_LIST_MAX.format(max_)}'
            if vars_ is not None:
                command += f'/{cls._API_LIST_VARS.format(",".join(vars_))}'
            return command
        else:
            return cls._OBJECTS_LIST.format(parent_type, parent_id, cls._ACCESS)

    # CAMERA SECTION
    @classmethod
    def camera_create(cls, driver_type, network_id):
        if API == driver_type:
            return cls._API_OBJECT_CREATE.format(cls._NETWORK, network_id, cls._CAMERA)
        else:
            return cls._OBJECT_CREATE.format(cls._NETWORK, network_id, cls._CAMERA)

    @classmethod
    def camera_read(cls, driver_type, camera_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._CAMERA, camera_id)
        else:
            return cls._OBJECT_EDIT.format(cls._CAMERA, camera_id)

    @classmethod
    def camera_update(cls, driver_type, camera_id):
        if API == driver_type:
            return cls._API_OBJECT_UPDATE.format(cls._CAMERA, camera_id)
        else:
            return cls._OBJECT_EDIT.format(cls._CAMERA, camera_id)

    @classmethod
    def camera_delete(cls, driver_type, camera_id):
        if API == driver_type:
            return cls._API_OBJECT_DELETE.format(cls._CAMERA, camera_id)
        else:
            return cls._OBJECT_EDIT.format(cls._CAMERA, camera_id)

    @classmethod
    def camera_list(cls, driver_type, network_id, skip=None, max_=None, vars_=None):
        if API == driver_type:
            command = cls._API_LIST_ITEMS.format(cls._NETWORK, network_id, cls._CAMERA)
            if skip is not None:
                command += f'/{cls._API_LIST_SKIP.format(skip)}'
            if max_ is not None:
                command += f'/{cls._API_LIST_MAX.format(max_)}'
            if vars_ is not None:
                command += f'/{cls._API_LIST_VARS.format(",".join(vars_))}'
            return command
        else:
            return cls._OBJECTS_LIST.format(cls._NETWORK, network_id, cls._CAMERA)

    # CONTROLLER PORT MAP SECTION
    @classmethod
    def controller_port_map_create(cls, driver_type, controller_id):
        if API == driver_type:
            return cls._API_OBJECT_CREATE.format(cls._CONTROLLER, controller_id, cls._PORT_MAP)
        else:
            return cls._OBJECT_CREATE.format(cls._CONTROLLER, controller_id, cls._PORT_MAP)

    @classmethod
    def controller_port_map_read(cls, driver_type, port_map_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._PORT_MAP, port_map_id)
        else:
            return cls._OBJECT_EDIT.format(cls._PORT_MAP, port_map_id)

    @classmethod
    def controller_port_map_update(cls, driver_type, port_map_id):
        if API == driver_type:
            return cls._API_OBJECT_UPDATE.format(cls._PORT_MAP, port_map_id)
        else:
            return cls._OBJECT_EDIT.format(cls._PORT_MAP, port_map_id)

    @classmethod
    def controller_port_map_delete(cls, driver_type, port_map_id):
        if API == driver_type:
            return cls._API_OBJECT_DELETE.format(cls._PORT_MAP, port_map_id)
        else:
            return cls._OBJECT_EDIT.format(cls._PORT_MAP, port_map_id)

    @classmethod
    def controller_port_map_list(cls, driver_type, controller_id, skip=None, max_=None, vars_=None):
        if API == driver_type:
            command = cls._API_LIST_ITEMS.format(cls._CONTROLLER, controller_id, cls._PORT_MAP)
            if skip is not None:
                command += f'/{cls._API_LIST_SKIP.format(skip)}'
            if max_ is not None:
                command += f'/{cls._API_LIST_MAX.format(max_)}'
            if vars_ is not None:
                command += f'/{cls._API_LIST_VARS.format(",".join(vars_))}'
            return command
        else:
            return cls._OBJECTS_LIST.format(cls._CONTROLLER, controller_id, cls._PORT_MAP)

    # STATION PORT MAP SECTION
    @classmethod
    def station_port_map_create(cls, driver_type, station_id):
        if API == driver_type:
            return cls._API_OBJECT_CREATE.format(cls._STATION, station_id, cls._PORT_MAP)
        else:
            return cls._OBJECT_CREATE.format(cls._STATION, station_id, cls._PORT_MAP)

    @classmethod
    def station_port_map_read(cls, driver_type, port_map_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._PORT_MAP, port_map_id)
        else:
            return cls._OBJECT_EDIT.format(cls._PORT_MAP, port_map_id)

    @classmethod
    def station_port_map_update(cls, driver_type, port_map_id):
        if API == driver_type:
            return cls._API_OBJECT_UPDATE.format(cls._PORT_MAP, port_map_id)
        else:
            return cls._OBJECT_EDIT.format(cls._PORT_MAP, port_map_id)

    @classmethod
    def station_port_map_delete(cls, driver_type, port_map_id):
        if API == driver_type:
            return cls._API_OBJECT_DELETE.format(cls._PORT_MAP, port_map_id)
        else:
            return cls._OBJECT_EDIT.format(cls._PORT_MAP, port_map_id)

    @classmethod
    def station_port_map_list(cls, driver_type, station_id, skip=None, max_=None, vars_=None):
        if API == driver_type:
            command = cls._API_LIST_ITEMS.format(cls._STATION, station_id, cls._PORT_MAP)
            if skip is not None:
                command += f'/{cls._API_LIST_SKIP.format(skip)}'
            if max_ is not None:
                command += f'/{cls._API_LIST_MAX.format(max_)}'
            if vars_ is not None:
                command += f'/{cls._API_LIST_VARS.format(",".join(vars_))}'
            return command
        else:
            return cls._OBJECTS_LIST.format(cls._STATION, station_id, cls._PORT_MAP)

    # SMART REDUNDANCY TELEPORT SECTION
    @classmethod
    def sr_teleport_create(cls, driver_type, sr_controller_id):
        if API == driver_type:
            return cls._API_OBJECT_CREATE.format(cls._SR_CONTROLLER, sr_controller_id, cls._SR_TELEPORT)
        else:
            return cls._OBJECT_CREATE.format(cls._SR_CONTROLLER, sr_controller_id, cls._SR_TELEPORT)

    @classmethod
    def sr_teleport_read(cls, driver_type, sr_tp_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._SR_TELEPORT, sr_tp_id)
        else:
            return cls._OBJECT_EDIT.format(cls._SR_TELEPORT, sr_tp_id)

    @classmethod
    def sr_teleport_update(cls, driver_type, sr_tp_id):
        if API == driver_type:
            return cls._API_OBJECT_UPDATE.format(cls._SR_TELEPORT, sr_tp_id)
        else:
            return cls._OBJECT_EDIT.format(cls._SR_TELEPORT, sr_tp_id)

    @classmethod
    def sr_teleport_delete(cls, driver_type, sr_tp_id):
        if API == driver_type:
            return cls._API_OBJECT_DELETE.format(cls._SR_TELEPORT, sr_tp_id)
        else:
            return cls._OBJECT_EDIT.format(cls._SR_TELEPORT, sr_tp_id)

    @classmethod
    def sr_teleport_log(cls, driver_type, sr_teleport_id):
        if API == driver_type:
            return cls._API_OBJECT_LOG.format(cls._SR_TELEPORT, sr_teleport_id)
        else:
            return cls._OBJECT_LOG.format(cls._SR_TELEPORT, sr_teleport_id)

    @classmethod
    def sr_teleport_status(cls, driver_type, sr_teleport_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._SR_TELEPORT, sr_teleport_id)
        else:
            return cls._OBJECT_STATUS.format(cls._SR_TELEPORT, sr_teleport_id)

    @classmethod
    def sr_teleport_list(cls, driver_type, sr_controller_id, skip=None, max_=None, vars_=None):
        if API == driver_type:
            command = cls._API_LIST_ITEMS.format(cls._SR_CONTROLLER, sr_controller_id, cls._SR_TELEPORT)
            if skip is not None:
                command += f'/{cls._API_LIST_SKIP.format(skip)}'
            if max_ is not None:
                command += f'/{cls._API_LIST_MAX.format(max_)}'
            if vars_ is not None:
                command += f'/{cls._API_LIST_VARS.format(",".join(vars_))}'
            return command
        else:
            return cls._OBJECTS_LIST.format(cls._SR_CONTROLLER, sr_controller_id, cls._SR_TELEPORT)

    # SMART REDUNDANCY LICENSE SECTION
    @classmethod
    def sr_license_create(cls, driver_type, network_id):
        if API == driver_type:
            return cls._API_OBJECT_CREATE.format(cls._NETWORK, network_id, cls._SR_LICENSE)
        else:
            return cls._OBJECT_CREATE.format(cls._NETWORK, network_id, cls._SR_LICENSE)

    @classmethod
    def sr_license_read(cls, driver_type, sr_license_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._SR_LICENSE, sr_license_id)
        else:
            return cls._OBJECT_EDIT.format(cls._SR_LICENSE, sr_license_id)

    @classmethod
    def sr_license_update(cls, driver_type, sr_license_id):
        if API == driver_type:
            return cls._API_OBJECT_UPDATE.format(cls._SR_LICENSE, sr_license_id)
        else:
            return cls._OBJECT_EDIT.format(cls._SR_LICENSE, sr_license_id)

    @classmethod
    def sr_license_delete(cls, driver_type, sr_license_id):
        if API == driver_type:
            return cls._API_OBJECT_DELETE.format(cls._SR_LICENSE, sr_license_id)
        else:
            return cls._OBJECT_EDIT.format(cls._SR_LICENSE, sr_license_id)

    @classmethod
    def sr_license_list(cls, driver_type, network_id, skip=None, max_=None, vars_=None):
        if API == driver_type:
            command = cls._API_LIST_ITEMS.format(cls._NETWORK, network_id, cls._SR_LICENSE)
            if skip is not None:
                command += f'/{cls._API_LIST_SKIP.format(skip)}'
            if max_ is not None:
                command += f'/{cls._API_LIST_MAX.format(max_)}'
            if vars_ is not None:
                command += f'/{cls._API_LIST_VARS.format(",".join(vars_))}'
            return command
        else:
            return cls._OBJECTS_LIST.format(cls._NETWORK, network_id, cls._SR_LICENSE)

    # SMART REDUNDANCY DEVICE SECTION
    @classmethod
    def device_create(cls, driver_type, sr_teleport_id):
        if API == driver_type:
            return cls._API_OBJECT_CREATE.format(cls._SR_TELEPORT, sr_teleport_id, cls._DEVICE)
        else:
            return cls._OBJECT_CREATE.format(cls._SR_TELEPORT, sr_teleport_id, cls._DEVICE)

    @classmethod
    def device_read(cls, driver_type, device_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._DEVICE, device_id)
        else:
            return cls._OBJECT_EDIT.format(cls._DEVICE, device_id)

    @classmethod
    def device_update(cls, driver_type, device_id):
        if API == driver_type:
            return cls._API_OBJECT_UPDATE.format(cls._DEVICE, device_id)
        else:
            return cls._OBJECT_EDIT.format(cls._DEVICE, device_id)

    @classmethod
    def device_delete(cls, driver_type, device_id):
        if API == driver_type:
            return cls._API_OBJECT_DELETE.format(cls._DEVICE, device_id)
        else:
            return cls._OBJECT_EDIT.format(cls._DEVICE, device_id)

    @classmethod
    def device_log(cls, driver_type, device_id):
        if API == driver_type:
            return cls._API_OBJECT_LOG.format(cls._DEVICE, device_id)
        else:
            return cls._OBJECT_LOG.format(cls._DEVICE, device_id)

    @classmethod
    def device_status(cls, driver_type, device_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._DEVICE, device_id)
        else:
            return cls._OBJECT_STATUS.format(cls._DEVICE, device_id)

    @classmethod
    def device_list(cls, driver_type, sr_teleport_id, skip=None, max_=None, vars_=None):
        if API == driver_type:
            command = cls._API_LIST_ITEMS.format(cls._SR_TELEPORT, sr_teleport_id, cls._DEVICE)
            if skip is not None:
                command += f'/{cls._API_LIST_SKIP.format(skip)}'
            if max_ is not None:
                command += f'/{cls._API_LIST_MAX.format(max_)}'
            if vars_ is not None:
                command += f'/{cls._API_LIST_VARS.format(",".join(vars_))}'
            return command
        else:
            return cls._OBJECTS_LIST.format(cls._SR_TELEPORT, sr_teleport_id, cls._DEVICE)

    # SW UPLOAD SECTION
    @classmethod
    def sw_upload_create(cls, driver_type, network_id):
        if API == driver_type:
            return cls._API_OBJECT_CREATE.format(cls._NETWORK, network_id, cls._SW_UPLOAD)
        else:
            return cls._OBJECT_CREATE.format(cls._NETWORK, network_id, cls._SW_UPLOAD)

    @classmethod
    def sw_upload_read(cls, driver_type, sw_upload_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._SW_UPLOAD, sw_upload_id)
        else:
            return cls._OBJECT_EDIT.format(cls._SW_UPLOAD, sw_upload_id)

    @classmethod
    def sw_upload_update(cls, driver_type, sw_upload_id):
        if API == driver_type:
            return cls._API_OBJECT_UPDATE.format(cls._SW_UPLOAD, sw_upload_id)
        else:
            return cls._OBJECT_EDIT.format(cls._SW_UPLOAD, sw_upload_id)

    @classmethod
    def sw_upload_delete(cls, driver_type, sw_upload_id):
        if API == driver_type:
            return cls._API_OBJECT_DELETE.format(cls._SW_UPLOAD, sw_upload_id)
        else:
            return cls._OBJECT_EDIT.format(cls._SW_UPLOAD, sw_upload_id)

    @classmethod
    def sw_upload_log(cls, driver_type, sw_upload_id):
        if API == driver_type:
            return cls._API_OBJECT_LOG.format(cls._SW_UPLOAD, sw_upload_id)
        else:
            return cls._OBJECT_LOG.format(cls._SW_UPLOAD, sw_upload_id)

    @classmethod
    def sw_upload_list(cls, driver_type, network_id, skip=None, max_=None, vars_=None):
        if API == driver_type:
            command = cls._API_LIST_ITEMS.format(cls._NETWORK, network_id, cls._SW_UPLOAD)
            if skip is not None:
                command += f'/{cls._API_LIST_SKIP.format(skip)}'
            if max_ is not None:
                command += f'/{cls._API_LIST_MAX.format(max_)}'
            if vars_ is not None:
                command += f'/{cls._API_LIST_VARS.format(",".join(vars_))}'
            return command
        else:
            return cls._OBJECTS_LIST.format(cls._NETWORK, network_id, cls._SW_UPLOAD)

    # Controller RIP SECTION
    @classmethod
    def controller_rip_create(cls, driver_type, controller_id):
        if API == driver_type:
            return cls._API_OBJECT_CREATE.format(cls._CONTROLLER, controller_id, cls._RIP)
        else:
            return cls._OBJECT_CREATE.format(cls._CONTROLLER, controller_id, cls._RIP)

    @classmethod
    def controller_rip_read(cls, driver_type, controller_rip_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._RIP, controller_rip_id)
        else:
            return cls._OBJECT_EDIT.format(cls._RIP, controller_rip_id)

    @classmethod
    def controller_rip_update(cls, driver_type, controller_rip_id):
        if API == driver_type:
            return cls._API_OBJECT_UPDATE.format(cls._RIP, controller_rip_id)
        else:
            return cls._OBJECT_EDIT.format(cls._RIP, controller_rip_id)

    @classmethod
    def controller_rip_delete(cls, driver_type, controller_rip_id):
        if API == driver_type:
            return cls._API_OBJECT_DELETE.format(cls._RIP, controller_rip_id)
        else:
            return cls._OBJECT_EDIT.format(cls._RIP, controller_rip_id)

    @classmethod
    def controller_rip_list(cls, driver_type, controller_id, skip=None, max_=None, vars_=None):
        if API == driver_type:
            command = cls._API_LIST_ITEMS.format(cls._CONTROLLER, controller_id, cls._RIP)
            if skip is not None:
                command += f'/{cls._API_LIST_SKIP.format(skip)}'
            if max_ is not None:
                command += f'/{cls._API_LIST_MAX.format(max_)}'
            if vars_ is not None:
                command += f'/{cls._API_LIST_VARS.format(",".join(vars_))}'
            return command
        else:
            return cls._OBJECTS_LIST.format(cls._CONTROLLER, controller_id, cls._RIP)

    # Station RIP SECTION
    @classmethod
    def station_rip_create(cls, driver_type, station_id):
        if API == driver_type:
            return cls._API_OBJECT_CREATE.format(cls._STATION, station_id, cls._RIP)
        else:
            return cls._OBJECT_CREATE.format(cls._STATION, station_id, cls._RIP)

    @classmethod
    def station_rip_read(cls, driver_type, station_rip_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._RIP, station_rip_id)
        else:
            return cls._OBJECT_EDIT.format(cls._RIP, station_rip_id)

    @classmethod
    def station_rip_update(cls, driver_type, station_rip_id):
        if API == driver_type:
            return cls._API_OBJECT_UPDATE.format(cls._RIP, station_rip_id)
        else:
            return cls._OBJECT_EDIT.format(cls._RIP, station_rip_id)

    @classmethod
    def station_rip_delete(cls, driver_type, station_rip_id):
        if API == driver_type:
            return cls._API_OBJECT_DELETE.format(cls._RIP, station_rip_id)
        else:
            return cls._OBJECT_EDIT.format(cls._RIP, station_rip_id)

    @classmethod
    def station_rip_list(cls, driver_type, station_id, skip=None, max_=None, vars_=None):
        if API == driver_type:
            command = cls._API_LIST_ITEMS.format(cls._STATION, station_id, cls._RIP)
            if skip is not None:
                command += f'/{cls._API_LIST_SKIP.format(skip)}'
            if max_ is not None:
                command += f'/{cls._API_LIST_MAX.format(max_)}'
            if vars_ is not None:
                command += f'/{cls._API_LIST_VARS.format(",".join(vars_))}'
            return command
        else:
            return cls._OBJECTS_LIST.format(cls._STATION, station_id, cls._RIP)

    # SCHEDULER SECTION
    @classmethod
    def scheduler_create(cls, driver_type, network_id):
        if API == driver_type:
            return cls._API_OBJECT_CREATE.format(cls._NETWORK, network_id, cls._SCHEDULER)
        else:
            return cls._OBJECT_CREATE.format(cls._NETWORK, network_id, cls._SCHEDULER)

    @classmethod
    def scheduler_read(cls, driver_type, scheduler_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._SCHEDULER, scheduler_id)
        else:
            return cls._OBJECT_EDIT.format(cls._SCHEDULER, scheduler_id)

    @classmethod
    def scheduler_update(cls, driver_type, scheduler_id):
        if API == driver_type:
            return cls._API_OBJECT_UPDATE.format(cls._SCHEDULER, scheduler_id)
        else:
            return cls._OBJECT_EDIT.format(cls._SCHEDULER, scheduler_id)

    @classmethod
    def scheduler_delete(cls, driver_type, scheduler_id):
        if API == driver_type:
            return cls._API_OBJECT_DELETE.format(cls._SCHEDULER, scheduler_id)
        else:
            return cls._OBJECT_EDIT.format(cls._SCHEDULER, scheduler_id)

    @classmethod
    def scheduler_list(cls, driver_type, network_id, skip=None, max_=None, vars_=None):
        if API == driver_type:
            command = cls._API_LIST_ITEMS.format(cls._NETWORK, network_id, cls._SCHEDULER)
            if skip is not None:
                command += f'/{cls._API_LIST_SKIP.format(skip)}'
            if max_ is not None:
                command += f'/{cls._API_LIST_MAX.format(max_)}'
            if vars_ is not None:
                command += f'/{cls._API_LIST_VARS.format(",".join(vars_))}'
            return command
        else:
            return cls._OBJECTS_LIST.format(cls._NETWORK, network_id, cls._SCHEDULER)

    # SCHEDULER RANGE SECTION
    @classmethod
    def sch_range_create(cls, driver_type, scheduler_id):
        if API == driver_type:
            return cls._API_OBJECT_CREATE.format(cls._SCHEDULER, scheduler_id, cls._SCH_RANGE)
        else:
            return cls._OBJECT_CREATE.format(cls._SCHEDULER, scheduler_id, cls._SCH_RANGE)

    @classmethod
    def sch_range_read(cls, driver_type, sch_range_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._SCH_RANGE, sch_range_id)
        else:
            return cls._OBJECT_EDIT.format(cls._SCH_RANGE, sch_range_id)

    @classmethod
    def sch_range_update(cls, driver_type, sch_range_id):
        if API == driver_type:
            return cls._API_OBJECT_UPDATE.format(cls._SCH_RANGE, sch_range_id)
        else:
            return cls._OBJECT_EDIT.format(cls._SCH_RANGE, sch_range_id)

    @classmethod
    def sch_range_delete(cls, driver_type, sch_range_id):
        if API == driver_type:
            return cls._API_OBJECT_DELETE.format(cls._SCH_RANGE, sch_range_id)
        else:
            return cls._OBJECT_EDIT.format(cls._SCH_RANGE, sch_range_id)

    @classmethod
    def sch_range_list(cls, driver_type, scheduler_id, skip=None, max_=None, vars_=None):
        if API == driver_type:
            command = cls._API_LIST_ITEMS.format(cls._SCHEDULER, scheduler_id, cls._SCH_RANGE)
            if skip is not None:
                command += f'/{cls._API_LIST_SKIP.format(skip)}'
            if max_ is not None:
                command += f'/{cls._API_LIST_MAX.format(max_)}'
            if vars_ is not None:
                command += f'/{cls._API_LIST_VARS.format(",".join(vars_))}'
            return command
        else:
            return cls._OBJECTS_LIST.format(cls._SCHEDULER, scheduler_id, cls._SCH_RANGE)

    # SCHEDULER SERVICE SECTION
    @classmethod
    def sch_service_create(cls, driver_type, scheduler_id):
        if API == driver_type:
            return cls._API_OBJECT_CREATE.format(cls._SCHEDULER, scheduler_id, cls._SCH_SERVICE)
        else:
            return cls._OBJECT_CREATE.format(cls._SCHEDULER, scheduler_id, cls._SCH_SERVICE)

    @classmethod
    def sch_service_read(cls, driver_type, sch_service_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._SCH_SERVICE, sch_service_id)
        else:
            return cls._OBJECT_EDIT.format(cls._SCH_SERVICE, sch_service_id)

    @classmethod
    def sch_service_update(cls, driver_type, sch_service_id):
        if API == driver_type:
            return cls._API_OBJECT_UPDATE.format(cls._SCH_SERVICE, sch_service_id)
        else:
            return cls._OBJECT_EDIT.format(cls._SCH_SERVICE, sch_service_id)

    @classmethod
    def sch_service_delete(cls, driver_type, sch_service_id):
        if API == driver_type:
            return cls._API_OBJECT_DELETE.format(cls._SCH_SERVICE, sch_service_id)
        else:
            return cls._OBJECT_EDIT.format(cls._SCH_SERVICE, sch_service_id)

    @classmethod
    def sch_service_list(cls, driver_type, scheduler_id, skip=None, max_=None, vars_=None):
        if API == driver_type:
            command = cls._API_LIST_ITEMS.format(cls._SCHEDULER, scheduler_id, cls._SCH_SERVICE)
            if skip is not None:
                command += f'/{cls._API_LIST_SKIP.format(skip)}'
            if max_ is not None:
                command += f'/{cls._API_LIST_MAX.format(max_)}'
            if vars_ is not None:
                command += f'/{cls._API_LIST_VARS.format(",".join(vars_))}'
            return command
        else:
            return cls._OBJECTS_LIST.format(cls._SCHEDULER, scheduler_id, cls._SCH_SERVICE)

    # SCHEDULER TASK SECTION
    @classmethod
    def sch_task_create(cls, driver_type, station_id):
        if API == driver_type:
            return cls._API_OBJECT_CREATE.format(cls._STATION, station_id, cls._SCH_TASK)
        else:
            return cls._OBJECT_CREATE.format(cls._STATION, station_id, cls._SCH_TASK)

    @classmethod
    def sch_task_read(cls, driver_type, sch_task_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._SCH_TASK, sch_task_id)
        else:
            return cls._OBJECT_EDIT.format(cls._SCH_TASK, sch_task_id)

    @classmethod
    def sch_task_update(cls, driver_type, sch_task_id):
        if API == driver_type:
            return cls._API_OBJECT_UPDATE.format(cls._SCH_TASK, sch_task_id)
        else:
            return cls._OBJECT_EDIT.format(cls._SCH_TASK, sch_task_id)

    @classmethod
    def sch_task_delete(cls, driver_type, sch_task_id):
        if API == driver_type:
            return cls._API_OBJECT_DELETE.format(cls._SCH_TASK, sch_task_id)
        else:
            return cls._OBJECT_EDIT.format(cls._SCH_TASK, sch_task_id)

    @classmethod
    def sch_task_list(cls, driver_type, station_id, skip=None, max_=None, vars_=None):
        if API == driver_type:
            command = cls._API_LIST_ITEMS.format(cls._STATION, station_id, cls._SCH_TASK)
            if skip is not None:
                command += f'/{cls._API_LIST_SKIP.format(skip)}'
            if max_ is not None:
                command += f'/{cls._API_LIST_MAX.format(max_)}'
            if vars_ is not None:
                command += f'/{cls._API_LIST_VARS.format(",".join(vars_))}'
            return command
        else:
            return cls._OBJECTS_LIST.format(cls._STATION, station_id, cls._SCH_TASK)

    # QoS SECTION
    @classmethod
    def qos_create(cls, driver_type, network_id):
        if API == driver_type:
            return cls._API_OBJECT_CREATE.format(cls._NETWORK, network_id, cls._QOS)
        else:
            return cls._OBJECT_CREATE.format(cls._NETWORK, network_id, cls._QOS)

    @classmethod
    def qos_read(cls, driver_type, qos_id):
        if API == driver_type:
            return cls._API_OBJECT_READ.format(cls._QOS, qos_id)
        else:
            return cls._OBJECT_EDIT.format(cls._QOS, qos_id)

    @classmethod
    def qos_update(cls, driver_type, qos_id):
        if API == driver_type:
            return cls._API_OBJECT_UPDATE.format(cls._QOS, qos_id)
        else:
            return cls._OBJECT_EDIT.format(cls._QOS, qos_id)

    @classmethod
    def qos_delete(cls, driver_type, qos_id):
        if API == driver_type:
            return cls._API_OBJECT_DELETE.format(cls._QOS, qos_id)
        else:
            return cls._OBJECT_EDIT.format(cls._QOS, qos_id)

    @classmethod
    def qos_list(cls, driver_type, network_id, skip=None, max_=None, vars_=None):
        if API == driver_type:
            command = cls._API_LIST_ITEMS.format(cls._NETWORK, network_id, cls._QOS)
            if skip is not None:
                command += f'/{cls._API_LIST_SKIP.format(skip)}'
            if max_ is not None:
                command += f'/{cls._API_LIST_MAX.format(max_)}'
            if vars_ is not None:
                command += f'/{cls._API_LIST_VARS.format(",".join(vars_))}'
            return command
        else:
            return cls._OBJECTS_LIST.format(cls._NETWORK, network_id, cls._QOS)
