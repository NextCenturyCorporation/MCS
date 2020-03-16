from machine_common_sense.mcs_goal import MCS_Goal
from machine_common_sense.mcs_pose import MCS_Pose
from machine_common_sense.mcs_return_status import MCS_Return_Status
from machine_common_sense.mcs_util import MCS_Util

class MCS_Step_Output:
    """
    Defines attributes of the output from a single step in the MCS 3D environment.

    Attributes
    ----------
    action_list : list of strings
        The list of all actions that are available for the next step.  See MCS_Action.
    depth_mask_list : list of Pillow.Image objects
        The list of depth mask images from the scene after the last action and physics simulation were run.  This is
        usually just a list with a single object, except for the MCS_Step_Output object returned from a call to
        controller.start_scene for a scene with a Pre-Interaction Phase.
    goal : MCS_Goal or None
        The goal for the whole scene.  Will be None in "Exploration" scenes.
    head_tilt : float
        How far your head is tilted up/down in degrees (between 90 and -90).  Changed by setting the horizon parameter
        in a "RotateLook" action.
    image_list : list of Pillow.Image objects
        The list of normal vision images from the scene after the last action and physics simulation were run.  This is
        usually just a list with a single object, except for the MCS_Step_Output object returned from a call to
        controller.start_scene for a scene with a Pre-Interaction Phase.
    object_list : list of MCS_Object objects
        The list of metadata for all objects in the scene.
    object_mask_list : list of Pillow.Image objects
        The list of object mask images from the scene after the last action and physics simulation were run.  This is
        usually just a list with a single object, except for the MCS_Step_Output object returned from a call to
        controller.start_scene for a scene with a Pre-Interaction Phase.
    pose : string
        Your current pose.  See MCS_Pose.
    return_status : string
        The return status from your last action.  See MCS_Return_Status.
    step_number : integer
        The step number of your last action, recorded since you started the current scene.
    """

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

