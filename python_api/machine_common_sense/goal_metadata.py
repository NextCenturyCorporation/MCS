from enum import Enum, unique
from .util import Util


class GoalMetadata:
    """
    Defines metadata for a goal in the MCS 3D environment.

    Attributes
    ----------
    action_list : list of lists of strings, or None
        The list of actions that are available for the scene at each step
        (outer list index).  Each inner list item is a list of action strings.
        For example, ['MoveAhead','RotateLook,rotation=180'] restricts the
        actions to either 'MoveAhead' or 'RotateLook' with the 'rotation'
        parameter set to 180. An action_list of None means that all
        actions are always available. An empty inner list means that all
        actions are available for that specific step.
    category : string
        The category that describes this goal and the properties in its
        metadata. See [Goals](#Goals).
    description : string
        A human-readable sentence describing this goal and containing
        the target task(s) and object(s).

        Sizes:
        - tiny: near the size of a baseball
        - small: near the size of a baby
        - medium: near the size of a child
        - large: near the size of an adult
        - huge: near the size of a sofa

        Weights:
        - light: can be held by a baby
        - heavy: cannot be held by a baby, but can be pushed or pulled
        - massive: cannot be moved by a baby

        Colors:
        black, blue, brown, green, grey, orange, purple, red, white, yellow

        Materials:
        See [Materials](#Materials).
    habituation_total : int
        The total count of habituation trials that will be in this scene.
    last_preview_phase_step : integer
        The last step of the Preview Phase of this scene, if a Preview Phase is
        scripted in the scene configuration. Each step of a Preview Phase
        normally has a single specific action defined in this goal's
        action_list property for the performer to choose, like ['Pass'].
        Default: 0 (no Preview Phase)
    last_step : integer
        The last step of this scene. This scene will automatically end
        following this step.
    metadata : dict
        The metadata specific to this goal. See [Goals](#Goals).
    """

    def __init__(
        self,
        action_list=None,
        category='',
        description='',
        habituation_total=0,
        last_preview_phase_step=0,
        last_step=None,
        metadata=None
    ):
        # The action_list must be None by default
        self.action_list = action_list
        self.category = category
        self.description = description
        self.habituation_total = habituation_total
        self.last_preview_phase_step = last_preview_phase_step
        self.last_step = last_step
        self.metadata = {} if metadata is None else metadata

    def __str__(self):
        return Util.class_to_str(self)


@unique
class GoalCategory(Enum):
    """
    Each goal will have a "category" string and a "metadata" dict with one or
    more properties depending on the "category".
    """

    INTPHYS = "intphys"
    """
    In a scenario that has an IntPhys goal, you must sit and observe a scene as
    objects move across your camera's viewport, and then decide whether the
    scene is "plausible" or "implausible". These scenarios will demand a
    "common sense" understanding of basic ("intuitive") physics. Based on
    Emmanuel Dupoux's IntPhys: A Benchmark for Visual Intuitive Physics
    Reasoning (http://intphys.com).

    Parameters
    ----------
    choose : list of strings
        The list of choices, one of which must be given in your call to
        end_scene. For IntPhys goals, this value will always be ["plausible",
        "implausible"].
    """

    RETRIEVAL = "retrieval"
    """
    In a scenario that has a retrieval goal, you must find and pickup a target
    object. This may involve exploring the scene, avoiding obstacles,
    interacting with objects (like closed containers), and (future evaluations)
    tracking moving objects. These scenarios will demand a "common sense"
    understanding of self navigation (how to move and rotate yourself within a
    scene and around obstacles), object interaction (how objects work,
    including opening containers), and (future evaluations) the basic physics
    of movement (kinematics, gravity, friction, etc.).

    Parameters
    ----------
    target.id : string
        The objectId of the target object to retrieve.

    target.image : list of lists of lists of integers
        An image of the target object to retrieve, given as a 3D RGB pixel
        array.

    target.info : list of strings
        Human-readable information describing the target object needed for the
        visualization interface.

    target.match_image : string
        Whether the image of the target object (target.image) exactly matches
        the actual target object in the scene. If false, then the actual object
        will be different in one way (for example, the image may depict a blue
        ball, but the actual object is a yellow ball, or a blue cube).
    """

    TRANSFERRAL = "transferral"
    """
    In a scenario that has a transferral goal, you must find and pickup the
    first target object and put it down either next to or on top of the second
    target object. This may involve exploring the scene, avoiding obstacles,
    interacting with objects (like closed receptacles), and (future
    evaluations) tracking moving objects. These scenarios will demand a "common
    sense" understanding of self navigation (how to move and rotate yourself
    within a scene and around obstacles), object interaction (how objects work,
    including opening containers), and (future evaluations) the basic physics
    of movement (kinematics, gravity, friction, etc.).

    Parameters
    ----------
    relationship : list of strings
        The required final position of the two target objects in relation to
        one another. For transferral goals, this value will always be either
        ["target_1", "next_to", "target_2"] or ["target_1", "on_top_of",
        "target_2"].

    target_1.id : string
        The objectId of the first target object to pickup and transfer to the
        second target object.

    target_1.image : list of lists of lists of integers
        An image of the first target object to pickup and transfer to the
        second target object, given as a 3D RGB pixel array.

    target_1.info : list of strings
        Human-readable information describing the target object needed for the
        visualization interface.

    target_1.match_image : string
        Whether the image of the first target object (target_1.image) exactly
        matches the actual object in the scene. If false, then the actual first
        target object will be different in one way (for example, the image may
        depict a blue ball, but the actual object is a yellow ball, or a blue
        cube).

    target_2.id : string
        The objectId of the second target object to which the first target
        object must be transferred.

    target_2.image : list of lists of lists of integers
        An image of the second target object to which the first target object
        must be transferred, given as a 3D RGB pixel array.

    target_2.info : list of strings
        Human-readable information describing the target object needed for the
        visualization interface.

    target_2.match_image : string
        Whether the image of the second target object (target_2.image) exactly
        matches the actual object in the scene. If false, then the actual
        second target object will be different in one way (for example, the
        image may depict a blue ball, but the actual object is a yellow ball,
        or a blue cube).
    """

    TRAVERSAL = "traversal"
    """
    In a scenario that has a traversal goal, you must find and move next to a
    target object. This may involve exploring the scene, and avoiding
    obstacles. These scenarios will demand a "common sense" understanding of
    self navigation (how to move and rotate yourself within a scene and around
    obstacles).

    Parameters
    ----------
    target.id : string
        The objectId of the target object to find and move next to.

    target.image : list of lists of lists of integers
        An image of the target object to find and move next to, given as a 3D
        RGB pixel array.

    target.info : list of strings
        Human-readable information describing the target object needed for the
        visualization interface.

    target.match_image : string
        Whether the image of the target object (target.image) exactly matches
        the actual target object in the scene. If false, then the actual object
        will be different in one way (for example, the image may depict a blue
        ball, but the actual object is a yellow ball, or a blue cube).
    """
