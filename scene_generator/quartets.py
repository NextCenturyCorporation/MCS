import copy
import logging
import random
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Type, Optional, Tuple

import goal
import intphys_goals
import objects
import ramps
import util


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


def get_position_step(target: Dict[str, Any], x_position: float,
                      left_to_right: bool, forwards: bool) -> int:
    """Get the step number at which the target reaches x_position"""
    positions = target['intphys_option']['position_by_step']
    if forwards:
        rang = range(len(positions))
        counting_up = not left_to_right
    else:
        rang = range(len(positions)-1, -1, -1)
        counting_up = left_to_right

    for i in rang:
        pos = positions[i]
        if counting_up and pos > x_position or \
           not counting_up and pos < x_position:
            return i
    raise goal.GoalException(f'cannot find step for position: {x_position}')


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
        logging.debug(f'OPQ: setup = f{self._goal._object_creator}')

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
                raise goal.GoalException('cannot fix start times for this goal, must start over')
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
            position = {
                'x': destination_x,
                'y': target['intphys_option']['position_y'],
                'z': target['shows'][0]['position']['z']
            }
            if random.random() <= 0.5:
                # delay emergence of the target
                target['hides'] = {'stepBegin': implausible_event_step}
                target['shows'].append({
                    'stepBegin': target['shows'][0]['stepBegin'] + destination_index + 1,
                    'position': position
                })
                scene['goal']['type_list'].append('teleport_delayed')
            else:
                # teleport the target
                target['teleports'] = [{
                    'stepBegin': implausible_event_step,
                    'stepEnd': implausible_event_step,
                    'position': position
                }]
                scene['goal']['type_list'].append('teleport_instantaneous')

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
                        'y': target['intphys_option']['position_y'],
                        'z': target['shows'][0]['position']['z']
                    }
                }]
            target['teleports'] = [{
                'stepBegin': implausible_event_step,
                'stepEnd': implausible_event_step,
                'position': {
                    'x': destination_x,
                    'y': target['intphys_option']['position_y'],
                    'z': target['shows'][0]['position']['z']
                }
            }]
        else:
            raise ValueError('unknown object creation function, cannot update scene')

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
                    'position': {
                        'x': other_object['shows'][0]['position']['x'],
                        'y': other_object['intphys_option']['position_y'],
                        'z': other_object['shows'][0]['position']['x']
                    }
                }]
                other_object['shows'][0]['position'] = original_position
        else:
            raise ValueError('unknown object creation function, cannot update scene')
        target['teleports'] = [{
            'stepBegin': implausible_event_step,
            'stepEnd': implausible_event_step,
            'position': {
                'x': destination_x,
                'y': target['intphys_option']['position_y'],
                'z': target['shows'][0]['position']['z']
            }
        }]

    def _move_later(self, scene: Dict[str, Any]) -> None:
        scene['answer']['choice'] = 'implausible'
        target = find_target(scene)
        if self._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_and_occluders_moving_across:
            scene['answer']['choice'] = 'implausible'
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


