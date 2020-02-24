from mcs_util import MCS_Util

class MCS_Goal:

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

