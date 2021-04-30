import logging

# from .reward import Reward
# from .step_metadata import StepMetadata

logger = logging.getLogger(__name__)


class ControllerOutputHandler():

    def __init__(self, config):
        # do nothing
        self._config = config
