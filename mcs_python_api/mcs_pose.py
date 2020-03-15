from enum import Enum, unique

@unique
class MCS_Pose(Enum):
    CRAWL = "CRAWL"
    LIE = "LIE"
    SQUAT = "SQUAT"
    STAND = "STAND"
    UNDEFINED = "UNDEFINED"

