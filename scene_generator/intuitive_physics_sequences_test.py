import intuitive_physics_sequences
import materials
import math
import objects
import occluders
import pytest
import random
import util


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


def test_get_position_step():
    target = {
        'chosenMovement': objects.get('INTPHYS')[0]['intuitivePhysics'][0]
    }
    x = 1.0
    expected_step = 2
    step = intuitive_physics_sequences.get_position_step(target, x, False,
                                                         True)
    assert step == expected_step


def test_shape_constancy_substitute_object():
    definition_list = objects.get('INTPHYS') + objects.get('INTPHYS_NOVEL')
    assert len(definition_list) >= 2
    for definition_1 in definition_list:
        x_size_1 = definition_1['dimensions']['x']
        substitute_count = 0
        for definition_2 in definition_list:
            x_size_2 = definition_2['dimensions']['x']
            if (
                definition_1 != definition_2 and
                x_size_1 >= x_size_2 and
                (x_size_1 - util.MAX_SIZE_DIFFERENCE) <= x_size_2
            ):
                substitute_count += 1
        print(f'TYPE={definition_1["type"]} MASS={definition_1["mass"]} '
              f'X_SIZE={x_size_1} substitute_count={substitute_count}')
        # We want at least two possible substitute objects.
        assert substitute_count >= 2


class IntuitivePhysicsTestIgnore():
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


def verify_scene(scene, is_move_across, implausible=False):
    assert scene['intuitivePhysics']
    assert scene['answer']['choice'] == (
        'implausible' if implausible else 'plausible'
    )
    assert scene['goal']['metadata']['choose'] == ['plausible', 'implausible']

    last_step = (60 if is_move_across else 40)
    assert scene['goal']['last_step'] == last_step
    assert scene['goal']['action_list'] == [['Pass']] * last_step
    assert scene['goal']['category'] == 'intuitive physics'
    assert 'passive' in scene['goal']['type_list']
    assert 'action none' in scene['goal']['type_list']
    assert 'intuitive physics' in scene['goal']['type_list']

    if is_move_across:
        assert 'move across' in scene['goal']['type_list']
    else:
        assert 'fall down' in scene['goal']['type_list']


def verify_sequence(tag_to_objects, room_wall_material):
    if len(tag_to_objects['background object']) > 5:
        print(f'[ERROR] TOO MANY BACKGROUND OBJECTS\n'
              f'{len(tag_to_objects["background_object"])}')
        return False

    # Verify background object position.
    max_x = intuitive_physics_sequences.BACKGROUND_MAX_X
    min_z = intuitive_physics_sequences.BACKGROUND_MIN_Z
    max_z = intuitive_physics_sequences.BACKGROUND_MAX_Z
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


def verify_sequence_ObjectPermanence(is_move_across, tag_to_objects, last_step,
                                     room_wall_material_name, ignore=None):
    if not ignore:
        ignore = IntuitivePhysicsTestIgnore()

    assert verify_sequence(tag_to_objects, room_wall_material_name)
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


def verify_sequence_ShapeConstancy(is_move_across, tag_to_objects, last_step,
                                   room_wall_material_name, ignore=None):
    if not ignore:
        ignore = IntuitivePhysicsTestIgnore()

    assert verify_sequence(tag_to_objects, room_wall_material_name)
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


def verify_sequence_SpatioTemporalContinuity(is_move_across, tag_to_objects,
                                             last_step,
                                             room_wall_material_name,
                                             ignore=None):
    if not ignore:
        ignore = IntuitivePhysicsTestIgnore()

    assert verify_sequence(tag_to_objects, room_wall_material_name)
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
    max_x = occluders.OCCLUDER_DEFAULT_MAX_X
    if -max_x > instance['shows'][0]['position']['x'] > max_x:
        print(f'[ERROR] {name} X POSITION SHOULD BE BETWEEN {-max_x} AND '
              f'{max_x}\n{name}={instance}')
        return False
    z_position_list = [
        intuitive_physics_sequences.OBJECT_NEAR_Z,
        intuitive_physics_sequences.OBJECT_FAR_Z
    ]
    if instance['shows'][0]['position']['z'] not in z_position_list:
        print(f'[ERROR] {name} Z POSITION SHOULD BE FROM THIS LIST '
              f'{z_position_list}\n{name}={instance}')
        return False
    if not (name == 'TARGET' and ignore.target_position):
        if (
            instance['shows'][0]['position']['y'] !=
            intuitive_physics_sequences.FALL_DOWN_OBJECT_Y
        ):
            print(f'[ERROR] {name} Y POSITION SHOULD ALWAYS BE '
                  f'{intuitive_physics_sequences.FALL_DOWN_OBJECT_Y}\n'
                  f'{name}={instance}')
            return False

    if not (name == 'TARGET' and ignore.target_show_step):
        # Verify object show step.
        min_begin = intuitive_physics_sequences.EARLIEST_ACTION_STEP
        max_begin = intuitive_physics_sequences.LATEST_ACTION_FALL_DOWN_STEP
        if min_begin > instance['shows'][0]['stepBegin'] > max_begin:
            print(f'[ERROR] {name} SHOW STEP BEGIN SHOULD BE BETWEEN '
                  f'{min_begin} AND {max_begin}\n{name}={instance}')
            return False

    # Verify object force properties.
    if 'forces' in instance:
        print(f'[ERROR] {name} SHOULD NOT HAVE FORCES LIST (GRAVITY IS '
              f'APPLIED AUTOMATICALLY)\n{name}={instance}')
        return False

    return True


