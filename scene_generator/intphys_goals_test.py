import copy
import materials
import pytest
import random
from intphys_goals import (
    IntPhysGoal, GravityGoal, ObjectPermanenceGoal,
    ShapeConstancyGoal, SpatioTemporalContinuityGoal
)


BODY_TEMPLATE = {
    'name': '',
    'ceilingMaterial': 'AI2-THOR/Materials/Walls/Drywall',
    'floorMaterial': 'AI2-THOR/Materials/Fabrics/CarpetWhite 3',
    'wallMaterial': 'AI2-THOR/Materials/Walls/DrywallBeige',
    'wallColors': ['white'],
    'performerStart': {
        'position': {
            'x': 0,
            'y': 0,
            'z': 0
        },
        'rotation': {
            'x': 0,
            'y': 0
        }
    },
    'objects': [],
    'goal': {},
    'answer': {}
}


class IntPhysQuartetTestIgnore():
    """Ignore testing specific properties in the verify functions."""

    def __init__(
        self,
        target=False,
        target_position=False,
        target_show_step=False
    ):
        self.target = target
        self.target_position = target_position
        self.target_show_step = target_show_step


def verify_body(body, is_move_across, implausible=False):
    assert body['passive']
    assert body['answer']['choice'] == (
        'implausible' if implausible else 'plausible'
    )
    assert body['goal']['metadata']['choose'] == ['plausible', 'implausible']

    last_step = (60 if is_move_across else 40)
    assert body['goal']['last_step'] == last_step
    assert body['goal']['action_list'] == [['Pass']] * last_step
    assert body['goal']['category'] == 'intphys'
    assert 'passive' in body['goal']['type_list']
    assert 'action none' in body['goal']['type_list']
    assert 'intphys' in body['goal']['type_list']

    if is_move_across:
        assert 'move across' in body['goal']['type_list']
    else:
        assert 'fall down' in body['goal']['type_list']


def verify_goal(tag_to_objects, room_wall_material):
    if len(tag_to_objects['background object']) > 5:
        print(f'[ERROR] TOO MANY BACKGROUND OBJECTS\n'
              f'{len(tag_to_objects["background_object"])}')
        return False

    # Verify background object position.
    max_x = IntPhysGoal.BACKGROUND_MAX_X
    min_z = IntPhysGoal.BACKGROUND_MIN_Z
    max_z = IntPhysGoal.BACKGROUND_MAX_Z
    for background_object in tag_to_objects['background object']:
        for corner in background_object['shows'][0]['boundingBox']:
            if -max_x > corner['x'] > max_x:
                print(f'[ERROR] BACKGROUND OBJECT X BOUNDS SHOULD BE BETWEEN '
                      f'{-max_x} AND {max_x} BUT WAS {corner["x"]}\n'
                      f'OBJECT={background_object}')
            if min_z > corner['z'] > max_z:
                print(f'[ERROR] BACKGROUND OBJECT Z BOUNDS SHOULD BE BETWEEN '
                      f'{min_z} AND {max_z} BUT WAS {corner["z"]}\n'
                      f'OBJECT={background_object}')

    for occluder in tag_to_objects['occluder']:
        if 'wall' in occluder['shape']:
            if room_wall_material in occluder['materials']:
                print(f'[ERROR] OCCLUDER MATERIAL SAME AS ROOM WALL '
                      f'ROOM_WALL_MATERIAL={room_wall_material} '
                      f'OCCLUDER={occluder}')
                return False

    return True


def verify_goal_ObjectPermanence(is_move_across, tag_to_objects, last_step,
                                 room_wall_material_name, ignore=None):
    if not ignore:
        ignore = IntPhysQuartetTestIgnore()

    assert verify_goal(tag_to_objects, room_wall_material_name)
    if not ignore.target:
        assert len(tag_to_objects['target']) == 1

    if is_move_across:
        assert 0 <= len(tag_to_objects['distractor']) <= 2
        assert verify_object_list_move_across(tag_to_objects['target'],
                                              tag_to_objects['distractor'],
                                              ignore)
        assert 2 <= len(tag_to_objects['occluder']) <= 8
        assert verify_occluder_list_move_across(tag_to_objects['occluder'],
                                                tag_to_objects['target'])
        assert last_step == 60

    else:
        assert 0 <= len(tag_to_objects['distractor']) <= 1
        assert verify_object_list_fall_down(tag_to_objects['target'],
                                            tag_to_objects['distractor'],
                                            ignore)
        assert 2 <= len(tag_to_objects['occluder']) <= 4
        if len(tag_to_objects['distractor']) == 1:
            assert len(tag_to_objects['occluder']) == 4
        assert verify_occluder_list_fall_down(tag_to_objects['occluder'],
                                              tag_to_objects['target'])
        assert last_step == 40

    return True


