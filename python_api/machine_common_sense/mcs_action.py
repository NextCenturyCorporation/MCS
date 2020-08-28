from enum import Enum, unique


@unique
class MCS_Action(Enum):
    """
    The actions available in the MCS simulation environment.
    """

    CLOSE_OBJECT = "CloseObject"
    """
    Close a nearby object.

    Parameters
    ----------
    objectId : string, optional
        The "uuid" of the target object. Required unless the "objectDirection"
        properties are given.
    objectDirectionX : float, optional
        The X of the directional vector pointing to the target object based on
        your current viewport. Can be used in place of the "objectId" property.
    objectDirectionY : float, optional
        The Y of the directional vector pointing to the target object based on
        your current viewport. Can be used in place of the "objectId" property.
    objectDirectionZ : float, optional
        The Z of the directional vector pointing to the target object based on
        your current viewport. Can be used in place of the "objectId" property.
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
        If the object corresponding to the "objectDirection" vector is not an
        interactable object.
    "NOT_OBJECT"
        If the object corresponding to the "objectId" (or object corresponding
        to the "objectDirection" vector) is not an object.
    "NOT_OPENABLE"
        If the object itself cannot be closed.
    "OBSTRUCTED"
        If you cannot close the object because your path is obstructed.
    "OUT_OF_REACH"
        If you cannot close the object because you are out of reach.
    "FAILED"
        Unexpected error; please report immediately to development team.
    """

    CRAWL = "Crawl"
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

    DROP_OBJECT = "DropObject"
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

    LIE_DOWN = "LieDown"
    """
    Change pose to "LYING". Can help you move underneath objects.

    Returns
    -------
    "SUCCESSFUL"
        Action successful.
    "FAILED"
        Unexpected error; please report immediately to development team.
    """

    MOVE_AHEAD = "MoveAhead"
    """
    Move yourself forward based on your current viewport.

    Parameters
    ----------
    amount : float
        Movement percentage between 0 (no distance) and 1 (maximum distance).
        (default 0.5)

    Returns
    -------
    "SUCCESSFUL"
        Action successful.
    "OBSTRUCTED"
        If you cannot move forward because your path is obstructed.
    "FAILED"
        Unexpected error; please report immediately to development team.
    """

    MOVE_BACK = "MoveBack"
    """
    Move yourself backward based on your current viewport.

    Parameters
    ----------
    amount : float
        Movement percentage between 0 (no distance) and 1 (maximum distance).
        (default 0.5)

    Returns
    -------
    "SUCCESSFUL"
        Action successful.
    "OBSTRUCTED"
        If you cannot move backward because your path is obstructed.
    "FAILED"
        Unexpected error; please report immediately to development team.
    """

    MOVE_LEFT = "MoveLeft"
    """
    Move yourself left based on your current viewport.

    Parameters
    ----------
    amount : float
        Movement percentage between 0 (no distance) and 1 (maximum distance).
        (default 0.5)

    Returns
    -------
    "SUCCESSFUL"
        Action successful.
    "OBSTRUCTED"
        If you cannot move left because your path is obstructed.
    "FAILED"
        Unexpected error; please report immediately to development team.
    """

    MOVE_RIGHT = "MoveRight"
    """
    Move yourself right based on your current viewport.

    Parameters
    ----------
    amount : float
        Movement percentage between 0 (no distance) and 1 (maximum distance).
        (default 0.5)

    Returns
    -------
    "SUCCESSFUL"
        Action successful.
    "OBSTRUCTED"
        If you cannot move right because your path is obstructed.
    "FAILED"
        Unexpected error; please report immediately to development team.
    """

    OPEN_OBJECT = "OpenObject"
    """
    Open a nearby object.

    Parameters
    ----------
    objectId : string, optional
        The "uuid" of the target object. Required unless the "objectDirection"
        properties are given.
    objectDirectionX : float, optional
        The X of the directional vector pointing to the target object based on
        your current viewport. Can be used in place of the "objectId" property.
    objectDirectionY : float, optional
        The Y of the directional vector pointing to the target object based on
        your current viewport. Can be used in place of the "objectId" property.
    objectDirectionZ : float, optional
        The Z of the directional vector pointing to the target object based on
        your current viewport. Can be used in place of the "objectId" property.
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
        If the object corresponding to the "objectDirection" vector is not an
        interactable object.
    "NOT_OBJECT"
        If the object corresponding to the "objectId" (or object corresponding
        to the "objectDirection" vector) is not an object.
    "NOT_OPENABLE"
        If the object itself cannot be opened.
    "OBSTRUCTED"
        If you cannot open the object because your path is obstructed.
    "OUT_OF_REACH"
        If you cannot open the object because you are out of reach.
    "FAILED"
        Unexpected error; please report immediately to development team.
    """

    PICKUP_OBJECT = "PickupObject"
    """
    Pick up a nearby object and hold it in your hand. This action incorporates
    reaching out your hand in front of you, opening your fingers, and grabbing
    the object.

    Parameters
    ----------
    objectId : string, optional
        The "uuid" of the target object. Required unless the "objectDirection"
        properties are given.
    objectDirectionX : float, optional
        The X of the directional vector pointing to the target object based on
        your current viewport. Can be used in place of the "objectId" property.
    objectDirectionY : float, optional
        The Y of the directional vector pointing to the target object based on
        your current viewport. Can be used in place of the "objectId" property.
    objectDirectionZ : float, optional
        The Z of the directional vector pointing to the target object based on
        your current viewport. Can be used in place of the "objectId" property.

    Returns
    -------
    "SUCCESSFUL"
        Action successful.
    "HAND_IS_FULL"
        If you cannot pick up the object because your hand is full.
    "NOT_INTERACTABLE"
        If the object corresponding to the "objectDirection" vector is not an
        interactable object.
    "NOT_OBJECT"
        If the object corresponding to the "objectId" (or object corresponding
        to the "objectDirection" vector) is not an object.
    "NOT_PICKUPABLE"
        If the object itself cannot be picked up.
    "OBSTRUCTED"
        If you cannot pick up the object because your path is obstructed.
    "OUT_OF_REACH"
        If you cannot pick up the object because you are out of reach.
    "FAILED"
        Unexpected error; please report immediately to development team.
    """

    PULL_OBJECT = "PullObject"
    """
    Pull a nearby object.

    Parameters
    ----------
    objectId : string, optional
        The "uuid" of the target object. Required unless the "objectDirection"
        properties are given.
    objectDirectionX : float, optional
        The X of the directional vector pointing to the target object based on
        your current viewport. Can be used in place of the "objectId" property.
    objectDirectionY : float, optional
        The Y of the directional vector pointing to the target object based on
        your current viewport. Can be used in place of the "objectId" property.
    objectDirectionZ : float, optional
        The Z of the directional vector pointing to the target object based on
        your current viewport. Can be used in place of the "objectId" property.
    force : float
        The amount of force, from 0 to 1, used to move the target object.
        Default: 0.5

    Returns
    -------
    "SUCCESSFUL"
        Action successful.
    "NOT_INTERACTABLE"
        If the object corresponding to the "objectDirection" vector is not an
        interactable object.
    "NOT_OBJECT"
        If the object corresponding to the "objectId" (or object corresponding
        to the "objectDirection" vector) is not an object.
    "NOT_PICKUPABLE"
        If the object itself cannot be moved by a baby.
    "OBSTRUCTED"
        If you cannot move the object because your path is obstructed.
    "OUT_OF_REACH"
        If you cannot move the object because you are out of reach.
    "FAILED"
        Unexpected error; please report immediately to development team.
    """

    PUSH_OBJECT = "PushObject"
    """
    Push a nearby object.

    Parameters
    ----------
    objectId : string, optional
        The "uuid" of the target object. Required unless the "objectDirection"
        properties are given.
    objectDirectionX : float, optional
        The X of the directional vector pointing to the target object based on
        your current viewport. Can be used in place of the "objectId" property.
    objectDirectionY : float, optional
        The Y of the directional vector pointing to the target object based on
        your current viewport. Can be used in place of the "objectId" property.
    objectDirectionZ : float, optional
        The Z of the directional vector pointing to the target object based on
        your current viewport. Can be used in place of the "objectId" property.
    force : float
        The amount of force, from 0 to 1, used to move the target object.
        Default: 0.5

    Returns
    -------
    "SUCCESSFUL"
        Action successful.
    "NOT_INTERACTABLE"
        If the object corresponding to the "objectDirection" vector is not an
        interactable object.
    "NOT_OBJECT"
        If the object corresponding to the "objectId" (or object corresponding
        to the "objectDirection" vector) is not an object.
    "NOT_PICKUPABLE"
        If the object itself cannot be moved by a baby.
    "OBSTRUCTED"
        If you cannot move the object because your path is obstructed.
    "OUT_OF_REACH"
        If you cannot move the object because you are out of reach.
    "FAILED"
        Unexpected error; please report immediately to development team.
    """

    PUT_OBJECT = "PutObject"
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
        "receptacleObjectDirection" properties are given.
    objectDirectionX : float, optional
        The X of the directional vector pointing to the target receptacle based
        on your current viewport. Can be used in place of the
        "receptacleObjectId" property.
    objectDirectionY : float, optional
        The Y of the directional vector pointing to the target receptacle based
        on your current viewport. Can be used in place of the
        "receptacleObjectId" property.
    objectDirectionZ : float, optional
        The Z of the directional vector pointing to the target receptacle based
        on your current viewport. Can be used in place of the
        "receptacleObjectId" property.

    Returns
    -------
    "SUCCESSFUL"
        Action successful.
    "NOT_HELD"
        If you cannot put down the object corresponding to the "objectId"
        because you are not holding it.
    "NOT_INTERACTABLE"
        If the object corresponding to the "objectDirection" or
        "receptacleObjectDirection" vector is not an interactable object.
    "NOT_OBJECT"
        If the object corresponding to the "objectId" and/or
        "receptacleObjectId" (or object corresponding to the
        "receptacleObjectDirection" vector) is not an object.
    "NOT_RECEPTACLE"
        If the object corresponding to the "receptacleObjectId" (or object
        corresponding to the "receptacleObjectDirection" vector) is not a
        receptacle.
    "OBSTRUCTED"
        If you cannot put down the object because your path is obstructed.
    "OUT_OF_REACH"
        If you cannot put down the object because you are out of reach.
    "FAILED"
        Unexpected error; please report immediately to development team.
    """

    ROTATE_LOOK = "RotateLook"
    """
    Rotate your viewport left/right and/or up/down based on your current
    viewport.

    Parameters
    ----------
    rotation : float
        Rotation degrees around the Y axis to change your look angle
        (left/right). If the rotation is not between [-360, 360], then 0 will
        be used.
    horizon : float
        Rotation degrees around the X axis to change your look angle (up/down).
        This affects your current "head tilt". If the horizon is not between
        [-90, 90], then 0 will be used.

    Returns
    -------
    "SUCCESSFUL"
        Action successful.
    "FAILED"
        Unexpected error; please report immediately to development team.
    """

    # ROTATE_OBJECT = "RotateObject"
    # ROTATE_OBJECT_IN_HAND = "RotateObjectInHand"

    STAND = "Stand"
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

    THROW_OBJECT = "ThrowObject"
    """
    Throw an object you are holding.

    Parameters
    ----------
    objectId : string, optional
        The "uuid" of the held object. Defaults to the first held object.
    objectDirectionX : float, optional
        The X of the directional vector pointing to where you would like to
        throw the object based on your current viewport.
    objectDirectionY : float, optional
        The Y of the directional vector pointing to where you would like to
        throw the object based on your current viewport.
    objectDirectionZ : float, optional
        The Z of the directional vector pointing to where you would like to
        throw the object based on your current viewport.

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

    # Pass should always be the last action in the enum.
    PASS = "Pass"
    """
    Do nothing.

    Returns
    -------
    "SUCCESSFUL"
        Action successful.
    "FAILED"
        Unexpected error; please report immediately to development team.
    """
