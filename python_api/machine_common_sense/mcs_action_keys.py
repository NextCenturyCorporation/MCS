from enum import Enum, unique


@unique
class Action_Keys(Enum):
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
