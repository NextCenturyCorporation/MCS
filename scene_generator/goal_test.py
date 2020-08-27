import geometry

from goal import generate_wall, MAX_WALL_WIDTH, MIN_WALL_WIDTH, \
    WALL_DEPTH, WALL_HEIGHT, WALL_Y_POS
from interaction_goals import RetrievalGoal


def create_tags_test_object_1():
    return {
        'id': 'test_sphere',
        'type': 'sphere',
        'dimensions': {
            'x': 0.1,
            'y': 0.1,
            'z': 0.1
        },
        'info': ['tiny', 'light', 'blue', 'plastic', 'ball'],
        'goalString': 'tiny light blue plastic ball',
        'mass': 0.5,
        'materials': ['test_material'],
        'materialCategory': ['plastic'],
        'salientMaterials': ['plastic'],
        'moveable': True,
        'novelColor': False,
        'novelCombination': False,
        'novelShape': False,
        'pickupable': True,
        'shows': [{
            'stepBegin': 0,
            'position': {
                'x': 0,
                'y': 0,
                'z': 0
            }
        }]
    }


def create_tags_test_object_2():
    return {
        'id': 'test_cube',
        'type': 'cube',
        'dimensions': {
            'x': 0.5,
            'y': 0.5,
            'z': 0.5
        },
        'info': ['medium', 'light', 'yellow', 'plastic', 'cube'],
        'goalString': 'medium light yellow plastic cube',
        'mass': 2.5,
        'materials': ['test_material'],
        'materialCategory': ['plastic'],
        'salientMaterials': ['plastic'],
        'moveable': True,
        'novelColor': False,
        'novelCombination': False,
        'novelShape': False,
        'pickupable': True,
        'shows': [{
            'stepBegin': 0,
            'position': {
                'x': 1,
                'y': 2,
                'z': 3
            }
        }]
    }


def test_generate_wall():
    wall = generate_wall(
        'test_material', [
            'test_color_1', 'test_color_2'], geometry.ORIGIN, [])

    assert wall
    assert wall['id']
    assert wall['materials'] == ['test_material']
    assert wall['type'] == 'cube'
    assert wall['kinematic'] == 'true'
    assert wall['structure'] == 'true'
    assert wall['mass'] == 200
    assert wall['info'] == ['test_color_1', 'test_color_2']

    assert len(wall['shows']) == 1
    assert wall['shows'][0]['stepBegin'] == 0
    assert wall['shows'][0]['scale']['x'] >= MIN_WALL_WIDTH and \
        wall['shows'][0]['scale']['x'] <= MAX_WALL_WIDTH
    assert wall['shows'][0]['scale']['y'] == WALL_HEIGHT
    assert wall['shows'][0]['scale']['z'] == WALL_DEPTH
    assert wall['shows'][0]['rotation']['x'] == 0
    assert wall['shows'][0]['rotation']['y'] % 90 == 0
    assert wall['shows'][0]['rotation']['z'] == 0
    assert wall['shows'][0]['position']['x'] is not None
    assert wall['shows'][0]['position']['y'] == WALL_Y_POS
    assert wall['shows'][0]['position']['z'] is not None
    assert wall['shows'][0]['boundingBox'] is not None

    assert 'hides' not in wall
    assert 'moves' not in wall
    assert 'rotates' not in wall
    assert 'teleports' not in wall

    player_rect = geometry.find_performer_rect(geometry.ORIGIN)
    player_poly = geometry.rect_to_poly(player_rect)
    wall_poly = geometry.rect_to_poly(wall['shows'][0]['boundingBox'])
    assert not wall_poly.intersects(player_poly)
    assert geometry.rect_within_room(wall['shows'][0]['boundingBox'])


def test_generate_wall_multiple():
    wall_1 = generate_wall('test_material', [], geometry.ORIGIN, [])
    wall_2 = generate_wall(
        'test_material', [], geometry.ORIGIN, [
            wall_1['shows'][0]['boundingBox']])
    wall_1_poly = geometry.rect_to_poly(wall_1['shows'][0]['boundingBox'])
    wall_2_poly = geometry.rect_to_poly(wall_2['shows'][0]['boundingBox'])
    assert not wall_1_poly.intersects(wall_2_poly)


