import intphys_goals
from quartets import SpatioTemporalContinuityQuartet, find_targets


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
    target = find_targets(scene)[0]
    assert target['teleports'][0]['stepBegin'] == target['teleports'][0]['stepEnd']
    if quartet._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_and_occluders_moving_across:
        implausible_event_index1 = target['intphys_option']['occluder_indices'][0]
        implausible_event_index2 = target['intphys_option']['occluder_indices'][1]
        assert target['teleports'][0]['stepBegin'] == min(implausible_event_index1, implausible_event_index2)
    else:
        assert target['teleports'][0]['stepBegin'] >= 8


def test_STCQ__teleport_backward():
    template = {'wallMaterial': 'dummy'}
    quartet = SpatioTemporalContinuityQuartet(template, False)
    scene = quartet.get_scene(3)
    target = find_targets(scene)[0]
    assert target['teleports'][0]['stepBegin'] == target['teleports'][0]['stepEnd']
    if quartet._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_and_occluders_moving_across:
        implausible_event_index1 = target['intphys_option']['occluder_indices'][0]
        implausible_event_index2 = target['intphys_option']['occluder_indices'][1]
        assert target['teleports'][0]['stepBegin'] == max(implausible_event_index1, implausible_event_index2)
    else:
        assert target['teleports'][0]['stepBegin'] >= 8


def test_STCQ__move_later():
    template = {'wallMaterial': 'dummy'}
    quartet = SpatioTemporalContinuityQuartet(template, False)
    scene = quartet.get_scene(4)
    target = find_targets(scene)[0]
    assert 'teleports' not in target
    if quartet._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_and_occluders_moving_across:
        later_step_begin = target['shows'][0]['stepBegin']
        orig_target = find_targets(quartet.get_scene(1))[0]
        orig_step_begin = orig_target['shows'][0]['stepBegin']
        assert later_step_begin > orig_step_begin