def verify_goal_ShapeConstancy(is_move_across, tag_to_objects, last_step,
                               room_wall_material_name, ignore=None):
    if not ignore:
        ignore = IntPhysQuartetTestIgnore()

    assert verify_goal(tag_to_objects, room_wall_material_name)
    if not ignore.target:
        assert len(tag_to_objects['target']) == 1

    if is_move_across:
        assert 0 <= len(tag_to_objects['distractor']) <= 2
        assert verify_object_list_move_across(tag_to_objects['target'],
                                              tag_to_objects['distractor'],
                                              ignore)
        assert 2 <= len(tag_to_objects['occluder']) <= 8
        assert verify_occluder_list_move_across(tag_to_objects['occluder'],
                                                tag_to_objects['target'])
        assert last_step == 60

    else:
        assert 0 <= len(tag_to_objects['distractor']) <= 1
        assert verify_object_list_fall_down(tag_to_objects['target'],
                                            tag_to_objects['distractor'],
                                            ignore)
        assert 2 <= len(tag_to_objects['occluder']) <= 4
        if len(tag_to_objects['distractor']) == 1:
            assert len(tag_to_objects['occluder']) == 4
        assert verify_occluder_list_fall_down(tag_to_objects['occluder'],
                                              tag_to_objects['target'])
        assert last_step == 40

    return True


def verify_goal_SpatioTemporalContinuity(is_move_across, tag_to_objects,
                                         last_step, room_wall_material_name,
                                         ignore=None):
    if not ignore:
        ignore = IntPhysQuartetTestIgnore()

    assert verify_goal(tag_to_objects, room_wall_material_name)
    if not ignore.target:
        assert len(tag_to_objects['target']) == 1

    target = tag_to_objects['target'][0]

    if is_move_across:
        assert 0 <= len(tag_to_objects['distractor']) <= 2
        assert verify_object_list_move_across(tag_to_objects['target'],
                                              tag_to_objects['distractor'],
                                              ignore)
        assert 4 <= len(tag_to_objects['occluder']) <= 8
        # Pass the target here twice to verify both of its paired occluders.
        assert verify_occluder_list_move_across(tag_to_objects['occluder'],
                                                [target, target])
        assert last_step == 60

    else:
        assert len(tag_to_objects['distractor']) == 0
        assert verify_object_list_fall_down(tag_to_objects['target'],
                                            tag_to_objects['distractor'],
                                            ignore)
        assert len(tag_to_objects['occluder']) == 4
        assert verify_occluder_list_fall_down(tag_to_objects['occluder'],
                                              [target])
        assert last_step == 40

    return True


def verify_object_fall_down(instance, name, ignore):
    # Verify object X and Y and Z position.
    max_x = IntPhysGoal.OCCLUDER_DEFAULT_MAX_X
    if -max_x > instance['shows'][0]['position']['x'] > max_x:
        print(f'[ERROR] {name} X POSITION SHOULD BE BETWEEN {-max_x} AND '
              f'{max_x}\n{name}={instance}')
        return False
    z_position_list = [IntPhysGoal.OBJECT_NEAR_Z, IntPhysGoal.OBJECT_FAR_Z]
    if instance['shows'][0]['position']['z'] not in z_position_list:
        print(f'[ERROR] {name} Z POSITION SHOULD BE FROM THIS LIST '
              f'{z_position_list}\n{name}={instance}')
        return False
    if not (name == 'TARGET' and ignore.target_position):
        if (
            instance['shows'][0]['position']['y'] !=
            IntPhysGoal.FALL_DOWN_OBJECT_Y
        ):
            print(f'[ERROR] {name} Y POSITION SHOULD ALWAYS BE '
                  f'{IntPhysGoal.FALL_DOWN_OBJECT_Y}\n{name}={instance}')
            return False

    if not (name == 'TARGET' and ignore.target_show_step):
        # Verify object show step.
        min_step_begin = IntPhysGoal.EARLIEST_ACTION_STEP
        max_step_begin = IntPhysGoal.LATEST_ACTION_FALL_DOWN_STEP
        if min_step_begin > instance['shows'][0]['stepBegin'] > max_step_begin:
            print(f'[ERROR] {name} SHOW STEP BEGIN SHOULD BE BETWEEN '
                  f'{min_step_begin} AND {max_step_begin}\n{name}={instance}')
            return False

    # Verify object force properties.
    if 'forces' in instance:
        print(f'[ERROR] {name} SHOULD NOT HAVE FORCES LIST (GRAVITY IS '
              f'APPLIED AUTOMATICALLY)\n{name}={instance}')
        return False

    return True


