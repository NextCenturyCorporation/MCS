from machine_common_sense.mcs_util import MCS_Util

class MCS_Goal:
    """
    Defines attributes of an MCS goal.

    Attributes
    ----------
    action_list : list of lists of strings, or None
        The list of actions that are available for the scene at each step (outer list index).  Each inner list item is
        a list of action strings. For example, ['MoveAhead','RotateLook,rotation=180'] restricts the actions to either
        'MoveAhead' or 'RotateLook' with the 'rotation' parameter set to 180. An action_list of None means that all
        actions are always available. An empty inner list means that all actions are available for that specific step.
    info_list : list
        The list of information for the visualization interface associated with this goal.
    last_step : integer
        The last step of this scene. This scene will automatically end following this step.
    task_list : list of strings
        The list of tasks associated with this goal (secondary to its types).
    type_list : list of strings
        The list of types associated with this goal, including the relevant MCS core domains.
    metadata : dict
        The metadata specific to this goal.
    """

    def __init__(
        self,
        action_list=None,
        info_list=None,
        last_step=None,
        task_list=None,
        type_list=None,
        metadata=None
    ):
        self.action_list = action_list
        self.info_list = [] if info_list is None else info_list
        self.last_step = last_step
        self.task_list = [] if task_list is None else task_list
        self.type_list = [] if type_list is None else type_list
        self.metadata = {} if metadata is None else metadata

    def __str__(self):
        return MCS_Util.class_to_str(self)

