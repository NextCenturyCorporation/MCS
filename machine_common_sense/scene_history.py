from typing import Dict, List

from .stringifier import Stringifier


class SceneHistory(object):
    def __init__(
        self,
        step=-1,
        action=None,
        args=None,
        params=None,
        # Use classification and confidence rather than rating and score to be
        # compatible with old history files.
        classification: str = None,
        confidence: float = None,
        violations_xy_list: List[Dict[str, float]] = None,
        internal_state: object = None,
        delta_time_millis=0,
        output=None,
        target_visible=False

    ):
        self.step = step
        self.action = action
        self.args = args
        self.params = params
        self.classification = classification
        self.confidence = confidence
        self.violations_xy_list = violations_xy_list
        self.internal_state = internal_state
        self.delta_time_millis = delta_time_millis
        self.output = output
        self.target_visible = target_visible

    def __str__(self):
        return Stringifier.class_to_str(self)

    # Allows converting the class to a dictionary, along with allowing
    #   certain fields to be left out of output file
    def __iter__(self):
        yield 'step', self.step
        yield 'action', self.action
        yield 'args', self.args
        yield 'params', self.params
        yield 'classification', self.classification
        yield 'confidence', self.confidence
        yield 'violations_xy_list', self.violations_xy_list
        yield 'internal_state', self.internal_state
        yield 'output', dict(self.output) if(
            self.output) is not None else self.output
        yield 'delta_time_millis', self.delta_time_millis
        yield 'target_visible', self.target_visible