def verify_object_list_fall_down(target_list, distractor_list, ignore):
    if not ignore:
        ignore = IntPhysQuartetTestIgnore()

    for target in target_list:
        assert verify_object_fall_down(target, 'TARGET', ignore)
    for distractor in distractor_list:
        assert verify_object_fall_down(distractor, 'DISTRACTOR', ignore)

    # Verify each object position relative to one another.
    separation = (IntPhysGoal.OCCLUDER_MIN_SCALE_X * 2) + \
        IntPhysGoal.OCCLUDER_SEPARATION_X
    object_list = target_list + distractor_list
    for i in range(len(object_list)):
        for j in range(len(object_list)):
            if i != j:
                x_1 = object_list[i]['shows'][0]['position']['x']
                x_2 = object_list[j]['shows'][0]['position']['x']
                if abs(x_1 - x_2) < separation:
                    print(f'[ERROR] X POSITIONS USED BY TWO FALL DOWN OBJECTS '
                          f'ARE TOO CLOSE BECAUSE SEPARATION MUST BE AT LEAST '
                          f'{separation} BUT WAS {abs(x_1 - x_2)} '
                          f'X_1={x_1} X_2={x_2}\nOBJECT_LISTt={object_list}')
                    return False

    return True


def verify_object_move_across(instance, name, ignore):
    left_to_right = (instance['shows'][0]['position']['x'] < 0)
    last_action_step = IntPhysGoal.LAST_STEP_MOVE_ACROSS - \
        IntPhysGoal.OCCLUDER_MOVEMENT_TIME

    if not (name == 'TARGET' and ignore.target_position):
        # Verify object X and Z position.
        x_position = instance['shows'][0]['position']['x']
        z_position = instance['shows'][0]['position']['z']
        if (abs(x_position) == 4.2 or abs(x_position) == 5.3):
            if z_position != IntPhysGoal.OBJECT_NEAR_Z:
                print(f'[ERROR] {name} Z POSITION SHOULD BE '
                      f'{IntPhysGoal.OBJECT_NEAR_Z}\n{name}={instance}')
                return False
        elif (abs(x_position) == 4.8 or abs(x_position) == 5.9):
            if z_position != IntPhysGoal.OBJECT_FAR_Z:
                print(f'[ERROR] {name} Z POSITION SHOULD BE '
                      f'{IntPhysGoal.OBJECT_FAR_Z}\n{name}={instance}')
                return False
        else:
            x_position_list = [-5.9, -5.3, -4.8, -4.2, 4.2, 4.8, 5.3, 5.9]
            print(f'[ERROR] {name} X POSITION SHOULD BE FROM THIS LIST '
                  f'{x_position_list}\n{name}={instance}')
            return False

        # Verify object position-by-step list.
        for i in range(len(instance['intphysOption']['positionByStep']) - 1):
            position = instance['intphysOption']['positionByStep'][i]
            position_next = instance['intphysOption']['positionByStep'][i + 1]
            if left_to_right:
                if position >= position_next:
                    print(f'[ERROR] LEFT-TO-RIGHT {name} POSITION BY STEP '
                          f'SHOULD BE INCREASING\n{name}={instance}\n'
                          f'X_POSITION={position}\n'
                          f'X_POSITION_NEXT={position_next}')
                    return False
            else:
                if position <= position_next:
                    print(f'[ERROR] RIGHT-TO-LEFT {name} POSITION BY STEP '
                          f'SHOULD BE DECREASING\n{name}={instance}\n'
                          f'X_POSITION={position}\n'
                          f'X_POSITION_NEXT={position_next}')
                    return False

        # Verify object force properties.
        if instance['forces'][0]['stepEnd'] != last_action_step:
            print(f'[ERROR] {name} FORCE STEP END SHOULD BE LAST ACTION STEP\n'
                  f'{name}={instance}')
            return False
        if left_to_right:
            if instance['forces'][0]['vector']['x'] < 0:
                print(f'[ERROR] LEFT-TO-RIGHT {name} FORCE VECTOR X SHOULD BE '
                      f'POSITIVE\n{name}={instance}')
                return False
        else:
            if instance['forces'][0]['vector']['x'] > 0:
                print(f'[ERROR] RIGHT-TO-LEFT {name} FORCE VECTOR X SHOULD BE '
                      f'NEGATIVE\n{name}={instance}')
                return False

    if (not name == 'TARGET' and not ignore.target_show_step):
        # Verify object show step.
        min_step_begin = IntPhysGoal.EARLIEST_ACTION_STEP
        max_step_begin = last_action_step - \
            len(instance['intphysOption']['positionByStep']) - 1
        if min_step_begin > instance['shows'][0]['stepBegin'] > max_step_begin:
            print(f'[ERROR] {name} SHOW STEP BEGIN SHOULD BE BETWEEN '
                  f'{min_step_begin} AND {max_step_begin}\n{name}={instance}')
            return False
        if (
            instance['forces'][0]['stepBegin'] !=
            instance['shows'][0]['stepBegin']
        ):
            print(f'[ERROR] {name} FORCE STEP BEGIN SHOULD BE SAME AS SHOW '
                  f'STEP BEGIN\n{name}={instance}')
            return False

    return True


