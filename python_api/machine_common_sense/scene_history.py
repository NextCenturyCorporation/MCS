import machine_common_sense as mcs


class Scene_History(object):
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
        return mcs.Util.class_to_str(self)

