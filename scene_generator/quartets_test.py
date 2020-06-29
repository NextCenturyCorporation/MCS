import intphys_goals
import objects
import pytest
from quartets import GravityQuartet, ShapeConstancyQuartet, ObjectPermanenceQuartet, SpatioTemporalContinuityQuartet, \
        find_targets, get_position_step


TEMPLATE = {'wallMaterial': 'dummy', 'wallColors': ['color']}

def test_get_position_step():
    target = {
        'intphys_option': objects.OBJECTS_INTPHYS[0]['intphys_options'][0]
    }
    x = 1.0
    expected_step = 2
    step = get_position_step(target, x, False, True)
    assert step == expected_step


def test_STCQ_get_scene():
    quartet = SpatioTemporalContinuityQuartet(TEMPLATE, False)
    scene_1 = quartet.get_scene(1)
    assert scene_1 is not None
    assert scene_1['goal']['last_step'] > 0
    move_across = 'move across' in scene_1['goal']['type_list']
    fall_down = 'fall down' in scene_1['goal']['type_list']
    for q in [2, 3, 4]:
        scene = quartet.get_scene(q)
        assert scene is not None
        assert scene['goal']['last_step'] == scene_1['goal']['last_step']
        assert scene['goal']['action_list'] == [['Pass']] * scene['goal']['last_step']
        assert scene['goal']['category'] == 'intphys'
        assert scene['goal']['domain_list'] == ['objects', 'object solidity', 'object motion', 'object permanence']
        assert 'passive' in scene['goal']['type_list']
        assert 'action none' in scene['goal']['type_list']
        assert 'intphys' in scene['goal']['type_list']
        assert 'spatio temporal continuity' in scene['goal']['type_list']
        if move_across:
            assert 'move across' in scene['goal']['type_list']
        if fall_down:
            assert 'fall down' in scene['goal']['type_list']
        assert len(scene['objects']) >= 1


def test_STCQ_get_scene_1():
    quartet = SpatioTemporalContinuityQuartet(TEMPLATE, False)
    scene = quartet.get_scene(1)
    target = find_targets(scene, quartet._goal)[0]
    assert scene['answer']['choice'] == 'plausible'
    assert 'spatio temporal continuity move earlier' in scene['goal']['type_list']
    assert 'hides' not in target
    assert 'teleports' not in target
    # TODO MCS-82 More asserts to test specific behavior


def test_STCQ_get_scene_2_teleport_forward():
    quartet = SpatioTemporalContinuityQuartet(TEMPLATE, False)
    scene = quartet.get_scene(2)
    target = find_targets(scene, quartet._goal)[0]
    assert scene['answer']['choice'] == 'implausible'
    assert 'spatio temporal continuity teleport forward' in scene['goal']['type_list']
    assert ('teleports' in target) or ('hides' in target)
    if 'teleports' in target:
        assert target['teleports'][0]['stepBegin'] == target['teleports'][0]['stepEnd']
        if quartet._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_and_occluders_moving_across:
            implausible_event_index1 = target['intphys_option']['occluder_indices'][0]
            implausible_event_index2 = target['intphys_option']['occluder_indices'][1]
            assert target['teleports'][0]['stepBegin'] == min(implausible_event_index1, implausible_event_index2) + target['forces'][0]['stepBegin']
        else:
            assert target['teleports'][0]['stepBegin'] >= 8
    # TODO MCS-82 Test behavior if 'hides' in target


def test_STCQ_get_scene_3_teleport_backward():
    quartet = SpatioTemporalContinuityQuartet(TEMPLATE, False)
    scene = quartet.get_scene(3)
    target = find_targets(scene, quartet._goal)[0]
    assert scene['answer']['choice'] == 'implausible'
    assert 'spatio temporal continuity teleport backward' in scene['goal']['type_list']
    assert 'teleports' in target
    assert target['teleports'][0]['stepBegin'] == target['teleports'][0]['stepEnd']
    if quartet._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_and_occluders_moving_across:
        implausible_event_index1 = target['intphys_option']['occluder_indices'][0]
        implausible_event_index2 = target['intphys_option']['occluder_indices'][1]
        assert target['teleports'][0]['stepBegin'] == max(implausible_event_index1, implausible_event_index2) + target['forces'][0]['stepBegin']
    else:
        assert target['teleports'][0]['stepBegin'] >= 8


def test_STCQ_get_scene_4_move_later():
    quartet = SpatioTemporalContinuityQuartet(TEMPLATE, False)
    scene = quartet.get_scene(4)
    target = find_targets(scene, quartet._goal)[0]
    assert scene['answer']['choice'] == 'plausible'
    assert 'spatio temporal continuity move later' in scene['goal']['type_list']
    assert 'hides' not in target
    assert 'teleports' not in target
    if quartet._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_and_occluders_moving_across:
        later_step_begin = target['shows'][0]['stepBegin']
        orig_target = find_targets(quartet.get_scene(1), quartet._goal)[0]
        orig_step_begin = orig_target['shows'][0]['stepBegin']
        assert later_step_begin > orig_step_begin


