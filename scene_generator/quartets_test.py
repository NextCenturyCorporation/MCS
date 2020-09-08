import exceptions
from intphys_goals import IntPhysGoal
from intphys_goals_test import IntPhysQuartetTestIgnore, verify_body, \
    verify_goal_ObjectPermanence, verify_goal_ShapeConstancy, \
    verify_goal_SpatioTemporalContinuity
import math
import objects
import pytest
from quartets import GravityQuartet, ShapeConstancyQuartet, \
    ObjectPermanenceQuartet, SpatioTemporalContinuityQuartet, \
    get_position_step


TEMPLATE = {'wallMaterial': 'dummy', 'wallColors': ['color']}


def test_get_position_step():
    target = {
        'intphysOption': objects.get('INTPHYS')[0]['intphysOptions'][0]
    }
    x = 1.0
    expected_step = 2
    step = get_position_step(target, x, False, True)
    assert step == expected_step


def test_get_scene_exception():
    quartet = ObjectPermanenceQuartet(TEMPLATE, False)
    with pytest.raises(exceptions.SceneException):
        quartet.get_scene(0)


def find_implausible_event_step_offset(target, occluder):
    """Return the list of implausible event step offsets for the given
    move-across target."""
    factor = (
        IntPhysGoal.NEAR_SIGHT_ANGLE_FACTOR_X
        if target['shows'][0]['position']['z'] == IntPhysGoal.OBJECT_NEAR_Z
        else IntPhysGoal.FAR_SIGHT_ANGLE_FACTOR_X
    )
    occluder_x = occluder['shows'][0]['position']['x'] / factor
    for i in range(len(target['intphysOption']['positionByStep'])):
        target_x = target['intphysOption']['positionByStep'][i]
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


def verify_target_implausible_hide_step(goal, target):
    if goal.is_move_across():
        step_offset = find_implausible_event_step_offset(
            target,
            goal._tag_to_objects['occluder'][0]
        )
        assert step_offset > 0
        assert target['hides'][0]['stepBegin'] == (
            target['shows'][0]['stepBegin'] + step_offset
        )
    else:
        assert target['hides'][0]['stepBegin'] == (
            target['shows'][0]['stepBegin'] + IntPhysGoal.OBJECT_FALL_TIME
        )
    return True


def verify_target_implausible_show_step(goal, target):
    # Find the original show step from the target template in the goal.
    original_show_action = goal._tag_to_objects['target'][0]['shows'][0]
    if goal.is_move_across():
        step_offset = find_implausible_event_step_offset(
            target,
            goal._tag_to_objects['occluder'][0]
        )
        assert step_offset > 0
        assert target['shows'][0]['stepBegin'] == (
            original_show_action['stepBegin'] + step_offset
        )
        assert target['shows'][0]['position']['x'] == (
            target['intphysOption']['positionByStep'][step_offset]
        )
        assert target['shows'][0]['position']['z'] == (
            original_show_action['position']['z']
        )
    else:
        assert target['shows'][0]['stepBegin'] == (
            original_show_action['stepBegin'] + IntPhysGoal.OBJECT_FALL_TIME
        )
        assert target['shows'][0]['position']['x'] == (
            original_show_action['position']['x']
        )
        assert target['shows'][0]['position']['z'] == (
            original_show_action['position']['z']
        )
    return True


def verify_quartet_ObjectPermanence_scene_1(quartet):
    scene = quartet.get_scene(1)
    goal = quartet._goal

    target = scene['objects'][0]
    print(f'TARGET={target}')
    assert target['id'] == goal._tag_to_objects['target'][0]['id']

    verify_body(scene, goal.is_move_across())
    verify_goal_ObjectPermanence(goal.is_move_across(), {
        'target': [target],
        'distractor': goal._tag_to_objects['distractor'],
        'occluder': goal._tag_to_objects['occluder'],
        'background object': goal._tag_to_objects['background object']
    }, goal._last_step, scene['wallMaterial'])

    assert 'object permanence show object' in scene['goal']['type_list']
    assert 'hides' not in target


