import random
import string
from typing import Any, Dict, List, Optional, Tuple

from .action import (FORCE_ACTIONS, OBJECT_IMAGE_ACTIONS, OBJECT_MOVE_ACTIONS,
                     RECEPTACLE_ACTIONS, Action)
from .config_manager import ConfigManager, MetadataTier
from .controller import DEFAULT_MOVE


def compare_param_values(value_1: Any, value_2: Any) -> bool:
    """Compares two parameter values and returns if they are equal,
    making sure that string numbers are converted to floats, and integer
    floats are converted to ints."""
    data = {'value_1': value_1, 'value_2': value_2}
    for key, value in data.items():
        if isinstance(value, str):
            try:
                data[key] = float(value)
            except ValueError:
                ...
        if isinstance(value, float) and value.is_integer():
            data[key] = int(value)
    return data['value_1'] == data['value_2']


def rebuild_endhabituation(step_action_list: List) -> str:
    '''Rebuilds EndHabituation parameters from the goal's action list for the
    current step. Parameters can include some or all of xPosition, zPosition,
    and yRotation. Parameters are removed from the step_metadata list of
    potentital actions in order for teleportation/displacement to be hidden
    from AIs.
    '''
    # sourcery skip: use-named-expression
    action = Action.END_HABITUATION.value
    endhabituation_action = next((
        item for item in step_action_list
        if item[0] == action), None)
    if endhabituation_action is not None:
        params = ",".join(
            f"{k}={v}" for k,
            v in endhabituation_action[1].items())
        if params:
            action = f"{action},{params}"
    return action


