import uuid

from goals import *
from util import instantiate_object


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
        'info_string': 'tiny light blue plastic ball',
        'mass': 0.5,
        'materials': ['test_material'],
        'materialCategory': ['plastic'],
        'salientMaterials': ['plastic'],
        'moveable': True,
        'novel_color': False,
        'novel_combination': False,
        'novel_shape': False,
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
        'info_string': 'medium light yellow plastic cube',
        'mass': 2.5,
        'materials': ['test_material'],
        'materialCategory': ['plastic'],
        'salientMaterials': ['plastic'],
        'moveable': True,
        'novel_color': False,
        'novel_combination': False,
        'novel_shape': False,
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


def test_Goal_tags():
    goal_object = RetrievalGoal()
    target = create_tags_test_object_1()
    goal = goal_object.get_config([target], { 'target': [target] })
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
    goal = goal_object.get_config([target_1, target_2], { 'target': [target_1, target_2] })
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
    goal = goal_object.get_config([target], { 'target': [target], 'distractor': [distractor] })
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
    goal = goal_object.get_config([target_1, target_2], { 'target': [target_1, target_2], \
            'distractor': [distractor_1, distractor_2] })
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
    occluder_wall = { 'info': ['white'] }
    occluder_pole = { 'info': ['brown'] }
    goal = goal_object.get_config([target], { 'target': [target], 'occluder': [occluder_wall, occluder_pole] })
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
    wall = { 'info': ['white'] }
    goal = goal_object.get_config([target], { 'target': [target], 'wall': [wall] })
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
    background_object = { 'info': ['red'] }
    goal = goal_object.get_config([target], { 'target': [target], 'background object': [background_object] })
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
    goal = goal_object.get_config([target], { 'target': [target] })
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
    target['novel_color'] = True
    goal = goal_object.get_config([target], { 'target': [target] })
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
    target['novel_combination'] = True
    goal = goal_object.get_config([target], { 'target': [target] })
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
    target['novel_shape'] = True
    goal = goal_object.get_config([target], { 'target': [target] })
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
    target['novel_color'] = True
    target['novel_shape'] = True
    goal = goal_object.get_config([target], { 'target': [target] })
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
    goal = goal_object.get_config([target], { 'target': [target], 'distractor': [distractor] })
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
    distractor['novel_color'] = True
    goal = goal_object.get_config([target], { 'target': [target], 'distractor': [distractor] })
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
    distractor['novel_combination'] = True
    goal = goal_object.get_config([target], { 'target': [target], 'distractor': [distractor] })
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
    distractor['novel_shape'] = True
    goal = goal_object.get_config([target], { 'target': [target], 'distractor': [distractor] })
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
    distractor['novel_color'] = True
    distractor['novel_shape'] = True
    goal = goal_object.get_config([target], { 'target': [target], 'distractor': [distractor] })
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
    target['novel_color'] = True
    target['novel_shape'] = True
    distractor = create_tags_test_object_2()
    distractor['locationParent'] = 'parent'
    distractor['novel_color'] = True
    distractor['novel_shape'] = True
    goal = goal_object.get_config([target], { 'target': [target], 'distractor': [distractor] })
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

