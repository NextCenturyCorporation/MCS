import materials
from geometry import ORIGIN
from goals import *

from intphys_goals import IntPhysGoal
from objects import OBJECTS_INTPHYS
from util import instantiate_object, random_real


def test_random_real():
    n = random_real(0, 1, 0.1)
    assert 0 <= n <= 1
    # need to multiply by 10 and mod by 1 instead of 0.1 to avoid weird roundoff
    assert n * 10 % 1 < 1e-8


def test_GravityGoal_compute_objects():
    goal = GravityGoal()
    target_objs, all_objs, rects = goal.compute_objects('dummy wall material')
    assert len(target_objs) > 0
    assert len(all_objs) > 0
    assert len(rects) == 0


# test for MCS-214
def test_GravityGoal__get_ramp_and_objects():
    goal = GravityGoal()
    ramp_type, left_to_right, ramp_objs, object_list = goal._get_ramp_and_objects('dummy')
    assert len(ramp_objs) >= 1
    for obj in object_list:
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
    obj = instantiate_object(obj_def, {'position': ORIGIN})
    assert obj['shows'][0]['rotation'] == obj_def['rotation']

    class TestGoal(IntPhysGoal):
        TEMPLATE = {'type_list': [], 'metadata': {}}
        pass

    goal = TestGoal()
    objs = goal._get_objects_moving_across('dummy', 55)
    for obj in objs:
        assert obj['shows'][0]['stepBegin'] == obj['forces'][0]['stepBegin']

    body = {'wallMaterial': 'dummy'}
    goal._scenery_count = 0
    goal.update_body(body, False)
