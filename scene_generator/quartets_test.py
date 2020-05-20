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
    if quartet._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_and_occluders_moving_across:
        target = find_targets(scene)[0]
        assert target['teleports'][0]['stepBegin'] == target['teleports'][0]['stepEnd']
        assert target['teleports'][0]['vector']['x'] > 0


def test_STCQ__teleport_backward():
    template = {'wallMaterial': 'dummy'}
    quartet = SpatioTemporalContinuityQuartet(template, False)
    scene = quartet.get_scene(3)
    if quartet._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_and_occluders_moving_across:
        target = find_targets(scene)[0]
        assert target['teleports'][0]['stepBegin'] == target['teleports'][0]['stepEnd']
        assert target['teleports'][0]['vector']['x'] > 0


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
