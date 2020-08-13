from enum import Enum, unique


@unique
class Goal_Category(Enum):
    RETRIEVAL = "retrieval"
    TRANSFERRAL = "transferral"
    TRAVERSAL = "traversal"
    INTPHYS = "intphys"