def verify_object_list_fall_down(target_list, distractor_list, ignore):
    if not ignore:
        ignore = IntuitivePhysicsTestIgnore()

    for target in target_list:
        assert verify_object_fall_down(target, 'TARGET', ignore)
    for distractor in distractor_list:
        assert verify_object_fall_down(distractor, 'DISTRACTOR', ignore)

    # Verify each object position relative to one another.
    separation = (occluders.OCCLUDER_MIN_SCALE_X * 2) + \
        occluders.OCCLUDER_SEPARATION_X
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
    last_action_step = intuitive_physics_sequences.LAST_STEP_MOVE_ACROSS - \
        occluders.OCCLUDER_MOVEMENT_TIME

    if not (name == 'TARGET' and ignore.target_position):
        # Verify object X and Z position.
        x_position = instance['shows'][0]['position']['x']
        z_position = instance['shows'][0]['position']['z']
        if (abs(x_position) == 4.2 or abs(x_position) == 5.3):
            if z_position != intuitive_physics_sequences.OBJECT_NEAR_Z:
                print(f'[ERROR] {name} Z POSITION SHOULD BE '
                      f'{intuitive_physics_sequences.OBJECT_NEAR_Z}\n'
                      f'{name}={instance}')
                return False
        elif (abs(x_position) == 4.8 or abs(x_position) == 5.9):
            if z_position != intuitive_physics_sequences.OBJECT_FAR_Z:
                print(f'[ERROR] {name} Z POSITION SHOULD BE '
                      f'{intuitive_physics_sequences.OBJECT_FAR_Z}\n'
                      f'{name}={instance}')
                return False
        else:
            x_position_list = [-5.9, -5.3, -4.8, -4.2, 4.2, 4.8, 5.3, 5.9]
            print(f'[ERROR] {name} X POSITION SHOULD BE FROM THIS LIST '
                  f'{x_position_list}\n{name}={instance}')
            return False

        # Verify object position-by-step list.
        for i in range(len(instance['chosenMovement']['positionByStep']) - 1):
            position = instance['chosenMovement']['positionByStep'][i]
            position_next = instance['chosenMovement']['positionByStep'][i + 1]
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
        min_begin = intuitive_physics_sequences.EARLIEST_ACTION_STEP
        max_begin = last_action_step - \
            len(instance['chosenMovement']['positionByStep']) - 1
        if min_begin > instance['shows'][0]['stepBegin'] > max_begin:
            print(f'[ERROR] {name} SHOW STEP BEGIN SHOULD BE BETWEEN '
                  f'{min_begin} AND {max_begin}\n{name}={instance}')
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
        ignore = IntuitivePhysicsTestIgnore()

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
                    force_1 = object_1['chosenMovement']['force']['x'] / \
                        object_1['mass']
                    force_2 = object_2['chosenMovement']['force']['x'] / \
                        object_2['mass']
                    if abs(force_2) > abs(force_1):
                        print(f'[ERROR] MOVE ACROSS OBJECT IN FRONT OF SECOND '
                              f'OBJECT SHOULD HAVE GREATER FORCE '
                              f'OBJECT_1={object_1} OBJECT_2={object_2}')
                        return False

    return True


def verify_occluder(occluder_wall, occluder_pole, sideways=False):
    # Verify occluder wall scale.
    min_scale = occluders.OCCLUDER_MIN_SCALE_X
    max_scale = occluders.OCCLUDER_MAX_SCALE_X
    if min_scale > occluder_wall['shows'][0]['scale']['x'] > max_scale:
        print(f'[ERROR] OCCLUDER WALL X SCALE SHOULD BE BETWEEN {min_scale} '
              f'AND {max_scale}\nOCCLUDER_WALL={occluder_wall}')
        return False

    # Verify occluder wall position.
    max_x = occluders.OCCLUDER_MAX_X - \
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
                    occluders.OCCLUDER_SEPARATION_X +
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
            intuitive_physics_sequences.NEAR_SIGHT_ANGLE_FACTOR_X
            if target['shows'][0]['position']['z'] ==
            intuitive_physics_sequences.OBJECT_NEAR_Z
            else intuitive_physics_sequences.FAR_SIGHT_ANGLE_FACTOR_X
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
            intuitive_physics_sequences.NEAR_SIGHT_ANGLE_FACTOR_X
            if target['shows'][0]['position']['z'] ==
            intuitive_physics_sequences.OBJECT_NEAR_Z
            else intuitive_physics_sequences.FAR_SIGHT_ANGLE_FACTOR_X
        )
        x_position = occluder_wall['shows'][0]['position']['x'] / factor
        x_position_verified = False
        for position in target['chosenMovement']['positionByStep']:
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


def test_ObjectPermanenceSequence_default_objects_fall_down():
    sequence = intuitive_physics_sequences.ObjectPermanenceSequence(
        BODY_TEMPLATE,
        is_fall_down=True
    )
    assert sequence.is_fall_down()
    wall_material_tuple = random.choice(materials.CEILING_AND_WALL_MATERIALS)
    tag_to_objects = sequence._create_default_objects(wall_material_tuple[0],
                                                      wall_material_tuple[1])
    assert verify_sequence_ObjectPermanence(sequence.is_move_across(),
                                            tag_to_objects,
                                            sequence._last_step,
                                            wall_material_tuple[0])


def test_ObjectPermanenceSequence_default_objects_move_across():
    sequence = intuitive_physics_sequences.ObjectPermanenceSequence(
        BODY_TEMPLATE,
        is_move_across=True
    )
    assert sequence.is_move_across()
    wall_material_tuple = random.choice(materials.CEILING_AND_WALL_MATERIALS)
    tag_to_objects = sequence._create_default_objects(wall_material_tuple[0],
                                                      wall_material_tuple[1])
    assert verify_sequence_ObjectPermanence(sequence.is_move_across(),
                                            tag_to_objects,
                                            sequence._last_step,
                                            wall_material_tuple[0])


