import copy
import random
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Type, Optional

import goal
import intphys_goals
import objects
import util


def find_target(scene: Dict[str, Any]) -> Dict[str, Any]:
    """Find a 'target' object in the scene. (IntPhys goals don't really
    have them, but they do have objects that may behave plausibly or
    implausibly.)
    """
    target_id = scene['goal']['metadata']['objects'][0]
    return next((obj for obj in scene['objects'] if obj['id'] == target_id))


class Quartet(ABC):
    def __init__(self, template: Dict[str, Any], find_path: bool):
        self._template = template
        self._find_path = find_path
        self._scenes: List[Optional[Dict[str, Any]]] = [None]*4

    @abstractmethod
    def get_scene(self, q: int) -> Dict[str, Any]:
        pass


class ObjectPermanenceQuartet(Quartet):
    def __init__(self, template: Dict[str, Any], find_path: bool):
        super(ObjectPermanenceQuartet, self).__init__(template, find_path)
        self._goal = intphys_goals.ObjectPermanenceGoal()
        self._scenes[0] = copy.deepcopy(self._template)
        self._goal.update_body(self._scenes[0], self._find_path)

    def _appear_behind_occluder(self, body: Dict[str, Any]) -> None:
        target = find_target(body)
        if self._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_and_occluders_moving_across:
            implausible_event_index = target['intphys_option']['implausible_event_index']
            implausible_event_step = implausible_event_index + target['forces'][0]['stepBegin']
            implausible_event_x = target['intphys_option']['position_by_step'][implausible_event_index]
            target['shows'][0]['position']['x'] = implausible_event_x
        elif self._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_falling_down:
            # 8 is enough steps for anything to fall to the ground
            implausible_event_step = 8 + target['shows'][0]['stepBegin']
            target['shows'][0]['position']['y'] = target['intphys_option']['position_y']
        else:
            raise ValueError('unknown object creation function, cannot update scene')
        target['shows'][0]['stepBegin'] = implausible_event_step

    def _disappear_behind_occluder(self, body: Dict[str, Any]) -> None:
        target = find_target(body)
        if self._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_and_occluders_moving_across:
            implausible_event_step = target['intphys_option']['implausible_event_index'] + \
                target['forces'][0]['stepBegin']
        elif self._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_falling_down:
            # 8 is enough steps for anything to fall to the ground
            implausible_event_step = 8 + target['shows'][0]['stepBegin']
        else:
            raise ValueError('unknown object creation function, cannot update scene')
        target['hides'] = [{
            'stepBegin': implausible_event_step
        }]

    def get_scene(self, q: int) -> Dict[str, Any]:
        if q < 1 or q > 4:
            raise ValueError(f'q must be between 1 and 4 (exclusive), not {q}')
        scene = self._scenes[q - 1]
        if scene is None:
            scene = copy.deepcopy(self._scenes[0])
            if q == 2:
                # target moves behind occluder and disappears (implausible)
                scene['answer']['choice'] = 'implausible'
                self._disappear_behind_occluder(scene)
            elif q == 3:
                # target first appears from behind occluder (implausible)
                scene['answer']['choice'] = 'implausible'
                self._appear_behind_occluder(scene)
            elif q == 4:
                # target not in the scene (plausible)
                target_id = scene['goal']['metadata']['objects'][0]
                for i in range(len(scene['objects'])):
                    obj = scene['objects'][i]
                    if obj['id'] == target_id:
                        del scene['objects'][i]
                        break
            self._scenes[q - 1] = scene
        return scene


