from .mcs_step_output import MCS_Step_Output
import random


class MCS_Controller:
    """
    Starts and ends scenes, runs actions on each step, and returns scene
    output data.
    """

    def __init__(self):
        pass

    def end_scene(self, choice, confidence=1.0):
        """
        Ends the current scene.

        Parameters
        ----------
        choice : string, optional
            The selected choice required for ending scenes with
            violation-of-expectation or classification goals.
            Is not required for other goals. (default None)
        confidence : float, optional
            The choice confidence between 0 and 1 required for ending scenes
            with violation-of-expectation or classification goals.
            Is not required for other goals. (default None)
        """

        # TODO Override
        pass

    def start_scene(self, config_data):
        """
        Starts a new scene using the given scene configuration data dict and
        returns the scene output data object.

        Parameters
        ----------
        config_data : dict
            The MCS scene configuration data for the scene to start.

        Returns
        -------
        MCS_Step_Output
            The output data object from the start of the scene (the output from
            an "Initialize" action).
        """

        # TODO Override
        return MCS_Step_Output()

    def step(self, action, **kwargs):
        """
        Runs the given action within the current scene and unpauses the scene's
        physics simulation for a few frames.

        Parameters
        ----------
        action : string
            A selected action string from the list of available actions.
        **kwargs
            Zero or more key-and-value parameters for the action.

        Returns
        -------
        MCS_Step_Output
            The MCS output data object from after the selected action and the
            physics simulation were run. Returns None if you have passed the
            "last_step" of this scene.
        """

        # TODO Override
        return MCS_Step_Output()

    def generate_noise(self):
        """
        Returns a random value between -0.05 and 0.05 used to add noise to all
        numerical action parameters enable_noise is True.

        Returns
        -------
        float
            A value between -0.05 and 0.05 (using random.uniform).
        """

        return random.uniform(-0.5, 0.5)