def test_ObjectPermanenceSequence_default_scene_fall_down():
    sequence = intuitive_physics_sequences.ObjectPermanenceSequence(
        BODY_TEMPLATE,
        is_fall_down=True
    )
    assert sequence.is_fall_down()
    scene = sequence._create_default_scene(
        BODY_TEMPLATE,
        intuitive_physics_sequences.ObjectPermanenceSequence.GOAL_TEMPLATE
    )
    verify_scene(scene, sequence.is_move_across())
    assert set(scene['goal']['domain_list']) == set(
        ['objects', 'object solidity', 'object motion', 'object permanence']
    )
    assert 'object permanence' in scene['goal']['type_list']


def test_ObjectPermanenceSequence_default_scene_move_across():
    sequence = intuitive_physics_sequences.ObjectPermanenceSequence(
        BODY_TEMPLATE,
        is_move_across=True
    )
    assert sequence.is_move_across()
    scene = sequence._create_default_scene(
        BODY_TEMPLATE,
        intuitive_physics_sequences.ObjectPermanenceSequence.GOAL_TEMPLATE
    )
    verify_scene(scene, sequence.is_move_across())
    assert set(scene['goal']['domain_list']) == set(
        ['objects', 'object solidity', 'object motion', 'object permanence']
    )
    assert 'object permanence' in scene['goal']['type_list']


def test_ShapeConstancySequence_default_objects_fall_down():
    sequence = intuitive_physics_sequences.ShapeConstancySequence(
        BODY_TEMPLATE,
        is_fall_down=True
    )
    assert sequence.is_fall_down()
    wall_material_tuple = random.choice(materials.CEILING_AND_WALL_MATERIALS)
    tag_to_objects = sequence._create_default_objects(wall_material_tuple[0],
                                                      wall_material_tuple[1])
    assert verify_sequence_ShapeConstancy(sequence.is_move_across(),
                                          tag_to_objects, sequence._last_step,
                                          wall_material_tuple[0])


def test_ShapeConstancySequence_default_objects_move_across():
    sequence = intuitive_physics_sequences.ShapeConstancySequence(
        BODY_TEMPLATE,
        is_move_across=True
    )
    assert sequence.is_move_across()
    wall_material_tuple = random.choice(materials.CEILING_AND_WALL_MATERIALS)
    tag_to_objects = sequence._create_default_objects(wall_material_tuple[0],
                                                      wall_material_tuple[1])
    assert verify_sequence_ShapeConstancy(sequence.is_move_across(),
                                          tag_to_objects, sequence._last_step,
                                          wall_material_tuple[0])


def test_ShapeConstancySequence_default_scene_fall_down():
    sequence = intuitive_physics_sequences.ShapeConstancySequence(
        BODY_TEMPLATE,
        is_fall_down=True
    )
    assert sequence.is_fall_down()
    scene = sequence._create_default_scene(
        BODY_TEMPLATE,
        intuitive_physics_sequences.ShapeConstancySequence.GOAL_TEMPLATE
    )
    verify_scene(scene, sequence.is_move_across())
    assert set(scene['goal']['domain_list']) == set(
        ['objects', 'object solidity', 'object motion', 'object permanence']
    )
    assert 'shape constancy' in scene['goal']['type_list']


def test_ShapeConstancySequence_default_scene_move_across():
    sequence = intuitive_physics_sequences.ShapeConstancySequence(
        BODY_TEMPLATE,
        is_move_across=True
    )
    assert sequence.is_move_across()
    scene = sequence._create_default_scene(
        BODY_TEMPLATE,
        intuitive_physics_sequences.ShapeConstancySequence.GOAL_TEMPLATE
    )
    verify_scene(scene, sequence.is_move_across())
    assert set(scene['goal']['domain_list']) == set(
        ['objects', 'object solidity', 'object motion', 'object permanence']
    )
    assert 'shape constancy' in scene['goal']['type_list']


def test_SpatioTemporalContinuitySequence_default_objects_fall_down():
    sequence = intuitive_physics_sequences.SpatioTemporalContinuitySequence(
        BODY_TEMPLATE,
        is_fall_down=True
    )
    assert sequence.is_fall_down()
    wall_material_tuple = random.choice(materials.CEILING_AND_WALL_MATERIALS)
    tag_to_objects = sequence._create_default_objects(wall_material_tuple[0],
                                                      wall_material_tuple[1])
    assert verify_sequence_SpatioTemporalContinuity(sequence.is_move_across(),
                                                    tag_to_objects,
                                                    sequence._last_step,
                                                    wall_material_tuple[0])


def test_SpatioTemporalContinuitySequence_default_objects_move_across():
    sequence = intuitive_physics_sequences.SpatioTemporalContinuitySequence(
        BODY_TEMPLATE,
        is_move_across=True
    )
    assert sequence.is_move_across()
    wall_material_tuple = random.choice(materials.CEILING_AND_WALL_MATERIALS)
    tag_to_objects = sequence._create_default_objects(wall_material_tuple[0],
                                                      wall_material_tuple[1])
    assert verify_sequence_SpatioTemporalContinuity(sequence.is_move_across(),
                                                    tag_to_objects,
                                                    sequence._last_step,
                                                    wall_material_tuple[0])


def test_SpatioTemporalContinuitySequence_default_scene_fall_down():
    sequence = intuitive_physics_sequences.SpatioTemporalContinuitySequence(
        BODY_TEMPLATE,
        is_fall_down=True
    )
    assert sequence.is_fall_down()
    scene = sequence._create_default_scene(
        BODY_TEMPLATE,
        intuitive_physics_sequences.SpatioTemporalContinuitySequence.GOAL_TEMPLATE  # noqa: E501
    )
    verify_scene(scene, sequence.is_move_across())
    assert set(scene['goal']['domain_list']) == set(
        ['objects', 'object solidity', 'object motion', 'object permanence']
    )
    assert 'spatio temporal continuity' in scene['goal']['type_list']


