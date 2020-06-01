import materials
import objects
import util
from geometry import ORIGIN
from goals import *

from intphys_goals import random_real, IntPhysGoal
from objects import OBJECTS_INTPHYS


def test_random_real():
    n = random_real(0, 1, 0.1)
    assert 0 <= n <= 1
    # need to multiply by 10 and mod by 1 instead of 0.1 to avoid weird roundoff
    assert n * 10 % 1 < 1e-8


def test_IntPhysGoal_compute_performer_start():
    class TestGoal(IntPhysGoal):
        pass

    expected_start = {
        'position': {
            'x': 0,
            'y': 0,
            'z': -4.5
        },
        'rotation': {
            'y': 0
        }
    }
    goal_obj = TestGoal()
    start = goal_obj.compute_performer_start()
    assert start == expected_start


def test_IntPhysGoal_update_body():
    class TestGoal(IntPhysGoal):
        TEMPLATE = {'type_list': [], 'metadata':{}}

    goal_obj = TestGoal()
    body = { 'wallMaterial': 'dummy material' }
    goal_obj.update_body(body, False)
    assert body['observation'] == True
    assert body['answer']['choice'] == 'plausible'


def test_IntPhysGoal_get_config():
    class TestGoal(IntPhysGoal):
        TEMPLATE = {'type_list': [], 'metadata':{}}
    goal_obj = TestGoal()
    goal_objects, all_objs, rects = goal_obj.compute_objects('dummy material')
    goal_obj._goal_objects = goal_objects
    config = goal_obj.get_config(goal_objects, all_objs)
    assert config['action_list'] == [['Pass']] * config['last_step']
    assert len(config['metadata']['objects']) == len(goal_obj._goal_objects)


def test_IntPhysGoal_compute_objects():
    class TestGoal(IntPhysGoal):
        pass

    goal = TestGoal()
    target_objs, all_objs, rects = goal.compute_objects('dummy wall material')
    assert len(target_objs) > 0
    assert len(all_objs) > 0
    assert len(rects) == 0


def test_IntPhysGoal__get_num_occluders():
    class TestGoal(IntPhysGoal):
        pass

    goal = TestGoal()
    num_occluders = goal._get_num_occluders()
    assert 1 <= num_occluders <= 4


def test_IntPhysGoal__get_num_paired_occluders():
    class TestGoal(IntPhysGoal):
        pass

    goal = TestGoal()
    num_paired_occluders = goal._get_num_paired_occluders()
    assert num_paired_occluders == 1


def test_IntPhysGoal__get_paired_occluder():
    class TestGoal(IntPhysGoal):
        pass

    goal = TestGoal()
    target_objs = goal._get_objects_moving_across('dummy wall material', 60)
    occluder = goal._get_paired_occluder(target_objs[0], [],
                                         materials.CEILING_AND_WALL_MATERIALS,
                                         materials.METAL_MATERIALS)
    assert occluder is not None


def test_GravityGoal_compute_objects():
    goal = GravityGoal()
    target_objs, all_objs, rects = goal.compute_objects('dummy wall material')
    assert len(target_objs) > 0
    assert len(all_objs) > 0
    assert len(rects) == 0


# test for MCS-214
def test_GravityGoal__get_ramp_and_objects():
    goal = GravityGoal()
    object_list = goal._get_ramp_and_objects('dummy')
    assert len(object_list) > 0
    for obj in object_list:
        if 'intphys_option' in obj:
            assert obj['intphys_option']['y'] == 0


def test_IntPhysGoal__get_objects_and_occluders_moving_across():
    class TestGoal(IntPhysGoal):
        pass

    goal = TestGoal()
    wall_material = random.choice(materials.CEILING_AND_WALL_MATERIALS)[0]
    objs, occluders = goal._get_objects_and_occluders_moving_across(wall_material)
    assert 1 <= len(objs) <= 3
    assert 1 <= len(occluders) <= 4 * 2  # each occluder is actually 2 objects
    # the first occluder should be at one of the positions for the first object
    occluder_x = occluders[0]['shows'][0]['position']['x']
    first_obj = objs[0]
    found = False
    multiplier = 0.9 if first_obj['shows'][0]['position']['z'] == 1.6 else 0.8
    for position in first_obj['intphys_option']['position_by_step']:
        adjusted_x = position * multiplier
        if adjusted_x == occluder_x:
            found = True
            break
    assert found
    for o in occluders:
        assert o['materials'] != wall_material


def test_IntPhysGoal__get_objects_moving_across_collisions():
    class TestGoal(IntPhysGoal):
        pass

    goal = TestGoal()
    wall_material = random.choice(materials.CEILING_AND_WALL_MATERIALS)[0]
    objs = goal._get_objects_moving_across(wall_material, 55)
    for obj in objs:
        x = obj['shows'][0]['position']['x']
        z = obj['shows'][0]['position']['z']
        # check for possible collision with all other objects
        for other in (o for o in objs if o != obj):
            other_x = other['shows'][0]['position']['x']
            other_z = other['shows'][0]['position']['z']
            # could other catch up to obj?
            if other_z == z and abs(other_x) > abs(x):
                obj_a = obj['intphys_option']['force']['x'] / obj['mass']
                other_a = other['intphys_option']['force']['x'] / obj['mass']
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
            for point in scenery['shows'][0]['bounding_box']:
                assert -6.5 <= point['x'] <= 6.5
                assert 3.25 <= point['z'] <= 4.95


def test__get_objects_falling_down():
    class TestGoal(IntPhysGoal):
        pass

    goal = TestGoal()
    wall_material = random.choice(materials.CEILING_AND_WALL_MATERIALS)[0]
    obj_list, occluders = goal._get_objects_falling_down(wall_material)
    assert 1 <= len(obj_list) <= 2
    assert len(obj_list)*2 <= len(occluders) <= 4
    for obj in obj_list:
        assert -2.5 <= obj['shows'][0]['position']['x'] <= 2.5
        assert obj['shows'][0]['position']['y'] == 3.8
        z = obj['shows'][0]['position']['z']
        assert z == 1.6 or z == 2.7
        assert 13 <= obj['shows'][0]['stepBegin'] <= 20


def test_mcs_209():
    obj_defs = OBJECTS_INTPHYS.copy()
    random.shuffle(obj_defs)
    obj_def = next((od for od in obj_defs if 'rotation' in od))
    obj = util.instantiate_object(obj_def, {'position': ORIGIN})
    assert obj['shows'][0]['rotation'] == obj_def['rotation']

    class TestGoal(IntPhysGoal):
        TEMPLATE = {'type_list': [], 'metadata':{}}
        pass

    goal = TestGoal()
    objs = goal._get_objects_moving_across('dummy', 55)
    for obj in objs:
        assert obj['shows'][0]['stepBegin'] == obj['forces'][0]['stepBegin']

    body = {'wallMaterial': 'dummy'}
    goal._scenery_count = 0
    goal.update_body(body, False)
