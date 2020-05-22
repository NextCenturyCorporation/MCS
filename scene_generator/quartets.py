import copy
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Type, Optional, Tuple

import intphys_goals
from goal import GoalException


def find_target(scene: Dict[str, Any]) -> Dict[str, Any]:
    """Find a 'target' object in the scene. (IntPhys goals don't really
    have them, but they do have objects that may behave plausibly or
    implausibly.)
    """
    target_id = scene['goal']['metadata']['objects'][0]
    return next((obj for obj in scene['objects'] if obj['id'] == target_id))


def find_targets(scene: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Find 'target' objects in the scene. (IntPhys goals don't really
    have them, but they do have objects that may behave plausibly or
    implausibly.)
    """
    target_ids = scene['goal']['metadata']['objects']
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
        target = find_targets(self._scenes[0])[0]
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

    def _find_other_occluder(self, target: Dict[str, Any], scene: Dict[str, Any]) -> \
            Tuple[Dict[str, Any], Dict[str, Any]]:
        target_id = target['id']
        other_occluder = None
        other_object_id = None
        for obj in scene['objects']:
            if obj.get('intphys_option', {}).get('is_occluder', False):
                occluded_id = obj.get('intphys_option', {}).get('occluded_id', None)
                if occluded_id != target_id:
                    other_occluder = obj
                    other_object_id = occluded_id
                    break
        if other_occluder is None:
            raise GoalException('cannot find a second occluder, error generating scene')
        if other_object_id is None:
            other_object = None
        else:
            other_object = next((obj for obj in scene['objects'] if obj['id'] == other_object_id))
        return other_occluder, other_object

    def _teleport_forward(self, scene: Dict[str, Any]) -> None:
        scene['answer']['choice'] = 'implausible'
        all_targets = find_targets(scene)
        target = all_targets[0]
        if self._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_and_occluders_moving_across:
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
        elif self._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_falling_down:
            # 8 is enough for it to fall to the ground
            implausible_event_step = 8 + target['shows'][0]['stepBegin']
            # find another occluder besides the target's
            other_occluder, other_object = self._find_other_occluder(target, scene)
            # teleport the target behind the other occluder
            factor = intphys_goals.IntPhysGoal.NEAR_X_PERSPECTIVE_FACTOR \
                if target['shows'][0]['position']['z'] == intphys_goals.IntPhysGoal.OBJECT_NEAR_Z \
                else intphys_goals.IntPhysGoal.FAR_X_PERSPECTIVE_FACTOR
            destination_x = other_occluder['shows'][0]['position']['x'] / factor
            # if the other occluder had an object behind it, teleport
            # that where the target was
            if other_object is not None:
                other_object['teleports'] = [{
                    'stepBegin': implausible_event_step,
                    'stepEnd': implausible_event_step,
                    'position': {
                        'x': target['shows'][0]['position']['x'],
                        'y': target['shows'][0]['position']['y'],
                        'z': target['shows'][0]['position']['z']
                    }
                }]
        else:
            raise ValueError('unknown object creation function, cannot update scene')
        target['teleports'] = [{
            'stepBegin': implausible_event_step,
            'stepEnd': implausible_event_step,
            'position': {
                'x': destination_x,
                'y': target['shows'][0]['position']['y'],
                'z': target['shows'][0]['position']['z']
            }
        }]

    def _teleport_backward(self, scene: Dict[str, Any]) -> None:
        target = find_targets(scene)[0]
        if self._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_and_occluders_moving_across:
            scene['answer']['choice'] = 'implausible'
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
        elif self._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_falling_down:
            # 8 is enough for it to fall to the ground
            implausible_event_step = 8 + target['shows'][0]['stepBegin']
            # find another occluder besides the target's
            other_occluder, other_object = self._find_other_occluder(target, scene)
            # start behind the other occluder
            original_position = target['shows'][0]['position'].copy()
            factor = intphys_goals.IntPhysGoal.NEAR_X_PERSPECTIVE_FACTOR \
                if target['shows'][0]['position']['z'] == intphys_goals.IntPhysGoal.OBJECT_NEAR_Z \
                else intphys_goals.IntPhysGoal.FAR_X_PERSPECTIVE_FACTOR
            target['shows'][0]['position']['x'] = other_occluder['shows'][0]['position']['x'] / factor
            # later teleport back to its original position
            destination_x = original_position['x']
            # If the other occluder had an object behind it, start it
            # in this object's original position and then teleport it
            # back to its original position.
            if other_object is not None:
                other_object['teleports'] = [{
                    'stepBegin': implausible_event_step,
                    'stepEnd': implausible_event_step,
                    'position': other_object['shows'][0]['position'].copy()
                }]
                other_object['shows'][0]['position'] = original_position
        else:
            raise ValueError('unknown object creation function, cannot update scene')
        target['teleports'] = [{
            'stepBegin': implausible_event_step,
            'stepEnd': implausible_event_step,
            'position': {
                'x': destination_x,
                'y': target['shows'][0]['position']['y'],
                'z': target['shows'][0]['position']['z']
            }
        }]

    def _move_later(self, scene: Dict[str, Any]) -> None:
        scene['answer']['choice'] = 'implausible'
        target = find_targets(scene)[0]
        if self._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_and_occluders_moving_across:
            implausible_event_index1 = target['intphys_option']['occluder_indices'][0]
            implausible_event_index2 = target['intphys_option']['occluder_indices'][1]
            adjustment = abs(implausible_event_index1 - implausible_event_index2)
            target['shows'][0]['stepBegin'] += adjustment
            if 'forces' in target:
                target['forces'][0]['stepBegin'] += adjustment
        elif self._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_falling_down:
            # find another occluder besides the target's
            other_occluder, other_object = self._find_other_occluder(target, scene)
            # move target behind the other occluder
            original_position = target['shows'][0]['position'].copy()
            factor = intphys_goals.IntPhysGoal.NEAR_X_PERSPECTIVE_FACTOR \
                if target['shows'][0]['position']['z'] == intphys_goals.IntPhysGoal.OBJECT_NEAR_Z \
                else intphys_goals.IntPhysGoal.FAR_X_PERSPECTIVE_FACTOR
            target['shows'][0]['position']['x'] = other_occluder['shows'][0]['position']['x'] / factor
            # If there was another object behind the occluder, put it
            # where the target was
            if other_object is not None:
                other_object['shows'][0]['position'] = original_position
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


QUARTET_TYPES: List[Type[Quartet]] = [ObjectPermanenceQuartet, SpatioTemporalContinuityQuartet]


def get_quartet_class(name: str) -> Type[Quartet]:
    class_name = name + 'Quartet'
    klass = globals()[class_name]
    return klass


def get_quartet_types() -> List[str]:
    return [klass.__name__.replace('Quartet', '') for klass in QUARTET_TYPES]
