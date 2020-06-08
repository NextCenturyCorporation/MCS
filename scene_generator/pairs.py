import copy
from abc import ABC, abstractmethod
import random
from typing import Tuple, Dict, Any, Type

import geometry
import objects
import util


def move_to_location(obj_def: Dict[str, Any], obj: Dict[str, Any],
                     location: Dict[str, Any]):
    """Move the passed object to a new location"""
    obj['original_location'] = copy.deepcopy(location)
    new_location = copy.deepcopy(location)
    if 'offset' in obj_def:
        new_location['position']['x'] -= obj_def['offset']['x']
        new_location['position']['z'] -= obj_def['offset']['z']
    obj['shows'][0]['position'] = new_location['position']
    obj['shows'][0]['rotation'] = new_location['rotation']
    obj['shows'][0]['bounding_box'] = new_location['bounding_box']


class InteractionPair(ABC):
    def __init__(self, template: Dict[str, Any], find_path: bool):
        self._template = template
        self._find_path = find_path
        self._compute_performer_start()

    @abstractmethod
    def get_scenes(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        pass

    def _compute_performer_start(self) -> None:
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


class ImmediatelyVisiblePair(InteractionPair):
    def __init__(self, template: Dict[str, Any], find_path: bool):
        super(ImmediatelyVisiblePair, self).__init__(template, find_path)

    def _get_empty_scene(self) -> Dict[str, Any]:
        scene = copy.deepcopy(self._template)
        scene['performerStart'] = self._performer_start
        return scene

    def get_scenes(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        # choose target object
        target_def = util.finalize_object_definition(random.choice(objects.get_all_object_defs()))
        scene1 = self._get_empty_scene()
        # place target object in scene 1 right in front of the performer
        in_front_location = geometry.get_location_in_front_of_performer(self._performer_start, target_def)
        target = util.instantiate_object(target_def, in_front_location)
        scene1['objects'] = [target]
        scene2 = self._get_empty_scene()
        # place target object in scene 2 behind the performer
        behind_location = geometry.get_location_behind_performer(self._performer_start, target_def)
        target2 = copy.deepcopy(target)
        move_to_location(target_def, target2, behind_location)
        scene2['objects'] = [target2]
        return scene1, scene2


_INTERACTION_PAIR_CLASSES = [ImmediatelyVisiblePair]


def get_pair_class() -> Type[InteractionPair]:
    return random.choice(_INTERACTION_PAIR_CLASSES)
