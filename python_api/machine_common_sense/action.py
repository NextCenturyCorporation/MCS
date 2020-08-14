from enum import Enum, unique


@unique
class Action(Enum):
    CLOSE_OBJECT = "CloseObject"
    # CRAWL = "Crawl"
    DROP_OBJECT = "DropObject"
    # LIE_DOWN = "LieDown"
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
    # STAND = "Stand"
    THROW_OBJECT = "ThrowObject"
    # Pass should always be the last action in the enum.
    PASS = "Pass"


@unique
class ActionApiDescription(Enum):
    CLOSE_OBJECT = "Close a nearby object. (objectId=string, amount=float " \
        "(default:1), objectDirectionX=float, objectDirectionY=float, " \
        "objectDirectionZ=float)"
    CRAWL = "Change pose to 'CRAWLING' (no params)"
    DROP_OBJECT = "Drop an object you are holding. (objectId=string)"
    LIE_DOWN = "Change pose to 'LYING' (rotation=float)"
    MOVE_AHEAD = "Move yourself ahead based on your current view. " \
        "(amount=float (default:0.5))"
    MOVE_BACK = "Move yourself back based on your current view. " \
        "(amount=float (default:0.5))"
    MOVE_LEFT = "Move yourself to your left based on your current view. " \
        "(amount=float (default:0.5))"
    MOVE_RIGHT = "Move yourself to your right based on your current view. " \
        "(amount=float(default: 0.5))"
    OPEN_OBJECT = "Open a nearby object. (objectId=string, " \
        "amount=float (default:1), objectDirectionX=float, " \
        "objectDirectionY=float, objectDirectionZ=float)"
    PASS = "Do nothing. (no params)"
    PICKUP_OBJECT = "Pickup a nearby object and hold it in your hand. " \
        "(objectId=string, objectDirectionX=float, objectDirectionY=float, " \
        "objectDirectionZ=float)"
    PULL_OBJECT = "Pull a nearby object. (objectId=string, rotation=float, " \
        "horizon=float, force=float (default:0.5), objectDirectionX=float, " \
        "objectDirectionY=float, objectDirectionZ=float)"
    PUSH_OBJECT = "Push a nearby object. (objectId=string, rotation=float, " \
        "horizon=float, force=float (default:0.5), objectDirectionX=float, " \
        "objectDirectionY=float, objectDirectionZ=float)"
    PUT_OBJECT = "Place an object you are holding into/onto a nearby " \
        "receptacle object. (objectId=string, receptacleObjectId=string, " \
        "receptacleObjectDirectionX=float, receptacleObjectDirectionY=float," \
        " receptacleObjectDirectionZ=float)"
    ROTATE_LOOK = "Rotate your view left/right and/or up/down based on your " \
        "current view. (rotation=float, horizon=float)"
    ROTATE_OBJECT_IN_HAND = "Rotate a held object. (objectId=string, " \
        "rotationX=float, rotationY=float, rotationZ=float, " \
        "objectDirectionX=float, objectDirectionY=float, " \
        "objectDirectionZ=float)"
    STAND = "Change pose to 'STANDING' (no params)"
    THROW_OBJECT = "Throw an object you are holding. (objectId=string, " \
        "objectDirectionX=float, objectDirectionY=float, " \
        "objectDirectionZ=float, force=float (default:0.5))"


@unique
class ActionKeys(Enum):
    CLOSE_OBJECT = "1"
    CRAWL = "c"
    DROP_OBJECT = "2"
    LIE_DOWN = "l"
    MOVE_AHEAD = "w"
    MOVE_BACK = "s"
    MOVE_LEFT = "a"
    MOVE_RIGHT = "d"
    OPEN_OBJECT = "3"
    PASS = " "
    PICKUP_OBJECT = "4"
    PULL_OBJECT = "5"
    PUSH_OBJECT = "6"
    PUT_OBJECT = "7"
    ROTATE_LOOK = "r"
    ROTATE_OBJECT_IN_HAND = "t"
    STAND = "u"
    THROW_OBJECT = "q"