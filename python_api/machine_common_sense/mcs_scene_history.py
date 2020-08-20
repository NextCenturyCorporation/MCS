from .mcs_step_output import MCS_Step_Output
from .mcs_util import MCS_Util


class MCS_Scene_History(object):
    def __init__(
        self,
        step=-1,
        action=None,
        args=None,
        params=None,
        output=None
    ):
        self.step = step
        self.action = action
        self.args = args
        self.params = params
        self.output = output

    def __str__(self):
        return MCS_Util.class_to_str(self)

