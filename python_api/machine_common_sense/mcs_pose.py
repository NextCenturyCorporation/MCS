from enum import Enum, unique

@unique
class MCS_Pose(Enum):
    CRAWLING = "CRAWLING"
    LYING = "LYING"
    STANDING = "STANDING"
    UNDEFINED = "UNDEFINED"

