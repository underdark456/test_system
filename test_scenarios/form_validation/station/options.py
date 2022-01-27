from src.enum_types_constants import ControllerModesStr

system = {

}

options = {
    'star_valid_ctrl_modes': (ControllerModesStr.MF_HUB, ControllerModesStr.INROUTE,),
    'mesh_valid_ctrl_modes': (ControllerModesStr.MF_HUB, ControllerModesStr.INROUTE,),
    'dama_valid_ctrl_modes': (ControllerModesStr.DAMA_HUB, ControllerModesStr.DAMA_INROUTE,),
    'hubless_valid_ctrl_modes': (ControllerModesStr.HUBLESS_MASTER,),
    'rx_only_valid_ctrl_modes': (
        ControllerModesStr.DAMA_HUB,
        ControllerModesStr.MF_HUB,
        ControllerModesStr.OUTROUTE,
    ),
}

