from src.enum_types_constants import ControllerModes, StationModes

system = {

}

options = {
    'sum_of_all_queues': 16000,
    'controller_modes': [
        ControllerModes.MF_HUB,
        ControllerModes.OUTROUTE,
        ControllerModes.DAMA_HUB,
        ControllerModes.HUBLESS_MASTER,
        ControllerModes.GATEWAY,
    ],
    'station_modes': [
        StationModes.STAR,
        StationModes.MESH,
        StationModes.DAMA,
        StationModes.HUBLESS,
        StationModes.RX_ONLY,
    ],
}