def verify_quartet_ObjectPermanence_scene_2(quartet):
    # _appear_behind_occluder
    scene = quartet.get_scene(2)
    goal = quartet._goal

    target = scene['objects'][0]
    print(f'TARGET={target}')
    assert target['id'] == goal._tag_to_objects['target'][0]['id']

    verify_body(scene, goal.is_move_across(), implausible=True)
    verify_goal_ObjectPermanence(goal.is_move_across(), {
        'target': [target],
        'distractor': goal._tag_to_objects['distractor'],
        'occluder': goal._tag_to_objects['occluder'],
        'background object': goal._tag_to_objects['background object']
    }, goal._last_step, scene['wallMaterial'])

    assert (
        'object permanence show then hide object' in scene['goal']['type_list']
    )
    assert verify_target_implausible_hide_step(goal, target)


def verify_quartet_ObjectPermanence_scene_3(quartet):
    # _disappear_behind_occluder
    scene = quartet.get_scene(3)
    goal = quartet._goal

    target = scene['objects'][0]
    print(f'TARGET={target}')
    assert target['id'] == goal._tag_to_objects['target'][0]['id']

    verify_body(scene, goal.is_move_across(), implausible=True)
    ignore = IntPhysQuartetTestIgnore(target_position=True,
                                      target_show_step=True)
    verify_goal_ObjectPermanence(goal.is_move_across(), {
        'target': [target],
        'distractor': goal._tag_to_objects['distractor'],
        'occluder': goal._tag_to_objects['occluder'],
        'background object': goal._tag_to_objects['background object']
    }, goal._last_step, scene['wallMaterial'], ignore)

    assert (
        'object permanence hide then show object' in scene['goal']['type_list']
    )
    assert 'hides' not in target
    assert verify_target_implausible_show_step(goal, target)


def verify_quartet_ObjectPermanence_scene_4(quartet):
    scene = quartet.get_scene(4)
    goal = quartet._goal

    assert scene['objects'][0]['id'] != goal._tag_to_objects['target'][0]['id']

    verify_body(scene, goal.is_move_across())
    ignore = IntPhysQuartetTestIgnore(target=True)
    verify_goal_ObjectPermanence(goal.is_move_across(), {
        'target': [],
        'distractor': goal._tag_to_objects['distractor'],
        'occluder': goal._tag_to_objects['occluder'],
        'background object': goal._tag_to_objects['background object']
    }, goal._last_step, scene['wallMaterial'], ignore)

    assert 'object permanence hide object' in scene['goal']['type_list']


def verify_quartet_ShapeConstancy_scene_1(quartet):
    scene = quartet.get_scene(1)
    goal = quartet._goal

    target_a = scene['objects'][0]
    verify_shape_constancy_two_targets(goal._tag_to_objects['target'][0],
                                       quartet._b_template, target_a, None)

    verify_body(scene, goal.is_move_across())
    verify_goal_ShapeConstancy(goal.is_move_across(), {
        'target': [target_a],
        'distractor': goal._tag_to_objects['distractor'],
        'occluder': goal._tag_to_objects['occluder'],
        'background object': goal._tag_to_objects['background object']
    }, goal._last_step, scene['wallMaterial'])

    assert 'shape constancy object one' in scene['goal']['type_list']
    assert 'hides' not in target_a


def verify_quartet_ShapeConstancy_scene_2(quartet):
    # _turn_a_into_b
    scene = quartet.get_scene(2)
    goal = quartet._goal

    target_a = scene['objects'][0]
    target_b = scene['objects'][-1]
    verify_shape_constancy_two_targets(goal._tag_to_objects['target'][0],
                                       quartet._b_template, target_a, target_b)

    verify_body(scene, goal.is_move_across(), implausible=True)
    verify_goal_ShapeConstancy(goal.is_move_across(), {
        'target': [target_a],
        'distractor': goal._tag_to_objects['distractor'],
        'occluder': goal._tag_to_objects['occluder'],
        'background object': goal._tag_to_objects['background object']
    }, goal._last_step, scene['wallMaterial'])

    assert 'shape constancy object one into two' in scene['goal']['type_list']
    assert (
        target_a['hides'][0]['stepBegin'] == target_b['shows'][0]['stepBegin']
    )
    assert verify_target_implausible_hide_step(goal, target_a)
    assert verify_target_implausible_show_step(goal, target_b)


