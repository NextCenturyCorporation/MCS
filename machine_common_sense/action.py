from enum import Enum, unique
from typing import Tuple

import typeguard


@unique
class Action(Enum):
    """
    The actions available in the MCS simulation environment.

    For actions requiring objectImageCoords or receptacleObjectImageCoords,
    note that (0,0) represents the top left corner of the viewport, and that
    inputs must be greater than (0,0).
    """

    INITIALIZE = (
        "Initialize",
        "0",
        "Initialization"
    )
    """
    Initialize the scene. Intended only for internal use.
    """

    CLOSE_OBJECT = (
        "CloseObject",
        "1",
        "Close a nearby object. (objectId=string, amount=float "
        "(default:1), objectImageCoordsX=float, objectImageCoordsY=float)"
    )
    """
    Close a nearby object.

    Parameters
    ----------
    objectId : string, optional
        The "uuid" of the target object. Required unless the
        "objectImageCoords" properties are given.
    objectImageCoordsX : float, optional
        The X of a pixel coordinate on the target object based on
        your current viewport. Can be used in place of the "objectId" property.
        (See note under "Action" header regarding image coordinates.)
    objectImageCoordsY : float, optional
        The Y of a pixel coordinate on the target object based on
        your current viewport. Can be used in place of the "objectId" property.
        (See note under "Action" header regarding image coordinates.)
    amount : float
        The amount to close the object between 0 (completely opened) and 1
        (completely closed). Default: 1

    Returns
    -------
    "SUCCESSFUL"
        Action successful.
    "IS_CLOSED_COMPLETELY"
        If the object is completely closed.
    "NOT_INTERACTABLE"
        If the object corresponding to the "objectImageCoords" vector is not an
        interactable object. This includes structural objects like the room's
        walls.
    "NOT_OBJECT"
        If the object corresponding to the "objectId" (or object corresponding
        to the "objectImageCoords" vector) is not an object.
    "NOT_OPENABLE"
        If the object itself cannot be closed.
    "NOT_RECEPTACLE"
        If the object corresponding to the "objectImageCoords" vector is not a
        receptacle object.
    "OBSTRUCTED"
        If you cannot close the object because your path is obstructed.
    "OUT_OF_REACH"
        If you cannot close the object because you are out of reach.
    "FAILED"
        Unexpected error; please report immediately to development team.
    """

    DROP_OBJECT = (
        "DropObject",
        "2",
        "Drop an object you are holding. (objectId=string)"
    )
    """
    Drop an object you are holding.

    Parameters
    ----------
    objectId : string, optional
        The "uuid" of the held object. Defaults to the first held object.

    Returns
    -------
    "SUCCESSFUL"
        Action successful.
    "NOT_HELD"
        If you cannot put down the object corresponding to the "objectId"
        because you are not holding it.
    "NOT_OBJECT"
        If the object corresponding to the "objectId" is not an object.
    "FAILED"
        Unexpected error; please report immediately to development team.
    """

    MOVE_AHEAD = (
        "MoveAhead",
        "w",
        "Move yourself ahead based on your current view."
    )
    """
    Move yourself forward based on your current viewport.


    Returns
    -------
    "SUCCESSFUL"
        Action successful.
    "OBSTRUCTED"
        If you cannot move forward because your path is obstructed.
    "FAILED"
        Unexpected error; please report immediately to development team.
    """

    MOVE_BACK = (
        "MoveBack",
        "s",
        "Move yourself back based on your current view."
    )
    """
    Move yourself backward based on your current viewport.

    Returns
    -------
    "SUCCESSFUL"
        Action successful.
    "OBSTRUCTED"
        If you cannot move backward because your path is obstructed.
    "FAILED"
        Unexpected error; please report immediately to development team.
    """

    MOVE_LEFT = (
        "MoveLeft",
        "a",
        "Move yourself to your left based on your current view."
    )
    """
    Move yourself left based on your current viewport.

    Returns
    -------
    "SUCCESSFUL"
        Action successful.
    "OBSTRUCTED"
        If you cannot move left because your path is obstructed.
    "FAILED"
        Unexpected error; please report immediately to development team.
    """

    MOVE_RIGHT = (
        "MoveRight",
        "d",
        "Move yourself to your right based on your current view."
    )
    """
    Move yourself right based on your current viewport.

    Returns
    -------
    "SUCCESSFUL"
        Action successful.
    "OBSTRUCTED"
        If you cannot move right because your path is obstructed.
    "FAILED"
        Unexpected error; please report immediately to development team.
    """

    OPEN_OBJECT = (
        "OpenObject",
        "3",
        "Open a nearby object. (objectId=string, "
        "amount=float (default:1), objectImageCoordsX=float, "
        "objectImageCoordsY=float)"
    )
    """
    Open a nearby object.

    Parameters
    ----------
    objectId : string, optional
        The "uuid" of the target object. Required unless the
        "objectImageCoords" properties are given.
    objectImageCoordsX : float, optional
        The X of a pixel coordinate on the target object based on
        your current viewport. Can be used in place of the "objectId" property.
        (See note under "Action" header regarding image coordinates.)
    objectImageCoordsY : float, optional
        The Y of a pixel coordinate on the target object based on
        your current viewport. Can be used in place of the "objectId" property.
        (See note under "Action" header regarding image coordinates.)
    amount : float
        The amount to open the object between 0 (completely closed) and 1
        (completely opened). Default: 1

    Returns
    -------
    "SUCCESSFUL"
        Action successful.
    "IS_OPENED_COMPLETELY"
        If the object is completely opened.
    "NOT_INTERACTABLE"
        If the object corresponding to the "objectImageCoords" vector is not an
        interactable object. This includes structural objects like the room's
        walls.
    "NOT_OBJECT"
        If the object corresponding to the "objectId" (or object corresponding
        to the "objectImageCoords" vector) is not an object.
    "NOT_OPENABLE"
        If the object itself cannot be opened.
    "NOT_RECEPTACLE"
        If the object corresponding to the "objectImageCoords" vector is not a
        receptacle object.
    "OBSTRUCTED"
        If you cannot open the object because your path is obstructed.
    "OUT_OF_REACH"
        If you cannot open the object because you are out of reach.
    "FAILED"
        Unexpected error; please report immediately to development team.
    """

    PICKUP_OBJECT = (
        "PickupObject",
        "4",
        "Pickup a nearby object and hold it in your hand. "
        "(objectId=string, objectImageCoordsX=float, objectImageCoordsY=float)"
    )
    """
    Pick up a nearby object and hold it in your hand. This action incorporates
    reaching out your hand in front of you, opening your fingers, and grabbing
    the object.

    Parameters
    ----------
    objectId : string, optional
        The "uuid" of the target object. Required unless the
        "objectImageCoords" properties are given.
    objectImageCoordsX : float, optional
        The X of a pixel coordinate on the target object based on
        your current viewport. Can be used in place of the "objectId" property.
        (See note under "Action" header regarding image coordinates.)
    objectImageCoordsY : float, optional
        The Y of a pixel coordinate on the target object based on
        your current viewport. Can be used in place of the "objectId" property.
        (See note under "Action" header regarding image coordinates.)

    Returns
    -------
    "SUCCESSFUL"
        Action successful.
    "HAND_IS_FULL"
        If you cannot pick up the object because your hand is full.
    "NOT_INTERACTABLE"
        If the object corresponding to the "objectImageCoords" vector is not an
        interactable object.
    "NOT_OBJECT"
        If the object corresponding to the "objectId" (or object corresponding
        to the "objectImageCoords" vector) is not an object.
    "NOT_PICKUPABLE"
        If the object itself cannot be picked up.
    "OBSTRUCTED"
        If you cannot pick up the object because your path is obstructed.
    "OUT_OF_REACH"
        If you cannot pick up the object because you are out of reach.
    "FAILED"
        Unexpected error; please report immediately to development team.
    """

    PULL_OBJECT = (
        "PullObject",
        "5",
        "Pull a nearby object. (objectId=string, force=float (default:0.5), "
        "objectImageCoordsX=float, objectImageCoordsY=float)"
    )
    """
    Pull a nearby object by applying a physical force directly toward you on
    the X/Z axis to the center point of the object.

    Parameters
    ----------
    objectId : string, optional
        The "uuid" of the target object. Required unless the
        "objectImageCoords" properties are given.
    objectImageCoordsX : float, optional
        The X of a pixel coordinate on the target object based on
        your current viewport. Can be used in place of the "objectId" property.
        (See note under "Action" header regarding image coordinates.)
    objectImageCoordsY : float, optional
        The Y of a pixel coordinate on the target object based on
        your current viewport. Can be used in place of the "objectId" property.
        (See note under "Action" header regarding image coordinates.)
    force : float
        The amount of force, from 0 to 1, used to move the target object.
        Default: 0.5

    Returns
    -------
    "SUCCESSFUL"
        Action successful.
    "NOT_INTERACTABLE"
        If the object corresponding to the "objectImageCoords" vector is not an
        interactable object.
    "NOT_OBJECT"
        If the object corresponding to the "objectId" (or object corresponding
        to the "objectImageCoords" vector) is not an object.
    "NOT_MOVEABLE"
        If the object itself cannot be moved by a baby.
    "OBSTRUCTED"
        If you cannot move the object because your path is obstructed.
    "OUT_OF_REACH"
        If you cannot move the object because you are out of reach.
    "FAILED"
        Unexpected error; please report immediately to development team.
    """

    PUSH_OBJECT = (
        "PushObject",
        "6",
        "Push a nearby object. (objectId=string, force=float (default:0.5), "
        "objectImageCoordsX=float, objectImageCoordsY=float)"
    )
    """
    Push a nearby object by applying a physical force directly away from you on
    the X/Z axis to the center point of the object.

    Parameters
    ----------
    objectId : string, optional
        The "uuid" of the target object. Required unless the
        "objectImageCoords" properties are given.
    objectImageCoordsX : float, optional
        The X of a pixel coordinate on the target object based on
        your current viewport. Can be used in place of the "objectId" property.
        (See note under "Action" header regarding image coordinates.)
    objectImageCoordsY : float, optional
        The Y of a pixel coordinate on the target object based on
        your current viewport. Can be used in place of the "objectId" property.
        (See note under "Action" header regarding image coordinates.)
    force : float
        The amount of force, from 0 to 1, used to move the target object.
        Default: 0.5

    Returns
    -------
    "SUCCESSFUL"
        Action successful.
    "NOT_INTERACTABLE"
        If the object corresponding to the "objectImageCoords" vector is not an
        interactable object.
    "NOT_OBJECT"
        If the object corresponding to the "objectId" (or object corresponding
        to the "objectImageCoords" vector) is not an object.
    "NOT_MOVEABLE"
        If the object itself cannot be moved by a baby.
    "OBSTRUCTED"
        If you cannot move the object because your path is obstructed.
    "OUT_OF_REACH"
        If you cannot move the object because you are out of reach.
    "FAILED"
        Unexpected error; please report immediately to development team.
    """

    PUT_OBJECT = (
        "PutObject",
        "7",
        "Place an object you are holding into/onto a nearby "
        "receptacle object. (objectId=string, receptacleObjectId=string, "
        "receptacleObjectImageCoordsX=float, "
        "receptacleObjectImageCoordsY=float)"
    )
    """
    Put down an object you are holding into/onto a nearby receptacle object. A
    receptacle is an object that can hold other objects, like a block, box,
    drawer, shelf, or table.

    Parameters
    ----------
    objectId : string, optional
        The "uuid" of the held object. Defaults to the first held object.
    receptacleObjectId : string, optional
        The "uuid" of the target receptacle. Required unless the
        "receptacleObjectImageCoords" properties are given.
    receptacleObjectImageCoordsX : float, optional
        The X of a pixel coordinate on the target receptacle based
        on your current viewport. Can be used in place of the
        "receptacleObjectId" property.
        (See note under "Action" header regarding image coordinates.)
    receptacleObjectImageCoordsY : float, optional
        The Y of a pixel coordinate on the target receptacle based
        on your current viewport. Can be used in place of the
        "receptacleObjectId" property.
        (See note under "Action" header regarding image coordinates.)

    Returns
    -------
    "SUCCESSFUL"
        Action successful.
    "NOT_HELD"
        If you cannot put down the object corresponding to the "objectId"
        because you are not holding it.
    "NOT_INTERACTABLE"
        If the object corresponding to the "objectImageCoords" or
        "receptacleObjectImageCoords" vector is not an interactable object.
        This includes structural objects like the room's walls.
    "NOT_OBJECT"
        If the object corresponding to the "objectId" and/or
        "receptacleObjectId" (or object corresponding to the
        "receptacleObjectImageCoords" vector) is not an object.
    "NOT_RECEPTACLE"
        If the object corresponding to the "receptacleObjectId" (or object
        corresponding to the "receptacleObjectImageCoords" vector) is not a
        receptacle.
    "OBSTRUCTED"
        If you cannot put down the object because your path is obstructed.
    "OUT_OF_REACH"
        If you cannot put down the object because you are out of reach.
    "FAILED"
        Unexpected error; please report immediately to development team.
    """

    TORQUE_OBJECT = (
        "TorqueObject",
        "8",
        "Apply torque to a nearby object. (objectId=string, "
        "force=float(default:0.5), objectImageCoordsX=float, "
        "objectImageCoordsY=float)"
    )
    """
    Apply torque to a nearby object.

    Parameters
    ----------
    objectId : string, optional
        The "uuid" of the target object. Required unless the
        "objectImageCoords" properties are given.
    objectImageCoordsX : float, optional
        The X of a pixel coordinate on the target object based on
        your current viewport. Can be used in place of the "objectId" property.
        (See note under "Action" header regarding image coordinates.)
    objectImageCoordsY : float, optional
        The Y of a pixel coordinate on the target object based on
        your current viewport. Can be used in place of the "objectId" property.
        (See note under "Action" header regarding image coordinates.)
    force : float
        The amount of force, from -1 to 1, used to move the target object.
        Default: 0.5

    Returns
    -------
    "SUCCESSFUL"
        Action successful.
    "NOT_INTERACTABLE"
        If the object corresponding to the "objectImageCoords" vector is not an
        interactable object.
    "NOT_OBJECT"
        If the object corresponding to the "objectId" (or object corresponding
        to the "objectImageCoords" vector) is not an object.
    "NOT_MOVEABLE"
        If the object itself cannot be moved by a baby.
    "OBSTRUCTED"
        If you cannot move the object because your path is obstructed.
    "OUT_OF_REACH"
        If you cannot move the object because you are out of reach.
    "FAILED"
        Unexpected error; please report immediately to development team.
    """

    ROTATE_OBJECT = (
        "RotateObject",
        "9",
        "Apply a rotation of 5 degrees to a nearby object. "
        "(objectId=string, "
        "clockwise=bool(default:True), objectImageCoordsX=float, "
        "objectImageCoordsY=float)"
    )
    """
    Apply a rotation of 5 degrees to a nearby object.

    Parameters
    ----------
    objectId : string, optional
        The "uuid" of the target object. Required unless the
        "objectImageCoords" properties are given.
    objectImageCoordsX : float, optional
        The X of a pixel coordinate on the target object based on
        your current viewport. Can be used in place of the "objectId" property.
        (See note under "Action" header regarding image coordinates.)
    objectImageCoordsY : float, optional
        The Y of a pixel coordinate on the target object based on
        your current viewport. Can be used in place of the "objectId" property.
        (See note under "Action" header regarding image coordinates.)
    clockwise : bool
        If the rotation should be clockwise.
        Default: True

    Returns
    -------
    "SUCCESSFUL"
        Action successful.
    "NOT_INTERACTABLE"
        If the object corresponding to the "objectImageCoords" vector is not an
        interactable object.
    "NOT_OBJECT"
        If the object corresponding to the "objectId" (or object corresponding
        to the "objectImageCoords" vector) is not an object.
    "NOT_MOVEABLE"
        If the object itself cannot be moved by a baby.
    "OBSTRUCTED"
        If you cannot move the object because your path is obstructed.
    "OUT_OF_REACH"
        If you cannot move the object because you are out of reach.
    "FAILED"
        Unexpected error; please report immediately to development team.
    """

    MOVE_OBJECT = (
        "MoveObject",
        "0",
        "Apply a movement of 0.1 meters to a nearby object. "
        "(objectId=string, "
        "lateral=int(default:0), "
        "straight=int(default:1), "
        "objectImageCoordsX=float, "
        "objectImageCoordsY=float)"
    )
    """
    Apply a movement of 0.1 meters units to a nearby object.

    Parameters
    ----------
    objectId : string, optional
        The "uuid" of the target object. Required unless the
        "objectImageCoords" properties are given.
    objectImageCoordsX : float, optional
        The X of a pixel coordinate on the target object based on
        your current viewport. Can be used in place of the "objectId" property.
        (See note under "Action" header regarding image coordinates.)
    objectImageCoordsY : float, optional
        The Y of a pixel coordinate on the target object based on
        your current viewport. Can be used in place of the "objectId" property.
        (See note under "Action" header regarding image coordinates.)
    lateral : int
        The x axis direction of movement on the object relative to the agent.
        Can be -1, 0, 1. If only lateral is given,
        straight will default to 0
        Default: 0
    straight : int
        The x axis direction of movement on the object relative to the agent.
        Can be -1, 0, 1. If only straight is given,
        lateral will default to 0
        Default: 1

    Returns
    -------
    "SUCCESSFUL"
        Action successful.
    "NOT_INTERACTABLE"
        If the object corresponding to the "objectImageCoords" vector is not an
        interactable object.
    "NOT_OBJECT"
        If the object corresponding to the "objectId" (or object corresponding
        to the "objectImageCoords" vector) is not an object.
    "NOT_MOVEABLE"
        If the object itself cannot be moved by a baby.
    "OBSTRUCTED"
        If you cannot move the object because your path is obstructed.
    "OUT_OF_REACH"
        If you cannot move the object because you are out of reach.
    "FAILED"
        Unexpected error; please report immediately to development team.
    """

    INTERACT_WITH_AGENT = (
        "InteractWithAgent",
        "T",
        "Interact with an agent. If that agent has an object, "
        "it will hold out the object for you to pickup; "
        "otherwise, the agent will look sad."
        "(objectId=string, "
        "objectImageCoordsX=float, "
        "objectImageCoordsY=float)"
    )
    """
    Interact with an agent. If that agent has an object, it will hold
    out the object for you to pickup; otherwise, the agent will look sad.

    Parameters
    ----------
    objectId : string, optional
        The "uuid" of the target object. Required unless the
        "objectImageCoords" properties are given.
    objectImageCoordsX : float, optional
        The X of a pixel coordinate on the target object based on
        your current viewport. Can be used in place of the "objectId" property.
        (See note under "Action" header regarding image coordinates.)
    objectImageCoordsY : float, optional
        The Y of a pixel coordinate on the target object based on
        your current viewport. Can be used in place of the "objectId" property.
        (See note under "Action" header regarding image coordinates.)

    Returns
    -------
    "SUCCESSFUL"
        Action successful.
    "NOT_INTERACTABLE"
        If the object corresponding to the "objectImageCoords" vector is not an
        interactable object.
    "NOT_OBJECT"
        If the object corresponding to the "objectId" (or object corresponding
        to the "objectImageCoords" vector) is not an object.
    "NOT_AGENT"
        If the object being interacted with is not a simulation agent
    "AGENT_CURRENTLY_INTERACTING_WTIH_PERFORMER"
        If the object being interacted with is a simulation agent already
        interacting with the performer
    "OBSTRUCTED"
        If you cannot move the object because your path is obstructed.
    "OUT_OF_REACH"
        If you cannot move the object because you are out of reach.
    "FAILED"
        Unexpected error; please report immediately to development team.
    """

    LOOK_UP = (
        "LookUp",
        "i",
        "Rotate your view up (subtract 10 degrees from head tilt)."
    )
    """
    Rotate your view up (subtract 10 degrees from head tilt).

    Returns
    -------
    "SUCCESSFUL"
        Action successful.
    "CANNOT_ROTATE"
        Failed because you cannot look down/up more than +/- 90 degrees.
    "FAILED"
        Unexpected error; please report immediately to development team.
    """

    LOOK_DOWN = (
        "LookDown",
        "k",
        "Rotate your view down (add 10 degrees to head tilt)."
    )
    """
    Rotate your viewport down (add 10 degrees to head tilt).

    Returns
    -------
    "SUCCESSFUL"
        Action successful.
    "CANNOT_ROTATE"
        Failed because you cannot look down/up more than +/- 90 degrees.
    "FAILED"
        Unexpected error; please report immediately to development team.
    """

    ROTATE_LEFT = (
        "RotateLeft",
        "j",
        "Rotate your view left by 10 degrees."
    )
    """
    Rotate your viewport left by 10 degrees.

    Returns
    -------
    "SUCCESSFUL"
        Action successful.
    "FAILED"
        Unexpected error; please report immediately to development team.
    """

    ROTATE_RIGHT = (
        "RotateRight",
        "l",
        "Rotate your view right by 10 degrees."
    )
    """
    Rotate your viewport right by 10 degrees.

    Returns
    -------
    "SUCCESSFUL"
        Action successful.
    "FAILED"
        Unexpected error; please report immediately to development team.
    """

    END_HABITUATION = (
        "EndHabituation",
        "h",
        "Ends a habituation trial for the scene by blanking the screen "
        "for one action (and teleporting the agent if needed). Sometimes"
        " needed depending on the task type."
    )
    """
    Ends a habituation trial for the scene by blanking the screen for one
    action (and teleporting the agent if needed). Sometimes needed depending
    on the task type.

    Note that we currently plan to use the starting position/rotation as
    teleport parameters here for applicable cases. We cannot currently
    guarantee that using a position intersecting another object or outside
    the room won't cause issues or errors.

    Returns
    -------
    "SUCCESSFUL"
        Action successful.
    "FAILED"
        Unexpected error; please report immediately to development team.
    """

    # Pass should always be the last action in the enum.
    END_SCENE = (
        "EndScene",
        " ",
        "There is no action available and end_scene needs to be called."
    )
    """
    Call end_scene now there is no actions available.
    Does nothing.

    Returns
    -------
    "SUCCESSFUL"
        Action successful.
    "FAILED"
        Unexpected error; please report immediately to development team.
    """

    # Pass should always be the last action in the enum.
    PASS = (
        "Pass",
        " ",
        "Do nothing. (no params)"
    )
    """
    Do nothing.

    Returns
    -------
    "SUCCESSFUL"
        Action successful.
    "FAILED"
        Unexpected error; please report immediately to development team.
    """

    def __new__(cls, action, key, desc):
        obj = object.__new__(cls)
        obj._value_ = action
        obj._key = key
        obj._desc = desc
        # The following line is to get enum name from more than one value:
        # https://stackoverflow.com/a/43210118/6997391
        cls._value2member_map_[key] = obj
        return obj

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}.{self._name_}: "
            f"{', '.join([self._value_, self._key, self._desc])}>")

    @property
    def key(self):
        return self._key

    @property
    def desc(self):
        return self._desc

    @staticmethod
    @typeguard.typechecked
    def input_to_action_and_params(input_str: str) -> Tuple:
        """
        Transforms the given input string into an action string
        and parameter dict.

        Parameters
        ----------
        input_value : string
            The input value.

        Returns
        -------
        string
            The action string, or None if the given input had an error
            transforming the action string.
        dict
            The parameter dict, or None if the given input had an error
            transforming parameters.
        """
        input_split = input_str.split(',')
        action = input_split[0]

        try:
            _ = Action(action).name
        except BaseException:
            return None, {}

        if len(input_split) < 2:
            return action, {}

        params = {}

        try:
            for param in input_split[1:]:
                param_key, param_value = param.split('=')
                params[param_key.strip()] = param_value.strip()

                try:
                    params[param_key.strip()] = float(param_value.strip())
                except ValueError:
                    pass

        except BaseException:
            return action, None

        return action, params


FORCE_ACTIONS = [
    Action.PUSH_OBJECT,
    Action.PULL_OBJECT,
    Action.TORQUE_OBJECT]
OBJECT_MOVE_ACTIONS = [
    Action.CLOSE_OBJECT,
    Action.OPEN_OBJECT]
MOVE_ACTIONS = [
    Action.MOVE_AHEAD,
    Action.MOVE_LEFT,
    Action.MOVE_RIGHT,
    Action.MOVE_BACK]
OBJECT_IMAGE_ACTIONS = [
    Action.CLOSE_OBJECT,
    Action.OPEN_OBJECT,
    Action.PICKUP_OBJECT,
    Action.PUSH_OBJECT,
    Action.PULL_OBJECT,
    Action.TORQUE_OBJECT,
    Action.ROTATE_OBJECT,
    Action.INTERACT_WITH_AGENT,
    Action.MOVE_OBJECT]
RECEPTACLE_ACTIONS = [
    Action.PUT_OBJECT]
