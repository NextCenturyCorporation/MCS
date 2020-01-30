from goal import Goal

class StepOutput:

    actionList = []
    goal = None
    metadata = None
    step_number = None

    def __init__(self, step_number=None, goal=Goal(), actionList=[], metadata=None):
        self.step_number = step_number
        self.goal = goal
        self.actionList = actionList
        self.metadata = metadata
        # TODO