class Parameter:

    # AI2-THOR creates a square grid across the scene that is
    # uses for "snap-to-grid" movement. (This value may not
    # really matter because we set continuous to True in
    # the step input.)
    GRID_SIZE = 0.1

    DEFAULT_HORIZON = 0.0
    DEFAULT_ROTATION = 0.0
    DEFAULT_AMOUNT = 0.5
    DEFAULT_IMG_COORD = None
    DEFAULT_IMG_DICT = {'x': 0, 'y': 0}
    DEFAULT_OBJECT_MOVE_AMOUNT = 1.0
    DEFAULT_OBJECT_ROTATION_CLOCKWISE = True
    DEFAULT_OBJECT_MOVEMENT_X_DIRECTION = 0
    DEFAULT_OBJECT_MOVEMENT_Z_DIRECTION = 1

    MAX_AMOUNT_TORQUE = 1.0
    MIN_AMOUNT_TORQUE = -1.0
    MAX_AMOUNT = 1.0
    MIN_AMOUNT = 0.0
    MIN_AMOUNT_MOVEMENT_DIRECTION = -1
    MAX_AMOUNT_MOVEMENT_DIRECTION = 1

    MIN_NOISE = -0.5
    MAX_NOISE = 0.5

    ROTATION_KEY = 'rotation'
    HORIZON_KEY = 'horizon'
    FORCE_KEY = 'force'
    AMOUNT_KEY = 'amount'
    CLOCKWISE_KEY = 'clockwise'
    MOVEMENT_X_DIRECTION_KEY = 'lateral'
    MOVEMENT_Z_DIRECTION_KEY = 'straight'

    OBJECT_IMAGE_COORDS_X_KEY = 'objectImageCoordsX'
    OBJECT_IMAGE_COORDS_Y_KEY = 'objectImageCoordsY'
    RECEPTACLE_IMAGE_COORDS_X_KEY = 'receptacleObjectImageCoordsX'
    RECEPTACLE_IMAGE_COORDS_Y_KEY = 'receptacleObjectImageCoordsY'

    # used for EndHabituation teleport
    TELEPORT_X_POS = 'xPosition'
    TELEPORT_Z_POS = 'zPosition'
    TELEPORT_Y_ROT = 'yRotation'

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

    def _get_amount(self, action: Action, **kwargs) -> float:
        amount = kwargs.get(
            self.AMOUNT_KEY,
            self.DEFAULT_OBJECT_MOVE_AMOUNT
            if action in OBJECT_MOVE_ACTIONS
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

    def _get_force(self, action: Action, **kwargs) -> float:
        force = kwargs.get(self.FORCE_KEY, self.DEFAULT_AMOUNT)
        if force is not None:
            try:
                force = float(force)
            except ValueError as err:
                raise ValueError('Force is not a number') from err

            if action == Action.TORQUE_OBJECT:
                if (force < self.MIN_AMOUNT_TORQUE or force >
                        self.MAX_AMOUNT_TORQUE):
                    raise ValueError(
                        f'Force not in acceptable range of '
                        f'({self.MIN_AMOUNT_TORQUE} and '
                        f'{self.MAX_AMOUNT_TORQUE})')

            elif force < self.MIN_AMOUNT or force > self.MAX_AMOUNT:
                raise ValueError(
                    f'Force not in acceptable range of '
                    f'({self.MIN_AMOUNT} and {self.MAX_AMOUNT})')
        else:
            force = self.DEFAULT_AMOUNT
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
        elif default is not None:
            val = float(default)
        return val

    def _get_clockwise(self, **kwargs) -> bool:
        direction_clockwise = kwargs.get(
            self.CLOCKWISE_KEY,
            self.DEFAULT_OBJECT_ROTATION_CLOCKWISE
        )
        if isinstance(direction_clockwise, str):
            direction_clockwise = direction_clockwise.capitalize()
            try:
                direction_clockwise = eval(direction_clockwise)
            except Exception as err:
                raise ValueError(
                    f"{direction_clockwise} is not a bool") from err
        elif not isinstance(direction_clockwise, bool):
            raise ValueError(
                f"{direction_clockwise} is not a bool")
        return direction_clockwise

    def _get_movement_direction(self, **kwargs) -> Tuple:
        """
        If no args are given, the default movement for (x,z) is (0,1)
        If only x arg is given, movement is (x,0)
        If only z arg is given, movement is (0,z)
        If x,z args are given, movement is (x,z)
        """

        lateral = kwargs.get(
            self.MOVEMENT_X_DIRECTION_KEY
        )
        straight = kwargs.get(
            self.MOVEMENT_Z_DIRECTION_KEY
        )
        l_none = lateral is None
        s_none = straight is None

        if l_none and s_none:
            lateral = self.DEFAULT_OBJECT_MOVEMENT_X_DIRECTION
            straight = self.DEFAULT_OBJECT_MOVEMENT_Z_DIRECTION
            return (lateral, straight)

        direction_output = (
            f"{'(lateral: ' f'{lateral})' if not l_none else ''}"
            f"{'' if l_none else ' and ' if not s_none else ' is'}"
            f"{'(straight: ' f'{straight})' if not s_none else ''}"
            f"{' is' if l_none else ' are' if not s_none else ''}"
            f" not "
            f"{'both ints' if not l_none and not s_none else 'an int'}"
            f" of acceptable range "
            f"({self.MIN_AMOUNT_MOVEMENT_DIRECTION}"
            f" and {self.MAX_AMOUNT_MOVEMENT_DIRECTION})")

        if isinstance(lateral, bool) or isinstance(straight, bool):
            raise ValueError(direction_output)

        try:
            if not l_none:
                lateral = int(lateral) if float(
                    lateral).is_integer() else lateral
                if isinstance(lateral, float):
                    raise ValueError(direction_output)
            if not s_none:
                straight = int(straight) if float(
                    straight).is_integer() else straight
                if isinstance(straight, float):
                    raise ValueError(direction_output)
        except Exception as err:
            raise ValueError(direction_output) from err

        if not l_none and s_none:
            if (lateral < self.MIN_AMOUNT_MOVEMENT_DIRECTION or
                    lateral > self.MAX_AMOUNT_MOVEMENT_DIRECTION):
                raise ValueError(direction_output)
            else:
                straight = 0
        elif l_none:
            if (straight < self.MIN_AMOUNT_MOVEMENT_DIRECTION or
                    straight > self.MAX_AMOUNT_MOVEMENT_DIRECTION):
                raise ValueError(direction_output)
            else:
                lateral = 0
        elif (lateral < self.MIN_AMOUNT_MOVEMENT_DIRECTION or
              lateral > self.MAX_AMOUNT_MOVEMENT_DIRECTION or
              straight < self.MIN_AMOUNT_MOVEMENT_DIRECTION or
              straight > self.MAX_AMOUNT_MOVEMENT_DIRECTION):
            raise ValueError(direction_output)
        return (lateral, straight)

    def _get_move_magnitude(self, action: Action, force: float,
                            amount: float) -> float:
        # Set the Move Magnitude to the appropriate amount based on the action
        move_magnitude = DEFAULT_MOVE
        if action in FORCE_ACTIONS:
            move_magnitude = force * self.MAX_AMOUNT
        elif action in OBJECT_MOVE_ACTIONS:
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
        return {
            'x': teleport_pos_x_input,
            'z': teleport_pos_z_input} \
            if teleport_pos_x_input is not None and \
            teleport_pos_z_input is not None else None

    def _get_teleport_rotation(self, **kwargs) -> Optional[Dict]:
        '''Extract teleport rotation from kwargs if it exists.
        Otherwise, rotation will be None.
        '''
        teleport_rot_input = self._get_number(self.TELEPORT_Y_ROT, **kwargs)
        return {'y': teleport_rot_input} \
            if teleport_rot_input is not None else None

    def _get_vector(
            self,
            x_key: string,
            y_key: string,
            default_coord: int,
            object_id: string,
            **kwargs) -> Dict:
        image_coords_x = self._get_number_with_default(
            x_key, default_coord, **kwargs)
        image_coords_y = self._get_number_with_default(
            y_key, default_coord, **kwargs)

        # If the user passes no x or y parameter and no object Id,
        #   throw an error, else if an object id only is sent, pass
        #   the default values of 0,0 so Unity doesn't blow up.
        if (image_coords_x is None and image_coords_y is None and
                kwargs.get(object_id) is None):
            raise Exception('MCS Action Failed to provide coordinate value')
        elif (image_coords_x is None and image_coords_y is None and
                kwargs.get(object_id) is not None):
            return self.DEFAULT_IMG_DICT

        return {
            'x': int(image_coords_x),
            'y': self._convert_y_image_coord_for_unity(
                int(image_coords_y))
        }

    def _get_receptacle_vector(self, **kwargs) -> Dict:
        return self._get_vector(
            self.RECEPTACLE_IMAGE_COORDS_X_KEY,
            self.RECEPTACLE_IMAGE_COORDS_Y_KEY,
            self.DEFAULT_IMG_COORD,
            "receptacleObjectId",
            **kwargs
        )

    def _get_object_vector(self, **kwargs) -> Dict:
        return self._get_vector(
            self.OBJECT_IMAGE_COORDS_X_KEY,
            self.OBJECT_IMAGE_COORDS_Y_KEY,
            self.DEFAULT_IMG_COORD,
            "objectId",
            **kwargs
        )

    def _validate_and_convert_params(self, **kwargs) -> Tuple[Action, Dict]:
        """Need a validation/conversion step for what ai2thor will accept as input
        to keep parameters more simple for the user (in this case, wrapping
        rotation degrees into an object)
        """
        action = Action(kwargs.get('action'))
        kwargs.pop('action')
        amount = self._get_amount(action, **kwargs)
        force = self._get_force(action, **kwargs)

        # TODO Consider the current "head tilt" value while validating the
        # input "horizon" value.
        horizon = kwargs.get(self.HORIZON_KEY, self.DEFAULT_HORIZON)
        rotation = kwargs.get(self.ROTATION_KEY, self.DEFAULT_ROTATION)

        rotation_vector = {'y': rotation}

        # Need to return a default value, Unity fails if returning None, or
        #  x: None, y: None for both vectors below
        object_vector = self._get_object_vector(**kwargs) if (
            action in OBJECT_IMAGE_ACTIONS) else self.DEFAULT_IMG_DICT

        receptacle_vector = self._get_receptacle_vector(**kwargs) if (
            action in RECEPTACLE_ACTIONS) else self.DEFAULT_IMG_DICT

        move_magnitude = self._get_move_magnitude(action, force, amount)
        (teleport_rotation, teleport_position) = self._get_teleport(**kwargs)
        clockwise = self._get_clockwise(**kwargs)
        (lateral, straight) = self._get_movement_direction(**kwargs)

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
            receptacleObjectImageCoords=receptacle_vector,
            clockwise=clockwise,
            lateral=lateral,
            straight=straight
        )

    def _mcs_action_to_ai2thor_action(self, action: Action) -> str:
        if action == Action.CLOSE_OBJECT:
            # The AI2-THOR Python library has buggy error checking
            # specifically for the CloseObject action,
            # so just use our own custom action here.
            return "MCSCloseObject"
        elif action == Action.DROP_OBJECT:
            return "DropHandObject"
        elif action == Action.OPEN_OBJECT:
            # The AI2-THOR Python library has buggy error checking
            # specifically for the OpenObject action,
            # so just use our own custom action here.
            return "MCSOpenObject"

        return action.value

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