def test_SpatioTemporalContinuitySequence_default_scene_move_across():
    sequence = intuitive_physics_sequences.SpatioTemporalContinuitySequence(
        BODY_TEMPLATE,
        is_move_across=True
    )
    assert sequence.is_move_across()
    scene = sequence._create_default_scene(
        BODY_TEMPLATE,
        intuitive_physics_sequences.SpatioTemporalContinuitySequence.GOAL_TEMPLATE  # noqa: E501
    )
    verify_scene(scene, sequence.is_move_across())
    assert set(scene['goal']['domain_list']) == set(
        ['objects', 'object solidity', 'object motion', 'object permanence']
    )
    assert 'spatio temporal continuity' in scene['goal']['type_list']


def find_implausible_event_step_offset(target, occluder):
    """Return the list of implausible event step offsets for the given
    move-across target."""
    factor = (
        intuitive_physics_sequences.NEAR_SIGHT_ANGLE_FACTOR_X
        if target['shows'][0]['position']['z'] ==
        intuitive_physics_sequences.OBJECT_NEAR_Z
        else intuitive_physics_sequences.FAR_SIGHT_ANGLE_FACTOR_X
    )
    occluder_x = occluder['shows'][0]['position']['x'] / factor
    for i in range(len(target['chosenMovement']['positionByStep'])):
        target_x = target['chosenMovement']['positionByStep'][i]
        if math.isclose(occluder_x, target_x):
            print(f'RETURN {i}\nTARGET_X={target_x}\nOCCLUDER_X={occluder_x}')
            return i
    print(f'OCCLUDER={occluder}')
    pytest.fail()


def verify_shape_constancy_two_targets(template_a, template_b, target_a,
                                       target_b):
    if target_a:
        print(f'TARGET_A={target_a}')
        assert target_a['id'] == template_a['id']
        assert target_a['type'] == template_a['type']
        assert target_a['id'] == template_b['id']
        assert target_a['type'] != template_b['type']
    if target_b:
        print(f'TARGET_B={target_b}')
        assert target_b['id'] == template_b['id']
        assert target_b['type'] == template_b['type']
        assert target_b['id'] == template_a['id']
        assert target_b['type'] != template_a['type']


def verify_target_implausible_hide_step(sequence, target):
    if sequence.is_move_across():
        step_offset = find_implausible_event_step_offset(
            target,
            sequence._occluder_list[0]
        )
        assert step_offset > 0
        assert target['hides'][0]['stepBegin'] == (
            target['shows'][0]['stepBegin'] + step_offset
        )
    else:
        assert target['hides'][0]['stepBegin'] == (
            target['shows'][0]['stepBegin'] +
            intuitive_physics_sequences.OBJECT_FALL_TIME
        )
    return True


def verify_target_implausible_show_step(sequence, target):
    # Find the original show step from the target template in the sequence.
    original_show_action = sequence._target_list[0]['shows'][0]
    if sequence.is_move_across():
        step_offset = find_implausible_event_step_offset(
            target,
            sequence._occluder_list[0]
        )
        assert step_offset > 0
        assert target['shows'][0]['stepBegin'] == (
            original_show_action['stepBegin'] + step_offset
        )
        assert target['shows'][0]['position']['x'] == (
            target['chosenMovement']['positionByStep'][step_offset]
        )
        assert target['shows'][0]['position']['z'] == (
            original_show_action['position']['z']
        )
    else:
        assert target['shows'][0]['stepBegin'] == (
            original_show_action['stepBegin'] +
            intuitive_physics_sequences.OBJECT_FALL_TIME
        )
        assert target['shows'][0]['position']['x'] == (
            original_show_action['position']['x']
        )
        assert target['shows'][0]['position']['z'] == (
            original_show_action['position']['z']
        )
    return True


def verify_sequence_ObjectPermanence_scene_1(sequence):
    scene = sequence.get_scenes()[0]

    target = scene['objects'][0]
    print(f'TARGET={target}')
    assert target['id'] == sequence._target_list[0]['id']

    verify_scene(scene, sequence.is_move_across())
    verify_sequence_ObjectPermanence(sequence.is_move_across(), {
        'target': [target],
        'distractor': sequence._distractor_list,
        'occluder': sequence._occluder_list,
        'background object': sequence._background_list
    }, sequence._last_step, scene['wallMaterial'])

    assert 'object permanence show object' in scene['goal']['type_list']
    assert 'hides' not in target


def verify_sequence_ObjectPermanence_scene_2(sequence):
    # _appear_behind_occluder
    scene = sequence.get_scenes()[1]

    target = scene['objects'][0]
    print(f'TARGET={target}')
    assert target['id'] == sequence._target_list[0]['id']

    verify_scene(scene, sequence.is_move_across(), implausible=True)
    verify_sequence_ObjectPermanence(sequence.is_move_across(), {
        'target': [target],
        'distractor': sequence._distractor_list,
        'occluder': sequence._occluder_list,
        'background object': sequence._background_list
    }, sequence._last_step, scene['wallMaterial'])

    assert (
        'object permanence show then hide object' in scene['goal']['type_list']
    )
    assert verify_target_implausible_hide_step(sequence, target)


def verify_sequence_ObjectPermanence_scene_3(sequence):
    # _disappear_behind_occluder
    scene = sequence.get_scenes()[2]

    target = scene['objects'][0]
    print(f'TARGET={target}')
    assert target['id'] == sequence._target_list[0]['id']

    verify_scene(scene, sequence.is_move_across(), implausible=True)
    ignore = IntuitivePhysicsTestIgnore(target_position=True,
                                        target_show_step=True)
    verify_sequence_ObjectPermanence(sequence.is_move_across(), {
        'target': [target],
        'distractor': sequence._distractor_list,
        'occluder': sequence._occluder_list,
        'background object': sequence._background_list
    }, sequence._last_step, scene['wallMaterial'], ignore)

    assert (
        'object permanence hide then show object' in scene['goal']['type_list']
    )
    assert 'hides' not in target
    assert verify_target_implausible_show_step(sequence, target)