class ShapeConstancyQuartet(Quartet):
    """This quartet is about one object turning into another object of a
    different shape. The 'a' object may turn into the 'b' object or
    vice versa.
    """

    def __init__(self, template: Dict[str, Any], find_path: bool):
        super(ShapeConstancyQuartet, self).__init__(template, find_path)
        self._goal = intphys_goals.ShapeConstancyGoal()
        self._scenes[0] = copy.deepcopy(self._template)
        self._goal.update_body(self._scenes[0], self._find_path)
        logging.debug(f'SCQ: setup = f{self._goal._object_creator}')
        # we need the b object for 3/4 of the scenes, so generate it now
        self._b = self._create_b()

    def _create_b(self) -> Dict[str, Any]:
        a = self._scenes[0]['objects'][0]
        possible_defs = []
        normalized_scale = a['shows'][0]['scale']
        # cylinders have "special" scaling: scale.y is half what it is
        # for other objects (because Unity automatically doubles the
        # scale.y of cylinders)
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
        logging.debug(f'a type: {a["type"]}\tb type: {b["type"]}')
        return b

    def _turn_a_into_b(self, scene: Dict[str, Any]) -> None:
        scene['answer']['choice'] = 'implausible'
        a = scene['objects'][0]
        b = copy.deepcopy(self._b)
        if self._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_and_occluders_moving_across:
            implausible_event_index = a['intphys_option']['occluder_indices'][0]
            implausible_event_step = implausible_event_index + a['forces'][0]['stepBegin']
            implausible_event_x = a['intphys_option']['position_by_step'][implausible_event_index]
            b['shows'][0]['position']['x'] = implausible_event_x
            b['forces'] = copy.deepcopy(a['forces'])
        elif self._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_falling_down:
            # 8 steps is enough time for the object to fall to the ground
            implausible_event_step = 8 + a['shows'][0]['stepBegin']
            b['shows'][0]['position']['x'] = a['shows'][0]['position']['x']
            b['shows'][0]['position']['y'] = a['intphys_option']['position_y']
        else:
            raise ValueError(f'unknown object creation function, cannot update scene: {self._goal._object_creator}')
        b['shows'][0]['position']['z'] = a['shows'][0]['position']['z']
        b['shows'][0]['stepBegin'] = implausible_event_step
        logging.debug(f'hiding a ({a["id"]}) at step {implausible_event_step}')
        a['hides'] = [{
            'stepBegin': implausible_event_step
        }]
        scene['objects'].append(b)

    def _turn_b_into_a(self, scene: Dict[str, Any]) -> None:
        scene['answer']['choice'] = 'implausible'
        a = scene['objects'][0]
        b = copy.deepcopy(self._b)
        b['shows'][0]['position']['x'] = a['shows'][0]['position']['x']
        if self._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_and_occluders_moving_across:
            implausible_event_index = a['intphys_option']['occluder_indices'][0]
            implausible_event_step = implausible_event_index + a['forces'][0]['stepBegin']
            implausible_event_x = a['intphys_option']['position_by_step'][implausible_event_index]
            b['forces'] = copy.deepcopy(a['forces'])
            a['shows'][0]['position']['x'] = implausible_event_x
            pass
        elif self._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_falling_down:
            implausible_event_step = 8 + a['shows'][0]['stepBegin']
            b['shows'][0]['position']['y'] = a['shows'][0]['position']['y']
            a['shows'][0]['position']['y'] = a['intphys_option']['position_y']
            pass
        else:
            raise ValueError(f'unknown object creation function, cannot update scene: {self._goal._object_creator}')
        b['shows'][0]['stepBegin'] = a['shows'][0]['stepBegin']
        a['shows'][0]['stepBegin'] = implausible_event_step
        b['shows'][0]['position']['z'] = a['shows'][0]['position']['z']
        logging.debug(f'hiding b ({b["id"]}) at step {implausible_event_step}')
        b['hides'] = [{
            'stepBegin': implausible_event_step
        }]
        scene['objects'].append(b)

    def _b_replaces_a(self, scene: Dict[str, Any]) -> None:
        a = scene['objects'][0]
        b = copy.deepcopy(self._b)
        b['shows'] = a['shows']
        if 'forces' in a:
            b['forces'] = a['forces']
        scene['objects'][0] = b

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
            # May have added and/or deleted an object, so regenerate
            # goal.info_list
            del scene['goal']['info_list']
            self._goal._update_goal_info_list(scene['goal'], scene['objects'])
            self._scenes[q - 1] = scene
        logging.debug(f'get_scene: q={q}\thides? {scene["objects"][0].get("hides", None)}')
        return scene


