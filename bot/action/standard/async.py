from bot.action.core.action import IntermediateAction
from bot.api.api import Api


class AsyncApiAction(IntermediateAction):
    def setup(self, api: Api, *args):
        # setup is not meant to be overridden, proceed with caution
        super().setup(api.async, *args)
