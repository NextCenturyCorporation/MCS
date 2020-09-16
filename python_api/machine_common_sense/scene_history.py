from .util import Util
from typing import Dict, List


class SceneHistory(object):
    def __init__(
        self,
        step=-1,
        action=None,
        args=None,
        params=None,
        classification: str = None,
        confidence: float = None,
        violations_xy_list: List[Dict[str, float]] = None,
        internal_state: object = None,
        output=None
    ):
        self.step = step
        self.action = action
        self.args = args
        self.params = params
        self.output = output
        self.classification = classification
        self.confidence = confidence
        self.internal_state = internal_state
        self.violations_xy_list = violations_xy_list

    def __str__(self):
        return Util.class_to_str(self)
