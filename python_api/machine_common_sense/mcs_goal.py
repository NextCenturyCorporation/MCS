from .mcs_util import MCS_Util


class MCS_Goal:
    """
    Defines an MCS goal.

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
    domain_list : list of strings
        The list of MCS "core domains" associated with this goal (for the
        visualization interface).
    info_list : list
        The list of information for the visualization interface associated
        with this goal.
    last_preview_phase_step : integer
        The last step of the Preview Phase of this scene, if a Preview Phase is
        scripted in the scene configuration. Each step of a Preview Phase
        normally has a single specific action defined in this goal's
        action_list property for the performer to choose, like ['Pass'].
        Default: 0 (no Preview Phase)
    last_step : integer
        The last step of this scene. This scene will automatically end
        following this step.
    type_list : list of strings
        The list of types associated with this goal (for the
        visualization interface).
    metadata : dict
        The metadata specific to this goal. See [Goals](#Goals).
    """

    def __init__(
        self,
        action_list=None,
        category='',
        description='',
        domain_list=None,
        info_list=None,
        last_preview_phase_step=0,
        last_step=None,
        type_list=None,
        metadata=None
    ):
        # The action_list must be None by default
        self.action_list = action_list
        self.category = category
        self.description = description
        self.domain_list = [] if domain_list is None else domain_list
        self.info_list = [] if info_list is None else info_list
        self.last_preview_phase_step = last_preview_phase_step
        self.last_step = last_step
        self.type_list = [] if type_list is None else type_list
        self.metadata = {} if metadata is None else metadata

    def __str__(self):
        return MCS_Util.class_to_str(self)
