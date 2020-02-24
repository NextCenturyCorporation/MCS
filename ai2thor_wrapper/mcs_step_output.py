from mcs_goal import MCS_Goal
from mcs_pose import MCS_Pose
from mcs_return_status import MCS_Return_Status
from mcs_util import MCS_Util

class MCS_Step_Output:

    def __init__(
        self,
        action_list=[],
        depth_mask_list=[],
        goal=MCS_Goal(),
        head_tilt=0,
        image_list=[],
        object_list=[],
        object_mask_list=[],
        pose=MCS_Pose.UNDEFINED,
        return_status=MCS_Return_Status.UNDEFINED,
        step_number=0
    ):
        self.action_list = action_list
        self.depth_mask_list = depth_mask_list
        self.goal = goal
        self.head_tilt = head_tilt
        self.image_list = image_list
        self.object_list = object_list
        self.object_mask_list = object_mask_list
        self.pose = pose
        self.return_status = return_status
        self.step_number = step_number

    def __str__(self):
        return MCS_Util.class_to_str(self)