def test_generate_wall_with_bounds_list():
    bounds = [{'x': 4, 'y': 0, 'z': 4}, {'x': 4, 'y': 0, 'z': 1},
              {'x': 1, 'y': 0, 'z': 1}, {'x': 1, 'y': 0, 'z': 4}]
    wall = generate_wall('test_material', [], geometry.ORIGIN, [bounds])
    poly = geometry.rect_to_poly(bounds)
    wall_poly = geometry.rect_to_poly(wall['shows'][0]['boundingBox'])
    assert not wall_poly.intersects(poly)


def test_generate_wall_with_target_list():
    bounds = [{'x': 4, 'y': 0, 'z': 4}, {'x': 4, 'y': 0, 'z': 3},
              {'x': 3, 'y': 0, 'z': 3}, {'x': 3, 'y': 0, 'z': 4}]
    target = {'shows': [{'boundingBox': bounds}]}
    wall = generate_wall(
        'test_material',
        [],
        geometry.ORIGIN,
        [bounds],
        [target])
    wall_poly = geometry.rect_to_poly(wall['shows'][0]['boundingBox'])
    assert not geometry.does_fully_obstruct_target(
        geometry.ORIGIN, target, wall_poly)


def test_Goal_update_goal_info_list():
    goal_object = RetrievalGoal()

    info_list = goal_object.update_goal_info_list([], {})
    assert info_list == []

    info_list = goal_object.update_goal_info_list([], {'target': []})
    assert info_list == []

    info_list = goal_object.update_goal_info_list(
        [], {'target': [{'info': []}]})
    assert info_list == []

    info_list = goal_object.update_goal_info_list(
        [], {'target': [{'info': ['a', 'b']}]})
    assert set(info_list) == set(['target a', 'target b'])

    info_list = goal_object.update_goal_info_list(
        ['target a'], {'target': [{'info': ['a', 'b']}]})
    assert set(info_list) == set(['target a', 'target b'])

    info_list = goal_object.update_goal_info_list(
        ['target a'], {'target': [{'info': ['b', 'c']}]})
    assert set(info_list) == set(['target a', 'target b', 'target c'])

    info_list = goal_object.update_goal_info_list(
        ['target a'], {'target': [{'info': ['a', 'b']}, {'info': ['b', 'c']}]}
    )
    assert set(info_list) == set(['target a', 'target b', 'target c'])

    info_list = goal_object.update_goal_info_list(
        ['target a', 'distractor b'],
        {
            'target': [{'info': ['a', 'b']}],
            'distractor': [{'info': ['b', 'c']}]
        }
    )
    assert set(info_list) == set(
        ['target a', 'target b', 'distractor b', 'distractor c'])


def test_Goal_reset_performer_start():
    goal_object = RetrievalGoal()
    old_performer_start = goal_object.get_performer_start()
    assert old_performer_start == goal_object.get_performer_start()
    new_performer_start = goal_object.reset_performer_start()
    assert new_performer_start == goal_object.get_performer_start()
    assert old_performer_start != new_performer_start


def test_Goal_tags():
    goal_object = RetrievalGoal()
    target = create_tags_test_object_1()
    goal = goal_object._get_config({'target': [target]})
    assert set(goal['info_list']) == {
        'target tiny',
        'target light',
        'target blue',
        'target plastic',
        'target ball',
        'target tiny light blue plastic ball'
    }

    # Assert positives
    assert 'target not novel color' in goal['type_list']
    assert 'target not novel combination' in goal['type_list']
    assert 'target not novel shape' in goal['type_list']
    assert 'target not enclosed' in goal['type_list']
    assert 'targets 1' in goal['type_list']

    # Assert negatives
    assert 'target novel color' not in goal['type_list']
    assert 'target novel combination' not in goal['type_list']
    assert 'target novel shape' not in goal['type_list']
    assert 'target enclosed' not in goal['type_list']
    assert 'distractor not novel color' not in goal['type_list']
    assert 'distractor not novel combination' not in goal['type_list']
    assert 'distractor not novel shape' not in goal['type_list']
    assert 'distractor not enclosed' not in goal['type_list']
    assert 'distractor novel color' not in goal['type_list']
    assert 'distractor novel combination' not in goal['type_list']
    assert 'distractor novel shape' not in goal['type_list']
    assert 'distractor enclosed' not in goal['type_list']
    assert 'background objects 0' not in goal['type_list']
    assert 'distractors 0' not in goal['type_list']
    assert 'occluders 0' not in goal['type_list']
    assert 'ramps 0' not in goal['type_list']
    assert 'walls 0' not in goal['type_list']


