import logging
from enum import Enum, unique
from typing import List, Optional

import typeguard

from .action import Action
from .stringifier import Stringifier

logger = logging.getLogger(__name__)


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
    steps_allowed_in_lava : integer
        The number of steps allowed in lava before the scene ends
    triggered_by_target_sequence : List of strings
        The target sequence the performer must open containers to trigger
        the targets placement by a placer for imitation tasks.
    """

    # Don't allow a user to call the EndHabituation action unless it's
    # specifically configured in the action_list of the scene file.
    DEFAULT_ACTIONS = [
        (item.value, {}) for item in Action
        if item not in [Action.END_HABITUATION, Action.INITIALIZE]
    ]
    # Each passive scene should have its own action_list, but if it doesn't for
    # some reason, then only allow calling Pass actions by default.
    DEFAULT_PASSIVE_SCENE_ACTIONS = [('Pass', {})]

    def __init__(
        self,
        action_list=None,
        category='',
        description='',
        habituation_total=0,
        last_preview_phase_step=0,
        last_step=None,
        metadata=None,
        steps_allowed_in_lava=0,
        triggered_by_target_sequence=None
    ):
        # The action_list must be None by default
        self.action_list = action_list
        self.category = category
        self.description = description
        self.habituation_total = habituation_total
        self.last_preview_phase_step = last_preview_phase_step
        self.last_step = last_step
        self.metadata = {} if metadata is None else metadata
        self.steps_allowed_in_lava = steps_allowed_in_lava
        self.triggered_by_target_sequence = triggered_by_target_sequence

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
        yield 'triggered_by_target_sequence', self.triggered_by_target_sequence

    @typeguard.typechecked
    def retrieve_action_list_at_step(
        self,
        step_number: int,
        steps_in_lava: Optional[int] = 0,
        triggered_by_sequence_incorrect: Optional[bool] = False,
        is_passive_scene: bool = False
    ) -> List:
        """Return the action list from the given goal at the given step as a
        a list of actions tuples by default."""
        action_list = self._retrieve_unfiltered_action_list(
            step_number, steps_in_lava,
            triggered_by_sequence_incorrect, is_passive_scene)
        # remove EndHabituation parameters
        return [
            (action, params)
            if action != 'EndHabituation' else ('EndHabituation', {})
            for (action, params) in action_list
        ]

    def _retrieve_unfiltered_action_list(
        self,
        step_number: int,
        steps_in_lava: Optional[int] = 0,
        triggered_by_sequence_incorrect: Optional[bool] = False,
        is_passive_scene: bool = False
    ) -> List:
        # If steps in lava is greater than allowed, over ride
        #   action list and only return EndScene
        if steps_in_lava is not None and (
                steps_in_lava > self.steps_allowed_in_lava):
            return [("EndScene", {})]

        if triggered_by_sequence_incorrect:
            return [("EndScene", {})]

        '''Unfiltered action list from goal'''
        if self.action_list is not None:
            if step_number < self.last_preview_phase_step:
                return [('Pass', {})]
            if self.last_step is not None and step_number >= self.last_step:
                return []

            adjusted_step = step_number - self.last_preview_phase_step
            if (
                len(self.action_list) > adjusted_step and
                len(self.action_list[adjusted_step]) > 0
            ):
                return [
                    action if isinstance(action, tuple) else
                    Action.input_to_action_and_params(action)
                    for action in self.action_list[adjusted_step]
                ]

        if is_passive_scene:
            logger.warning(
                'Passive scene should have an action_list but does not; '
                'allowing only Pass actions by default.'
            )
            return GoalMetadata.DEFAULT_PASSIVE_SCENE_ACTIONS
        return GoalMetadata.DEFAULT_ACTIONS


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

    This goal category is only used for the **passive/VoE agent tasks**. All
    interactive agent tasks will use either the `retrieval` or
    `multi retrieval` goal category.

    Notes
    -----
    You are required to call `controller.end_scene()` at the end of each scene
    with a continuous plausibility `rating`, from 0.0 (completely implausible)
    to 1.0 (completely plausible). You are not required to also pass it a
    `score`.
    """

    IMITATION = "imitation"
    """
    In a trial that has an imitation goal, you must imitate the actions of
    another agent in the scene to find and pickup a target object. Executing
    the same actions, on the same objects, in the same order, is of critical
    importance; if you do not imitate the actions correctly, you will be
    forced to end the scene (by calling end_scene, or using the END_SCENE
    action), without achieving the reward. In MCS Evaluation 4 and onward, the
    target object will always be a soccer ball (football), and, in MCS
    Evaluation 6, the imitated actions will always be opening containers of
    various colors and shapes (using the normal OpenObject action).

    Notes
    -----
    At `oracle` metadata level, the `metadata` dict property of this
    GoalMetadata object will contain a `target` property, which is a dict
    containing the following parameters:

    Parameters
    ----------
    id : string
        The unique objectId of the target object to retrieve.
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

    PASSIVE = "passive"
    """
    In a trial that has a Passive goal, you must sit and observe a scene as
    action unfolds in your camera's viewport, and then decide whether the scene
    is "plausible" or "implausible". These trials will demand a "common sense"
    understanding of places, objects, or agency. This goal category covers all
    passive scenes that do not fall under the "agents" or "intuitive physics"
    categories.

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
    object. In MCS Evaluation 4 and onward, the target object will always be a
    soccer ball (football).

    This may involve exploring the scene, avoiding obstacles,
    interacting with objects (like closed containers) or agents, and tracking
    moving objects. These trials will demand a "common sense" understanding of
    self navigation (how to move and rotate yourself within a scene and around
    obstacles), object interaction (how objects work, including opening
    containers), the basic physics of movement (kinematics, gravity, friction,
    etc.), and agency (identifying people and using them to achieve a goal).

    Notes
    -----
    At `oracle` metadata level, the `metadata` dict property of this
    GoalMetadata object will contain a `target` property, which is a dict
    containing the following parameters:

    Parameters
    ----------
    id : string
        The unique objectId of the target object to retrieve.
    """

    MULTI_RETRIEVAL = "multi retrieval"
    """
    In a trial that has a multi retrieval goal, you must find and pickup one or
    more target objects. In MCS Evaluation 4 and onward, the target object will
    always be a soccer ball (football).

    This may involve exploring the scene, avoiding obstacles,
    interacting with objects (like closed containers) or agents, and tracking
    moving objects. These trials will demand a "common sense" understanding of
    self navigation (how to move and rotate yourself within a scene and around
    obstacles), object interaction (how objects work, including opening
    containers), the basic physics of movement (kinematics, gravity, friction,
    etc.), and agency (identifying people and using them to achieve a goal).

    Notes
    -----
    At `oracle` metadata level, the `metadata` dict property of this
    GoalMetadata object will contain a `targets` property, which is a list of
    dicts that each contain the following parameters:

    Parameters
    ----------
    id : string
        The unique objectId of one of the target objects to retrieve.
    """
