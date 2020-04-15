from enum import Enum, unique

@unique
class MCS_Goal_Category(Enum):
    RETRIEVAL = "retrieval"
    TRANSFERRAL = "transferral"
    TRAVERSAL = "traversal"
    INTPHYS = "intphys"