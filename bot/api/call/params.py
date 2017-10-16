import json

from bot.api.domain import OutApiObject, ApiObjectList, ApiObject


class ApiCallParams:
    def __init__(self, params: dict):
        self.send_params = params
        self.local_params = self.__pop_local_params(self.send_params)
        self.__flat_params(self.send_params)

    @staticmethod
    def __pop_local_params(params):
        local_params = {}
        for local_param in OutApiObject.LOCAL_PARAMS:
            if local_param in params:
                local_params[local_param] = params.pop(local_param)
        return local_params

    @staticmethod
    def __flat_params(params):
        for param, value in params.copy().items():
            if isinstance(value, (ApiObjectList, ApiObject)):
                value = value.unwrap_api_object()
                # not saving now as we assume it will also enter the next if
            if type(value) in (list, dict, tuple):
                params[param] = json.dumps(value, separators=(',', ':'))

    @property
    def send(self):
        return self.send_params

    @property
    def scheduler(self):
        return self.local_params.get(OutApiObject.LOCAL_PARAM_SCHEDULER)

    @property
    def error_callback(self):
        return self.local_params.get(OutApiObject.LOCAL_PARAM_ERROR_CALLBACK)
