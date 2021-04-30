import enum


class EventType(enum.Enum):
    ON_INIT = 1
    ON_START_SCENE = 2
    ON_BEFORE_STEP = 3
    ON_AFTER_STEP = 4
    ON_END_SCENE = 5
