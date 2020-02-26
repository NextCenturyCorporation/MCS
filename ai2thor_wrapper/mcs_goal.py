from mcs_util import MCS_Util

class MCS_Goal:
    """
    Defines attributes of an MCS goal.

    Attributes
    ----------
    details : dict
        The metadata specific to this goal.
    domains : list of strings
        The list of core MCS domains associated with this goal.
    tasks : list of strings
        The list of tasks associated with this goal.
    types : list of strings
        The list of types associated with this goal.
    """

    def __init__(
        self,
        details={},
        domains=[],
        tasks=[],
        types=[]
    ):
        self.details = details
        self.domains = domains
        self.tasks = tasks
        self.types = types

    def __str__(self):
        return MCS_Util.class_to_str(self)

