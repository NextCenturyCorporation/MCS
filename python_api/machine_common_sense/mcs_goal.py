from machine_common_sense.mcs_util import MCS_Util

class MCS_Goal:
    """
    Defines attributes of an MCS goal.

    Attributes
    ----------
    type_list : list of strings
        The list of types associated with this goal, including the relevant MCS core domains.
    task_list : list of strings
        The list of tasks associated with this goal (secondary to its types).
    info_list : list
        The list of information for the visualization interface associated with this goal.
    metadata : dict
        The metadata specific to this goal.
    """

    def __init__(
        self,
        type_list=None,
        task_list=None,
        info_list=None,
        metadata=None
    ):
        self.type_list = [] if type_list is None else type_list
        self.task_list = [] if task_list is None else task_list
        self.info_list = [] if info_list is None else info_list
        self.metadata = {} if metadata is None else metadata

    def __str__(self):
        return MCS_Util.class_to_str(self)