def verify_object_list_move_across(target_list, distractor_list, ignore):
    if not ignore:
        ignore = IntPhysQuartetTestIgnore()

    for target in target_list:
        assert verify_object_move_across(target, 'TARGET', ignore)
    for distractor in distractor_list:
        assert verify_object_move_across(distractor, 'DISTRACTOR', ignore)

    # Verify each object position relative to one another.
    position_dict = {}
    object_list = target_list + distractor_list
    for instance in object_list:
        x_str = str(instance['shows'][0]['position']['x'])
        z_str = str(instance['shows'][0]['position']['z'])
        if x_str in position_dict and z_str in position_dict[x_str]:
            print(f'[ERROR] SAME LOCATION USED BY TWO MOVE ACROSS OBJECTS '
                  f'X={x_str} Z={z_str}\nOBJECT_LIST={object_list}')
            return False
        position_dict[x_str] = position_dict[x_str] if x_str in position_dict \
            else {}
        position_dict[x_str][z_str] = True

    for object_1 in object_list:
        x_1 = object_1['shows'][0]['position']['x']
        z_1 = object_1['shows'][0]['position']['z']
        for object_2 in object_list:
            if object_1 == object_2:
                x_2 = object_2['shows'][0]['position']['x']
                z_2 = object_2['shows'][0]['position']['z']
                if z_2 == z_1 and abs(x_2) > abs(x_1):
                    begin_1 = object_1['shows'][0]['stepBegin']
                    begin_2 = object_2['shows'][0]['stepBegin']
                    if begin_2 <= begin_1:
                        print(f'[ERROR] MOVE ACROSS OBJECT IN FRONT OF SECOND '
                              f'OBJECT SHOULD HAVE SMALLER SHOW STEP BEGIN '
                              f'OBJECT_1={object_1} OBJECT_2={object_2}')
                        return False
                    force_1 = object_1['intphysOption']['force']['x'] / \
                        object_1['mass']
                    force_2 = object_2['intphysOption']['force']['x'] / \
                        object_2['mass']
                    if abs(force_2) > abs(force_1):
                        print(f'[ERROR] MOVE ACROSS OBJECT IN FRONT OF SECOND '
                              f'OBJECT SHOULD HAVE GREATER FORCE '
                              f'OBJECT_1={object_1} OBJECT_2={object_2}')
                        return False

    return True


