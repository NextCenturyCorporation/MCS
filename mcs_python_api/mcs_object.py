from mcs_python_api.mcs_material import MCS_Material
from mcs_python_api.mcs_util import MCS_Util

class MCS_Object:
    """
    Defines attributes of an object in the MCS 3D environment.

    Attributes
    ----------
    uuid : string
        The unique ID of this object, used with some actions.
    color : dict
        The "r", "g", and "b" pixel values of this object in images from the MCS_Step_Output's "object_mask_list".
    direction : dict
        The normalized direction vector of "x", "y", and "z" degrees between your position and this object's.
        Use "x" and "y" as "rotation" and "horizon" params (respectively) in a "RotateLook" action to face this object.
    distance : float
        The distance to this object in number of steps ("Move" actions).
    held : boolean
        Whether you are holding this object.
    mass : float
        Haptic feedback.  The mass of this object.
    material_list : list of strings
        Haptic feedback.  The materials of this object.
    point_list : list of dicts
        The list of 3D points (dicts with "x", "y", and "z") that form the outside shape of this object.
    visible : boolean
        Whether you can see this object in your camera view.
    """

    def __init__(
        self,
        uuid="",
        color=None,
        direction=None,
        distance=-1,
        held=False,
        mass=0,
        material_list=None,
        point_list=None,
        visible=False
    ):
        self.uuid = uuid
        self.color = color
        self.direction = direction
        self.distance = distance
        self.held = held
        self.mass = mass
        self.material_list = [] if material_list is None else material_list
        self.point_list = [] if point_list is None else point_list
        self.visible = visible

    def __str__(self):
        return MCS_Util.class_to_str(self)
