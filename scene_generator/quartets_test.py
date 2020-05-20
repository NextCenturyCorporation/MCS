import intphys_goals
from quartets import ShapeConstancyQuartet


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
    if quartet._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_and_occluders_moving_across:
        a = scene['objects'][0]
        b = scene['objects'][-1]
        assert a['hides'][0]['stepBegin'] == b['shows'][0]['stepBegin']
        assert a['forces'] == b['forces']
    else:
        # TODO: in MCS-131
        pass


def test_ShapeConstancyQuartet_get_scene_3():
    # tests turn_b_into_a
    template = {'wallMaterial': 'dummy'}
    quartet = ShapeConstancyQuartet(template, False)
    scene = quartet.get_scene(3)
    if quartet._goal._object_creator == intphys_goals.IntPhysGoal._get_objects_and_occluders_moving_across:
        a = scene['objects'][0]
        b = scene['objects'][-1]
        assert b['hides'][0]['stepBegin'] == a['shows'][0]['stepBegin']
        assert a['forces'] == b['forces']
    else:
        # TODO: in MCS-131
        pass