def test_Goal_tags_multiple_target():
    goal_object = RetrievalGoal()
    target_1 = create_tags_test_object_1()
    target_2 = create_tags_test_object_2()
    goal = goal_object._get_config({'target': [target_1, target_2]})
    assert set(goal['info_list']) == {
        'target tiny',
        'target light',
        'target blue',
        'target plastic',
        'target ball',
        'target tiny light blue plastic ball',
        'target medium',
        'target yellow',
        'target cube',
        'target medium light yellow plastic cube'
    }
    assert 'target not novel color' in goal['type_list']
    assert 'target not novel combination' in goal['type_list']
    assert 'target not novel shape' in goal['type_list']
    assert 'target not enclosed' in goal['type_list']
    assert 'targets 2' in goal['type_list']


def test_Goal_tags_with_distractor():
    goal_object = RetrievalGoal()
    target = create_tags_test_object_1()
    distractor = create_tags_test_object_2()
    goal = goal_object._get_config(
        {'target': [target], 'distractor': [distractor]})
    assert set(goal['info_list']) == {
        'target tiny',
        'target light',
        'target blue',
        'target plastic',
        'target ball',
        'target tiny light blue plastic ball',
        'distractor medium',
        'distractor light',
        'distractor yellow',
        'distractor plastic',
        'distractor cube',
        'distractor medium light yellow plastic cube'
    }
    assert 'target not novel color' in goal['type_list']
    assert 'target not novel combination' in goal['type_list']
    assert 'target not novel shape' in goal['type_list']
    assert 'target not enclosed' in goal['type_list']
    assert 'distractor not novel color' in goal['type_list']
    assert 'distractor not novel combination' in goal['type_list']
    assert 'distractor not novel shape' in goal['type_list']
    assert 'distractor not enclosed' in goal['type_list']
    assert 'targets 1' in goal['type_list']
    assert 'distractors 1' in goal['type_list']


def test_Goal_tags_multiple_target_multiple_distractor():
    goal_object = RetrievalGoal()
    target_1 = create_tags_test_object_1()
    target_2 = create_tags_test_object_1()
    distractor_1 = create_tags_test_object_2()
    distractor_2 = create_tags_test_object_2()
    goal = goal_object._get_config(
        {
            'target': [target_1, target_2],
            'distractor': [distractor_1, distractor_2]
        }
    )
    assert set(goal['info_list']) == {
        'target tiny',
        'target light',
        'target blue',
        'target plastic',
        'target ball',
        'target tiny light blue plastic ball',
        'distractor medium',
        'distractor light',
        'distractor yellow',
        'distractor plastic',
        'distractor cube',
        'distractor medium light yellow plastic cube'
    }
    assert 'target not novel color' in goal['type_list']
    assert 'target not novel combination' in goal['type_list']
    assert 'target not novel shape' in goal['type_list']
    assert 'target not enclosed' in goal['type_list']
    assert 'distractor not novel color' in goal['type_list']
    assert 'distractor not novel combination' in goal['type_list']
    assert 'distractor not novel shape' in goal['type_list']
    assert 'distractor not enclosed' in goal['type_list']
    assert 'targets 2' in goal['type_list']
    assert 'distractors 2' in goal['type_list']


def test_Goal_tags_with_occluder():
    goal_object = RetrievalGoal()
    target = create_tags_test_object_1()
    occluder_wall = {'info': ['white']}
    occluder_pole = {'info': ['brown']}
    goal = goal_object._get_config(
        {'target': [target], 'occluder': [occluder_wall, occluder_pole]})
    assert set(goal['info_list']) == {
        'target tiny',
        'target light',
        'target blue',
        'target plastic',
        'target ball',
        'target tiny light blue plastic ball',
        'occluder white',
        'occluder brown'
    }
    assert 'target not novel color' in goal['type_list']
    assert 'target not novel combination' in goal['type_list']
    assert 'target not novel shape' in goal['type_list']
    assert 'target not enclosed' in goal['type_list']
    assert 'targets 1' in goal['type_list']
    assert 'occluders 1' in goal['type_list']


