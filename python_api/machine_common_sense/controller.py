import random

from .step_output import StepOutput


class Controller:
    """
    Starts and ends scenes, runs actions on each step, and returns scene
    output data.

    Parameters
    ----------
    enable_noise : boolean, optional
        An optional flag to enable noise in the system for move, amount,
        force actions
    """

    def __init__(self, enable_noise=False):
        self.__enable_noise = enable_noise


    def end_scene(self, classification: str, confidence: float):
        """Ends the current scene.

        Parameters
        ----------
        classification : string, optional
            The selected classification for "classify" goals.  Is not required for other goals.
        confidence : float, optional
            The classification confidence between 0 and 1 for "classify" goals.  Is not required for other goals.
        """
        # TODO Override
        pass


    def start_scene(self, config_data):
        """Starts a new scene using the given scene configuration data dict and returns the scene output data object.

        Parameters
        ----------
        config_data : dict
            The MCS scene configuration data for the scene to start.

        Returns
        -------
        MCS_Step_Output
            The output data object from the start of the scene (the output from an "Initialize" action).
        """
        # TODO Override
        return StepOutput()


    def step(self, action, **kwargs):
        """Runs the given action within the current scene and unpauses the scene's physics simulation for a few frames.

        Parameters
        ----------
        action : string
            An action string from the list of available MCS actions.
        **kwargs
            Zero or more additional parameters depending on the specific action.

        Returns
        -------
        Step_Output
            The output data object from after the action and the physics simulation were run.
        """
        # TODO Override
        return StepOutput()

    def generate_noise(self):
        """Calculates a random value float between -0.05 and 0.05 to add some noise into move, amount, force actions

        Returns
        -------
        float
            A float value for the amount of noise that will be applied to actions.
        """
        return random.uniform(-0.5, 0.5)
