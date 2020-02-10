from goal import Goal

class StepOutput:

    actionList = []
    depth_mask = None
    goal = None
    image = None
    metadata = None
    object_mask = None
    step_number = None

    def __init__(
        self,
        step_number=None,
        goal=Goal(),
        actionList=[],
        image=None,
        depth_mask=None,
        object_mask=None,
        metadata=None
    ):
        self.step_number = step_number
        self.goal = goal
        self.actionList = actionList
        self.image = image
        self.depth_mask = depth_mask
        self.object_mask = object_mask
        self.metadata = metadata
        # TODO