class ShapeConstancyQuartet(Quartet):
    def __init__(self, template: Dict[str, Any], find_path: bool):
        super(ShapeConstancyQuartet, self).__init__(template, find_path)
        self._goal = intphys_goals.ShapeConstancyGoal()
        self._scenes[0] = copy.deepcopy(self._template)
        self._goal.update_body(self._scenes[0], self._find_path)
        # we need the b object for 3/4 of the scenes, so generate it now
        self._b = self._create_b()

    def _create_b(self) -> Dict[str, Any]:
        a = self._scenes[0]['objects'][0]
        possible_defs = []
        normalized_scale = a['shows'][0]['scale']
        # cylinders have "special" scaling: scale.y is half what it is
        # for other objects
        if a['type'] == 'cylinder':
            normalized_scale = normalized_scale.copy()
            normalized_scale['y'] *= 2
        for obj_def in objects.OBJECTS_INTPHYS:
            if obj_def['type'] != a['type']:
                def_scale = obj_def['scale']
                if obj_def['type'] == 'cylinder':
                    def_scale = def_scale.copy()
                    def_scale['y'] *= 2
                if def_scale == normalized_scale:
                    possible_defs.append(obj_def)
        if len(possible_defs) == 0:
            raise goal.GoalException(f'no valid choices for "b" object. a = {a}')
        b_def = random.choice(possible_defs)
        b_def = util.finalize_object_definition(b_def)
        b = util.instantiate_object(b_def, a['original_location'], a['materials_list'])
        return b

    def _turn_a_into_b(self, scene: Dict[str, Any]) -> None:
        scene['answer']['choice'] = 'implausible'
        a = self._scenes[0]['objects'][0]
        b = copy.deepcopy(self._b)
        if self._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_and_occluders_moving_across:
            implausible_event_index = a['intphys_option']['implausible_event_index']
            implausible_event_step = implausible_event_index + a['forces'][0]['stepBegin']
            implausible_event_x = a['intphys_option']['position_by_step'][implausible_event_index]
            b['shows'][0]['position']['x'] = implausible_event_x
            b['shows'][0]['position']['z'] = a['shows'][0]['position']['z']
            b['forces'] = copy.deepcopy(a['forces'])
        elif self._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_falling_down:
            # 8 steps is enough time for the object to fall to the ground
            implausible_event_step = 8 + a['shows'][0]['stepBegin']
            b['shows'][0]['position']['x'] = a['shows'][0]['position']['x']
            b['shows'][0]['position']['z'] = a['shows'][0]['position']['z']
            b['shows'][0]['position']['y'] = a['intphys_option']['y']
        else:
            raise ValueError(f'unknown object creation function, cannot update scene: {self._goal._object_creator}')
        b['shows'][0]['stepBegin'] = implausible_event_step
        a['hides'] = [{
            'stepBegin': implausible_event_step
        }]
        scene['objects'].append(b)

    def _turn_b_into_a(self, scene: Dict[str, Any]) -> None:
        scene['answer']['choice'] = 'implausible'
        a = self._scenes[0]['objects'][0]
        b = copy.deepcopy(self._b)
        b['shows'][0]['position']['x'] = a['shows'][0]['position']['x']
        if self._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_and_occluders_moving_across:
            implausible_event_index = a['intphys_option']['implausible_event_index']
            implausible_event_step = implausible_event_index + a['forces'][0]['stepBegin']
            implausible_event_x = a['intphys_option']['position_by_step'][implausible_event_index]
            b['forces'] = copy.deepcopy(a['forces'])
            a['shows'][0]['position']['x'] = implausible_event_x
            pass
        elif self._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_falling_down:
            implausible_event_step = 8 + a['shows'][0]['stepBegin']
            b['shows'][0]['position']['y'] = a['shows'][0]['position']['y']
            a['shows'][0]['position']['y'] = a['intphys_option']['y']
            pass
        else:
            raise ValueError(f'unknown object creation function, cannot update scene: {self._goal._object_creator}')
        a['shows'][0]['stepBegin'] = implausible_event_step
        b['shows'][0]['position']['z'] = a['shows'][0]['position']['z']
        b['hides'] = [{
            'stepBegin': implausible_event_step
        }]
        scene['objects'].append(b)

    def _b_replaces_a(self, body: Dict[str, Any]) -> None:
        body['objects'][0] = self._b

    def get_scene(self, q: int) -> Dict[str, Any]:
        if q < 1 or q > 4:
            raise ValueError(f'q must be between 1 and 4 (exclusive), not {q}')
        scene = self._scenes[q - 1]
        if scene is None:
            scene = copy.deepcopy(self._scenes[0])
            if q == 2:
                # Object A moves behind an occluder, then object B emerges
                # from behind the occluder (implausible)
                self._turn_a_into_b(scene)
            elif q == 3:
                # Object B moves behind an occluder (replacing object A's
                # movement), then object A emerges from behind the
                # occluder (implausible)
                self._turn_b_into_a(scene)
            elif q == 4:
                # Object B moves normally (replacing object A's movement),
                # object A is never added to the scene (plausible)
                self._b_replaces_a(scene)
            self._scenes[q - 1] = scene
        return scene


QUARTET_TYPES = [ObjectPermanenceQuartet, ShapeConstancyQuartet]


def get_quartet_class(name: str) -> Type[Quartet]:
    class_name = name + 'Quartet'
    klass = globals()[class_name]
    return klass


def get_quartet_types() -> List[str]:
    return [klass.__name__.replace('Quartet', '') for klass in QUARTET_TYPES]