def verify_occluder(occluder_wall, occluder_pole, sideways=False):
    # Verify occluder wall scale.
    min_scale = IntPhysGoal.OCCLUDER_MIN_SCALE_X
    max_scale = IntPhysGoal.OCCLUDER_MAX_SCALE_X
    if min_scale > occluder_wall['shows'][0]['scale']['x'] > max_scale:
        print(f'[ERROR] OCCLUDER WALL X SCALE SHOULD BE BETWEEN {min_scale} '
              f'AND {max_scale}\nOCCLUDER_WALL={occluder_wall}')
        return False

    # Verify occluder wall position.
    max_x = IntPhysGoal.OCCLUDER_MAX_X - \
        (occluder_wall['shows'][0]['scale']['x'] / 2.0)
    if -max_x > occluder_wall['shows'][0]['position']['x'] > max_x:
        print(f'[ERROR] OCCLUDER WALL X POSITION SHOULD BE BETWEEN {-max_x} '
              f'AND {max_x}\nOCCLUDER_WALL={occluder_wall}')
        return False
    if (not sideways) and (
        occluder_pole['shows'][0]['position']['x'] !=
        occluder_wall['shows'][0]['position']['x']
    ):
        print(f'[ERROR] OCCLUDER POLE X POSITION SHOULD BE SAME AS '
              f'OCCLUDER WALL\nOCCLUDER_POLE={occluder_pole}\n'
              f'OCCLUDER_WALL={occluder_wall}')
        return False

    return True


def verify_occluder_list(occluder_list, target_list, sideways=False):
    for i in range(int(len(occluder_list) / 2)):
        assert verify_occluder(occluder_list[i * 2],
                               occluder_list[(i * 2) + 1],
                               sideways)

    # Each even index is a wall and each odd is a pole.
    # Only look at the wall indices.
    for i in range(int(len(occluder_list) / 2)):
        for j in range(int(len(occluder_list) / 2)):
            if i != j:
                separation = (
                    IntPhysGoal.OCCLUDER_SEPARATION_X +
                    (occluder_list[i * 2]['shows'][0]['scale']['x'] / 2.0) +
                    (occluder_list[j * 2]['shows'][0]['scale']['x'] / 2.0)
                )
                x_1 = occluder_list[i * 2]['shows'][0]['position']['x']
                x_2 = occluder_list[j * 2]['shows'][0]['position']['x']
                if abs(x_1 - x_2) < separation:
                    print(f'[ERROR] X POSITIONS USED BY TWO OCCLUDERS ARE TOO '
                          f'CLOSE BECAUSE SEPARATION MUST BE AT LEAST '
                          f'{separation} BUT WAS {abs(x_1 - x_2)} X_1={x_1} '
                          f'X_2={x_2}\nOCCLUDER_LIST={occluder_list}')
                    return False

    for i in range(len(target_list)):
        target = target_list[i]
        occluder_wall = occluder_list[i * 2]
        if occluder_wall['shows'][0]['scale']['x'] < target['dimensions']['x']:
            print(f'[ERROR] PAIRED OCCLUDER WALL X SCALE SHOULD BE GREATER '
                  f'THAN TARGET X DIMENSIONS\nOCCLUDER_WALL={occluder_wall}\n'
                  f'TARGET={target}')
            return False

    return True


def verify_occluder_list_fall_down(occluder_list, target_list):
    assert verify_occluder_list(occluder_list, target_list, sideways=True)

    for i in range(len(target_list)):
        target = target_list[i]
        occluder_wall = occluder_list[i * 2]
        factor = (
            IntPhysGoal.NEAR_SIGHT_ANGLE_FACTOR_X
            if target['shows'][0]['position']['z'] == IntPhysGoal.OBJECT_NEAR_Z
            else IntPhysGoal.FAR_SIGHT_ANGLE_FACTOR_X
        )
        x_position = occluder_wall['shows'][0]['position']['x'] / factor
        if target['shows'][0]['position']['x'] != pytest.approx(x_position):
            print(f'[ERROR] PAIRED FALL DOWN OCCLUDER WALL X POSITION '
                  f'SHOULD BE CALCULATED FROM TARGET X POSITION\n'
                  f'OCCLUDER_WALL={occluder_wall}\nTARGET={target}\n'
                  f'X_POSITION={x_position}\nFACTOR={factor}')
            return False

    return True


def verify_occluder_list_move_across(occluder_list, target_list):
    assert verify_occluder_list(occluder_list, target_list)

    for i in range(len(target_list)):
        target = target_list[i]
        occluder_wall = occluder_list[i * 2]
        factor = (
            IntPhysGoal.NEAR_SIGHT_ANGLE_FACTOR_X
            if target['shows'][0]['position']['z'] == IntPhysGoal.OBJECT_NEAR_Z
            else IntPhysGoal.FAR_SIGHT_ANGLE_FACTOR_X
        )
        x_position = occluder_wall['shows'][0]['position']['x'] / factor
        x_position_verified = False
        for position in target['intphysOption']['positionByStep']:
            if position == pytest.approx(x_position):
                x_position_verified = True
                break
        if not x_position_verified:
            print(f'[ERROR] PAIRED MOVE ACROSS OCCLUDER WALL X POSITION '
                  f'SHOULD BE CALCULATED FROM TARGET POSITION BY STEP LIST\n'
                  f'OCCLUDER_WALL={occluder_wall}\nTARGET={target}\n'
                  f'X_POSITION={x_position}\nFACTOR={factor}')
            return False

    return True