def verify_quartet_ShapeConstancy_scene_3(quartet):
    # _turn_b_into_a
    scene = quartet.get_scene(3)
    goal = quartet._goal

    target_a = scene['objects'][0]
    target_b = scene['objects'][-1]
    verify_shape_constancy_two_targets(goal._tag_to_objects['target'][0],
                                       quartet._b_template, target_a, target_b)

    verify_body(scene, goal.is_move_across(), implausible=True)
    verify_goal_ShapeConstancy(goal.is_move_across(), {
        'target': [target_b],
        'distractor': goal._tag_to_objects['distractor'],
        'occluder': goal._tag_to_objects['occluder'],
        'background object': goal._tag_to_objects['background object']
    }, goal._last_step, scene['wallMaterial'])

    assert 'shape constancy object two into one' in scene['goal']['type_list']
    assert (
        target_b['hides'][0]['stepBegin'] == target_a['shows'][0]['stepBegin']
    )
    assert verify_target_implausible_hide_step(goal, target_b)
    assert verify_target_implausible_show_step(goal, target_a)


def verify_quartet_ShapeConstancy_scene_4(quartet):
    # _b_replaces_a
    scene = quartet.get_scene(4)
    goal = quartet._goal

    target_b = scene['objects'][0]
    verify_shape_constancy_two_targets(goal._tag_to_objects['target'][0],
                                       quartet._b_template, None, target_b)

    verify_body(scene, goal.is_move_across())
    verify_goal_ShapeConstancy(goal.is_move_across(), {
        'target': [target_b],
        'distractor': goal._tag_to_objects['distractor'],
        'occluder': goal._tag_to_objects['occluder'],
        'background object': goal._tag_to_objects['background object']
    }, goal._last_step, scene['wallMaterial'])

    assert 'shape constancy object two' in scene['goal']['type_list']
    assert 'hides' not in target_b


def verify_quartet_SpatioTemporalContinuity_scene_1(quartet):
    scene = quartet.get_scene(1)
    goal = quartet._goal

    target = scene['objects'][0]
    print(f'TARGET={target}')
    assert target['id'] == goal._tag_to_objects['target'][0]['id']

    occluder_list = goal._tag_to_objects['occluder']
    print(f'OCCLUDER_LIST={occluder_list}')

    verify_body(scene, goal.is_move_across())
    verify_goal_SpatioTemporalContinuity(goal.is_move_across(), {
        'target': [target],
        'distractor': goal._tag_to_objects['distractor'],
        'occluder': occluder_list,
        'background object': goal._tag_to_objects['background object']
    }, goal._last_step, scene['wallMaterial'])

    assert (
        'spatio temporal continuity move earlier' in scene['goal']['type_list']
    )
    assert 'hides' not in target
    assert 'teleports' not in target

    return goal, scene, target, occluder_list


def verify_quartet_SpatioTemporalContinuity_scene_2(quartet):
    # _teleport_forward
    scene = quartet.get_scene(2)
    goal = quartet._goal

    target = scene['objects'][0]
    print(f'TARGET={target}')
    assert target['id'] == goal._tag_to_objects['target'][0]['id']

    occluder_list = goal._tag_to_objects['occluder']
    print(f'OCCLUDER_LIST={occluder_list}')

    verify_body(scene, goal.is_move_across(), implausible=True)
    verify_goal_SpatioTemporalContinuity(goal.is_move_across(), {
        'target': [target],
        'distractor': goal._tag_to_objects['distractor'],
        'occluder': goal._tag_to_objects['occluder'],
        'background object': goal._tag_to_objects['background object']
    }, goal._last_step, scene['wallMaterial'])

    assert (
        'spatio temporal continuity teleport forward'
        in scene['goal']['type_list']
    )

    if goal.is_fall_down() or 'hides' not in target:
        teleport = target['teleports'][0]
        assert teleport['stepBegin'] == teleport['stepEnd']
        assert teleport['position']['y'] == target['shows'][0]['position']['y']
        assert teleport['position']['z'] == target['shows'][0]['position']['z']
        assert teleport['rotation'] == target['shows'][0]['rotation']

    return goal, scene, target, occluder_list


