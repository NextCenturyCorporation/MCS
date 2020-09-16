from .step_metadata import StepMetadata
import random
import PIL
from typing import Dict, List


class Controller:
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
        StepMetadata
            The output data object from the start of the scene (the output from
            an "Initialize" action).
        """

        # TODO Override
        return StepMetadata()

    def step(self, action: str, choice: str = None,
             confidence: float = None,
             violations_xy_list: List[Dict[str, float]] = None,
             heatmap_img: PIL.Image = None,
             internal_state: object = None,
             **kwargs) -> StepMetadata:
        """
        Runs the given action within the current scene and unpauses the scene's
        physics simulation for a few frames. Can also optionally send
        information about scene plausability if applicable.

        Parameters
        ----------
        action : string
            A selected action string from the list of available actions.
        choice : string, optional
            The selected choice required by the end of scenes with
            violation-of-expectation or classification goals.
            Is not required for other goals. (default None)
        confidence : float, optional
            The choice confidence between 0 and 1 required by the end of
            scenes with violation-of-expectation or classification goals.
            Is not required for other goals. (default None)
        violations_xy_list : List[Dict[str, float]], optional
            A list of one or more (x, y) locations (ex: [{"x": 1, "y": 3.4}]),
            each representing a potential violation-of-expectation. Required
            on each step for passive tasks. (default None)
        heatmap_img : PIL.Image, optional
            An image representing scene plausiblility at a particular
            moment. Will be saved as a .png type. (default None)
        internal_state : object, optional
            A properly formatted json object representing various kinds of
            internal states at a particular moment. Examples include the
            estimated position of the agent, current map of the world, etc.
            (default None)
        **kwargs
            Zero or more key-and-value parameters for the action.

        Returns
        -------
        StepMetadata
            The MCS output data object from after the selected action and the
            physics simulation were run. Returns None if you have passed the
            "last_step" of this scene.
        """

        # TODO Override
        return StepMetadata()

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