@pytest.mark.skip(reason="TODO MCS-273")
def test_GravityGoal_compute_objects():
    goal = GravityGoal()
    tag_to_objects = goal.compute_objects(
        'dummy wall material', 'dummy wall color')
    assert len(tag_to_objects['target']) >= 1
    assert len(tag_to_objects['distractor']) >= 0
    assert len(tag_to_objects['background object']) >= 0
    assert len(tag_to_objects['ramp']) >= 1
    assert goal._last_step > 0


@pytest.mark.skip(reason="TODO MCS-273")
def test_GravityGoal_update_body():
    goal = GravityGoal()
    body = goal.update_body(copy.deepcopy(BODY_TEMPLATE), False)
    assert body['goal']['last_step'] > 0
    assert body['goal']['action_list'] == [
        ['Pass']] * body['goal']['last_step']
    assert body['goal']['category'] == 'intphys'
    assert set(body['goal']['domain_list']) == set(
        ['objects', 'object solidity', 'object motion', 'gravity'])
    assert 'passive' in body['goal']['type_list']
    assert 'action none' in body['goal']['type_list']
    assert 'intphys' in body['goal']['type_list']
    assert 'gravity' in body['goal']['type_list']
    assert ('ramp 30-degree' in body['goal']['type_list']) or \
        ('ramp 45-degree' in body['goal']['type_list']) or \
        ('ramp 90-degree' in body['goal']['type_list']) or \
        ('ramp 30-degree-90-degree' in body['goal']['type_list']) or \
        ('ramp 45-degree-90-degree' in body['goal']['type_list'])
    assert body['answer']['choice'] == 'plausible'
    assert len(body['objects']) >= 1


def test_ObjectPermanenceGoal_compute_objects_fall_down():
    goal = ObjectPermanenceGoal(is_fall_down=True)
    assert goal.is_fall_down()
    wall_material_tuple = random.choice(materials.CEILING_AND_WALL_MATERIALS)
    tag_to_objects = goal.compute_objects(wall_material_tuple[0],
                                          wall_material_tuple[1])
    assert verify_goal_ObjectPermanence(goal.is_move_across(),
                                        tag_to_objects, goal._last_step,
                                        wall_material_tuple[0])


def test_ObjectPermanenceGoal_compute_objects_move_across():
    goal = ObjectPermanenceGoal(is_move_across=True)
    assert goal.is_move_across()
    wall_material_tuple = random.choice(materials.CEILING_AND_WALL_MATERIALS)
    tag_to_objects = goal.compute_objects(wall_material_tuple[0],
                                          wall_material_tuple[1])
    assert verify_goal_ObjectPermanence(goal.is_move_across(),
                                        tag_to_objects, goal._last_step,
                                        wall_material_tuple[0])


def test_ObjectPermanenceGoal_update_body_fall_down():
    goal = ObjectPermanenceGoal(is_fall_down=True)
    assert goal.is_fall_down()
    body = goal.update_body(copy.deepcopy(BODY_TEMPLATE), False)
    verify_body(body, goal.is_move_across())
    assert set(body['goal']['domain_list']) == set(
        ['objects', 'object solidity', 'object motion', 'object permanence']
    )
    assert 'object permanence' in body['goal']['type_list']


def test_ObjectPermanenceGoal_update_body_move_across():
    goal = ObjectPermanenceGoal(is_move_across=True)
    assert goal.is_move_across()
    body = goal.update_body(copy.deepcopy(BODY_TEMPLATE), False)
    verify_body(body, goal.is_move_across())
    assert set(body['goal']['domain_list']) == set(
        ['objects', 'object solidity', 'object motion', 'object permanence']
    )
    assert 'object permanence' in body['goal']['type_list']