def verify_sequence_ObjectPermanence_scene_4(sequence):
    scene = sequence.get_scenes()[3]

    assert scene['objects'][0]['id'] != sequence._target_list[0]['id']

    verify_scene(scene, sequence.is_move_across())
    ignore = IntuitivePhysicsTestIgnore(target=True)
    verify_sequence_ObjectPermanence(sequence.is_move_across(), {
        'target': [],
        'distractor': sequence._distractor_list,
        'occluder': sequence._occluder_list,
        'background object': sequence._background_list
    }, sequence._last_step, scene['wallMaterial'], ignore)

    assert 'object permanence hide object' in scene['goal']['type_list']


def test_ObjectPermanenceQuartet_get_scene_1_fall_down():
    sequence = intuitive_physics_sequences.ObjectPermanenceSequence(
        BODY_TEMPLATE,
        is_fall_down=True
    )
    assert sequence.is_fall_down()
    verify_sequence_ObjectPermanence_scene_1(sequence)


def test_ObjectPermanenceQuartet_get_scene_1_move_across():
    sequence = intuitive_physics_sequences.ObjectPermanenceSequence(
        BODY_TEMPLATE,
        is_move_across=True
    )
    assert sequence.is_move_across()
    verify_sequence_ObjectPermanence_scene_1(sequence)


def test_ObjectPermanenceQuartet_get_scene_2_fall_down():
    sequence = intuitive_physics_sequences.ObjectPermanenceSequence(
        BODY_TEMPLATE,
        is_fall_down=True
    )
    assert sequence.is_fall_down()
    verify_sequence_ObjectPermanence_scene_2(sequence)


def test_ObjectPermanenceQuartet_get_scene_2_move_across():
    sequence = intuitive_physics_sequences.ObjectPermanenceSequence(
        BODY_TEMPLATE,
        is_move_across=True
    )
    assert sequence.is_move_across()
    verify_sequence_ObjectPermanence_scene_2(sequence)


def test_ObjectPermanenceQuartet_get_scene_3_fall_down():
    sequence = intuitive_physics_sequences.ObjectPermanenceSequence(
        BODY_TEMPLATE,
        is_fall_down=True
    )
    assert sequence.is_fall_down()
    verify_sequence_ObjectPermanence_scene_3(sequence)


def test_ObjectPermanenceQuartet_get_scene_3_move_across():
    sequence = intuitive_physics_sequences.ObjectPermanenceSequence(
        BODY_TEMPLATE,
        is_move_across=True
    )
    assert sequence.is_move_across()
    verify_sequence_ObjectPermanence_scene_3(sequence)


def test_ObjectPermanenceQuartet_get_scene_4_fall_down():
    sequence = intuitive_physics_sequences.ObjectPermanenceSequence(
        BODY_TEMPLATE,
        is_fall_down=True
    )
    assert sequence.is_fall_down()
    verify_sequence_ObjectPermanence_scene_4(sequence)


def test_ObjectPermanenceQuartet_get_scene_4_move_across():
    sequence = intuitive_physics_sequences.ObjectPermanenceSequence(
        BODY_TEMPLATE,
        is_move_across=True
    )
    assert sequence.is_move_across()
    verify_sequence_ObjectPermanence_scene_4(sequence)


def verify_sequence_ShapeConstancy_scene_1(sequence):
    scene = sequence.get_scenes()[0]

    target_a = scene['objects'][0]
    verify_shape_constancy_two_targets(sequence._target_list[0],
                                       sequence._b_template, target_a, None)

    verify_scene(scene, sequence.is_move_across())
    verify_sequence_ShapeConstancy(sequence.is_move_across(), {
        'target': [target_a],
        'distractor': sequence._distractor_list,
        'occluder': sequence._occluder_list,
        'background object': sequence._background_list
    }, sequence._last_step, scene['wallMaterial'])

    assert 'shape constancy object one' in scene['goal']['type_list']
    assert 'hides' not in target_a


def verify_sequence_ShapeConstancy_scene_2(sequence):
    # _turn_a_into_b
    scene = sequence.get_scenes()[1]

    target_a = scene['objects'][0]
    target_b = scene['objects'][-1]
    verify_shape_constancy_two_targets(sequence._target_list[0],
                                       sequence._b_template, target_a,
                                       target_b)

    verify_scene(scene, sequence.is_move_across(), implausible=True)
    verify_sequence_ShapeConstancy(sequence.is_move_across(), {
        'target': [target_a],
        'distractor': sequence._distractor_list,
        'occluder': sequence._occluder_list,
        'background object': sequence._background_list
    }, sequence._last_step, scene['wallMaterial'])

    assert 'shape constancy object one into two' in scene['goal']['type_list']
    assert (
        target_a['hides'][0]['stepBegin'] == target_b['shows'][0]['stepBegin']
    )
    assert verify_target_implausible_hide_step(sequence, target_a)
    assert verify_target_implausible_show_step(sequence, target_b)


def verify_sequence_ShapeConstancy_scene_3(sequence):
    # _turn_b_into_a
    scene = sequence.get_scenes()[2]

    target_a = scene['objects'][0]
    target_b = scene['objects'][-1]
    verify_shape_constancy_two_targets(sequence._target_list[0],
                                       sequence._b_template, target_a,
                                       target_b)

    verify_scene(scene, sequence.is_move_across(), implausible=True)
    verify_sequence_ShapeConstancy(sequence.is_move_across(), {
        'target': [target_b],
        'distractor': sequence._distractor_list,
        'occluder': sequence._occluder_list,
        'background object': sequence._background_list
    }, sequence._last_step, scene['wallMaterial'])

    assert 'shape constancy object two into one' in scene['goal']['type_list']
    assert (
        target_b['hides'][0]['stepBegin'] == target_a['shows'][0]['stepBegin']
    )
    assert verify_target_implausible_hide_step(sequence, target_b)
    assert verify_target_implausible_show_step(sequence, target_a)


