import intphys_goals
import objects
from quartets import ShapeConstancyQuartet, ObjectPermanenceQuartet, SpatioTemporalContinuityQuartet, find_targets, get_position_step


def test_get_position_step():
    target = {
        'intphys_option': objects.OBJECTS_INTPHYS[0]['intphys_options'][0]
    }
    x = 1.0
    expected_step = 2
    step = get_position_step(target, x, True)
    assert step == expected_step


def test_STCQ_get_scene():
    template = {'wallMaterial': 'dummy'}
    quartet = SpatioTemporalContinuityQuartet(template, False)
    for q in range(1, 5):
        scene = quartet.get_scene(q)
        assert scene is not None


def test_STCQ__teleport_forward():
    template = {'wallMaterial': 'dummy'}
    quartet = SpatioTemporalContinuityQuartet(template, False)
    scene = quartet.get_scene(2)
    if quartet._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_and_occluders_moving_across:
        target = find_targets(scene)[0]
        assert target['teleports'][0]['stepBegin'] == target['teleports'][0]['stepEnd']


def test_STCQ__teleport_backward():
    template = {'wallMaterial': 'dummy'}
    quartet = SpatioTemporalContinuityQuartet(template, False)
    scene = quartet.get_scene(3)
    if quartet._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_and_occluders_moving_across:
        target = find_targets(scene)[0]
        assert target['teleports'][0]['stepBegin'] == target['teleports'][0]['stepEnd']


def test_STCQ__move_later():
    template = {'wallMaterial': 'dummy'}
    quartet = SpatioTemporalContinuityQuartet(template, False)
    scene = quartet.get_scene(4)
    if quartet._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_and_occluders_moving_across:
        target = find_targets(scene)[0]
        assert 'teleports' not in target
        later_step_begin = target['shows'][0]['stepBegin']
        orig_target = find_targets(quartet.get_scene(1))[0]
        orig_step_begin = orig_target['shows'][0]['stepBegin']
        assert later_step_begin > orig_step_begin


def test_ShapeConstancyQuartet():
    template = {'wallMaterial': 'dummy'}
    quartet = ShapeConstancyQuartet(template, False)
    assert quartet is not None
    a = quartet._scenes[0]['objects'][0]
    assert a['type'] != quartet._b['type']
    assert a['shows'][0]['scale']['x'] == quartet._b['shows'][0]['scale']['x']
    assert a['shows'][0]['scale']['z'] == quartet._b['shows'][0]['scale']['z']
    assert a['materials'] == quartet._b['materials']


def test_ShapeConstancyQuartet_get_scene_2():
    # tests _turn_a_into_b
    template = {'wallMaterial': 'dummy'}
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
    template = {'wallMaterial': 'dummy'}
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
    template = {'wallMaterial': 'dummy'}
    quartet = ObjectPermanenceQuartet(template, False)
    for q in range(1, 5):
        scene = quartet.get_scene(q)
        # at least one object and occluder (itself 2 objects)
        assert len(scene['objects']) >= 3