def test_ShapeConstancyGoal_compute_objects_fall_down():
    goal = ShapeConstancyGoal(is_fall_down=True)
    assert goal.is_fall_down()
    wall_material_tuple = random.choice(materials.CEILING_AND_WALL_MATERIALS)
    tag_to_objects = goal.compute_objects(wall_material_tuple[0],
                                          wall_material_tuple[1])
    assert verify_goal_ShapeConstancy(goal.is_move_across(),
                                      tag_to_objects, goal._last_step,
                                      wall_material_tuple[0])


def test_ShapeConstancyGoal_compute_objects_move_across():
    goal = ShapeConstancyGoal(is_move_across=True)
    assert goal.is_move_across()
    wall_material_tuple = random.choice(materials.CEILING_AND_WALL_MATERIALS)
    tag_to_objects = goal.compute_objects(wall_material_tuple[0],
                                          wall_material_tuple[1])
    assert verify_goal_ShapeConstancy(goal.is_move_across(),
                                      tag_to_objects, goal._last_step,
                                      wall_material_tuple[0])


def test_ShapeConstancyGoal_update_body_fall_down():
    goal = ShapeConstancyGoal(is_fall_down=True)
    assert goal.is_fall_down()
    body = goal.update_body(copy.deepcopy(BODY_TEMPLATE), False)
    verify_body(body, goal.is_move_across())
    assert set(body['goal']['domain_list']) == set(
        ['objects', 'object solidity', 'object motion', 'object permanence']
    )
    assert 'shape constancy' in body['goal']['type_list']


def test_ShapeConstancyGoal_update_body_move_across():
    goal = ShapeConstancyGoal(is_move_across=True)
    assert goal.is_move_across()
    body = goal.update_body(copy.deepcopy(BODY_TEMPLATE), False)
    verify_body(body, goal.is_move_across())
    assert set(body['goal']['domain_list']) == set(
        ['objects', 'object solidity', 'object motion', 'object permanence']
    )
    assert 'shape constancy' in body['goal']['type_list']


def test_SpatioTemporalContinuityGoal_compute_objects_fall_down():
    goal = SpatioTemporalContinuityGoal(is_fall_down=True)
    assert goal.is_fall_down()
    wall_material_tuple = random.choice(materials.CEILING_AND_WALL_MATERIALS)
    tag_to_objects = goal.compute_objects(wall_material_tuple[0],
                                          wall_material_tuple[1])
    assert verify_goal_SpatioTemporalContinuity(goal.is_move_across(),
                                                tag_to_objects,
                                                goal._last_step,
                                                wall_material_tuple[0])


def test_SpatioTemporalContinuityGoal_compute_objects_move_across():
    goal = SpatioTemporalContinuityGoal(is_move_across=True)
    assert goal.is_move_across()
    wall_material_tuple = random.choice(materials.CEILING_AND_WALL_MATERIALS)
    tag_to_objects = goal.compute_objects(wall_material_tuple[0],
                                          wall_material_tuple[1])
    assert verify_goal_SpatioTemporalContinuity(goal.is_move_across(),
                                                tag_to_objects,
                                                goal._last_step,
                                                wall_material_tuple[0])


def test_SpatioTemporalContinuityGoal_update_body_fall_down():
    goal = SpatioTemporalContinuityGoal(is_fall_down=True)
    assert goal.is_fall_down()
    body = goal.update_body(copy.deepcopy(BODY_TEMPLATE), False)
    verify_body(body, goal.is_move_across())
    assert set(body['goal']['domain_list']) == set(
        ['objects', 'object solidity', 'object motion', 'object permanence']
    )
    assert 'spatio temporal continuity' in body['goal']['type_list']


def test_SpatioTemporalContinuityGoal_update_body_move_across():
    goal = SpatioTemporalContinuityGoal(is_move_across=True)
    assert goal.is_move_across()
    body = goal.update_body(copy.deepcopy(BODY_TEMPLATE), False)
    verify_body(body, goal.is_move_across())
    assert set(body['goal']['domain_list']) == set(
        ['objects', 'object solidity', 'object motion', 'object permanence']
    )
    assert 'spatio temporal continuity' in body['goal']['type_list']


# test for MCS-214
@pytest.mark.skip(reason="TODO MCS-273")
def test_GravityGoal__get_ramp_and_objects():
    goal = GravityGoal()
    (
        ramp_type,
        left_to_right,
        ramp_objs,
        object_list
    ) = goal._get_ramp_and_objects('dummy')
    assert len(ramp_objs) >= 1
    for obj in object_list:
        assert obj['intphysOption']['y'] == 0
        assert obj['type'] != 'cube'
