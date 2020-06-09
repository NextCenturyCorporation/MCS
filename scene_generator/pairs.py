import copy
from abc import ABC, abstractmethod
import random
from typing import Tuple, Dict, Any

import geometry


class InteractionPair(ABC):
    def __init__(self, template: Dict[str, Any], find_path: bool):
        self._template = template
        self._find_path = find_path
        self._compute_performer_start()
    
    @abstractmethod
    def get_scenes(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        pass

    def _compute_performer_start(self) -> Dict[str, Dict[str, float]]:
        """Set the starting location (position & rotation) for the performer
        (_performer_start). This default implementation chooses a
        random location.
        """
        if getattr(self, '_performer_start', None) is None:
            self._performer_start = {
                'position': {
                    'x': geometry.random_position(),
                    'y': 0,
                    'z': geometry.random_position()
                },
                'rotation': {
                    'y': geometry.random_rotation()
                }
            }


def get_pair_class():
    # TODO in future tickets
    return None
