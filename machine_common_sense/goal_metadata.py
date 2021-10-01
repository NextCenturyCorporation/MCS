from enum import Enum, unique

from .action import Action
from .stringifier import Stringifier


class GoalMetadata:
    """
    Defines metadata for a goal in the MCS 3D environment.

    Attributes
    ----------
    action_list : list of lists of (string, dict) tuples, or None
        The list of all actions that are available for the scene at each step
        (outer list). Each inner list is the list of all actions that are
        available for the single step corresponding to the inner list's index
        within the outer list. Each action is returned as a tuple containing
        the action string and the action's restricted paramters, if any.

        For example: ("Pass", {}) forces a Pass action; ("PickupObject", {})
        forces a PickupObject action with any parameters; and
        ("PickupObject", {"objectId": "a"}) forces a PickupObject action with
        the specific parameters objectId=a.

        An action_list of None means that all actions are always available.
        An empty inner list means that all actions will be available on that
        specific step.

        See :mod:`StepMetadata.action_list <machine_common_sense.StepMetadata>`
        for the available actions of the current step.
        May be a subset of all possible actions. See
        :mod:`Action <machine_common_sense.Action>`.
    category : string
        The category that describes this goal and the properties in its
        metadata. See :mod:`Goal <machine_common_sense.GoalCategory>`.
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
        See :mod:`Material <machine_common_sense.Material>`.
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
        The metadata specific to this goal. See
        :mod:`Goal <machine_common_sense.GoalCategory>`.
    """

    ACTION_LIST = [(item.value, {}) for item in Action]

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
        return Stringifier.class_to_str(self)

    # Allows converting the class to a dictionary, along with allowing
    #   certain fields to be left out of output file
    def __iter__(self):
        yield 'action_list', self.action_list
        yield 'category', self.category
        yield 'description', self.description
        # yield 'domain_list', self.domain_list
        # yield 'info_list', self.info_list
        yield 'last_preview_phase_step', self.last_preview_phase_step
        yield 'last_step', self.last_step
        # yield 'type_list', self.type_list
        yield 'metadata', self.metadata

    def retrieve_action_list_at_step(self, step_number):
        """Return the action list from the given goal at the given step as a
        a list of actions tuples by default."""
        if self is not None and self.action_list is not None:
            if step_number < self.last_preview_phase_step:
                return ['Pass']
            if self.last_step is not None and step_number == self.last_step:
                return []
            adjusted_step = step_number - self.last_preview_phase_step
            if len(self.action_list) > adjusted_step:
                if len(self.action_list[adjusted_step]) > 0:
                    return self.action_list[adjusted_step]

        return GoalMetadata.ACTION_LIST


@unique
class GoalCategory(Enum):
    """
    Each goal dict will have a "category" string that describes the type of
    scene (or, the type of task within the scene) being run. Each goal dict
    will also have a "metadata" dict containing one or more properties
    depending on the "category".
    """

    AGENTS = "agents"
    """
    In a trial that has an Agents goal, you must sit and observe a scene as one
    or more simulation-controlled agents act in predefined ways within your
    camera's viewport, and then decide whether the scene is "expected" or
    "unexpected". The camera will always be positioned at an isometric
    perspective, like you're standing on an elevated platform looking down at
    the scene. Each scene will consist of eight sequential habituation trials,
    depicting expected agent behaviors and separated by EndHabituation actions
    (each of which generates a black frame image when called), immediately
    followed by the test trial, depicting either an expected or unexpected
    agent behavior. All nine of these trials happen within the same "scene".
    These trials will demand a "common sense" understanding of agents, their
    behaviors, and their interactions with objects in the environment.

    Notes
    -----
    You are required to call `controller.end_scene()` at the end of each scene
    with a continuous plausibility `rating`, from 0.0 (completely implausible)
    to 1.0 (completely plausible). You are not required to also pass it a
    `score`.
    """

    INTUITIVE_PHYSICS = "intuitive physics"
    """
    In a trial that has an Intuitive Physics goal, you must sit and observe a
    scene as objects move across your camera's viewport, and then decide
    whether the scene is "plausible" or "implausible". These trials will demand
    a "common sense" understanding of basic ("intuitive") physics, like object
    permanence or shape constancy. Inspired by Emmanuel Dupoux's "IntPhys: A
    Benchmark for Visual Intuitive Physics Reasoning" (http://intphys.com).

    Notes
    -----
    You are required to call `controller.end_scene()` at the end of each scene
    with a binary plausibility `rating` -- either 0 (implausible) or 1
    (plausible) -- and a continuous plausibility `score` -- from 0.0
    (completely implausible) to 1.0 (completely plausible). This is also
    where you would submit any retrospective reporting on a per step basis via
    `report`.
    """

    RETRIEVAL = "retrieval"
    """
    In a trial that has a retrieval goal, you must find and pickup a target
    object. This may involve exploring the scene, avoiding obstacles,
    interacting with objects (like closed containers), and (future evaluations)
    tracking moving objects. These trials will demand a "common sense"
    understanding of self navigation (how to move and rotate yourself within a
    scene and around obstacles), object interaction (how objects work,
    including opening containers), and (future evaluations) the basic physics
    of movement (kinematics, gravity, friction, etc.).

    Parameters
    ----------
    target.id : string
        The objectId of the target object to retrieve.
        Will only be available at `oracle` metadata level.

    target.info : list of strings
        Human-readable information describing the target object needed for the
        visualization interface.

    """

    TRANSFERRAL = "transferral"
    """
    NOT USED IN MCS EVAL 4+

    In a trial that has a transferral goal, you must find and pickup the
    first target object and put it down either next to or on top of the second
    target object. This may involve exploring the scene, avoiding obstacles,
    interacting with objects (like closed receptacles), and (future
    evaluations) tracking moving objects. These trials will demand a "common
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

    target_1.image : list of numpy arrays
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

    target_2.image : list of numpy arrays
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
    NOT USED IN MCS EVAL 4+

    In a trial that has a traversal goal, you must find and move next to a
    target object. This may involve exploring the scene, and avoiding
    obstacles. These trials will demand a "common sense" understanding of
    self navigation (how to move and rotate yourself within a scene and around
    obstacles).

    Parameters
    ----------
    target.id : string
        The objectId of the target object to find and move next to.

    target.image : list of numpy arrays
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
