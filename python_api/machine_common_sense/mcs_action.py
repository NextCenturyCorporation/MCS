from enum import Enum, unique


@unique
class MCS_Action(Enum):
    CLOSE_OBJECT = "CloseObject"
    CRAWL = "Crawl"
    DROP_OBJECT = "DropObject"
    LIE_DOWN = "LieDown"
    MOVE_AHEAD = "MoveAhead"
    MOVE_BACK = "MoveBack"
    MOVE_LEFT = "MoveLeft"
    MOVE_RIGHT = "MoveRight"
    OPEN_OBJECT = "OpenObject"
    PICKUP_OBJECT = "PickupObject"
    PULL_OBJECT = "PullObject"
    PUSH_OBJECT = "PushObject"
    PUT_OBJECT = "PutObject"
    ROTATE_LOOK = "RotateLook"
    # ROTATE_OBJECT = "RotateObject"
    # ROTATE_OBJECT_IN_HAND = "RotateObjectInHand"
    STAND = "Stand"
    THROW_OBJECT = "ThrowObject"
    # Pass should always be the last action in the enum.
    PASS = "Pass"
