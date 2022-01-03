import random
from typing import Any, Dict, Optional, Tuple

from .action import Action
from .config_manager import ConfigManager, MetadataTier
from .controller import DEFAULT_MOVE


class Parameter:

    # AI2-THOR creates a square grid across the scene that is
    # uses for "snap-to-grid" movement. (This value may not
    # really matter because we set continuous to True in
    # the step input.)
    GRID_SIZE = 0.1

    DEFAULT_HORIZON = 0.0
    DEFAULT_ROTATION = 0.0
    DEFAULT_FORCE = 0.5
    DEFAULT_AMOUNT = 0.5
    DEFAULT_IMG_COORD = 0
    DEFAULT_OBJECT_MOVE_AMOUNT = 1.0

    MAX_FORCE = 1.0
    MIN_FORCE = 0.0
    MAX_AMOUNT = 1.0
    MIN_AMOUNT = 0.0

    MIN_NOISE = -0.5
    MAX_NOISE = 0.5

    ROTATION_KEY = 'rotation'
    HORIZON_KEY = 'horizon'
    FORCE_KEY = 'force'
    AMOUNT_KEY = 'amount'

    OBJECT_IMAGE_COORDS_X_KEY = 'objectImageCoordsX'
    OBJECT_IMAGE_COORDS_Y_KEY = 'objectImageCoordsY'
    RECEPTACLE_IMAGE_COORDS_X_KEY = 'receptacleObjectImageCoordsX'
    RECEPTACLE_IMAGE_COORDS_Y_KEY = 'receptacleObjectImageCoordsY'

    # used for EndHabituation teleport
    TELEPORT_X_POS = 'xPosition'
    TELEPORT_Z_POS = 'zPosition'
    TELEPORT_Y_ROT = 'yRotation'

    # # Hard coding actions that effect MoveMagnitude so the appropriate
    # # value is set based off of the action
    # # TODO: Move this to an enum or some place, so that you can determine
    # # special move interactions that way
    FORCE_ACTIONS = ["PushObject", "PullObject"]
    OBJECT_MOVE_ACTIONS = ["CloseObject", "OpenObject"]
    # DW: not used anywhere
    # MOVE_ACTIONS = ["MoveAhead", "MoveLeft", "MoveRight", "MoveBack"]

    def __init__(self, config: ConfigManager):
        self.config = config

    def wrap_step(self, **kwargs) -> Dict:
        # whether or not to randomize segmentation mask colors
        metadata_tier = self.config.get_metadata_tier()
        consistent_colors = (metadata_tier == MetadataTier.ORACLE)
        # Create the step data dict for the AI2-THOR step function.
        return dict(
            continuous=True,
            gridSize=self.GRID_SIZE,
            logs=True,
            renderDepthImage=self.config.is_depth_maps_enabled(),
            renderObjectImage=self.config.is_object_masks_enabled(),
            snapToGrid=False,
            consistentColors=consistent_colors,
            **kwargs
        )

    def build_ai2thor_step(self, **kwargs) -> Tuple:
        action, params = self._validate_and_convert_params(**kwargs)
        action = self._mcs_action_to_ai2thor_action(action)
        wrapped_step = self.wrap_step(action=action, **params)
        return wrapped_step, params

    def _convert_y_image_coord_for_unity(self, y_coord: int) -> int:
        '''Pixel coordinates are expected to start at the top left,
        but in Unity, (0,0) is the bottom left.
        '''
        if not isinstance(y_coord, int):
            raise TypeError(f"{y_coord} y_coord is not an integer")
        screen_height = self.config.get_screen_height()
        if(0 <= y_coord < screen_height):
            return screen_height - y_coord - 1
        raise ValueError(f"{y_coord} is not in range 0-{screen_height-1}")

    def _get_amount(self, **kwargs) -> float:
        action = kwargs.get('action')
        amount = kwargs.get(
            self.AMOUNT_KEY,
            self.DEFAULT_OBJECT_MOVE_AMOUNT
            if action in self.OBJECT_MOVE_ACTIONS
            else self.DEFAULT_AMOUNT
        )
        if amount is not None:
            try:
                amount = float(amount)
            except ValueError as err:
                raise ValueError(f"Amount {amount} is not a number") from err
        else:
            amount = self.DEFAULT_AMOUNT

        if amount < self.MIN_AMOUNT or amount > self.MAX_AMOUNT:
            raise ValueError(
                "Amount not in acceptable range of "
                f"({self.MIN_AMOUNT}-{self.MAX_AMOUNT})"
            )
        return amount

    def _get_force(self, **kwargs) -> float:
        force = kwargs.get(self.FORCE_KEY, self.DEFAULT_FORCE)
        if force is not None:
            try:
                force = float(force)
            except ValueError as err:
                raise ValueError('Force is not a number') from err

            if force < self.MIN_FORCE or force > self.MAX_FORCE:
                raise ValueError(
                    f'Force not in acceptable range of '
                    f'({self.MIN_FORCE}-{self.MAX_FORCE})')
        else:
            force = self.DEFAULT_FORCE
        return force

    def _get_number(self, key: str, **kwargs) -> Optional[Any]:
        val = kwargs.get(key)
        if val is not None:
            try:
                val = float(val)
            except ValueError as err:
                raise ValueError(f"{key}") from err
        return val

    def _get_number_with_default(
            self, key: str, default: Any, **kwargs) -> Any:
        val = kwargs.get(key, default)
        if val is not None:
            try:
                val = float(val)
            except ValueError as err:
                raise ValueError(f"{key}") from err
        else:
            val = float(default)
        return val

    def _get_move_magnitude(self, action: str, force: float,
                            amount: float) -> float:
        # Set the Move Magnitude to the appropriate amount based on the action
        move_magnitude = DEFAULT_MOVE
        if action in self.FORCE_ACTIONS:
            move_magnitude = force * self.MAX_FORCE
        elif action in self.OBJECT_MOVE_ACTIONS:
            move_magnitude = amount
        return move_magnitude

    def _get_teleport(self, **kwargs) -> Tuple:
        teleport_rotation = self._get_teleport_rotation(**kwargs)
        teleport_position = self._get_teleport_position(**kwargs)
        return (teleport_rotation, teleport_position)

    def _get_teleport_position(self, **kwargs) -> Optional[Dict]:
        '''Extract teleport xz position from kwargs if it exists.
        Otherwise, position will be None.
        '''
        teleport_pos_x_input = self._get_number(self.TELEPORT_X_POS, **kwargs)
        teleport_pos_z_input = self._get_number(self.TELEPORT_Z_POS, **kwargs)
        teleport_position = None
        if teleport_pos_x_input is not None and \
                teleport_pos_z_input is not None:
            teleport_position = {
                'x': teleport_pos_x_input,
                'z': teleport_pos_z_input}
        return teleport_position

    def _get_teleport_rotation(self, **kwargs) -> Optional[Dict]:
        '''Extract teleport rotation from kwargs if it exists.
        Otherwise, rotation will be None.
        '''
        teleport_rot_input = self._get_number(self.TELEPORT_Y_ROT, **kwargs)
        return {'y': teleport_rot_input} \
            if teleport_rot_input is not None else None

    def _validate_and_convert_params(self, **kwargs) -> Tuple:
        """Need a validation/conversion step for what ai2thor will accept as input
        to keep parameters more simple for the user (in this case, wrapping
        rotation degrees into an object)
        """
        action = kwargs.get('action')
        amount = self._get_amount(**kwargs)
        force = self._get_force(**kwargs)
        object_image_coords_x = int(self._get_number_with_default(
            self.OBJECT_IMAGE_COORDS_X_KEY, self.DEFAULT_IMG_COORD, **kwargs))
        object_image_coords_y = int(self._get_number_with_default(
                                    self.OBJECT_IMAGE_COORDS_Y_KEY,
                                    self.DEFAULT_IMG_COORD, **kwargs))
        receptable_image_coords_x = int(self._get_number_with_default(
            self.RECEPTACLE_IMAGE_COORDS_X_KEY,
            self.DEFAULT_IMG_COORD,
            **kwargs))
        receptacle_image_coords_y = int(self._get_number_with_default(
            self.RECEPTACLE_IMAGE_COORDS_Y_KEY,
            self.DEFAULT_IMG_COORD,
            **kwargs))
        # TODO Consider the current "head tilt" value while validating the
        # input "horizon" value.
        horizon = kwargs.get(self.HORIZON_KEY, self.DEFAULT_HORIZON)
        rotation = kwargs.get(self.ROTATION_KEY, self.DEFAULT_ROTATION)

        rotation_vector = {'y': rotation}
        object_vector = {
            'x': object_image_coords_x,
            'y': self._convert_y_image_coord_for_unity(
                object_image_coords_y),
        }

        receptacle_vector = {
            'x': receptable_image_coords_x,
            'y': self._convert_y_image_coord_for_unity(
                receptacle_image_coords_y)
        }
        move_magnitude = self._get_move_magnitude(action, force, amount)
        (teleport_rotation, teleport_position) = self._get_teleport(**kwargs)

        # TODO is this a feature we need?
        if self.config.is_noise_enabled():
            rotation = rotation * (1 + self._generate_noise())
            horizon = horizon * (1 + self._generate_noise())
            move_magnitude = move_magnitude * (1 + self._generate_noise())

        return action, dict(
            objectId=kwargs.get("objectId"),
            receptacleObjectId=kwargs.get("receptacleObjectId"),
            rotation=rotation_vector,
            horizon=horizon,
            teleportRotation=teleport_rotation,
            teleportPosition=teleport_position,
            moveMagnitude=move_magnitude,
            objectImageCoords=object_vector,
            receptacleObjectImageCoords=receptacle_vector
        )

    def _mcs_action_to_ai2thor_action(self, action: str) -> str:
        if action == Action.CLOSE_OBJECT.value:
            # The AI2-THOR Python library has buggy error checking
            # specifically for the CloseObject action,
            # so just use our own custom action here.
            return "MCSCloseObject"
        elif action == Action.DROP_OBJECT.value:
            return "DropHandObject"
        elif action == Action.OPEN_OBJECT.value:
            # The AI2-THOR Python library has buggy error checking
            # specifically for the OpenObject action,
            # so just use our own custom action here.
            return "MCSOpenObject"

        return action

    def _generate_noise(self) -> float:
        """
        Returns a random value between -0.05 and 0.05 used to add noise to all
        numerical action parameters noise_enabled is True.
        Returns
        -------
        float
            A value between -0.05 and 0.05 (using random.uniform).
        """

        return random.uniform(self.MIN_NOISE, self.MAX_NOISE)
