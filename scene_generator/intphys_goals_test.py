import copy
import materials
import objects
from geometry import ORIGIN
from goals import *

from intphys_goals import IntPhysGoal
from util import instantiate_object, random_real

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


def test_GravityGoal_compute_objects():
    goal = GravityGoal()
    tag_to_objects = goal.compute_objects(
        'dummy wall material', 'dummy wall color')
    assert len(tag_to_objects['target']) >= 1
    assert len(tag_to_objects['distractor']) >= 0
    assert len(tag_to_objects['background object']) >= 0
    assert len(tag_to_objects['ramp']) >= 1
    assert goal._last_step > 0


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
    assert ('ramp 30-degree' in body['goal']['type_list']) or ('ramp 45-degree' in body['goal']['type_list']) or \
        ('ramp 90-degree' in body['goal']['type_list']) or \
        ('ramp 30-degree-90-degree' in body['goal']['type_list']) or \
        ('ramp 45-degree-90-degree' in body['goal']['type_list'])
    assert body['answer']['choice'] == 'plausible'
    assert len(body['objects']) >= 1


def test_ObjectPermanenceGoal_compute_objects():
    goal = ObjectPermanenceGoal()
    tag_to_objects = goal.compute_objects(
        'dummy wall material', 'dummy wall color')
    assert len(tag_to_objects['target']) >= 1
    assert len(tag_to_objects['distractor']) >= 0
    assert len(tag_to_objects['background object']) >= 0
    assert len(tag_to_objects['occluder']) >= 1
    assert (goal._object_creator == IntPhysGoal._get_objects_and_occluders_moving_across) or \
        (goal._object_creator == IntPhysGoal._get_objects_falling_down)
    assert goal._last_step > 0


def test_ObjectPermanenceGoal_update_body():
    goal = ObjectPermanenceGoal()
    body = goal.update_body(copy.deepcopy(BODY_TEMPLATE), False)
    assert body['goal']['last_step'] > 0
    assert body['goal']['action_list'] == [
        ['Pass']] * body['goal']['last_step']
    assert body['goal']['category'] == 'intphys'
    assert set(body['goal']['domain_list']) == set(
        ['objects', 'object solidity', 'object motion', 'object permanence'])
    assert 'passive' in body['goal']['type_list']
    assert 'action none' in body['goal']['type_list']
    assert 'intphys' in body['goal']['type_list']
    assert 'object permanence' in body['goal']['type_list']
    assert ('move across' in body['goal']['type_list']) or (
        'fall down' in body['goal']['type_list'])
    assert body['answer']['choice'] == 'plausible'
    assert len(body['objects']) >= 1


def test_ShapeConstancyGoal_compute_objects():
    goal = ShapeConstancyGoal()
    tag_to_objects = goal.compute_objects(
        'dummy wall material', 'dummy wall color')
    assert len(tag_to_objects['target']) >= 1
    assert len(tag_to_objects['distractor']) >= 0
    assert len(tag_to_objects['background object']) >= 0
    assert len(tag_to_objects['occluder']) >= 1
    assert (goal._object_creator == IntPhysGoal._get_objects_and_occluders_moving_across) or \
        (goal._object_creator == IntPhysGoal._get_objects_falling_down)
    assert goal._last_step > 0


def test_ShapeConstancyGoal_update_body():
    goal = ShapeConstancyGoal()
    body = goal.update_body(copy.deepcopy(BODY_TEMPLATE), False)
    assert body['goal']['last_step'] > 0
    assert body['goal']['action_list'] == [
        ['Pass']] * body['goal']['last_step']
    assert body['goal']['category'] == 'intphys'
    assert set(body['goal']['domain_list']) == set(
        ['objects', 'object solidity', 'object motion', 'object permanence'])
    assert 'passive' in body['goal']['type_list']
    assert 'action none' in body['goal']['type_list']
    assert 'intphys' in body['goal']['type_list']
    assert 'shape constancy' in body['goal']['type_list']
    assert ('move across' in body['goal']['type_list']) or (
        'fall down' in body['goal']['type_list'])
    assert body['answer']['choice'] == 'plausible'
    assert len(body['objects']) >= 1


def test_SpatioTemporalContinuityGoal_compute_objects():
    goal = SpatioTemporalContinuityGoal()
    tag_to_objects = goal.compute_objects(
        'dummy wall material', 'dummy wall color')
    assert len(tag_to_objects['target']) >= 1
    assert len(tag_to_objects['distractor']) >= 0
    assert len(tag_to_objects['background object']) >= 0
    assert len(tag_to_objects['occluder']) >= 1
    assert (goal._object_creator == IntPhysGoal._get_objects_and_occluders_moving_across) or \
        (goal._object_creator == IntPhysGoal._get_objects_falling_down)
    assert goal._last_step > 0