def test_ShapeConstancyQuartet():
    quartet = ShapeConstancyQuartet(TEMPLATE, False)
    assert quartet is not None
    a = quartet._scene_template['objects'][0]
    assert a['type'] != quartet._b['type']
    assert a['id'] == quartet._b['id']
    assert a['dimensions']['x'] == pytest.approx(quartet._b['dimensions']['x'], abs=intphys_goals.MAX_SIZE_DIFFERENCE)
    assert a['materials'] == quartet._b['materials']


def test_ShapeConstancyQuartet_get_scene():
    quartet = ShapeConstancyQuartet(TEMPLATE, False)
    scene_1 = quartet.get_scene(1)
    assert scene_1 is not None
    assert scene_1['goal']['last_step'] > 0
    move_across = 'move across' in scene_1['goal']['type_list']
    fall_down = 'fall down' in scene_1['goal']['type_list']
    for q in [2, 3, 4]:
        scene = quartet.get_scene(q)
        assert scene is not None
        assert scene['goal']['last_step'] == scene_1['goal']['last_step']
        assert scene['goal']['action_list'] == [['Pass']] * scene['goal']['last_step']
        assert scene['goal']['category'] == 'intphys'
        assert scene['goal']['domain_list'] == ['objects', 'object solidity', 'object motion', 'object permanence']
        assert 'passive' in scene['goal']['type_list']
        assert 'action none' in scene['goal']['type_list']
        assert 'intphys' in scene['goal']['type_list']
        assert 'shape constancy' in scene['goal']['type_list']
        if move_across:
            assert 'move across' in scene['goal']['type_list']
        if fall_down:
            assert 'fall down' in scene['goal']['type_list']
        assert len(scene['objects']) >= 1


def test_ShapeConstancyQuartet_get_scene_1():
    quartet = ShapeConstancyQuartet(TEMPLATE, False)
    scene = quartet.get_scene(1)
    assert scene['answer']['choice'] == 'plausible'
    assert 'shape constancy object one' in scene['goal']['type_list']
    assert 'hides' not in scene['objects'][0]
    # TODO MCS-82 More asserts to test specific behavior


def test_ShapeConstancyQuartet_get_scene_2():
    # tests _turn_a_into_b
    quartet = ShapeConstancyQuartet(TEMPLATE, False)
    scene = quartet.get_scene(2)
    assert scene['answer']['choice'] == 'implausible'
    assert 'shape constancy object one into two' in scene['goal']['type_list']
    a = scene['objects'][0]
    b = scene['objects'][-1]
    assert a['id'] == b['id']
    assert a['hides'][0]['stepBegin'] == b['shows'][0]['stepBegin']
    if quartet._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_and_occluders_moving_across:
        assert a['forces'] == b['forces']
    else:
        assert a['shows'][0]['stepBegin'] >= 8
        assert b['shows'][0]['position']['x'] == a['shows'][0]['position']['x']
        assert b['shows'][0]['position']['y'] == a['intphys_option']['position_y']


def test_ShapeConstancyQuartet_get_scene_3():
    # tests turn_b_into_a
    quartet = ShapeConstancyQuartet(TEMPLATE, False)
    scene = quartet.get_scene(3)
    assert scene['answer']['choice'] == 'implausible'
    assert 'shape constancy object two into one' in scene['goal']['type_list']
    a = scene['objects'][0]
    b = scene['objects'][-1]
    assert a['id'] == b['id']
    assert b['hides'][0]['stepBegin'] == a['shows'][0]['stepBegin']
    if quartet._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_and_occluders_moving_across:
        assert a['forces'] == b['forces']
    else:
        assert a['shows'][0]['stepBegin'] >= 8
        assert a['shows'][0]['position']['y'] == a['intphys_option']['position_y']


def test_ShapeConstancyQuartet_get_scene_4():
    quartet = ShapeConstancyQuartet(TEMPLATE, False)
    scene = quartet.get_scene(4)
    assert scene['answer']['choice'] == 'plausible'
    assert 'shape constancy object two' in scene['goal']['type_list']
    assert 'hides' not in scene['objects'][0]
    # TODO MCS-82 More asserts to test specific behavior