def verify_sequence_ShapeConstancy_scene_4(sequence):
    # _b_replaces_a
    scene = sequence.get_scenes()[3]

    target_b = scene['objects'][0]
    verify_shape_constancy_two_targets(sequence._target_list[0],
                                       sequence._b_template, None, target_b)

    verify_scene(scene, sequence.is_move_across())
    verify_sequence_ShapeConstancy(sequence.is_move_across(), {
        'target': [target_b],
        'distractor': sequence._distractor_list,
        'occluder': sequence._occluder_list,
        'background object': sequence._background_list
    }, sequence._last_step, scene['wallMaterial'])

    assert 'shape constancy object two' in scene['goal']['type_list']
    assert 'hides' not in target_b


def test_ShapeConstancyQuartet_get_scene_1_fall_down():
    sequence = intuitive_physics_sequences.ShapeConstancySequence(
        BODY_TEMPLATE,
        is_fall_down=True
    )
    assert sequence.is_fall_down()
    verify_sequence_ShapeConstancy_scene_1(sequence)


def test_ShapeConstancyQuartet_get_scene_1_move_across():
    sequence = intuitive_physics_sequences.ShapeConstancySequence(
        BODY_TEMPLATE,
        is_move_across=True
    )
    assert sequence.is_move_across()
    verify_sequence_ShapeConstancy_scene_1(sequence)


def test_ShapeConstancyQuartet_get_scene_2_fall_down():
    sequence = intuitive_physics_sequences.ShapeConstancySequence(
        BODY_TEMPLATE,
        is_fall_down=True
    )
    assert sequence.is_fall_down()
    verify_sequence_ShapeConstancy_scene_2(sequence)


def test_ShapeConstancyQuartet_get_scene_2_move_across():
    sequence = intuitive_physics_sequences.ShapeConstancySequence(
        BODY_TEMPLATE,
        is_move_across=True
    )
    assert sequence.is_move_across()
    verify_sequence_ShapeConstancy_scene_2(sequence)


def test_ShapeConstancyQuartet_get_scene_3_fall_down():
    sequence = intuitive_physics_sequences.ShapeConstancySequence(
        BODY_TEMPLATE,
        is_fall_down=True
    )
    assert sequence.is_fall_down()
    verify_sequence_ShapeConstancy_scene_3(sequence)


def test_ShapeConstancyQuartet_get_scene_3_move_across():
    sequence = intuitive_physics_sequences.ShapeConstancySequence(
        BODY_TEMPLATE,
        is_move_across=True
    )
    assert sequence.is_move_across()
    verify_sequence_ShapeConstancy_scene_3(sequence)


def test_ShapeConstancyQuartet_get_scene_4_fall_down():
    sequence = intuitive_physics_sequences.ShapeConstancySequence(
        BODY_TEMPLATE,
        is_fall_down=True
    )
    assert sequence.is_fall_down()
    verify_sequence_ShapeConstancy_scene_4(sequence)


def test_ShapeConstancyQuartet_get_scene_4_move_across():
    sequence = intuitive_physics_sequences.ShapeConstancySequence(
        BODY_TEMPLATE,
        is_move_across=True
    )
    assert sequence.is_move_across()
    verify_sequence_ShapeConstancy_scene_4(sequence)


def verify_sequence_SpatioTemporalContinuity_scene_1(sequence):
    scene = sequence.get_scenes()[0]

    target = scene['objects'][0]
    print(f'TARGET={target}')
    assert target['id'] == sequence._target_list[0]['id']

    occluder_list = sequence._occluder_list
    print(f'OCCLUDER_LIST={occluder_list}')

    verify_scene(scene, sequence.is_move_across())
    verify_sequence_SpatioTemporalContinuity(sequence.is_move_across(), {
        'target': [target],
        'distractor': sequence._distractor_list,
        'occluder': occluder_list,
        'background object': sequence._background_list
    }, sequence._last_step, scene['wallMaterial'])

    assert (
        'spatio temporal continuity move earlier' in scene['goal']['type_list']
    )
    assert 'hides' not in target
    assert 'teleports' not in target

    return scene, target, occluder_list


def verify_sequence_SpatioTemporalContinuity_scene_2(sequence):
    # _teleport_forward
    scene = sequence.get_scenes()[1]

    target = scene['objects'][0]
    print(f'TARGET={target}')
    assert target['id'] == sequence._target_list[0]['id']

    occluder_list = sequence._occluder_list
    print(f'OCCLUDER_LIST={occluder_list}')

    verify_scene(scene, sequence.is_move_across(), implausible=True)
    verify_sequence_SpatioTemporalContinuity(sequence.is_move_across(), {
        'target': [target],
        'distractor': sequence._distractor_list,
        'occluder': sequence._occluder_list,
        'background object': sequence._background_list
    }, sequence._last_step, scene['wallMaterial'])

    assert (
        'spatio temporal continuity teleport forward'
        in scene['goal']['type_list']
    )

    if sequence.is_fall_down() or 'hides' not in target:
        teleport = target['teleports'][0]
        assert teleport['stepBegin'] == teleport['stepEnd']
        assert teleport['position']['y'] == target['shows'][0]['position']['y']
        assert teleport['position']['z'] == target['shows'][0]['position']['z']
        assert teleport['rotation'] == target['shows'][0]['rotation']

    return scene, target, occluder_list