def test_SpatioTemporalContinuityGoal_update_body():
    goal = SpatioTemporalContinuityGoal()
    body = goal.update_body(copy.deepcopy(BODY_TEMPLATE), False)
    assert body['goal']['last_step'] > 0
    assert body['goal']['action_list'] == [
        ['Pass']] * body['goal']['last_step']
    assert body['goal']['category'] == 'intphys'
    assert set(body['goal']['domain_list']) == set(
        ['objects', 'object solidity', 'object motion', 'object permanence'])
    assert 'passive' in body['goal']['type_list']
    assert 'action none' in body['goal']['type_list']
    assert 'intphys' in body['goal']['type_list']
    assert 'spatio temporal continuity' in body['goal']['type_list']
    assert ('move across' in body['goal']['type_list']) or (
        'fall down' in body['goal']['type_list'])
    assert body['answer']['choice'] == 'plausible'
    assert len(body['objects']) >= 1


# test for MCS-214
def test_GravityGoal__get_ramp_and_objects():
    goal = GravityGoal()
    ramp_type, left_to_right, ramp_objs, object_list = goal._get_ramp_and_objects(
        'dummy')
    assert len(ramp_objs) >= 1
    for obj in object_list:
        assert obj['intphysOption']['y'] == 0
        assert obj['type'] != 'cube'


def test_IntPhysGoal__get_objects_and_occluders_moving_across():
    class TestGoal(IntPhysGoal):
        def __init__(self):
            super(TestGoal, self).__init__('test')

    goal = TestGoal()
    wall_material = random.choice(materials.CEILING_AND_WALL_MATERIALS)[0]
    objs, occluders = goal._get_objects_and_occluders_moving_across(
        wall_material)
    assert 1 <= len(objs) <= 3
    assert 1 <= len(occluders) <= 4 * 2  # each occluder is actually 2 objects
    # the first occluder should be at one of the positions for the first object
    occluder_x = occluders[0]['shows'][0]['position']['x']
    first_obj = objs[0]
    found = False
    multiplier = 0.9 if first_obj['shows'][0]['position']['z'] == 1.6 else 0.8
    for position in first_obj['intphysOption']['position_by_step']:
        adjusted_x = position * multiplier
        if adjusted_x == occluder_x:
            found = True
            break
    assert found
    for o in occluders:
        assert o['materials'] != wall_material


def test_IntPhysGoal__get_objects_moving_across_collisions():
    class TestGoal(IntPhysGoal):
        def __init__(self):
            super(TestGoal, self).__init__('test')

    goal = TestGoal()
    wall_material = random.choice(materials.CEILING_AND_WALL_MATERIALS)[0]
    objs = goal._get_objects_moving_across(
        wall_material, 55, goal._object_defs)
    for obj in objs:
        x = obj['shows'][0]['position']['x']
        z = obj['shows'][0]['position']['z']
        # check for possible collision with all other objects
        for other in (o for o in objs if o != obj):
            other_x = other['shows'][0]['position']['x']
            other_z = other['shows'][0]['position']['z']
            # could other catch up to obj?
            if other_z == z and abs(other_x) > abs(x):
                obj_a = obj['intphysOption']['force']['x'] / obj['mass']
                other_a = other['intphysOption']['force']['x'] / obj['mass']
                assert abs(other_a) <= abs(obj_a)


def test_IntPhysGoal__compute_scenery():
    goal = GravityGoal()
    # There's a good chance of no scenery, so keep trying until we get
    # some.
    scenery_generated = False
    while not scenery_generated:
        scenery_list = goal._compute_scenery()
        assert 0 <= len(scenery_list) <= 5
        scenery_generated = len(scenery_list) > 0
        for scenery in scenery_list:
            for point in scenery['shows'][0]['boundingBox']:
                assert -6.5 <= point['x'] <= 6.5
                assert 3.25 <= point['z'] <= 4.95


def test__get_objects_falling_down():
    class TestGoal(IntPhysGoal):
        def __init__(self):
            super(TestGoal, self).__init__('test')

    goal = TestGoal()
    wall_material = random.choice(materials.CEILING_AND_WALL_MATERIALS)[0]
    obj_list, occluders = goal._get_objects_falling_down(wall_material)
    assert 1 <= len(obj_list) <= 2
    assert len(obj_list) * 2 <= len(occluders) <= 4
    for obj in obj_list:
        assert -2.5 <= obj['shows'][0]['position']['x'] <= 2.5
        assert obj['shows'][0]['position']['y'] == 3.8
        z = obj['shows'][0]['position']['z']
        assert z == 1.6 or z == 2.7
        assert 13 <= obj['shows'][0]['stepBegin'] <= 20


def test_mcs_209():
    obj_defs = objects.get('INTPHYS')
    random.shuffle(obj_defs)
    obj_def = next((od for od in obj_defs if 'rotation' in od))
    obj = instantiate_object(obj_def, {'position': ORIGIN})
    assert obj['shows'][0]['rotation'] == obj_def['rotation']

    class TestGoal(IntPhysGoal):
        TEMPLATE = {'type_list': [], 'metadata': {}}

        def __init__(self):
            super(TestGoal, self).__init__('test')

    goal = TestGoal()
    objs = goal._get_objects_moving_across('dummy', 55, goal._object_defs)
    for obj in objs:
        assert obj['shows'][0]['stepBegin'] == obj['forces'][0]['stepBegin']

    body = {'wallMaterial': 'dummy', 'wallColors': ['color']}
    goal._scenery_count = 0
    goal.update_body(body, False)