def test_Goal_tags_with_wall():
    goal_object = RetrievalGoal()
    target = create_tags_test_object_1()
    wall = {'info': ['white']}
    goal = goal_object._get_config({'target': [target], 'wall': [wall]})
    assert set(goal['info_list']) == {
        'target tiny',
        'target light',
        'target blue',
        'target plastic',
        'target ball',
        'target tiny light blue plastic ball',
        'wall white'
    }
    assert 'target not novel color' in goal['type_list']
    assert 'target not novel combination' in goal['type_list']
    assert 'target not novel shape' in goal['type_list']
    assert 'target not enclosed' in goal['type_list']
    assert 'targets 1' in goal['type_list']
    assert 'walls 1' in goal['type_list']


def test_Goal_tags_with_background_object():
    goal_object = RetrievalGoal()
    target = create_tags_test_object_1()
    background_object = {'info': ['red']}
    goal = goal_object._get_config(
        {'target': [target], 'background object': [background_object]})
    assert set(goal['info_list']) == {
        'target tiny',
        'target light',
        'target blue',
        'target plastic',
        'target ball',
        'target tiny light blue plastic ball',
        'background object red'
    }
    assert 'target not novel color' in goal['type_list']
    assert 'target not novel combination' in goal['type_list']
    assert 'target not novel shape' in goal['type_list']
    assert 'target not enclosed' in goal['type_list']
    assert 'targets 1' in goal['type_list']
    assert 'background objects 1' in goal['type_list']


def test_Goal_tags_target_enclosed():
    goal_object = RetrievalGoal()
    target = create_tags_test_object_1()
    target['locationParent'] = 'parent'
    goal = goal_object._get_config({'target': [target]})
    assert set(goal['info_list']) == {
        'target tiny',
        'target light',
        'target blue',
        'target plastic',
        'target ball',
        'target tiny light blue plastic ball'
    }
    assert 'target not novel color' in goal['type_list']
    assert 'target not novel combination' in goal['type_list']
    assert 'target not novel shape' in goal['type_list']
    assert 'targets 1' in goal['type_list']
    assert 'target enclosed' in goal['type_list']


def test_Goal_tags_target_novel_color():
    goal_object = RetrievalGoal()
    target = create_tags_test_object_1()
    target['novelColor'] = True
    goal = goal_object._get_config({'target': [target]})
    assert set(goal['info_list']) == {
        'target tiny',
        'target light',
        'target blue',
        'target plastic',
        'target ball',
        'target tiny light blue plastic ball'
    }
    assert 'target novel color' in goal['type_list']
    assert 'target not novel combination' in goal['type_list']
    assert 'target not novel shape' in goal['type_list']
    assert 'targets 1' in goal['type_list']
    assert 'target not enclosed' in goal['type_list']


def test_Goal_tags_target_novel_combination():
    goal_object = RetrievalGoal()
    target = create_tags_test_object_1()
    target['novelCombination'] = True
    goal = goal_object._get_config({'target': [target]})
    assert set(goal['info_list']) == {
        'target tiny',
        'target light',
        'target blue',
        'target plastic',
        'target ball',
        'target tiny light blue plastic ball'
    }
    assert 'target not novel color' in goal['type_list']
    assert 'target novel combination' in goal['type_list']
    assert 'target not novel shape' in goal['type_list']
    assert 'targets 1' in goal['type_list']
    assert 'target not enclosed' in goal['type_list']


def test_Goal_tags_target_novel_shape():
    goal_object = RetrievalGoal()
    target = create_tags_test_object_1()
    target['novelShape'] = True
    goal = goal_object._get_config({'target': [target]})
    assert set(goal['info_list']) == {
        'target tiny',
        'target light',
        'target blue',
        'target plastic',
        'target ball',
        'target tiny light blue plastic ball'
    }
    assert 'target not novel color' in goal['type_list']
    assert 'target not novel combination' in goal['type_list']
    assert 'target novel shape' in goal['type_list']
    assert 'targets 1' in goal['type_list']
    assert 'target not enclosed' in goal['type_list']


