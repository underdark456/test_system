from src.custom_test_case import CustomTestCase
from src import nms_api, test_api
from src.enum_types_constants import ControllerModes, ModelTypes, ModelTypesStr, ControllerModesStr
from src.exceptions import ObjectNotCreatedException

options_path = 'test_scenarios.form_validation.controller'
backup_name = 'default_config.txt'


class UhpModelControllerModeCase(CustomTestCase):
    """Controller mode depending on uhp_model test case"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.20'
    __execution_time__ = 6  # approximate case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        nms_options = test_api.get_nms()
        nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))
        nms_api.load_config(backup_name)

    def test_uhp_model_controller_mode(self):
        """UHP model - Controller mode combinations"""
        net = nms_api.create('nms:0', 'network', {'name': 'test_net'})
        tp = nms_api.create(net, 'teleport', {'name': 'test_tp'})
        mf_hub = nms_api.create(net, 'controller', {'name': 'mf_hub', 'mode': ControllerModes.MF_HUB, 'teleport': tp})
        dama_hub = nms_api.create(
            net,
            'controller',
            {'name': 'dama_hub', 'mode': ControllerModes.DAMA_HUB, 'teleport': tp}
        )
        uhp_models = [*ModelTypes()]
        uhp_models_names = [*ModelTypesStr()]
        modes = [*ControllerModes()]
        modes_names = [*ControllerModesStr()]
        next_name = 0
        next_inroute = 1
        for i in range(len(uhp_models)):
            if int(uhp_models[i]) == ModelTypes.UHP232:
                continue  # not supported model yet
            for j in range(len(modes)):
                if modes[j] == ControllerModes.NONE:
                    continue
                with self.subTest(f'Controller mode {modes_names[j]}, uhp_model {uhp_models_names[i]}'):
                    next_name += 1

                    # 100 and 100X can work only as DAMA inroutes
                    if int(uhp_models[i]) in (ModelTypes.UHP100, ModelTypes.UHP100X):
                        if int(modes[j]) == ControllerModes.DAMA_INROUTE:
                            try:
                                nms_api.create(net, 'controller', {
                                    'name': next_name,
                                    'uhp_model': uhp_models[i],
                                    'mode': modes[j],
                                    'teleport': tp,
                                    'tx_controller': dama_hub
                                })
                            except ObjectNotCreatedException:
                                self.fail(f'Controller is not created')
                        else:
                            if int(modes[j]) in (
                                    ControllerModes.MF_HUB,
                                    ControllerModes.OUTROUTE,
                                    ControllerModes.DAMA_HUB,
                                    ControllerModes.HUBLESS_MASTER,
                                    ControllerModes.MF_INROUTE,
                            ):
                                with self.assertRaises(ObjectNotCreatedException):
                                    nms_api.create(net, 'controller', {
                                        'name': next_name,
                                        'uhp_model': uhp_models[i],
                                        'mode': modes[j],
                                        'teleport': tp
                                    })
                            elif int(modes[j]) in (ControllerModes.INROUTE, ControllerModes.GATEWAY):
                                next_inroute += 1
                                with self.assertRaises(ObjectNotCreatedException):
                                    nms_api.create(net, 'controller', {
                                        'name': next_name,
                                        'uhp_model': uhp_models[i],
                                        'mode': modes[j],
                                        'teleport': tp,
                                        'tx_controller': mf_hub,
                                        'inroute': next_inroute
                                    })
                    else:
                        if int(modes[j]) in (
                                ControllerModes.MF_HUB,
                                ControllerModes.OUTROUTE,
                                ControllerModes.DAMA_HUB,
                                ControllerModes.HUBLESS_MASTER,
                                ControllerModes.MF_INROUTE,
                        ):
                            try:
                                nms_api.create(
                                    net,
                                    'controller',
                                    {'name': next_name, 'uhp_model': uhp_models[i], 'mode': modes[j], 'teleport': tp})
                            except ObjectNotCreatedException:
                                self.fail(
                                    f'Controller {modes_names[j]} is not created for uhp_model {uhp_models_names[i]}'
                                )
                        elif int(modes[j]) in (ControllerModes.INROUTE, ControllerModes.GATEWAY):
                            try:
                                next_inroute += 1
                                nms_api.create(net, 'controller', {
                                    'name': next_name,
                                    'uhp_model': uhp_models[i],
                                    'mode': modes[j],
                                    'teleport': tp,
                                    'tx_controller': mf_hub,
                                    'inroute': next_inroute
                                })
                            except ObjectNotCreatedException:
                                self.fail(
                                    f'Controller {modes_names[j]} is not created for uhp_model {uhp_models_names[i]}'
                                )
                        elif int(modes[j]) == ControllerModes.DAMA_INROUTE:
                            try:
                                nms_api.create(net, 'controller', {
                                    'name': next_name,
                                    'uhp_model': uhp_models[i],
                                    'mode': modes[j],
                                    'teleport': tp,
                                    'tx_controller': dama_hub,
                                })
                            except ObjectNotCreatedException:
                                self.fail(
                                    f'Controller {modes_names[j]} is not created for uhp_model {uhp_models_names[i]}'
                                )
