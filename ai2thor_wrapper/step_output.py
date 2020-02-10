from goal import Goal

class StepOutput:

    action_list = []
    object_list = []
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
        action_list=[],
        object_list=[],
        image=None,
        depth_mask=None,
        object_mask=None,
        metadata=None
    ):
        self.step_number = step_number
        self.goal = goal
        self.action_list = action_list
        self.object_list = object_list
        self.image = image
        self.depth_mask = depth_mask
        self.object_mask = object_mask
        self.metadata = metadata
        # TODO

