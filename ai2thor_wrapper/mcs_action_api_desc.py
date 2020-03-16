from enum import Enum, unique

@unique
class MCS_Action_API_DESC(Enum):
    CLOSE_OBJECT = "Close a nearby object. (objectId=string, amount=float (default:1), objectDirectionX=float, objectDirectionY=float, objectDirectionZ=float)"
    CRAWL = "Change pose to 'CRAWL' (no params)"
    DROP_OBJECT = "Drop an object you are holding. (objectId=string)"
    LIE_DOWN = "Change pose to 'LIE' (rotation=float)"
    MOVE_AHEAD = "Move yourself ahead based on your current view. (amount=float (default:0.5))"
    MOVE_BACK = "Move yourself back based on your current view. (amount=float (default:0.5))"
    MOVE_LEFT = "Move yourself to your left based on your current view. (amount=float (default:0.5))"
    MOVE_RIGHT = "Move yourself to your right based on your current view. (amount=float (default:0.5))"
    OPEN_OBJECT = "Open a nearby object. (objectId=string, amount=float (default:1), objectDirectionX=float, objectDirectionY=float, objectDirectionZ=float)"
    PASS = "Do nothing. (no params)"
    PICKUP_OBJECT = "Pickup a nearby object and hold it in your hand. (objectId=string, objectDirectionX=float, objectDirectionY=float, objectDirectionZ=float)"
    PULL_OBJECT = "Pull a nearby object. (objectId=string, rotation=float, horizon=float, force=float (default:0.5), objectDirectionX=float, objectDirectionY=float, objectDirectionZ=float)"
    PUSH_OBJECT = "Push a nearby object. (objectId=string, rotation=float, horizon=float, force=float (default:0.5), objectDirectionX=float, objectDirectionY=float, objectDirectionZ=float)"
    PUT_OBJECT = "Place an object you are holding into/onto a nearby receptacle object. (objectId=string, receptacleObjectId=string, receptacleObjectDirectionX=float, receptacleObjectDirectionY=float, receptacleObjectDirectionZ=float)"
    ROTATE_LOOK = "Rotate your view left/right and/or up/down based on your current view. (rotation=float, horizon=float)"
    ROTATE_OBJECT_IN_HAND = "Rotate a held object. (objectId=string, rotationX=float, rotationY=float, rotationZ=float, , objectDirectionX=float, objectDirectionY=float, objectDirectionZ=float)"
    SQUAT = "Change pose to 'SQUAT' (no params)"
    STAND = "Change pose to 'STAND' (no params)"
    THROW_OBJECT = "Throw an object you are holding. (objectId=string, rotation=float, horizon=float, force=float (default:0.5))"