from .util import Util


class SceneHistory(object):
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
        return Util.class_to_str(self)