def test_ObjectPermanenceQuartet_get_scene():
    quartet = ObjectPermanenceQuartet(TEMPLATE, False)
    scene_1 = quartet.get_scene(1)
    assert scene_1 is not None
    assert scene_1['goal']['last_step'] > 0
    move_across = 'move across' in scene_1['goal']['type_list']
    fall_down = 'fall down' in scene_1['goal']['type_list']
    for q in [2, 3, 4]:
        scene = quartet.get_scene(q)
        assert scene is not None
        assert scene['goal']['last_step'] == scene_1['goal']['last_step']
        assert scene['goal']['action_list'] == [['Pass']] * scene['goal']['last_step']
        assert scene['goal']['category'] == 'intphys'
        assert scene['goal']['domain_list'] == ['objects', 'object solidity', 'object motion', 'object permanence']
        assert 'passive' in scene['goal']['type_list']
        assert 'action none' in scene['goal']['type_list']
        assert 'intphys' in scene['goal']['type_list']
        assert 'object permanence' in scene['goal']['type_list']
        if move_across:
            assert 'move across' in scene['goal']['type_list']
        if fall_down:
            assert 'fall down' in scene['goal']['type_list']
        assert len(scene['objects']) >= 1


def test_ObjectPermanenceQuartet_get_scene_1():
    quartet = ObjectPermanenceQuartet(TEMPLATE, False)
    scene = quartet.get_scene(1)
    assert scene['answer']['choice'] == 'plausible'
    assert 'object permanence show object' in scene['goal']['type_list']
    assert 'hides' not in scene['objects'][0]
    # TODO MCS-82 More asserts to test specific behavior


def test_ObjectPermanenceQuartet_get_scene_2():
    quartet = ObjectPermanenceQuartet(TEMPLATE, False)
    scene = quartet.get_scene(2)
    assert scene['answer']['choice'] == 'implausible'
    assert 'object permanence show then hide object' in scene['goal']['type_list']
    assert 'hides' in scene['objects'][0]
    # TODO MCS-82 More asserts to test specific behavior


def test_ObjectPermanenceQuartet_get_scene_3():
    quartet = ObjectPermanenceQuartet(TEMPLATE, False)
    scene = quartet.get_scene(3)
    assert scene['answer']['choice'] == 'implausible'
    assert 'object permanence hide then show object' in scene['goal']['type_list']
    assert 'hides' not in scene['objects'][0]
    # TODO MCS-82 More asserts to test specific behavior


def test_ObjectPermanenceQuartet_get_scene_4():
    quartet = ObjectPermanenceQuartet(TEMPLATE, False)
    scene = quartet.get_scene(4)
    assert scene['answer']['choice'] == 'plausible'
    assert 'object permanence hide object' in scene['goal']['type_list']
    assert 'hides' not in scene['objects'][0]
    # TODO MCS-82 More asserts to test specific behavior


def test_GravityQuartet_get_scene():
    quartet = GravityQuartet(TEMPLATE, False)
    scene_1 = quartet.get_scene(1)
    assert scene_1 is not None
    assert scene_1['goal']['last_step'] > 0
    for q in [2, 3, 4]:
        scene = quartet.get_scene(q)
        assert scene is not None
        assert scene['goal']['last_step'] == scene_1['goal']['last_step']
        assert scene['goal']['action_list'] == [['Pass']] * scene['goal']['last_step']
        assert scene['goal']['category'] == 'intphys'
        assert scene['goal']['domain_list'] == ['objects', 'object solidity', 'object motion', 'gravity']
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


def test_GravityQuartet_get_scene_1():
    quartet = GravityQuartet(TEMPLATE, False)
    scene = quartet.get_scene(1)
    assert scene['answer']['choice'] == 'plausible'
    assert ('gravity ramp fast further' in scene['goal']['type_list']) or \
            ('gravity ramp up slower' in scene['goal']['type_list'])
    # TODO MCS-82 More asserts to test specific behavior


def test_GravityQuartet_get_scene_2():
    quartet = GravityQuartet(TEMPLATE, False)
    scene = quartet.get_scene(2)
    assert scene['answer']['choice'] == 'plausible'
    assert ('gravity ramp slow shorter' in scene['goal']['type_list']) or \
            ('gravity ramp down faster' in scene['goal']['type_list'])
    # TODO MCS-82 More asserts to test specific behavior


def test_GravityQuartet_get_scene_3():
    quartet = GravityQuartet(TEMPLATE, False)
    scene = quartet.get_scene(3)
    assert scene['answer']['choice'] == 'implausible'
    assert ('gravity ramp fast shorter' in scene['goal']['type_list']) or \
            ('gravity ramp up faster' in scene['goal']['type_list'])
    # TODO MCS-82 More asserts to test specific behavior


def test_GravityQuartet_get_scene_4():
    quartet = GravityQuartet(TEMPLATE, False)
    scene = quartet.get_scene(4)
    assert scene['answer']['choice'] == 'implausible'
    assert ('gravity ramp slow further' in scene['goal']['type_list']) or \
            ('gravity ramp down slower' in scene['goal']['type_list'])
    # TODO MCS-82 More asserts to test specific behavior


