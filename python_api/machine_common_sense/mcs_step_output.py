from .mcs_goal import MCS_Goal
from .mcs_pose import MCS_Pose
from .mcs_return_status import MCS_Return_Status
from .mcs_util import MCS_Util

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
        The list of metadata for all the interactive objects in the scene. For metadata on structural objects like
        walls, please see structural_object_list
    object_mask_list : list of Pillow.Image objects
        The list of object mask images from the scene after the last action and physics simulation were run.  This is
        usually just a list with a single object, except for the MCS_Step_Output object returned from a call to
        controller.start_scene for a scene with a Pre-Interaction Phase.
    pose : string
        Your current pose.  See MCS_Pose.
    position : dict
        The "x", "y", and "z" coordinates for your global position.
    return_status : string
        The return status from your last action.  See MCS_Return_Status.
    reward : integer
        Reward is 1 on successful completion of a task, 0 otherwise.
    rotation : float
        Your current rotation angle in degrees.
    step_number : integer
        The step number of your last action, recorded since you started the current scene.
    structural_object_list : list of MCS_Object objects
        The list of metadata for all the structural objects (like walls) in the scene.
    """

    def __init__(
        self,
        action_list=None,
        depth_mask_list=None,
        goal=None,
        head_tilt=0.0,
        image_list=None,
        object_list=None,
        object_mask_list=None,
        pose=MCS_Pose.UNDEFINED,
        position=None,
        return_status=MCS_Return_Status.UNDEFINED,
        reward=0,
        rotation=0.0,
        step_number=0,
        structural_object_list=None
    ):
        self.action_list = [] if action_list is None else action_list
        self.depth_mask_list = [] if depth_mask_list is None else depth_mask_list
        self.goal = MCS_Goal() if goal is None else goal
        self.head_tilt = head_tilt
        self.image_list = [] if image_list is None else image_list
        self.object_list = [] if object_list is None else object_list
        self.object_mask_list = [] if object_mask_list is None else object_mask_list
        self.pose = pose
        self.position = {} if position is None else position
        self.return_status = return_status
        self.reward = reward
        self.rotation = rotation
        self.step_number = step_number
        self.structural_object_list = [] if structural_object_list is None else structural_object_list

    def __str__(self):
        return MCS_Util.class_to_str(self)
