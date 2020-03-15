from mcs_python_api.mcs_step_output import MCS_Step_Output

class MCS_Controller:
    """
    Starts and ends scenes, runs actions on each step, and returns scene output data.
    """

    def __init__(self):
        # TODO Override
        pass

    """
    Ends the current scene.

    Parameters
    ----------
    classification : string, optional
        The selected classification for "classify" goals.  Is not required for other goals.
    confidence : float, optional
        The classification confidence between 0 and 1 for "classify" goals.  Is not required for other goals.
    """
    def end_scene(self, classification, confidence):
        # TODO Override
        pass

    """
    Starts a new scene using the given scene configuration data dict and returns the scene output data object.

    Parameters
    ----------
    config_data : dict
        The MCS scene configuration data for the scene to start.

    Returns
    -------
    MCS_Step_Output
        The output data object from the start of the scene (the output from an "Initialize" action).
    """
    def start_scene(self, config_data):
        # TODO Override
        return MCS_Step_Output()


    """
    Runs the given action within the current scene and unpauses the scene's physics simulation for a few frames.

    Parameters
    ----------
    action : string
        An action string from the list of available MCS actions.
    **kwargs
        Zero or more additional parameters depending on the specific action.

    Returns
    -------
    MCS_Step_Output
        The output data object from after the action and the physics simulation were run.
    """
    def step(self, action, **kwargs):
        # TODO Override
        return MCS_Step_Output()