class GravityQuartet(Quartet):
    RAMP_30_BOTTOM_OFFSET = -1.55
    RAMP_45_BOTTOM_OFFSET = -2.4
    RAMP_30_TOP_OFFSET = 1
    RAMP_45_TOP_OFFSET = -1

    def __init__(self, template: Dict[str, Any], find_path: bool):
        super(GravityQuartet, self).__init__(template, find_path)
        # only need to specify ramp_type until MCS-133 is implemented
        ramp_type = random.choice((ramps.Ramp.RAMP_30, ramps.Ramp.RAMP_45))
        self._goal = intphys_goals.GravityGoal(ramp_type, roll_down = False, use_fastest = True)
        self._scenes[0] = copy.deepcopy(self._template)
        self._goal.update_body(self._scenes[0], self._find_path)

    def get_scene(self, q: int) -> Dict[str, Any]:
        if q > 0:
            if self._scenes[q - 1] is None:
                if self._goal.is_ramp_steep():
                    self._scenes[q - 1] = self._get_steep_scene(q)
                else:
                    self._scenes[q - 1] = self._get_gentle_scene(q)
        return self._scenes[q - 1]

    def _get_steep_scene(self, q: int) -> Dict[str, Any]:
        scene = copy.deepcopy(self._scenes[0])
        target = scene['objects'][0]
        if q == 2:
            # switch the target to use lowest force.x
            new_intphys_option = sorted(target['intphy_option']['saved_options'],
                                        key=lambda io: io['force']['x'])[0]
            orig_x_position = target['shows'][0]['position']['x']
            target['forces'][0]['x'] = new_intphys_option['force']['x']
        elif q == 3:
            # fast, falls too quickly
            scene['answer']['choice'] = 'implausible'
            # TODO
        elif q == 4:
            # slow, falls too slowly
            scene['answer']['choice'] = 'implausible'
            # TODO
        return scene

    def _get_gentle_scene(self, q: int) -> Dict[str, Any]:
        scene = copy.deepcopy(self._scenes[0])
        if q == 2:
            self._make_roll_down(scene)
        elif q == 3:
            scene['answer']['choice'] = 'implausible'
            self._make_object_faster(scene)
        elif q == 4:
            scene['answer']['choice'] = 'implausible'
            self._make_roll_down(scene)
            self._make_object_slower(scene)
        return scene

    def _make_roll_down(self, scene: Dict[str, Any]) -> None:
        ramp_type = self._goal.get_ramp_type()
        for obj in scene['objects']:
            if obj.get('intphys_option', {}).get('moving_object', False):
                obj['shows'][0]['position']['x'] *= -1
                obj['forces'][0]['vector']['x'] *= -1
                # adjust height to be on top of ramp
                obj['shows'][0]['position']['y'] += ramps.RAMP_OBJECT_HEIGHTS[ramp_type]
                # Add a downward force to all objects moving down the
                # ramps so that they will move more realistically.
                obj['forces'][0]['vector']['y'] = obj['mass'] * intphys_goals.IntPhysGoal.RAMP_DOWNWARD_FORCE

    def _get_ramp_offsets(self) -> Tuple[float, float]:
        bottom_offset = RAMP_30_BOTTOM_OFFSET \
            if self._goal.get_ramp_type() == ramps.Ramp.RAMP_30 \
               else RAMP_45_BOTTOM_OFFSET
        top_offset = RAMP_30_TOP_OFFSET \
            if self._goal.get_ramp_type() == ramps.Ramp.RAMP_30 \
               else RAMP_45_TOP_OFFSET
        left_to_right = self._goal.is_left_to_right()
        if left_to_right:
            bottom_offset *= -1
            top_offset *= -1
        return bottom_offset, top_offset

    def _make_object_faster(self, scene: Dict[str, Any]) -> None:
        target = find_target(scene)
        bottom_offset, top_offset = self._get_ramp_offsets()
        implausible_x_start = target['intphys_option']['ramp_x_term'] + bottom_offset
        implausible_step = get_position_step(target, implausible_x_start,
                                             self._goal.is_left_to_right(),
                                             True) + \
                                             target['shows'][0]['stepBegin']
        new_force = copy.deepcopy(target['forces'][0])
        new_force['stepBegin'] = implausible_step
        new_force['vector']['x'] *= 2
        target['forces'][0]['stepEnd'] = implausible_step - 1
        target['forces'].append(new_force)

    def _make_object_slower(self, scene: Dict[str, Any]) -> None:
        target = find_target(scene)
        bottom_offset, top_offset = self._get_ramp_offsets()
        implausible_x_start = target['intphys_option']['ramp_x_term'] + top_offset
        implausible_step = get_position_step(target, implausible_x_start,
                                             self._goal.is_left_to_right(),
                                             False) + \
                                             target['shows'][0]['stepBegin']
        new_force = copy.deepcopy(target['forces'][0])
        new_force['stepBegin'] = implausible_step
        new_force['vector']['x'] /= 2.0
        target['forces'][0]['stepEnd'] = implausible_step - 1
        target['forces'].append(new_force)
        pass


QUARTET_TYPES: List[Type[Quartet]] = [GravityQuartet, ObjectPermanenceQuartet, ShapeConstancyQuartet, SpatioTemporalContinuityQuartet]


def get_quartet_class(name: str) -> Type[Quartet]:
    class_name = name + 'Quartet'
    klass = globals()[class_name]
    return klass


def get_quartet_types() -> List[str]:
    return [klass.__name__.replace('Quartet', '') for klass in QUARTET_TYPES]
