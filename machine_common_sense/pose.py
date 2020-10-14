from enum import Enum, unique


@unique
class Pose(Enum):
    CRAWLING = "CRAWLING"
    LYING = "LYING"
    STANDING = "STANDING"
    UNDEFINED = "UNDEFINED"
