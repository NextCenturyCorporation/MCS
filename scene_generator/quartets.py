import copy
import logging
import random
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Type, Optional, Tuple

import exceptions
import intphys_goals
import ramps
import tags
import util


def get_position_step(target: Dict[str, Any], x_position: float,
                      left_to_right: bool, forwards: bool) -> int:
    """Return the step at which the target will reach the x_position."""
    position_by_step = target['intphysOption']['positionByStep']
    if forwards:
        index_range = range(len(position_by_step))
        counting_up = not left_to_right
    else:
        index_range = range(len(position_by_step) - 1, -1, -1)
        counting_up = left_to_right
    for i in index_range:
        position = position_by_step[i]
        if counting_up and position > x_position or \
           not counting_up and position < x_position:
            return i
    raise exceptions.SceneException(
        f'Cannot find corresponding step x_position={x_position} '
        f'position_by_step={position_by_step} left_to_right={left_to_right} '
        f'forwards={forwards}')


class Quartet(ABC):
    def __init__(self, template: Dict[str, Any],
                 find_path: bool, goal: intphys_goals.IntPhysGoal):
        self._template = template
        self._find_path = find_path
        self._scenes: List[Optional[Dict[str, Any]]] = [None] * 4
        self._scene_template = copy.deepcopy(self._template)
        self._goal = goal
        self._goal.update_body(self._scene_template, self._find_path)

    def get_scene(self, q: int) -> Dict[str, Any]:
        if q < 1 or q > 4:
            raise exceptions.SceneException(
                f'Quartet scene must be between 1 and 4 but was given {q}')
        if self._scenes[q - 1]:
            return self._scenes[q - 1]
        scene = copy.deepcopy(self._scene_template)
        return self._create_scene(scene, q)

    @abstractmethod
    def _create_scene(self, scene: Dict[str, Any], q: int) -> Dict[str, Any]:
        pass

    def _get_occluder_list(
        self,
        scene: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        # Find each occluder's ID in the goal template.
        occluder_id_list = [occluder['id'] for occluder in
                            self._goal._tag_to_objects['occluder']]
        # Then find each occluder in the given scene.
        occluder_list = []
        for instance in scene['objects']:
            if instance['id'] in occluder_id_list:
                occluder_list.append(instance)
        return occluder_list

    def _get_target(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        # Find the target's ID in the goal template.
        target_id = self._goal._tag_to_objects['target'][0]['id']
        # Then find the target in the given scene.
        for instance in scene['objects']:
            if instance['id'] == target_id:
                return instance
        return None


class ObjectPermanenceQuartet(Quartet):
    def __init__(
        self,
        template: Dict[str, Any],
        find_path=False,
        is_fall_down=False,
        is_move_across=False
    ):
        super(ObjectPermanenceQuartet, self).__init__(
            template,
            find_path,
            intphys_goals.ObjectPermanenceGoal(is_fall_down, is_move_across)
        )

    def _appear_behind_occluder(self, scene: Dict[str, Any]) -> None:
        target = self._get_target(scene)

        if self._goal.is_move_across():
            # Implausible event happens after target moves behind occluder
            # in scene 1 of the quartet.
            occluder_index = target['intphysOption']['occluderIndices'][0]
            implausible_event_step = occluder_index + \
                target['forces'][0]['stepBegin']
            # Set target's X position behind occluder.
            target_appear_x = target['intphysOption']['positionByStep'][
                occluder_index
            ]
            target['shows'][0]['position']['x'] = target_appear_x

        elif self._goal.is_fall_down():
            # Implausible event happens after target falls behind occluder
            # in scene 1 of the quartet.
            implausible_event_step = (
                intphys_goals.IntPhysGoal.OBJECT_FALL_TIME +
                target['shows'][0]['stepBegin']
            )
            # Set target's Y position stationary on the ground.
            target['shows'][0]['position']['y'] = target['offset']['y']

        else:
            raise exceptions.SceneException('Unknown scene setup function!')

        # Set target to appear at implausible event step.
        target['shows'][0]['stepBegin'] = implausible_event_step

    def _disappear_behind_occluder(self, scene: Dict[str, Any]) -> None:
        target = self._get_target(scene)

        if self._goal.is_move_across():
            # Implausible event happens after target moves behind occluder
            # in scene 1 of the quartet.
            occluder_index = target['intphysOption']['occluderIndices'][0]
            implausible_event_step = occluder_index + \
                target['forces'][0]['stepBegin']

        elif self._goal.is_fall_down():
            # Implausible event happens after target falls behind occluder
            # in scene 1 of the quartet.
            implausible_event_step = (
                intphys_goals.IntPhysGoal.OBJECT_FALL_TIME +
                target['shows'][0]['stepBegin']
            )

        else:
            raise exceptions.SceneException('Unknown scene setup function!')

        # Set target to disappear at implausible event step.
        target['hides'] = [{
            'stepBegin': implausible_event_step
        }]

    def _create_scene(self, scene: Dict[str, Any], q: int) -> Dict[str, Any]:
        if q == 1:
            scene['goal']['type_list'].append(
                tags.INTPHYS_OBJECT_PERMANENCE_Q1)
        elif q == 2:
            scene['answer']['choice'] = intphys_goals.IntPhysGoal.IMPLAUSIBLE
            scene['goal']['type_list'].append(
                tags.INTPHYS_OBJECT_PERMANENCE_Q2)
            self._disappear_behind_occluder(scene)
        elif q == 3:
            scene['answer']['choice'] = intphys_goals.IntPhysGoal.IMPLAUSIBLE
            scene['goal']['type_list'].append(
                tags.INTPHYS_OBJECT_PERMANENCE_Q3)
            self._appear_behind_occluder(scene)
        elif q == 4:
            scene['goal']['type_list'].append(
                tags.INTPHYS_OBJECT_PERMANENCE_Q4)
            # Remove the target from the scene.
            target_id = self._goal._tag_to_objects['target'][0]['id']
            for i in range(len(scene['objects'])):
                if scene['objects'][i]['id'] == target_id:
                    del scene['objects'][i]
                    break
        self._scenes[q - 1] = scene
        return scene


class SpatioTemporalContinuityQuartet(Quartet):
    def __init__(
        self,
        template: Dict[str, Any],
        find_path=False,
        is_fall_down=False,
        is_move_across=False
    ):
        super(SpatioTemporalContinuityQuartet, self).__init__(
            template,
            find_path,
            intphys_goals.SpatioTemporalContinuityGoal(is_fall_down,
                                                       is_move_across)
        )
        if self._goal.is_move_across():
            self._adjust_target_max_step_begin(self._scene_template)

    def _adjust_target_max_step_begin(self, scene: Dict[str, Any]) -> None:
        # In move-across scenes, the target's step-begin must give it time to
        # finish moving in teleport-backward and move-later scenes.
        target = self._get_target(scene)
        occluder_index_1 = target['intphysOption']['occluderIndices'][0]
        occluder_index_2 = target['intphysOption']['occluderIndices'][1]
        old_step_begin = target['shows'][0]['stepBegin']
        new_step_begin = old_step_begin + \
            abs(occluder_index_1 - occluder_index_2)
        max_step_begin = scene['goal']['last_step'] - \
            len(target['intphysOption']['positionByStep'])
        if new_step_begin > max_step_begin:
            diff = new_step_begin - max_step_begin
            if diff > old_step_begin:
                raise exceptions.SceneException(
                    f'Cannot adjust target\'s step begin and must redo '
                    f'old_step_begin={old_step_begin} '
                    f'new_step_begin={new_step_begin} '
                    f'max_step_begin={max_step_begin}')
            target['shows'][0]['stepBegin'] -= diff
            if 'forces' in target:
                target['forces'][0]['stepBegin'] -= diff

    def _teleport_forward(self, scene: Dict[str, Any]) -> None:
        target = self._get_target(scene)
        occluder_list = self._get_occluder_list(scene)

        if self._goal.is_move_across():
            # Implausible event happens after target moves behind occluder.
            # Teleport forward from the lower index to the higher index.
            occluder_index_1 = target['intphysOption']['occluderIndices'][0]
            occluder_index_2 = target['intphysOption']['occluderIndices'][1]
            if occluder_index_1 < occluder_index_2:
                occluder_start_index = occluder_index_1
                occluder_end_index = occluder_index_2
            else:
                occluder_start_index = occluder_index_2
                occluder_end_index = occluder_index_1
            target_teleport_x = target['intphysOption']['positionByStep'][
                occluder_end_index
            ]
            target_position = {
                'x': target_teleport_x,
                'y': target['shows'][0]['position']['y'],
                'z': target['shows'][0]['position']['z']
            }
            implausible_event_step = occluder_start_index + \
                target['forces'][0]['stepBegin']

            if random.random() <= 0.5:
                # Delay the teleport to the step at which the target is
                # expected to appear from behind its second paired occluder.
                target['hides'] = [{
                    'stepBegin': implausible_event_step
                }]
                show_step = target['shows'][0]['stepBegin'] + \
                    occluder_end_index + 1
                target['shows'].append({
                    'stepBegin': show_step,
                    'position': target_position,
                    'rotation': target['shows'][0]['rotation']
                })
                scene['goal']['type_list'].append(
                    tags.INTPHYS_TELEPORT_DELAYED)
            else:
                # Instantaneous teleport.
                target['teleports'] = [{
                    'stepBegin': implausible_event_step,
                    'stepEnd': implausible_event_step,
                    'position': target_position,
                    'rotation': target['shows'][0]['rotation']
                }]
                scene['goal']['type_list'].append(
                    tags.INTPHYS_TELEPORT_INSTANTANEOUS)

        elif self._goal.is_fall_down():
            # Implausible event happens after target falls behind occluder.
            implausible_event_step = (
                intphys_goals.IntPhysGoal.OBJECT_FALL_TIME +
                target['shows'][0]['stepBegin']
            )
            # Find the second occluder paired with the target.
            occluder_wall_2 = occluder_list[2]
            factor = self._goal.retrieve_sight_angle_position_factor(
                target['shows'][0]['position']['z']
            )
            target_teleport_x = (
                occluder_wall_2['shows'][0]['position']['x'] / factor
            )
            target['teleports'] = [{
                'stepBegin': implausible_event_step,
                'stepEnd': implausible_event_step,
                'position': {
                    'x': target_teleport_x,
                    'y': target['shows'][0]['position']['y'],
                    'z': target['shows'][0]['position']['z']
                },
                'rotation': target['shows'][0]['rotation']
            }]

        else:
            raise exceptions.SceneException('Unknown scene setup function!')

    def _teleport_backward(self, scene: Dict[str, Any]) -> None:
        target = self._get_target(scene)
        occluder_list = self._get_occluder_list(scene)

        if self._goal.is_move_across():
            # Implausible event happens after target moves behind occluder.
            # Teleport backward from the higher index to the lower index.
            occluder_index_1 = target['intphysOption']['occluderIndices'][0]
            occluder_index_2 = target['intphysOption']['occluderIndices'][1]
            if occluder_index_1 > occluder_index_2:
                occluder_start_index = occluder_index_1
                occluder_end_index = occluder_index_2
            else:
                occluder_start_index = occluder_index_2
                occluder_end_index = occluder_index_1
            target_teleport_x = target['intphysOption']['positionByStep'][
                occluder_end_index
            ]
            implausible_event_step = occluder_start_index + \
                target['forces'][0]['stepBegin']

        # In fall-down scenes, swap the target from one occluder to another.
        elif self._goal.is_fall_down():
            # Implausible event happens after target falls behind occluder.
            implausible_event_step = (
                intphys_goals.IntPhysGoal.OBJECT_FALL_TIME +
                target['shows'][0]['stepBegin']
            )
            # Find the second occluder paired with the target.
            occluder_wall_2 = occluder_list[2]
            original_x = target['shows'][0]['position']['x']
            factor = self._goal.retrieve_sight_angle_position_factor(
                target['shows'][0]['position']['z']
            )
            # Swap starting X position, then teleport back to original X.
            target['shows'][0]['position']['x'] = (
                occluder_wall_2['shows'][0]['position']['x'] / factor
            )
            target_teleport_x = original_x

        else:
            raise exceptions.SceneException('Unknown scene setup function!')

        target['teleports'] = [{
            'stepBegin': implausible_event_step,
            'stepEnd': implausible_event_step,
            'position': {
                'x': target_teleport_x,
                'y': target['shows'][0]['position']['y'],
                'z': target['shows'][0]['position']['z']
            },
            'rotation': target['shows'][0]['rotation']
        }]

    def _move_later(self, scene: Dict[str, Any]) -> None:
        target = self._get_target(scene)
        occluder_list = self._get_occluder_list(scene)

        if self._goal.is_move_across():
            # Delay movement so it lines up with teleport-backward movement.
            occluder_index_1 = target['intphysOption']['occluderIndices'][0]
            occluder_index_2 = target['intphysOption']['occluderIndices'][1]
            adjustment = abs(occluder_index_1 - occluder_index_2)
            target['shows'][0]['stepBegin'] += adjustment
            if 'forces' in target:
                target['forces'][0]['stepBegin'] += adjustment

        # In fall-down scenes, swap the target from one occluder to another.
        elif self._goal.is_fall_down():
            # Find the second occluder paired with the target.
            occluder_wall_2 = occluder_list[2]
            factor = self._goal.retrieve_sight_angle_position_factor(
                target['shows'][0]['position']['z']
            )
            # Swap starting X position.
            target['shows'][0]['position']['x'] = (
                occluder_wall_2['shows'][0]['position']['x'] / factor
            )

        else:
            raise exceptions.SceneException('Unknown scene setup function!')

    def _create_scene(self, scene: Dict[str, Any], q: int) -> Dict[str, Any]:
        if q == 1:
            scene['goal']['type_list'].append(
                tags.INTPHYS_SPATIO_TEMPORAL_CONTINUITY_Q1)
        elif q == 2:
            scene['answer']['choice'] = intphys_goals.IntPhysGoal.IMPLAUSIBLE
            scene['goal']['type_list'].append(
                tags.INTPHYS_SPATIO_TEMPORAL_CONTINUITY_Q2)
            self._teleport_forward(scene)
        elif q == 3:
            scene['answer']['choice'] = intphys_goals.IntPhysGoal.IMPLAUSIBLE
            scene['goal']['type_list'].append(
                tags.INTPHYS_SPATIO_TEMPORAL_CONTINUITY_Q3)
            self._teleport_backward(scene)
        elif q == 4:
            scene['goal']['type_list'].append(
                tags.INTPHYS_SPATIO_TEMPORAL_CONTINUITY_Q4)
            self._move_later(scene)
        self._scenes[q - 1] = scene
        return scene


class ShapeConstancyQuartet(Quartet):
    def __init__(
        self,
        template: Dict[str, Any],
        find_path=False,
        is_fall_down=False,
        is_move_across=False
    ):
        super(ShapeConstancyQuartet, self).__init__(
            template,
            find_path,
            intphys_goals.ShapeConstancyGoal(is_fall_down, is_move_across)
        )
        self._b_template = self._create_b(self._scene_template)

    def _create_b(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        object_a = self._get_target(scene)

        # Use the X dimensions because the performer will always be facing that
        # side of the object.
        size_a = object_a['dimensions']['x']

        object_definition_list = (
            intphys_goals.IntPhysGoal.FALL_DOWN_OBJECT_DEFINITION_LIST
            if self._goal.is_fall_down()
            else intphys_goals.IntPhysGoal.OBJECT_DEFINITION_LIST
        )
        possible_definition_list = []

        for object_definition in object_definition_list:
            if object_definition['type'] != object_a['type']:
                size_b = object_definition['dimensions']['x']
                # Ensure that object B is approx the same size as object A.
                # Object B must not be any bigger than object A or else it may
                # not be properly hidden by the paired occluder(s).
                if (
                    size_b <= size_a and
                    size_b >= (size_a - util.MAX_SIZE_DIFFERENCE)
                ):
                    possible_definition_list.append(object_definition)

        if len(possible_definition_list) == 0:
            raise exceptions.SceneException(
                f'Cannot find shape constancy substitute object {object_a}')

        definition_b = util.finalize_object_definition(
            random.choice(possible_definition_list)
        )
        object_b = util.instantiate_object(
            definition_b,
            object_a['originalLocation'],
            object_a['materialsList']
        )
        object_b['id'] = object_a['id']
        return object_b

    def _turn_a_into_b(self, scene: Dict[str, Any]) -> None:
        object_a = scene['objects'][0]
        object_b = copy.deepcopy(self._b_template)

        if self._goal.is_move_across():
            # Implausible event happens after target moves behind occluder.
            occluder_index = object_a['intphysOption']['occluderIndices'][0]
            implausible_event_step = occluder_index + \
                object_a['forces'][0]['stepBegin']
            implausible_event_x = object_a['intphysOption']['positionByStep'][
                occluder_index
            ]
            # Give object B the movement of object A.
            object_b['forces'] = copy.deepcopy(object_a['forces'])
            object_b['intphysOption'] = object_a['intphysOption']

        elif self._goal.is_fall_down():
            # Implausible event happens after target falls behind occluder.
            implausible_event_step = (
                intphys_goals.IntPhysGoal.OBJECT_FALL_TIME +
                object_a['shows'][0]['stepBegin']
            )
            implausible_event_x = object_a['shows'][0]['position']['x']

        else:
            raise exceptions.SceneException('Unknown scene setup function!')

        # Hide object A at the implausible event step and show object B in
        # object A's old position behind the occluder.
        object_a['hides'] = [{
            'stepBegin': implausible_event_step
        }]
        object_b['shows'][0]['stepBegin'] = implausible_event_step
        object_b['shows'][0]['position']['x'] = implausible_event_x
        object_b['shows'][0]['position']['z'] = \
            object_a['shows'][0]['position']['z']

        # Add object B to the scene.
        scene['objects'].append(object_b)

    def _turn_b_into_a(self, scene: Dict[str, Any]) -> None:
        object_a = scene['objects'][0]
        object_b = copy.deepcopy(self._b_template)

        # Show object B at object A's starting position.
        object_b['shows'][0]['stepBegin'] = object_a['shows'][0]['stepBegin']
        object_b['shows'][0]['position']['x'] = \
            object_a['shows'][0]['position']['x']
        object_b['shows'][0]['position']['z'] = \
            object_a['shows'][0]['position']['z']

        if self._goal.is_move_across():
            # Implausible event happens after target moves behind occluder.
            occluder_index = object_a['intphysOption']['occluderIndices'][0]
            implausible_event_step = occluder_index + \
                object_a['forces'][0]['stepBegin']
            implausible_event_x = object_a['intphysOption']['positionByStep'][
                occluder_index
            ]
            # Give object B the movement of object A.
            object_b['forces'] = copy.deepcopy(object_a['forces'])
            object_b['intphysOption'] = object_a['intphysOption']
            # Change the position of object A to behind the occluder.
            object_a['shows'][0]['position']['x'] = implausible_event_x

        elif self._goal.is_fall_down():
            # Implausible event happens after target falls behind occluder.
            implausible_event_step = (
                intphys_goals.IntPhysGoal.OBJECT_FALL_TIME +
                object_a['shows'][0]['stepBegin']
            )
            # Swap object A with object B.
            object_b['shows'][0]['position']['y'] = \
                object_a['shows'][0]['position']['y']
            # Move object A to the ground.
            object_a['shows'][0]['position']['y'] = object_a['offset']['y']

        else:
            raise exceptions.SceneException('Unknown scene setup function!')

        # Wait to show object A at the implausible event step.
        object_a['shows'][0]['stepBegin'] = implausible_event_step

        # Hide object B at the implausible event step and show object A in
        # object B's old position behind the occluder.
        object_b['hides'] = [{
            'stepBegin': implausible_event_step
        }]

        # Add object B to the scene.
        scene['objects'].append(object_b)

    def _b_replaces_a(self, scene: Dict[str, Any]) -> None:
        object_a = scene['objects'][0]
        object_b = copy.deepcopy(self._b_template)
        # Give object A's starting position and movement to object B.
        # Don't accidentally copy the 'rotation' from the 'shows' list because
        # it's unique per object.
        object_b['shows'][0]['stepBegin'] = object_a['shows'][0]['stepBegin']
        object_b['shows'][0]['position'] = object_a['shows'][0]['position']
        if self._goal.is_move_across():
            object_b['forces'] = object_a['forces']
            object_b['intphysOption'] = object_a['intphysOption']
        # Swap object A with object B.
        scene['objects'][0] = object_b

    def _create_scene(self, scene: Dict[str, Any], q: int) -> Dict[str, Any]:
        target_list = self._goal._tag_to_objects['target']
        if q == 1:
            scene['goal']['type_list'].append(tags.INTPHYS_SHAPE_CONSTANCY_Q1)
        elif q == 2:
            # Object A moves behind an occluder, then object B emerges
            # from behind the occluder (implausible)
            scene['answer']['choice'] = intphys_goals.IntPhysGoal.IMPLAUSIBLE
            scene['goal']['type_list'].append(tags.INTPHYS_SHAPE_CONSTANCY_Q2)
            self._turn_a_into_b(scene)
            target_list = target_list + [scene['objects'][-1]]
        elif q == 3:
            # Object B moves behind an occluder (replacing object A's
            # movement), then object A emerges from behind the
            # occluder (implausible)
            scene['answer']['choice'] = intphys_goals.IntPhysGoal.IMPLAUSIBLE
            scene['goal']['type_list'].append(tags.INTPHYS_SHAPE_CONSTANCY_Q3)
            self._turn_b_into_a(scene)
            target_list = target_list + [scene['objects'][-1]]
        elif q == 4:
            # Object B moves normally (replacing object A's movement),
            # object A is never added to the scene (plausible)
            scene['goal']['type_list'].append(tags.INTPHYS_SHAPE_CONSTANCY_Q4)
            self._b_replaces_a(scene)
            target_list = [scene['objects'][0]]
        # We may have added or deleted a target so recreate the goal info list.
        goal_info_list = []
        for info in scene['goal']['info_list']:
            if not info.startswith('target'):
                goal_info_list.append(info)
        scene['goal']['info_list'] = self._goal.update_goal_with_object_info(
            'target',
            goal_info_list,
            target_list
        )
        self._scenes[q - 1] = scene
        return scene


class GravityQuartet(Quartet):
    RAMP_OFFSETS = {
        ramps.Ramp.RAMP_30: (-1.55, 1),
        ramps.Ramp.RAMP_45: (-2.4, -1),
        ramps.Ramp.RAMP_90: (2, 2),
        ramps.Ramp.RAMP_30_90: (0, 0),
        ramps.Ramp.RAMP_45_90: (1, 1)
    }

    RAMP_30_BOTTOM_OFFSET = -1.55
    RAMP_45_BOTTOM_OFFSET = -2.4
    RAMP_30_TOP_OFFSET = 1
    RAMP_45_TOP_OFFSET = -1

    def __init__(self, template: Dict[str, Any], find_path: bool):
        super(GravityQuartet, self).__init__(
            template,
            find_path,
            intphys_goals.GravityGoal(roll_down=False, use_fastest=True)
        )

    def _create_scene(self, scene: Dict[str, Any], q: int) -> Dict[str, Any]:
        if self._goal.is_ramp_steep():
            scene = self._get_steep_scene(scene, q)
        else:
            scene = self._get_gentle_scene(scene, q)
        self._scenes[q - 1] = scene
        return scene

    def _get_steep_scene(
            self, scene: Dict[str, Any], q: int) -> Dict[str, Any]:
        target = scene['objects'][0]
        if q == 2 or q == 4:
            # switch the target to use lowest force.x
            new_intphys_option = sorted(
                target['intphysOption']['savedOptions'],
                key=lambda io: io['force']['x']
            )[0]
            target['forces'][0]['vector']['x'] = new_intphys_option['force']['x']  # noqa: E501
            if not self._goal.is_left_to_right():
                target['forces'][0]['vector']['x'] *= -1
            # Doing nothing here for q==4 causes the downward force to
            # start before the object reaches the top of the ramp, but
            # it shouldn't affect it so we won't bother recomputing
            # all the 'positionByStep' values for the slow speed to
            # get the top-of-ramp value.
        if q == 3 or q == 4:
            scene['answer']['choice'] = intphys_goals.IntPhysGoal.IMPLAUSIBLE
            _, top_offset = self._get_ramp_offsets()
            logging.debug(f'top_offset={top_offset}')
            implausible_x_start = (
                target['intphysOption']['ramp_x_term'] + top_offset
            )
            implausible_step = get_position_step(target, implausible_x_start,
                                                 self._goal.is_left_to_right(),
                                                 False) - 1 + \
                target['shows'][0]['stepBegin']
            new_force = copy.deepcopy(target['forces'][0])
            new_force['stepBegin'] = implausible_step
            factor = 2 if q == 3 else 0.5
            new_force['vector']['y'] *= factor
            target['forces'].append(new_force)
            target['forces'][0]['stepEnd'] = implausible_step - 1

        if q == 1:
            scene['goal']['type_list'].append(
                tags.INTPHYS_GRAVITY_TRAJECTORY_Q1)
        elif q == 2:
            scene['goal']['type_list'].append(
                tags.INTPHYS_GRAVITY_TRAJECTORY_Q2)
        elif q == 3:
            scene['goal']['type_list'].append(
                tags.INTPHYS_GRAVITY_TRAJECTORY_Q3)
        elif q == 4:
            scene['goal']['type_list'].append(
                tags.INTPHYS_GRAVITY_TRAJECTORY_Q4)

        return scene

    def _get_gentle_scene(
            self, scene: Dict[str, Any], q: int) -> Dict[str, Any]:
        if q == 1:
            scene['goal']['type_list'].append(
                tags.INTPHYS_GRAVITY_ACCELERATION_Q1)
        elif q == 2:
            scene['goal']['type_list'].append(
                tags.INTPHYS_GRAVITY_ACCELERATION_Q2)
            self._make_roll_down(scene)
        elif q == 3:
            scene['answer']['choice'] = intphys_goals.IntPhysGoal.IMPLAUSIBLE
            scene['goal']['type_list'].append(
                tags.INTPHYS_GRAVITY_ACCELERATION_Q3)
            self._make_object_faster(scene)
        elif q == 4:
            scene['answer']['choice'] = intphys_goals.IntPhysGoal.IMPLAUSIBLE
            scene['goal']['type_list'].append(
                tags.INTPHYS_GRAVITY_ACCELERATION_Q4)
            self._make_roll_down(scene)
            self._make_object_slower(scene)
        return scene

    def _make_roll_down(self, scene: Dict[str, Any]) -> None:
        ramp_type = self._goal.get_ramp_type()
        for obj in scene['objects']:
            if obj.get('intphysOption', {}).get('moving_object', False):
                obj['shows'][0]['position']['x'] *= -1
                obj['forces'][0]['vector']['x'] *= -1
                # adjust height to be on top of ramp
                obj['shows'][0]['position']['y'] += ramps.RAMP_OBJECT_HEIGHTS[
                    ramp_type
                ]
                # Add a downward force to all objects moving down the
                # ramps so that they will move more realistically.
                obj['forces'][0]['vector']['y'] = obj['mass'] * \
                    intphys_goals.IntPhysGoal.RAMP_DOWNWARD_FORCE

    def _get_ramp_offsets(self) -> Tuple[float, float]:
        bottom_offset, top_offset = GravityQuartet.RAMP_OFFSETS[
            self._goal.get_ramp_type()
        ]
        left_to_right = self._goal.is_left_to_right()
        if left_to_right:
            bottom_offset *= -1
            top_offset *= -1
        return bottom_offset, top_offset

    def _make_object_faster(self, scene: Dict[str, Any]) -> None:
        target = self._get_target(scene)
        bottom_offset, top_offset = self._get_ramp_offsets()
        implausible_x_start = (
            target['intphysOption']['ramp_x_term'] + bottom_offset
        )
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
        target = self._get_target(scene)
        bottom_offset, top_offset = self._get_ramp_offsets()
        implausible_x_start = (
            target['intphysOption']['ramp_x_term'] + top_offset
        )
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


QUARTET_TYPES: List[Type[Quartet]] = [GravityQuartet,
                                      ObjectPermanenceQuartet,
                                      ShapeConstancyQuartet,
                                      SpatioTemporalContinuityQuartet]


def get_quartet_class(name: str) -> Type[Quartet]:
    class_name = name + 'Quartet'
    klass = globals()[class_name]
    return klass


def get_quartet_types() -> List[str]:
    return [klass.__name__.replace('Quartet', '') for klass in QUARTET_TYPES]
