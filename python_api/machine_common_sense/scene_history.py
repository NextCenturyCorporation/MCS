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
<<<<<<< HEAD:python_api/machine_common_sense/scene_history.py
        return mcs.Util.class_to_str(self)

=======
        return MCS_Util.class_to_str(self)
>>>>>>> 5f4454c6154f8f0b599e6d944915db6a28a980a1:python_api/machine_common_sense/mcs_scene_history.py
