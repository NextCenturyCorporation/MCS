from .goal_metadata import GoalMetadata
from .pose import Pose
from .return_status import ReturnStatus
from .util import Util


class StepMetadata:
    """
    Defines output metadata from an action step in the MCS 3D environment.

    Attributes
    ----------
    action_list : list of strings
        The list of all actions that are available for the next step.
        May be a subset of all possible actions. See [Actions](#Actions).
    camera_aspect_ratio : (float, float)
        The player camera's aspect ratio. This will remain constant for the
        whole scene.
    camera_clipping_planes : (float, float)
        The player camera's near and far clipping planes. This will remain
        constant for the whole scene.
    camera_field_of_view : float
        The player camera's field of view. This will remain constant for
        the whole scene.
    camera_height : float
        The player camera's height. This will change if the player uses
        actions like "LieDown", "Stand", or "Crawl".
    depth_map_list : list of 2D numpy arrays
        The list of 2-dimensional numpy arrays of depth float data from the
        scene after the last action and physics simulation were run. This is
        usually a list with 1 array, except for the output from start_scene
        for a scene with a scripted Preview Phase.
        Each depth float in a 2-dimensional numpy array is a value between 0
        and the camera's far clipping plane (default 15) correspondings to the
        depth in simulation units at that pixel in the image.
    goal : GoalMetadata or None
        The goal for the whole scene. Will be None in "Exploration" scenes.
    habituation_trial : int or None
        The current habituation trial (as a positive integer), or None if the
        scene is not currently in a habituation trial (meaning this scene is
        in a test trial).
    head_tilt : float
        How far your head is tilted up/down in degrees (between 90 and -90).
        Changed by setting the "horizon" parameter in a "RotateLook" action.
    image_list : list of Pillow.Image objects
        The list of images from the scene after the last action and physics
        simulation were run. This is usually a list with 1 image, except for
        the output from start_scene for a scene with a scripted Preview Phase.
    object_list : list of ObjectMetadata objects
        The list of metadata for all the visible interactive objects in the
        scene. For metadata on structural objects like walls, please see
        structural_object_list
    object_mask_list : list of Pillow.Image objects
        The list of object mask (instance segmentation) images from the scene
        after the last action and physics simulation were run. This is usually
        a list with 1 image, except for the output from start_scene for a
        scene with a scripted Previous Phase.
        The color of each object in the mask corresponds to the "color"
        property in its ObjectMetadata object.
    pose : string
        Your current pose. Either "STANDING", "CRAWLING", or "LYING".
    position : dict
        The "x", "y", and "z" coordinates for your global position.
    return_status : string
        The return status from your last action. See [Actions](#Actions).
    reward : integer
        Reward is 1 on successful completion of a task, 0 otherwise.
    rotation : float
        Your current rotation angle in degrees.
    step_number : integer
        The step number of your last action, recorded since you started the
        current scene.
    structural_object_list : list of ObjectMetadata objects
        The list of metadata for all the visible structural objects (like
        walls, occluders, and ramps) in the scene. Please note that occluders
        are composed of two separate objects, the "wall" and the "pole", with
        corresponding object IDs (occluder_wall_<uuid> and
        occluder_pole_<uuid>), and ramps are composed of between one and three
        objects (depending on the type of ramp), with corresponding object IDs.
    """

    def __init__(
        self,
        action_list=None,
        camera_aspect_ratio=None,
        camera_clipping_planes=None,
        camera_field_of_view=0.0,
        camera_height=0.0,
        depth_map_list=None,
        goal=None,
        habituation_trial=None,
        head_tilt=0.0,
        image_list=None,
        object_list=None,
        object_mask_list=None,
        pose=Pose.UNDEFINED.value,
        position=None,
        return_status=ReturnStatus.UNDEFINED.value,
        reward=0,
        rotation=0.0,
        step_number=0,
        structural_object_list=None
    ):
        self.action_list = [] if action_list is None else action_list
        self.camera_aspect_ratio = (
            0.0, 0.0) if camera_aspect_ratio is None else camera_aspect_ratio
        self.camera_clipping_planes = (
            (0.0, 0.0)
            if camera_clipping_planes is None
            else camera_clipping_planes
        )
        self.camera_field_of_view = camera_field_of_view
        self.camera_height = camera_height
        self.depth_map_list = (
            [] if depth_map_list is None else depth_map_list
        )
        self.goal = GoalMetadata() if goal is None else goal
        self.habituation_trial = habituation_trial
        self.head_tilt = head_tilt
        self.image_list = [] if image_list is None else image_list
        self.object_list = [] if object_list is None else object_list
        self.object_mask_list = (
            [] if object_mask_list is None else object_mask_list
        )
        self.pose = pose
        self.position = {} if position is None else position
        self.return_status = return_status
        self.reward = reward
        self.rotation = rotation
        self.step_number = step_number
        self.structural_object_list = [
        ] if structural_object_list is None else structural_object_list

    def __str__(self):
        return Util.class_to_str(self)

    # Allows converting the class to a dictionary, along with allowing
    #   certain fields to be left out of output file
    def __iter__(self):
        yield 'action_list', self.action_list
        yield 'camera_aspect_ratio', self.camera_aspect_ratio
        yield 'camera_clipping_planes', self.camera_clipping_planes
        yield 'camera_field_of_view', self.camera_field_of_view
        yield 'camera_height', self.camera_height
        yield 'goal', dict(self.goal)
        yield 'head_tilt', self.head_tilt
        yield 'object_list', dict((obj.uuid, dict(
            obj)) for obj in self.object_list)
        yield 'pose', self.pose
        yield 'position', self.position
        yield 'return_status', self.return_status
        yield 'reward', self.reward
        yield 'rotation', self.rotation
        yield 'step_number', self.step_number
        yield 'structural_object_list', dict((obj.uuid, dict(
            obj)) for obj in self.structural_object_list)