def test_Goal_tags_target_enclosed_novel_color_novel_shape():
    goal_object = RetrievalGoal()
    target = create_tags_test_object_1()
    target['locationParent'] = 'parent'
    target['novelColor'] = True
    target['novelShape'] = True
    goal = goal_object._get_config({'target': [target]})
    assert set(goal['info_list']) == {
        'target tiny',
        'target light',
        'target blue',
        'target plastic',
        'target ball',
        'target tiny light blue plastic ball'
    }
    assert 'target novel color' in goal['type_list']
    assert 'target not novel combination' in goal['type_list']
    assert 'target novel shape' in goal['type_list']
    assert 'targets 1' in goal['type_list']
    assert 'target enclosed' in goal['type_list']


def test_Goal_tags_distractor_enclosed():
    goal_object = RetrievalGoal()
    target = create_tags_test_object_1()
    distractor = create_tags_test_object_2()
    distractor['locationParent'] = 'parent'
    goal = goal_object._get_config(
        {'target': [target], 'distractor': [distractor]})
    assert set(goal['info_list']) == {
        'target tiny',
        'target light',
        'target blue',
        'target plastic',
        'target ball',
        'target tiny light blue plastic ball',
        'distractor medium',
        'distractor light',
        'distractor yellow',
        'distractor plastic',
        'distractor cube',
        'distractor medium light yellow plastic cube'
    }
    assert 'target not novel color' in goal['type_list']
    assert 'target not novel combination' in goal['type_list']
    assert 'target not novel shape' in goal['type_list']
    assert 'target not enclosed' in goal['type_list']
    assert 'distractor not novel color' in goal['type_list']
    assert 'distractor not novel combination' in goal['type_list']
    assert 'distractor not novel shape' in goal['type_list']
    assert 'distractor enclosed' in goal['type_list']
    assert 'targets 1' in goal['type_list']
    assert 'distractors 1' in goal['type_list']


def test_Goal_tags_distractor_novel_color():
    goal_object = RetrievalGoal()
    target = create_tags_test_object_1()
    distractor = create_tags_test_object_2()
    distractor['novelColor'] = True
    goal = goal_object._get_config(
        {'target': [target], 'distractor': [distractor]})
    assert set(goal['info_list']) == {
        'target tiny',
        'target light',
        'target blue',
        'target plastic',
        'target ball',
        'target tiny light blue plastic ball',
        'distractor medium',
        'distractor light',
        'distractor yellow',
        'distractor plastic',
        'distractor cube',
        'distractor medium light yellow plastic cube'
    }
    assert 'target not novel color' in goal['type_list']
    assert 'target not novel combination' in goal['type_list']
    assert 'target not novel shape' in goal['type_list']
    assert 'target not enclosed' in goal['type_list']
    assert 'distractor novel color' in goal['type_list']
    assert 'distractor not novel combination' in goal['type_list']
    assert 'distractor not novel shape' in goal['type_list']
    assert 'distractor not enclosed' in goal['type_list']
    assert 'targets 1' in goal['type_list']
    assert 'distractors 1' in goal['type_list']


def test_Goal_tags_distractor_novel_combination():
    goal_object = RetrievalGoal()
    target = create_tags_test_object_1()
    distractor = create_tags_test_object_2()
    distractor['novelCombination'] = True
    goal = goal_object._get_config(
        {'target': [target], 'distractor': [distractor]})
    assert set(goal['info_list']) == {
        'target tiny',
        'target light',
        'target blue',
        'target plastic',
        'target ball',
        'target tiny light blue plastic ball',
        'distractor medium',
        'distractor light',
        'distractor yellow',
        'distractor plastic',
        'distractor cube',
        'distractor medium light yellow plastic cube'
    }
    assert 'target not novel color' in goal['type_list']
    assert 'target not novel combination' in goal['type_list']
    assert 'target not novel shape' in goal['type_list']
    assert 'target not enclosed' in goal['type_list']
    assert 'distractor not novel color' in goal['type_list']
    assert 'distractor novel combination' in goal['type_list']
    assert 'distractor not novel shape' in goal['type_list']
    assert 'distractor not enclosed' in goal['type_list']
    assert 'targets 1' in goal['type_list']
    assert 'distractors 1' in goal['type_list']


