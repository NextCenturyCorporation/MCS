import copy
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Type, Optional

import intphys_goals
from goal import GoalException


def find_target(scene: Dict[str, Any]) -> Dict[str, Any]:
    """Find a 'target' object in the scene. (IntPhys goals don't really
    have them, but they do have objects that may behave plausibly or
    implausibly.)
    """
    return find_targets(scene, 1)[0]


def find_targets(scene: Dict[str, Any], num_targets: Optional[int] = None) -> List[Dict[str, Any]]:
    """Find 'target' objects in the scene. (IntPhys goals don't really
    have them, but they do have objects that may behave plausibly or
    implausibly.)
    """
    target_ids = scene['goal']['metadata']['objects'][:num_targets]
    # This isn't the most efficient way to do this, but since there
    # will only be 2-3 'target' objects and maybe a dozen total
    # objects, that's ok.
    return [next((obj for obj in scene['objects'] if obj['id'] == target_id))
            for target_id in target_ids]


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
            implausible_event_index = target['intphys_option']['occluder_indices'][0]
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
            implausible_event_step = target['intphys_option']['occluder_indices'][0] + \
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
            raise ValueError(f'q must be between 1 and 4 (inclusive), not {q}')
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


class SpatioTemporalContinuityQuartet(Quartet):
    def __init__(self, template: Dict[str, Any], find_path: bool):
        super(SpatioTemporalContinuityQuartet, self).__init__(template, find_path)
        self._goal = intphys_goals.SpatioTemporalContinuityGoal()
        self._scenes[0] = copy.deepcopy(self._template)
        self._goal.update_body(self._scenes[0], self._find_path)
        if self._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_and_occluders_moving_across:

            self._check_stepBegin()

    def _check_stepBegin(self) -> None:
        target = find_target(self._scenes[0])
        implausible_event_index1 = target['intphys_option']['occluder_indices'][0]
        implausible_event_index2 = target['intphys_option']['occluder_indices'][1]
        orig_stepBegin = target['shows'][0]['stepBegin']
        new_stepBegin = orig_stepBegin + abs(implausible_event_index1 - implausible_event_index2)
        max_stepBegin = self._scenes[0]['goal']['last_step'] - len(target['intphys_option']['position_by_step'])
        if new_stepBegin > max_stepBegin:
            # need to adjust the original to accomodate what we need for scene #4
            diff = new_stepBegin - max_stepBegin
            if diff > orig_stepBegin:
                print(f'new_sb={new_stepBegin}\tmax_sb={max_stepBegin}\torig_sb={orig_stepBegin}')
                raise GoalException('cannot fix start times for this goal, must start over')
            target['shows'][0]['stepBegin'] -= diff
            if 'forces' in target:
                target['forces'][0]['stepBegin'] -= diff

    def _teleport_forward(self, scene: Dict[str, Any]) -> None:
        if self._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_and_occluders_moving_across:
            scene['answer']['choice'] = 'implausible'
            target = find_targets(scene)[0]
            # go from the lower index to the higher one so we teleport forward
            implausible_event_index1 = target['intphys_option']['occluder_indices'][0]
            implausible_event_index2 = target['intphys_option']['occluder_indices'][1]
            if implausible_event_index1 < implausible_event_index2:
                implausible_event_index = implausible_event_index1
                destination_index = implausible_event_index2
                destination_x = target['intphys_option']['position_by_step'][destination_index]
            else:
                implausible_event_index = implausible_event_index2
                destination_index = implausible_event_index1
                destination_x = target['intphys_option']['position_by_step'][destination_index]
            implausible_event_step = implausible_event_index + target['forces'][0]['stepBegin']
            target['teleports'] = [{
                'stepBegin': implausible_event_step,
                'stepEnd': implausible_event_step,
                'vector': {
                    'x': destination_x,
                    'y': 0,
                    'z': 0
                }
            }]
        elif self._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_falling_down:
            # TODO: in MCS-132
            pass
        else:
            raise ValueError('unknown object creation function, cannot update scene')

    def _teleport_backward(self, scene: Dict[str, Any]) -> None:
        if self._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_and_occluders_moving_across:
            scene['answer']['choice'] = 'implausible'
            target = find_targets(scene)[0]
            # go from the higher index to the lower one so we teleport backward
            implausible_event_index1 = target['intphys_option']['occluder_indices'][0]
            implausible_event_index2 = target['intphys_option']['occluder_indices'][1]
            if implausible_event_index1 > implausible_event_index2:
                implausible_event_index = implausible_event_index1
                destination_index = implausible_event_index2
                destination_x = target['intphys_option']['position_by_step'][destination_index]
            else:
                implausible_event_index = implausible_event_index2
                destination_index = implausible_event_index1
                destination_x = target['intphys_option']['position_by_step'][destination_index]
            implausible_event_step = implausible_event_index + target['forces'][0]['stepBegin']
            target['teleports'] = [{
                'stepBegin': implausible_event_step,
                'stepEnd': implausible_event_step,
                'vector': {
                    'x': destination_x,
                    'y': 0,
                    'z': 0
                }
            }]
        elif self._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_falling_down:
            # TODO: in MCS-132
            pass
        else:
            raise ValueError('unknown object creation function, cannot update scene')

    def _move_later(self, scene: Dict[str, Any]) -> None:
        scene['answer']['choice'] = 'implausible'
        target = find_target(scene)
        if self._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_and_occluders_moving_across:
            scene['answer']['choice'] = 'implausible'
            target = find_targets(scene)[0]
            implausible_event_index1 = target['intphys_option']['occluder_indices'][0]
            implausible_event_index2 = target['intphys_option']['occluder_indices'][1]
            adjustment = abs(implausible_event_index1 - implausible_event_index2)
            target['shows'][0]['stepBegin'] += adjustment
            if 'forces' in target:
                target['forces'][0]['stepBegin'] += adjustment
        elif self._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_falling_down:
            # TODO: in MCS-132
            pass
        else:
            raise ValueError('unknown object creation function, cannot update scene')

    def get_scene(self, q: int) -> Dict[str, Any]:
        if q < 1 or q > 4:
            raise ValueError(f'q must be between 1 and 4 (inclusive), not {q}')
        if self._scenes[q - 1] is None:
            scene = copy.deepcopy(self._scenes[0])
            if q == 2:
                self._teleport_forward(scene)
            elif q == 3:
                self._teleport_backward(scene)
            elif q == 4:
                self._move_later(scene)
            self._scenes[q - 1] = scene
        return self._scenes[q - 1]


QUARTET_TYPES = [ObjectPermanenceQuartet]


def get_quartet_class(name: str) -> Type[Quartet]:
    class_name = name + 'Quartet'
    klass = globals()[class_name]
    return klass


def get_quartet_types() -> List[str]:
    return [klass.__name__.replace('Quartet', '') for klass in QUARTET_TYPES]