def verify_sequence_SpatioTemporalContinuity_scene_3(sequence):
    # _teleport_backward
    scene = sequence.get_scenes()[2]

    target = scene['objects'][0]
    print(f'TARGET={target}')
    assert target['id'] == sequence._target_list[0]['id']

    occluder_list = sequence._occluder_list
    if sequence.is_fall_down():
        # Swap the 1st pair of occluder wall and pole objects with the 2nd pair
        # in the occluder list for the asserts in the verify_sequence function.
        occluder_list = occluder_list[2:] + occluder_list[:2]
    print(f'OCCLUDER_LIST={occluder_list}')

    verify_scene(scene, sequence.is_move_across(), implausible=True)
    verify_sequence_SpatioTemporalContinuity(sequence.is_move_across(), {
        'target': [target],
        'distractor': sequence._distractor_list,
        'occluder': occluder_list,
        'background object': sequence._background_list
    }, sequence._last_step, scene['wallMaterial'])

    assert (
        'spatio temporal continuity teleport backward'
        in scene['goal']['type_list']
    )

    assert 'teleports' in target
    teleport = target['teleports'][0]
    assert teleport['stepBegin'] == teleport['stepEnd']
    assert teleport['position']['y'] == target['shows'][0]['position']['y']
    assert teleport['position']['z'] == target['shows'][0]['position']['z']
    assert teleport['rotation'] == target['shows'][0]['rotation']

    return scene, target, occluder_list


def verify_sequence_SpatioTemporalContinuity_scene_4(sequence):
    # _move_later
    scene = sequence.get_scenes()[3]

    target = scene['objects'][0]
    print(f'TARGET={target}')
    assert target['id'] == sequence._target_list[0]['id']

    occluder_list = sequence._occluder_list
    if sequence.is_fall_down():
        # Swap the 1st pair of occluder wall and pole objects with the 2nd pair
        # in the occluder list for the asserts in the verify_sequence function.
        occluder_list = occluder_list[2:] + occluder_list[:2]
    print(f'OCCLUDER_LIST={occluder_list}')

    verify_scene(scene, sequence.is_move_across())
    verify_sequence_SpatioTemporalContinuity(sequence.is_move_across(), {
        'target': [target],
        'distractor': sequence._distractor_list,
        'occluder': occluder_list,
        'background object': sequence._background_list
    }, sequence._last_step, scene['wallMaterial'])

    assert (
        'spatio temporal continuity move later' in scene['goal']['type_list']
    )
    assert 'hides' not in target
    assert 'teleports' not in target

    return scene, target, occluder_list


def test_SpatioTemporalContinuityQuartet_get_scene_1_fall_down():
    sequence = intuitive_physics_sequences.SpatioTemporalContinuitySequence(
        BODY_TEMPLATE,
        is_fall_down=True
    )
    assert sequence.is_fall_down()
    scene, target, occluder_list = \
        verify_sequence_SpatioTemporalContinuity_scene_1(sequence)

    # SpatioTemporalContinuity fall-down scene 1 specific validation.
    factor = (
        intuitive_physics_sequences.NEAR_SIGHT_ANGLE_FACTOR_X
        if target['shows'][0]['position']['z'] ==
        intuitive_physics_sequences.OBJECT_NEAR_Z
        else intuitive_physics_sequences.FAR_SIGHT_ANGLE_FACTOR_X
    )
    # Show the target directly above the 1st occluder.
    assert target['shows'][0]['position']['x'] == pytest.approx(
        occluder_list[0]['shows'][0]['position']['x'] / factor
    )


def test_SpatioTemporalContinuityQuartet_get_scene_1_move_across():
    sequence = intuitive_physics_sequences.SpatioTemporalContinuitySequence(
        BODY_TEMPLATE,
        is_move_across=True
    )
    assert sequence.is_move_across()
    scene, target, occluder_list = \
        verify_sequence_SpatioTemporalContinuity_scene_1(sequence)

    # SpatioTemporalContinuity move-across scene 1 specific validation.
    assert target['shows'][0]['stepBegin'] == (
        sequence._target_list[0]['shows'][0]['stepBegin']
    )


def test_SpatioTemporalContinuityQuartet_get_scene_2_fall_down():
    sequence = intuitive_physics_sequences.SpatioTemporalContinuitySequence(
        BODY_TEMPLATE,
        is_fall_down=True
    )
    assert sequence.is_fall_down()
    scene, target, occluder_list = \
        verify_sequence_SpatioTemporalContinuity_scene_2(sequence)

    # SpatioTemporalContinuity fall-down scene 2 specific validation.
    teleport = target['teleports'][0]
    assert teleport['stepBegin'] == (
        target['shows'][0]['stepBegin'] +
        intuitive_physics_sequences.OBJECT_FALL_TIME
    )
    factor = (
        intuitive_physics_sequences.NEAR_SIGHT_ANGLE_FACTOR_X
        if target['shows'][0]['position']['z'] ==
        intuitive_physics_sequences.OBJECT_NEAR_Z
        else intuitive_physics_sequences.FAR_SIGHT_ANGLE_FACTOR_X
    )
    # Show the target directly above the 1st occluder...
    assert target['shows'][0]['position']['x'] == pytest.approx(
        occluder_list[0]['shows'][0]['position']['x'] / factor
    )
    # ...and then teleport it behind the 2nd occluder.
    assert teleport['position']['x'] == pytest.approx(
        occluder_list[2]['shows'][0]['position']['x'] / factor
    )


