from .util import Util


class ObjectMetadata(object):
    """
    Defines metadata for an object in the MCS 3D environment.

    Attributes
    ----------
    uuid : string
        The unique ID of this object, used with some actions.
    color : dict
        The "r", "g", and "b" pixel values of this object in images from the
        StepMetadata's "object_mask_list".
    dimensions : dict
        The dimensions of this object in the environment's 3D global
        coordinate system as a list of 8 points (dicts with "x", "y", and "z").
    direction : dict
        The direction vector of "x", "y", and "z" degrees between your position
        and this object's position (the difference in the two positions),
        normalized to 1. You can use the "x" and "y" as the "rotation" and
        "horizon" parameters (respectively) in a "RotateLook" action to face
        this object.
    distance : float
        DEPRECATED. Same as distance_in_steps. Please use distance_in_steps
        or distance_in_world.
    distance_in_steps : float
        The distance from you to this object in number of steps ("Move"
        actions) on the 2D X/Z movement grid.
    distance_in_world : float
        The distance from you to this object in the environment's 3D global
        coordinate system.
    held : boolean
        Whether you are holding this object.
    mass : float
        Haptic feedback. The mass of this object.
    material_list : list of strings
        Haptic feedback. The material(s) of this object.
        See [Materials](#Materials).
    position : dict
        The "x", "y", and "z" coordinates for the global position of the
        center of this object's 3D model.
    rotation : dict
        This object's rotation angles around the "x", "y", and "z" axes
        in degrees.
    shape : string
        This object's shape in plain English.
    texture_color_list : list of strings
        This object's colors, derived from its textures, in plain English.
    visible : boolean
        Whether you can see this object in your camera viewport.
    """

    def __init__(
        self,
        uuid="",
        color=None,
        dimensions=None,
        direction=None,
        distance=-1.0,
        distance_in_steps=-1.0,
        distance_in_world=-1.0,
        held=False,
        mass=0.0,
        material_list=None,
        position=None,
        rotation=None,
        shape="",
        texture_color_list=None,
        visible=False
    ):
        self.uuid = uuid
        self.color = {} if color is None else color
        self.dimensions = {} if dimensions is None else dimensions
        self.direction = {} if direction is None else direction
        self.distance = distance
        self.distance_in_steps = distance_in_steps
        self.distance_in_world = distance_in_world
        self.held = held
        self.mass = mass
        self.material_list = [] if material_list is None else material_list
        self.position = {} if position is None else position
        self.rotation = {} if rotation is None else rotation
        self.shape = shape
        self.texture_color_list = (
            [] if texture_color_list is None else texture_color_list
        )
        self.visible = visible

    def __str__(self):
        return Util.class_to_str(self)

    # Allows converting the class to a dictionary, along with allowing
    #   certain fields to be left out of output file
    def __iter__(self):
        yield 'uuid', self.uuid
        yield 'color', self.color
        yield 'dimensions', self.dimensions
        yield 'direction', self.direction
        yield 'distance', self.distance
        yield 'distance_in_steps', self.distance_in_steps
        yield 'distance_in_world', self.distance_in_world
        yield 'held', self.held
        yield 'mass', self.mass
        yield 'material_list', self.material_list
        yield 'position', self.position
        yield 'rotation', self.rotation
        yield 'shape', self.shape
        yield 'texture_color_list', self.texture_color_list
        yield 'visible', self.visible