def test_Goal_tags_distractor_novel_shape():
    goal_object = RetrievalGoal()
    target = create_tags_test_object_1()
    distractor = create_tags_test_object_2()
    distractor['novelShape'] = True
    goal = goal_object._get_config(
        {'target': [target], 'distractor': [distractor]})
    assert set(goal['info_list']) == {
        'target tiny',
        'target light',
        'target blue',
        'target plastic',
        'target ball',
        'target tiny light blue plastic ball',
        'distractor medium',
        'distractor light',
        'distractor yellow',
        'distractor plastic',
        'distractor cube',
        'distractor medium light yellow plastic cube'
    }
    assert 'target not novel color' in goal['type_list']
    assert 'target not novel combination' in goal['type_list']
    assert 'target not novel shape' in goal['type_list']
    assert 'target not enclosed' in goal['type_list']
    assert 'distractor not novel color' in goal['type_list']
    assert 'distractor not novel combination' in goal['type_list']
    assert 'distractor novel shape' in goal['type_list']
    assert 'distractor not enclosed' in goal['type_list']
    assert 'targets 1' in goal['type_list']
    assert 'distractors 1' in goal['type_list']


def test_Goal_tags_distractor_enclosed_novel_color_novel_shape():
    goal_object = RetrievalGoal()
    target = create_tags_test_object_1()
    distractor = create_tags_test_object_2()
    distractor['locationParent'] = 'parent'
    distractor['novelColor'] = True
    distractor['novelShape'] = True
    goal = goal_object._get_config(
        {'target': [target], 'distractor': [distractor]})
    assert set(goal['info_list']) == {
        'target tiny',
        'target light',
        'target blue',
        'target plastic',
        'target ball',
        'target tiny light blue plastic ball',
        'distractor medium',
        'distractor light',
        'distractor yellow',
        'distractor plastic',
        'distractor cube',
        'distractor medium light yellow plastic cube'
    }
    assert 'target not novel color' in goal['type_list']
    assert 'target not novel combination' in goal['type_list']
    assert 'target not novel shape' in goal['type_list']
    assert 'target not enclosed' in goal['type_list']
    assert 'distractor novel color' in goal['type_list']
    assert 'distractor not novel combination' in goal['type_list']
    assert 'distractor novel shape' in goal['type_list']
    assert 'distractor enclosed' in goal['type_list']
    assert 'targets 1' in goal['type_list']
    assert 'distractors 1' in goal['type_list']


def test_Goal_tags_target_distractor_enclosed_novel_color_novel_shape():
    goal_object = RetrievalGoal()
    target = create_tags_test_object_1()
    target['locationParent'] = 'parent'
    target['novelColor'] = True
    target['novelShape'] = True
    distractor = create_tags_test_object_2()
    distractor['locationParent'] = 'parent'
    distractor['novelColor'] = True
    distractor['novelShape'] = True
    goal = goal_object._get_config(
        {'target': [target], 'distractor': [distractor]})
    assert set(goal['info_list']) == {
        'target tiny',
        'target light',
        'target blue',
        'target plastic',
        'target ball',
        'target tiny light blue plastic ball',
        'distractor medium',
        'distractor light',
        'distractor yellow',
        'distractor plastic',
        'distractor cube',
        'distractor medium light yellow plastic cube'
    }
    assert 'target novel color' in goal['type_list']
    assert 'target not novel combination' in goal['type_list']
    assert 'target novel shape' in goal['type_list']
    assert 'target enclosed' in goal['type_list']
    assert 'distractor novel color' in goal['type_list']
    assert 'distractor not novel combination' in goal['type_list']
    assert 'distractor novel shape' in goal['type_list']
    assert 'distractor enclosed' in goal['type_list']
    assert 'targets 1' in goal['type_list']
    assert 'distractors 1' in goal['type_list']