def test_SpatioTemporalContinuityQuartet_get_scene_2_move_across():
    sequence = intuitive_physics_sequences.SpatioTemporalContinuitySequence(
        BODY_TEMPLATE,
        is_move_across=True
    )
    assert sequence.is_move_across()
    scene, target, occluder_list = \
        verify_sequence_SpatioTemporalContinuity_scene_2(sequence)

    # SpatioTemporalContinuity move-across scene 2 specific validation.
    step_offset_1 = find_implausible_event_step_offset(target,
                                                       occluder_list[0])
    step_offset_2 = find_implausible_event_step_offset(target,
                                                       occluder_list[2])
    assert step_offset_1 > 0
    assert step_offset_2 > 0

    # Instantaneous teleport.
    if 'hides' not in target:
        teleport = target['teleports'][0]
        # Teleport when the target is positioned behind the earlier occluder.
        assert teleport['stepBegin'] == (
            target['shows'][0]['stepBegin'] + min(step_offset_1, step_offset_2)
        )
        # Teleport to the position behind the later occluder.
        assert teleport['position']['x'] == (
            target['chosenMovement']['positionByStep'][
                max(step_offset_1, step_offset_2)
            ]
        )

    # Delayed teleport (it's really a hide-then-show).
    else:
        # Hide when the target is positioned behind the earlier occluder.
        assert target['hides'][0]['stepBegin'] == (
            target['shows'][0]['stepBegin'] + min(step_offset_1, step_offset_2)
        )
        assert len(target['shows']) == 2
        show_first = target['shows'][0]
        show_later = target['shows'][1]
        # Show when the target should be positioned behind the later occluder.
        assert show_later['stepBegin'] == (
            show_first['stepBegin'] + max(step_offset_1, step_offset_2) + 1
        )
        assert show_later['position']['x'] == (
            target['chosenMovement']['positionByStep'][
                max(step_offset_1, step_offset_2)
            ]
        )
        assert show_later['position']['y'] == show_first['position']['y']
        assert show_later['position']['z'] == show_first['position']['z']
        assert show_later['rotation'] == show_first['rotation']


def test_SpatioTemporalContinuityQuartet_get_scene_3_fall_down():
    sequence = intuitive_physics_sequences.SpatioTemporalContinuitySequence(
        BODY_TEMPLATE,
        is_fall_down=True
    )
    assert sequence.is_fall_down()
    scene, target, occluder_list = \
        verify_sequence_SpatioTemporalContinuity_scene_3(sequence)

    # SpatioTemporalContinuity fall-down scene 3 specific validation.
    teleport = target['teleports'][0]
    assert teleport['stepBegin'] == (
        target['shows'][0]['stepBegin'] +
        intuitive_physics_sequences.OBJECT_FALL_TIME
    )
    factor = (
        intuitive_physics_sequences.NEAR_SIGHT_ANGLE_FACTOR_X
        if target['shows'][0]['position']['z'] ==
        intuitive_physics_sequences.OBJECT_NEAR_Z
        else intuitive_physics_sequences.FAR_SIGHT_ANGLE_FACTOR_X
    )
    # Show the target directly above the 2nd occluder (remember that the
    # two occluder pairs in the list were switched above)...
    assert target['shows'][0]['position']['x'] == pytest.approx(
        occluder_list[0]['shows'][0]['position']['x'] / factor
    )
    # ...and then teleport it behind the 1st occluder.
    assert teleport['position']['x'] == pytest.approx(
        occluder_list[2]['shows'][0]['position']['x'] / factor
    )


def test_SpatioTemporalContinuityQuartet_get_scene_3_move_across():
    sequence = intuitive_physics_sequences.SpatioTemporalContinuitySequence(
        BODY_TEMPLATE,
        is_move_across=True
    )
    assert sequence.is_move_across()
    scene, target, occluder_list = \
        verify_sequence_SpatioTemporalContinuity_scene_3(sequence)

    # SpatioTemporalContinuity move-across scene 3 specific validation.
    teleport = target['teleports'][0]
    step_offset_1 = find_implausible_event_step_offset(target,
                                                       occluder_list[0])
    step_offset_2 = find_implausible_event_step_offset(target,
                                                       occluder_list[2])
    assert step_offset_1 > 0
    assert step_offset_2 > 0
    # Teleport when the target is positioned behind the later occluder.
    assert teleport['stepBegin'] == (
        target['shows'][0]['stepBegin'] + max(step_offset_1, step_offset_2)
    )
    # Teleport to the position behind the earlier occluder.
    assert teleport['position']['x'] == (
        target['chosenMovement']['positionByStep'][
            min(step_offset_1, step_offset_2)
        ]
    )


def test_SpatioTemporalContinuityQuartet_get_scene_4_fall_down():
    sequence = intuitive_physics_sequences.SpatioTemporalContinuitySequence(
        BODY_TEMPLATE,
        is_fall_down=True
    )
    assert sequence.is_fall_down()
    scene, target, occluder_list = \
        verify_sequence_SpatioTemporalContinuity_scene_4(sequence)

    # SpatioTemporalContinuity fall-down scene 4 specific validation.
    factor = (
        intuitive_physics_sequences.NEAR_SIGHT_ANGLE_FACTOR_X
        if target['shows'][0]['position']['z'] ==
        intuitive_physics_sequences.OBJECT_NEAR_Z
        else intuitive_physics_sequences.FAR_SIGHT_ANGLE_FACTOR_X
    )
    # Show the target directly above the 2nd occluder (remember that the
    # two occluder pairs in the list were switched above).
    assert target['shows'][0]['position']['x'] == pytest.approx(
        occluder_list[0]['shows'][0]['position']['x'] / factor
    )


def test_SpatioTemporalContinuityQuartet_get_scene_4_move_across():
    sequence = intuitive_physics_sequences.SpatioTemporalContinuitySequence(
        BODY_TEMPLATE,
        is_move_across=True
    )
    assert sequence.is_move_across()
    scene, target, occluder_list = \
        verify_sequence_SpatioTemporalContinuity_scene_4(sequence)

    # SpatioTemporalContinuity move-across scene 4 specific validation.
    step_offset_1 = find_implausible_event_step_offset(target,
                                                       occluder_list[0])
    step_offset_2 = find_implausible_event_step_offset(target,
                                                       occluder_list[2])
    assert step_offset_1 > 0
    assert step_offset_2 > 0
    assert target['shows'][0]['stepBegin'] == (
        sequence._target_list[0]['shows'][0]['stepBegin'] +
        abs(step_offset_1 - step_offset_2)
    )