def verify_quartet_SpatioTemporalContinuity_scene_3(quartet):
    # _teleport_backward
    scene = quartet.get_scene(3)
    goal = quartet._goal

    target = scene['objects'][0]
    print(f'TARGET={target}')
    assert target['id'] == goal._tag_to_objects['target'][0]['id']

    occluder_list = goal._tag_to_objects['occluder']
    if goal.is_fall_down():
        # Swap the 1st pair of occluder wall and pole objects with the 2nd pair
        # in the occluder list for the validation in the verify_goal function.
        occluder_list = occluder_list[2:] + occluder_list[:2]
    print(f'OCCLUDER_LIST={occluder_list}')

    verify_body(scene, goal.is_move_across(), implausible=True)
    verify_goal_SpatioTemporalContinuity(goal.is_move_across(), {
        'target': [target],
        'distractor': goal._tag_to_objects['distractor'],
        'occluder': occluder_list,
        'background object': goal._tag_to_objects['background object']
    }, goal._last_step, scene['wallMaterial'])

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

    return goal, scene, target, occluder_list


def verify_quartet_SpatioTemporalContinuity_scene_4(quartet):
    # _move_later
    scene = quartet.get_scene(4)
    goal = quartet._goal

    target = scene['objects'][0]
    print(f'TARGET={target}')
    assert target['id'] == goal._tag_to_objects['target'][0]['id']

    occluder_list = goal._tag_to_objects['occluder']
    if goal.is_fall_down():
        # Swap the 1st pair of occluder wall and pole objects with the 2nd pair
        # in the occluder list for the validation in the verify_goal function.
        occluder_list = occluder_list[2:] + occluder_list[:2]
    print(f'OCCLUDER_LIST={occluder_list}')

    verify_body(scene, goal.is_move_across())
    verify_goal_SpatioTemporalContinuity(goal.is_move_across(), {
        'target': [target],
        'distractor': goal._tag_to_objects['distractor'],
        'occluder': occluder_list,
        'background object': goal._tag_to_objects['background object']
    }, goal._last_step, scene['wallMaterial'])

    assert (
        'spatio temporal continuity move later' in scene['goal']['type_list']
    )
    assert 'hides' not in target
    assert 'teleports' not in target

    return goal, scene, target, occluder_list


def test_SpatioTemporalContinuityQuartet_get_scene_1_fall_down():
    quartet = SpatioTemporalContinuityQuartet(TEMPLATE, is_fall_down=True)
    assert quartet._goal.is_fall_down()
    goal, scene, target, occluder_list = \
        verify_quartet_SpatioTemporalContinuity_scene_1(quartet)

    # SpatioTemporalContinuity fall-down scene 1 specific validation.
    factor = (
        IntPhysGoal.NEAR_SIGHT_ANGLE_FACTOR_X
        if target['shows'][0]['position']['z'] == IntPhysGoal.OBJECT_NEAR_Z
        else IntPhysGoal.FAR_SIGHT_ANGLE_FACTOR_X
    )
    # Show the target directly above the 1st occluder.
    assert target['shows'][0]['position']['x'] == pytest.approx(
        occluder_list[0]['shows'][0]['position']['x'] / factor
    )


def test_SpatioTemporalContinuityQuartet_get_scene_1_move_across():
    quartet = SpatioTemporalContinuityQuartet(TEMPLATE, is_move_across=True)
    assert quartet._goal.is_move_across()
    goal, scene, target, occluder_list = \
        verify_quartet_SpatioTemporalContinuity_scene_1(quartet)

    # SpatioTemporalContinuity move-across scene 1 specific validation.
    assert target['shows'][0]['stepBegin'] == (
        goal._tag_to_objects['target'][0]['shows'][0]['stepBegin']
    )


