from enum import Enum, unique

@unique
class MCS_Goal_Category(Enum):
    RETRIEVAL = "RETRIEVAL"
    TRANSFERRAL = "TRANSFERRAL"
    INTPHYS = "INTPHYS"
    GOTO = "GOTO"