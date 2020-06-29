import intphys_goals
import objects
import pytest
from quartets import ShapeConstancyQuartet, ObjectPermanenceQuartet, SpatioTemporalContinuityQuartet, find_targets, get_position_step


def test_get_position_step():
    target = {
        'intphys_option': objects.OBJECTS_INTPHYS[0]['intphys_options'][0]
    }
    x = 1.0
    expected_step = 2
    step = get_position_step(target, x, False, True)
    assert step == expected_step


def test_STCQ_get_scene():
    template = {'wallMaterial': 'dummy', 'wallColors': ['color']}
    quartet = SpatioTemporalContinuityQuartet(template, False)
    for q in range(1, 5):
        scene = quartet.get_scene(q)
        assert scene is not None


def test_STCQ__teleport_forward():
    template = {'wallMaterial': 'dummy', 'wallColors': ['color']}
    quartet = SpatioTemporalContinuityQuartet(template, False)
    scene = quartet.get_scene(2)
    target = find_targets(scene, quartet._goal)[0]
    if 'teleports' in target:
        assert target['teleports'][0]['stepBegin'] == target['teleports'][0]['stepEnd']
        if quartet._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_and_occluders_moving_across:
            implausible_event_index1 = target['intphys_option']['occluder_indices'][0]
            implausible_event_index2 = target['intphys_option']['occluder_indices'][1]
            assert target['teleports'][0]['stepBegin'] == min(implausible_event_index1, implausible_event_index2) + target['forces'][0]['stepBegin']
        else:
            assert target['teleports'][0]['stepBegin'] >= 8


def test_STCQ__teleport_backward():
    template = {'wallMaterial': 'dummy', 'wallColors': ['color']}
    quartet = SpatioTemporalContinuityQuartet(template, False)
    scene = quartet.get_scene(3)
    target = find_targets(scene, quartet._goal)[0]
    assert target['teleports'][0]['stepBegin'] == target['teleports'][0]['stepEnd']
    if quartet._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_and_occluders_moving_across:
        implausible_event_index1 = target['intphys_option']['occluder_indices'][0]
        implausible_event_index2 = target['intphys_option']['occluder_indices'][1]
        assert target['teleports'][0]['stepBegin'] == max(implausible_event_index1, implausible_event_index2) + target['forces'][0]['stepBegin']
    else:
        assert target['teleports'][0]['stepBegin'] >= 8


def test_STCQ__move_later():
    template = {'wallMaterial': 'dummy', 'wallColors': ['color']}
    quartet = SpatioTemporalContinuityQuartet(template, False)
    scene = quartet.get_scene(4)
    target = find_targets(scene, quartet._goal)[0]
    assert 'teleports' not in target
    if quartet._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_and_occluders_moving_across:
        later_step_begin = target['shows'][0]['stepBegin']
        orig_target = find_targets(quartet.get_scene(1), quartet._goal)[0]
        orig_step_begin = orig_target['shows'][0]['stepBegin']
        assert later_step_begin > orig_step_begin


def test_ShapeConstancyQuartet():
    template = {'wallMaterial': 'dummy', 'wallColors': ['color']}
    quartet = ShapeConstancyQuartet(template, False)
    assert quartet is not None
    a = quartet._scenes[0]['objects'][0]
    assert a['type'] != quartet._b['type']
    assert a['dimensions']['x'] == pytest.approx(quartet._b['dimensions']['x'], abs=intphys_goals.MAX_SIZE_DIFFERENCE)
    assert a['materials'] == quartet._b['materials']


def test_ShapeConstancyQuartet_get_scene_2():
    # tests _turn_a_into_b
    template = {'wallMaterial': 'dummy', 'wallColors': ['color']}
    quartet = ShapeConstancyQuartet(template, False)
    scene = quartet.get_scene(2)
    a = scene['objects'][0]
    b = scene['objects'][-1]
    assert a['hides'][0]['stepBegin'] == b['shows'][0]['stepBegin']
    if quartet._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_and_occluders_moving_across:
        assert a['forces'] == b['forces']
    else:
        assert a['shows'][0]['stepBegin'] >= 8
        assert b['shows'][0]['position']['x'] == a['shows'][0]['position']['x']
        assert b['shows'][0]['position']['y'] == a['intphys_option']['position_y']


def test_ShapeConstancyQuartet_get_scene_3():
    # tests turn_b_into_a
    template = {'wallMaterial': 'dummy', 'wallColors': ['color']}
    quartet = ShapeConstancyQuartet(template, False)
    scene = quartet.get_scene(3)
    a = scene['objects'][0]
    b = scene['objects'][-1]
    assert b['hides'][0]['stepBegin'] == a['shows'][0]['stepBegin']
    if quartet._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_and_occluders_moving_across:
        assert a['forces'] == b['forces']
    else:
        assert a['shows'][0]['stepBegin'] >= 8
        assert a['shows'][0]['position']['y'] == a['intphys_option']['position_y']


def test_ObjectPermanenceQuartet_get_scene():
    template = {'wallMaterial': 'dummy', 'wallColors': ['color']}
    quartet = ObjectPermanenceQuartet(template, False)
    for q in range(1, 5):
        scene = quartet.get_scene(q)
        # at least one occluder (itself 2 objects)
        assert len(scene['objects']) >= 2