def test_SpatioTemporalContinuityQuartet_get_scene_2_fall_down():
    quartet = SpatioTemporalContinuityQuartet(TEMPLATE, is_fall_down=True)
    assert quartet._goal.is_fall_down()
    goal, scene, target, occluder_list = \
        verify_quartet_SpatioTemporalContinuity_scene_2(quartet)

    # SpatioTemporalContinuity fall-down scene 2 specific validation.
    teleport = target['teleports'][0]
    assert teleport['stepBegin'] == (
        target['shows'][0]['stepBegin'] + IntPhysGoal.OBJECT_FALL_TIME
    )
    factor = (
        IntPhysGoal.NEAR_SIGHT_ANGLE_FACTOR_X
        if target['shows'][0]['position']['z'] == IntPhysGoal.OBJECT_NEAR_Z
        else IntPhysGoal.FAR_SIGHT_ANGLE_FACTOR_X
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
    quartet = SpatioTemporalContinuityQuartet(TEMPLATE, is_move_across=True)
    assert quartet._goal.is_move_across()
    goal, scene, target, occluder_list = \
        verify_quartet_SpatioTemporalContinuity_scene_2(quartet)

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
            target['intphysOption']['positionByStep'][
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
            target['intphysOption']['positionByStep'][
                max(step_offset_1, step_offset_2)
            ]
        )
        assert show_later['position']['y'] == show_first['position']['y']
        assert show_later['position']['z'] == show_first['position']['z']
        assert show_later['rotation'] == show_first['rotation']


def test_SpatioTemporalContinuityQuartet_get_scene_3_fall_down():
    quartet = SpatioTemporalContinuityQuartet(TEMPLATE, is_fall_down=True)
    assert quartet._goal.is_fall_down()
    goal, scene, target, occluder_list = \
        verify_quartet_SpatioTemporalContinuity_scene_3(quartet)

    # SpatioTemporalContinuity fall-down scene 3 specific validation.
    teleport = target['teleports'][0]
    assert teleport['stepBegin'] == (
        target['shows'][0]['stepBegin'] + IntPhysGoal.OBJECT_FALL_TIME
    )
    factor = (
        IntPhysGoal.NEAR_SIGHT_ANGLE_FACTOR_X
        if target['shows'][0]['position']['z'] == IntPhysGoal.OBJECT_NEAR_Z
        else IntPhysGoal.FAR_SIGHT_ANGLE_FACTOR_X
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
    quartet = SpatioTemporalContinuityQuartet(TEMPLATE, is_move_across=True)
    assert quartet._goal.is_move_across()
    goal, scene, target, occluder_list = \
        verify_quartet_SpatioTemporalContinuity_scene_3(quartet)

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
        target['intphysOption']['positionByStep'][
            min(step_offset_1, step_offset_2)
        ]
    )


def test_SpatioTemporalContinuityQuartet_get_scene_4_fall_down():
    quartet = SpatioTemporalContinuityQuartet(TEMPLATE, is_fall_down=True)
    assert quartet._goal.is_fall_down()
    goal, scene, target, occluder_list = \
        verify_quartet_SpatioTemporalContinuity_scene_4(quartet)

    # SpatioTemporalContinuity fall-down scene 4 specific validation.
    factor = (
        IntPhysGoal.NEAR_SIGHT_ANGLE_FACTOR_X
        if target['shows'][0]['position']['z'] == IntPhysGoal.OBJECT_NEAR_Z
        else IntPhysGoal.FAR_SIGHT_ANGLE_FACTOR_X
    )
    # Show the target directly above the 2nd occluder (remember that the
    # two occluder pairs in the list were switched above).
    assert target['shows'][0]['position']['x'] == pytest.approx(
        occluder_list[0]['shows'][0]['position']['x'] / factor
    )


def test_SpatioTemporalContinuityQuartet_get_scene_4_move_across():
    quartet = SpatioTemporalContinuityQuartet(TEMPLATE, is_move_across=True)
    assert quartet._goal.is_move_across()
    goal, scene, target, occluder_list = \
        verify_quartet_SpatioTemporalContinuity_scene_4(quartet)

    # SpatioTemporalContinuity move-across scene 4 specific validation.
    step_offset_1 = find_implausible_event_step_offset(target,
                                                       occluder_list[0])
    step_offset_2 = find_implausible_event_step_offset(target,
                                                       occluder_list[2])
    assert step_offset_1 > 0
    assert step_offset_2 > 0
    assert target['shows'][0]['stepBegin'] == (
        goal._tag_to_objects['target'][0]['shows'][0]['stepBegin'] +
        abs(step_offset_1 - step_offset_2)
    )


def test_ShapeConstancyQuartet_get_scene_1_fall_down():
    quartet = ShapeConstancyQuartet(TEMPLATE, is_fall_down=True)
    assert quartet._goal.is_fall_down()
    verify_quartet_ShapeConstancy_scene_1(quartet)


def test_ShapeConstancyQuartet_get_scene_1_move_across():
    quartet = ShapeConstancyQuartet(TEMPLATE, is_move_across=True)
    assert quartet._goal.is_move_across()
    verify_quartet_ShapeConstancy_scene_1(quartet)


def test_ShapeConstancyQuartet_get_scene_2_fall_down():
    quartet = ShapeConstancyQuartet(TEMPLATE, is_fall_down=True)
    assert quartet._goal.is_fall_down()
    verify_quartet_ShapeConstancy_scene_2(quartet)


def test_ShapeConstancyQuartet_get_scene_2_move_across():
    quartet = ShapeConstancyQuartet(TEMPLATE, is_move_across=True)
    assert quartet._goal.is_move_across()
    verify_quartet_ShapeConstancy_scene_2(quartet)


def test_ShapeConstancyQuartet_get_scene_3_fall_down():
    quartet = ShapeConstancyQuartet(TEMPLATE, is_fall_down=True)
    assert quartet._goal.is_fall_down()
    verify_quartet_ShapeConstancy_scene_3(quartet)


def test_ShapeConstancyQuartet_get_scene_3_move_across():
    quartet = ShapeConstancyQuartet(TEMPLATE, is_move_across=True)
    assert quartet._goal.is_move_across()
    verify_quartet_ShapeConstancy_scene_3(quartet)


def test_ShapeConstancyQuartet_get_scene_4_fall_down():
    quartet = ShapeConstancyQuartet(TEMPLATE, is_fall_down=True)
    assert quartet._goal.is_fall_down()
    verify_quartet_ShapeConstancy_scene_4(quartet)


def test_ShapeConstancyQuartet_get_scene_4_move_across():
    quartet = ShapeConstancyQuartet(TEMPLATE, is_move_across=True)
    assert quartet._goal.is_move_across()
    verify_quartet_ShapeConstancy_scene_4(quartet)


def test_ObjectPermanenceQuartet_get_scene_1_fall_down():
    quartet = ObjectPermanenceQuartet(TEMPLATE, is_fall_down=True)
    assert quartet._goal.is_fall_down()
    verify_quartet_ObjectPermanence_scene_1(quartet)


def test_ObjectPermanenceQuartet_get_scene_1_move_across():
    quartet = ObjectPermanenceQuartet(TEMPLATE, is_move_across=True)
    assert quartet._goal.is_move_across()
    verify_quartet_ObjectPermanence_scene_1(quartet)


def test_ObjectPermanenceQuartet_get_scene_2_fall_down():
    quartet = ObjectPermanenceQuartet(TEMPLATE, is_fall_down=True)
    assert quartet._goal.is_fall_down()
    verify_quartet_ObjectPermanence_scene_2(quartet)


def test_ObjectPermanenceQuartet_get_scene_2_move_across():
    quartet = ObjectPermanenceQuartet(TEMPLATE, is_move_across=True)
    assert quartet._goal.is_move_across()
    verify_quartet_ObjectPermanence_scene_2(quartet)


def test_ObjectPermanenceQuartet_get_scene_3_fall_down():
    quartet = ObjectPermanenceQuartet(TEMPLATE, is_fall_down=True)
    assert quartet._goal.is_fall_down()
    verify_quartet_ObjectPermanence_scene_3(quartet)


def test_ObjectPermanenceQuartet_get_scene_3_move_across():
    quartet = ObjectPermanenceQuartet(TEMPLATE, is_move_across=True)
    assert quartet._goal.is_move_across()
    verify_quartet_ObjectPermanence_scene_3(quartet)


def test_ObjectPermanenceQuartet_get_scene_4_fall_down():
    quartet = ObjectPermanenceQuartet(TEMPLATE, is_fall_down=True)
    assert quartet._goal.is_fall_down()
    verify_quartet_ObjectPermanence_scene_4(quartet)


def test_ObjectPermanenceQuartet_get_scene_4_move_across():
    quartet = ObjectPermanenceQuartet(TEMPLATE, is_move_across=True)
    assert quartet._goal.is_move_across()
    verify_quartet_ObjectPermanence_scene_4(quartet)


@pytest.mark.skip(reason="TODO MCS-273")
def test_GravityQuartet_get_scene():
    quartet = GravityQuartet(TEMPLATE, False)
    scene_1 = quartet.get_scene(1)
    assert scene_1 is not None
    assert scene_1['goal']['last_step'] > 0
    for q in [2, 3, 4]:
        scene = quartet.get_scene(q)
        assert scene is not None
        assert scene['goal']['last_step'] == scene_1['goal']['last_step']
        assert scene['goal']['action_list'] == [
            ['Pass']] * scene['goal']['last_step']
        assert scene['goal']['category'] == 'intphys'
        assert set(scene['goal']['domain_list']) == set(
            ['objects', 'object solidity', 'object motion', 'gravity'])
        assert 'passive' in scene['goal']['type_list']
        assert 'action none' in scene['goal']['type_list']
        assert 'intphys' in scene['goal']['type_list']
        assert 'gravity' in scene['goal']['type_list']
        assert ('ramp 30-degree' in scene['goal']['type_list']) or \
            ('ramp 45-degree' in scene['goal']['type_list']) or \
            ('ramp 90-degree' in scene['goal']['type_list']) or \
            ('ramp 30-degree-90-degree' in scene['goal']['type_list']) or \
            ('ramp 45-degree-90-degree' in scene['goal']['type_list'])
        assert len(scene['objects']) >= 1


@pytest.mark.skip(reason="TODO MCS-273")
def test_GravityQuartet_get_scene_1():
    quartet = GravityQuartet(TEMPLATE, False)
    scene = quartet.get_scene(1)
    assert scene['answer']['choice'] == 'plausible'
    assert ('gravity ramp fast further' in scene['goal']['type_list']) or \
        ('gravity ramp up slower' in scene['goal']['type_list'])
    # TODO MCS-82 More asserts to test specific behavior


@pytest.mark.skip(reason="TODO MCS-273")
def test_GravityQuartet_get_scene_2():
    quartet = GravityQuartet(TEMPLATE, False)
    scene = quartet.get_scene(2)
    assert scene['answer']['choice'] == 'plausible'
    assert ('gravity ramp slow shorter' in scene['goal']['type_list']) or \
        ('gravity ramp down faster' in scene['goal']['type_list'])
    # TODO MCS-82 More asserts to test specific behavior


@pytest.mark.skip(reason="TODO MCS-273")
def test_GravityQuartet_get_scene_3():
    quartet = GravityQuartet(TEMPLATE, False)
    scene = quartet.get_scene(3)
    assert scene['answer']['choice'] == 'implausible'
    assert ('gravity ramp fast shorter' in scene['goal']['type_list']) or \
        ('gravity ramp up faster' in scene['goal']['type_list'])
    # TODO MCS-82 More asserts to test specific behavior


@pytest.mark.skip(reason="TODO MCS-273")
def test_GravityQuartet_get_scene_4():
    quartet = GravityQuartet(TEMPLATE, False)
    scene = quartet.get_scene(4)
    assert scene['answer']['choice'] == 'implausible'
    assert ('gravity ramp slow further' in scene['goal']['type_list']) or \
        ('gravity ramp down slower' in scene['goal']['type_list'])
    # TODO MCS-82 More asserts to test specific behavior
