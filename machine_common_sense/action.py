from enum import Enum, unique


@unique
class Action(Enum):
    """
    The actions available in the MCS simulation environment.

    For actions requiring objectImageCoords or receptacleObjectImageCoords,
    note that (0,0) represents the top left corner of the viewport, and that
    inputs must be greater than (0,0).
    """

    CLOSE_OBJECT = (
        "CloseObject",
        "1",
        "Close a nearby object. (objectId=string, amount=float " +
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
        interactable object.
    "NOT_OBJECT"
        If the object corresponding to the "objectId" (or object corresponding
        to the "objectImageCoords" vector) is not an object.
    "NOT_OPENABLE"
        If the object itself cannot be closed.
    "OBSTRUCTED"
        If you cannot close the object because your path is obstructed.
    "OUT_OF_REACH"
        If you cannot close the object because you are out of reach.
    "FAILED"
        Unexpected error; please report immediately to development team.
    """

    CRAWL = (
        "Crawl",
        "c",
        "Change pose to 'CRAWLING' (no params)"
    )
    """
    Change pose to "CRAWLING". Can help you move underneath or over objects.

    Returns
    -------
    "SUCCESSFUL"
        Action successful.
    "OBSTRUCTED"
        If you cannot enter the pose because the path above you is obstructed.
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

    LIE_DOWN = (
        "LieDown",
        "x",
        "Change pose to 'LYING' (rotation=float)"
    )
    """
    Change pose to "LYING". Can help you move underneath objects.

    Returns
    -------
    "SUCCESSFUL"
        Action successful.
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
        "Open a nearby object. (objectId=string, " +
        "amount=float (default:1), objectImageCoordsX=float, " +
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
        interactable object.
    "NOT_OBJECT"
        If the object corresponding to the "objectId" (or object corresponding
        to the "objectImageCoords" vector) is not an object.
    "NOT_OPENABLE"
        If the object itself cannot be opened.
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
        "Pickup a nearby object and hold it in your hand. " +
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
        "Pull a nearby object. (objectId=string, rotation=float, " +
        "horizon=float, force=float (default:0.5), " +
        "objectImageCoordsX=float, objectImageCoordsY=float)"
    )
    """
    Pull a nearby object.

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
    "NOT_PICKUPABLE"
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
        "Push a nearby object. (objectId=string, rotation=float, " +
        "horizon=float, force=float (default:0.5), " +
        "objectImageCoordsX=float, objectImageCoordsY=float)"
    )
    """
    Push a nearby object.

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
    "NOT_PICKUPABLE"
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
        "Place an object you are holding into/onto a nearby " +
        "receptacle object. (objectId=string, receptacleObjectId=string, " +
        "receptacleObjectImageCoordsX=float, " +
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

    LOOK_UP = (
        "LookUp",
        "i",
        "Rotate your view up by 10 degrees."
    )
    """
    Rotate your view up by 10 degrees.

    Returns
    -------
    "SUCCESSFUL"
        Action successful.
    "FAILED"
        Unexpected error; please report immediately to development team.
    """

    LOOK_DOWN = (
        "LookDown",
        "k",
        "Rotate your view down by 10 degrees."
    )
    """
    Rotate your viewport down by 10 degrees.

    Returns
    -------
    "SUCCESSFUL"
        Action successful.
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

    STAND = (
        "Stand",
        "u",
        "Change pose to 'STANDING' (no params)"
    )
    """
    Change pose to "STANDING". Can help you move over objects.

    Returns
    -------
    "SUCCESSFUL"
        Action successful.
    "OBSTRUCTED"
        If you cannot enter the pose because the path above you is obstructed.
    "FAILED"
        Unexpected error; please report immediately to development team.
    """

    THROW_OBJECT = (
        "ThrowObject",
        "q",
        "Throw an object you are holding. (objectId=string, " +
        "objectImageCoordsX=float, objectImageCoordsY=float, " +
        "force=float (default:0.5))"
    )
    """
    Throw an object you are holding.

    Parameters
    ----------
    objectId : string, optional
        The "uuid" of the held object. Defaults to the first held object.
    objectImageCoordsX : float, optional
        The X of a pixel coordinate on where you would like to
        throw the object based on your current viewport.
        (See note under "Action" header regarding image coordinates.)
    objectImageCoordsY : float, optional
        The Y of a pixel coordinate on where you would like to
        throw the object based on your current viewport.
        (See note under "Action" header regarding image coordinates.)

    Returns
    -------
    "SUCCESSFUL"
        Action successful.
    "NOT_HELD"
        If you cannot throw the object corresponding to the "objectId"
        because you are not holding it.
    "NOT_OBJECT"
        If the object corresponding to the "objectId" is not an object.
    "FAILED"
        Unexpected error; please report immediately to development team.
    """

    END_HABITUATION = (
        "EndHabituation",
        "h",
        "Ends a habituation trial for the scene by blanking the screen for" +
        "for one action. Sometimes needed for the passive tasks."
    )
    """
    Ends a habituation trial for the scene by blanking the screen for one
    action. Sometimes needed for the passive tasks.

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
        return '<%s.%s: %s>' % (
            self.__class__.__name__,
            self._name_,
            ', '.join([self._value_, self._key, self._desc])
        )

    @ property
    def key(self):
        return self._key

    @ property
    def desc(self):
        return self._desc
