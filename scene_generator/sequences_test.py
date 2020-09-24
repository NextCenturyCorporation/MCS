from sequences import Sequence


class MockSequence(Sequence):
    def __init__(self):
        super().__init__('mock', {}, {})

    def _create_scenes(self, body_template, goal_template):
        return [body_template]


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


def test_Sequence_create_scenes_on_init():
    sequence = MockSequence()
    assert len(sequence._scenes) == 1


def test_Sequence_update_list_with_object_info():
    sequence = MockSequence()

    info_list = sequence._update_list_with_object_info('target', [], [])
    assert info_list == []

    info_list = sequence._update_list_with_object_info(
        'target',
        [],
        [{'info': ['a', 'b']}]
    )
    assert set(info_list) == set(['target a', 'target b'])

    info_list = sequence._update_list_with_object_info(
        'target',
        ['target a'],
        [{'info': ['a', 'b']}]
    )
    assert set(info_list) == set(['target a', 'target b'])

    info_list = sequence._update_list_with_object_info(
        'target',
        ['target a'],
        [{'info': ['b', 'c']}]
    )
    assert set(info_list) == set(['target a', 'target b', 'target c'])

    info_list = sequence._update_list_with_object_info(
        'target',
        ['target a'],
        [{'info': ['a', 'b']}, {'info': ['b', 'c']}]
    )
    assert set(info_list) == set(['target a', 'target b', 'target c'])

    info_list = sequence._update_list_with_object_info(
        'distractor',
        ['target a', 'distractor b'],
        [{'info': ['a', 'b', 'c']}]
    )
    assert set(info_list) == set(
        ['target a', 'distractor b', 'distractor a', 'distractor c']
    )


def test_Sequence_tags():
    sequence = MockSequence()
    target = create_tags_test_object_1()
    scene = sequence._update_scene_objects({}, {'target': [target]})
    assert set(scene['goal']['info_list']) == {
        'target tiny',
        'target light',
        'target blue',
        'target plastic',
        'target ball',
        'target tiny light blue plastic ball'
    }

    # Assert positives
    assert 'target not novel color' in scene['goal']['type_list']
    assert 'target not novel combination' in scene['goal']['type_list']
    assert 'target not novel shape' in scene['goal']['type_list']
    assert 'target not enclosed' in scene['goal']['type_list']
    assert 'targets 1' in scene['goal']['type_list']

    # Assert negatives
    assert 'target novel color' not in scene['goal']['type_list']
    assert 'target novel combination' not in scene['goal']['type_list']
    assert 'target novel shape' not in scene['goal']['type_list']
    assert 'target enclosed' not in scene['goal']['type_list']
    assert 'distractor not novel color' not in scene['goal']['type_list']
    assert 'distractor not novel combination' not in scene['goal']['type_list']
    assert 'distractor not novel shape' not in scene['goal']['type_list']
    assert 'distractor not enclosed' not in scene['goal']['type_list']
    assert 'distractor novel color' not in scene['goal']['type_list']
    assert 'distractor novel combination' not in scene['goal']['type_list']
    assert 'distractor novel shape' not in scene['goal']['type_list']
    assert 'distractor enclosed' not in scene['goal']['type_list']
    assert 'background objects 0' not in scene['goal']['type_list']
    assert 'distractors 0' not in scene['goal']['type_list']
    assert 'occluders 0' not in scene['goal']['type_list']
    assert 'ramps 0' not in scene['goal']['type_list']
    assert 'walls 0' not in scene['goal']['type_list']


def test_Sequence_tags_multiple_target():
    sequence = MockSequence()
    target_1 = create_tags_test_object_1()
    target_2 = create_tags_test_object_2()
    scene = sequence._update_scene_objects(
        {},
        {'target': [target_1, target_2]}
    )
    assert set(scene['goal']['info_list']) == {
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
    assert 'target not novel color' in scene['goal']['type_list']
    assert 'target not novel combination' in scene['goal']['type_list']
    assert 'target not novel shape' in scene['goal']['type_list']
    assert 'target not enclosed' in scene['goal']['type_list']
    assert 'targets 2' in scene['goal']['type_list']


def test_Sequence_tags_with_distractor():
    sequence = MockSequence()
    target = create_tags_test_object_1()
    distractor = create_tags_test_object_2()
    scene = sequence._update_scene_objects(
        {},
        {'target': [target], 'distractor': [distractor]}
    )
    assert set(scene['goal']['info_list']) == {
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
    assert 'target not novel color' in scene['goal']['type_list']
    assert 'target not novel combination' in scene['goal']['type_list']
    assert 'target not novel shape' in scene['goal']['type_list']
    assert 'target not enclosed' in scene['goal']['type_list']
    assert 'distractor not novel color' in scene['goal']['type_list']
    assert 'distractor not novel combination' in scene['goal']['type_list']
    assert 'distractor not novel shape' in scene['goal']['type_list']
    assert 'distractor not enclosed' in scene['goal']['type_list']
    assert 'targets 1' in scene['goal']['type_list']
    assert 'distractors 1' in scene['goal']['type_list']


def test_Sequence_tags_multiple_target_multiple_distractor():
    sequence = MockSequence()
    target_1 = create_tags_test_object_1()
    target_2 = create_tags_test_object_1()
    distractor_1 = create_tags_test_object_2()
    distractor_2 = create_tags_test_object_2()
    scene = sequence._update_scene_objects(
        {},
        {
            'target': [target_1, target_2],
            'distractor': [distractor_1, distractor_2]
        }
    )
    assert set(scene['goal']['info_list']) == {
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
    assert 'target not novel color' in scene['goal']['type_list']
    assert 'target not novel combination' in scene['goal']['type_list']
    assert 'target not novel shape' in scene['goal']['type_list']
    assert 'target not enclosed' in scene['goal']['type_list']
    assert 'distractor not novel color' in scene['goal']['type_list']
    assert 'distractor not novel combination' in scene['goal']['type_list']
    assert 'distractor not novel shape' in scene['goal']['type_list']
    assert 'distractor not enclosed' in scene['goal']['type_list']
    assert 'targets 2' in scene['goal']['type_list']
    assert 'distractors 2' in scene['goal']['type_list']


def test_Sequence_tags_with_occluder():
    sequence = MockSequence()
    target = create_tags_test_object_1()
    occluder_wall = {'info': ['white']}
    occluder_pole = {'info': ['brown']}
    scene = sequence._update_scene_objects(
        {},
        {'target': [target], 'occluder': [occluder_wall, occluder_pole]}
    )
    assert set(scene['goal']['info_list']) == {
        'target tiny',
        'target light',
        'target blue',
        'target plastic',
        'target ball',
        'target tiny light blue plastic ball',
        'occluder white',
        'occluder brown'
    }
    assert 'target not novel color' in scene['goal']['type_list']
    assert 'target not novel combination' in scene['goal']['type_list']
    assert 'target not novel shape' in scene['goal']['type_list']
    assert 'target not enclosed' in scene['goal']['type_list']
    assert 'targets 1' in scene['goal']['type_list']
    assert 'occluders 1' in scene['goal']['type_list']


def test_Sequence_tags_with_wall():
    sequence = MockSequence()
    target = create_tags_test_object_1()
    wall = {'info': ['white']}
    scene = sequence._update_scene_objects(
        {},
        {'target': [target], 'wall': [wall]}
    )
    assert set(scene['goal']['info_list']) == {
        'target tiny',
        'target light',
        'target blue',
        'target plastic',
        'target ball',
        'target tiny light blue plastic ball',
        'wall white'
    }
    assert 'target not novel color' in scene['goal']['type_list']
    assert 'target not novel combination' in scene['goal']['type_list']
    assert 'target not novel shape' in scene['goal']['type_list']
    assert 'target not enclosed' in scene['goal']['type_list']
    assert 'targets 1' in scene['goal']['type_list']
    assert 'walls 1' in scene['goal']['type_list']


def test_Sequence_tags_with_background_object():
    sequence = MockSequence()
    target = create_tags_test_object_1()
    background_object = {'info': ['red']}
    scene = sequence._update_scene_objects(
        {},
        {'target': [target], 'background object': [background_object]}
    )
    assert set(scene['goal']['info_list']) == {
        'target tiny',
        'target light',
        'target blue',
        'target plastic',
        'target ball',
        'target tiny light blue plastic ball',
        'background object red'
    }
    assert 'target not novel color' in scene['goal']['type_list']
    assert 'target not novel combination' in scene['goal']['type_list']
    assert 'target not novel shape' in scene['goal']['type_list']
    assert 'target not enclosed' in scene['goal']['type_list']
    assert 'targets 1' in scene['goal']['type_list']
    assert 'background objects 1' in scene['goal']['type_list']


def test_Sequence_tags_target_enclosed():
    sequence = MockSequence()
    target = create_tags_test_object_1()
    target['locationParent'] = 'parent'
    scene = sequence._update_scene_objects({}, {'target': [target]})
    assert set(scene['goal']['info_list']) == {
        'target tiny',
        'target light',
        'target blue',
        'target plastic',
        'target ball',
        'target tiny light blue plastic ball'
    }
    assert 'target not novel color' in scene['goal']['type_list']
    assert 'target not novel combination' in scene['goal']['type_list']
    assert 'target not novel shape' in scene['goal']['type_list']
    assert 'targets 1' in scene['goal']['type_list']
    assert 'target enclosed' in scene['goal']['type_list']


def test_Sequence_tags_target_novel_color():
    sequence = MockSequence()
    target = create_tags_test_object_1()
    target['novelColor'] = True
    scene = sequence._update_scene_objects({}, {'target': [target]})
    assert set(scene['goal']['info_list']) == {
        'target tiny',
        'target light',
        'target blue',
        'target plastic',
        'target ball',
        'target tiny light blue plastic ball'
    }
    assert 'target novel color' in scene['goal']['type_list']
    assert 'target not novel combination' in scene['goal']['type_list']
    assert 'target not novel shape' in scene['goal']['type_list']
    assert 'targets 1' in scene['goal']['type_list']
    assert 'target not enclosed' in scene['goal']['type_list']


def test_Sequence_tags_target_novel_combination():
    sequence = MockSequence()
    target = create_tags_test_object_1()
    target['novelCombination'] = True
    scene = sequence._update_scene_objects({}, {'target': [target]})
    assert set(scene['goal']['info_list']) == {
        'target tiny',
        'target light',
        'target blue',
        'target plastic',
        'target ball',
        'target tiny light blue plastic ball'
    }
    assert 'target not novel color' in scene['goal']['type_list']
    assert 'target novel combination' in scene['goal']['type_list']
    assert 'target not novel shape' in scene['goal']['type_list']
    assert 'targets 1' in scene['goal']['type_list']
    assert 'target not enclosed' in scene['goal']['type_list']


def test_Sequence_tags_target_novel_shape():
    sequence = MockSequence()
    target = create_tags_test_object_1()
    target['novelShape'] = True
    scene = sequence._update_scene_objects({}, {'target': [target]})
    assert set(scene['goal']['info_list']) == {
        'target tiny',
        'target light',
        'target blue',
        'target plastic',
        'target ball',
        'target tiny light blue plastic ball'
    }
    assert 'target not novel color' in scene['goal']['type_list']
    assert 'target not novel combination' in scene['goal']['type_list']
    assert 'target novel shape' in scene['goal']['type_list']
    assert 'targets 1' in scene['goal']['type_list']
    assert 'target not enclosed' in scene['goal']['type_list']


def test_Sequence_tags_target_enclosed_novel_color_novel_shape():
    sequence = MockSequence()
    target = create_tags_test_object_1()
    target['locationParent'] = 'parent'
    target['novelColor'] = True
    target['novelShape'] = True
    scene = sequence._update_scene_objects({}, {'target': [target]})
    assert set(scene['goal']['info_list']) == {
        'target tiny',
        'target light',
        'target blue',
        'target plastic',
        'target ball',
        'target tiny light blue plastic ball'
    }
    assert 'target novel color' in scene['goal']['type_list']
    assert 'target not novel combination' in scene['goal']['type_list']
    assert 'target novel shape' in scene['goal']['type_list']
    assert 'targets 1' in scene['goal']['type_list']
    assert 'target enclosed' in scene['goal']['type_list']


def test_Sequence_tags_distractor_enclosed():
    sequence = MockSequence()
    target = create_tags_test_object_1()
    distractor = create_tags_test_object_2()
    distractor['locationParent'] = 'parent'
    scene = sequence._update_scene_objects(
        {},
        {'target': [target], 'distractor': [distractor]}
    )
    assert set(scene['goal']['info_list']) == {
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
    assert 'target not novel color' in scene['goal']['type_list']
    assert 'target not novel combination' in scene['goal']['type_list']
    assert 'target not novel shape' in scene['goal']['type_list']
    assert 'target not enclosed' in scene['goal']['type_list']
    assert 'distractor not novel color' in scene['goal']['type_list']
    assert 'distractor not novel combination' in scene['goal']['type_list']
    assert 'distractor not novel shape' in scene['goal']['type_list']
    assert 'distractor enclosed' in scene['goal']['type_list']
    assert 'targets 1' in scene['goal']['type_list']
    assert 'distractors 1' in scene['goal']['type_list']


def test_Sequence_tags_distractor_novel_color():
    sequence = MockSequence()
    target = create_tags_test_object_1()
    distractor = create_tags_test_object_2()
    distractor['novelColor'] = True
    scene = sequence._update_scene_objects(
        {},
        {'target': [target], 'distractor': [distractor]}
    )
    assert set(scene['goal']['info_list']) == {
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
    assert 'target not novel color' in scene['goal']['type_list']
    assert 'target not novel combination' in scene['goal']['type_list']
    assert 'target not novel shape' in scene['goal']['type_list']
    assert 'target not enclosed' in scene['goal']['type_list']
    assert 'distractor novel color' in scene['goal']['type_list']
    assert 'distractor not novel combination' in scene['goal']['type_list']
    assert 'distractor not novel shape' in scene['goal']['type_list']
    assert 'distractor not enclosed' in scene['goal']['type_list']
    assert 'targets 1' in scene['goal']['type_list']
    assert 'distractors 1' in scene['goal']['type_list']


def test_Sequence_tags_distractor_novel_combination():
    sequence = MockSequence()
    target = create_tags_test_object_1()
    distractor = create_tags_test_object_2()
    distractor['novelCombination'] = True
    scene = sequence._update_scene_objects(
        {},
        {'target': [target], 'distractor': [distractor]}
    )
    assert set(scene['goal']['info_list']) == {
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
    assert 'target not novel color' in scene['goal']['type_list']
    assert 'target not novel combination' in scene['goal']['type_list']
    assert 'target not novel shape' in scene['goal']['type_list']
    assert 'target not enclosed' in scene['goal']['type_list']
    assert 'distractor not novel color' in scene['goal']['type_list']
    assert 'distractor novel combination' in scene['goal']['type_list']
    assert 'distractor not novel shape' in scene['goal']['type_list']
    assert 'distractor not enclosed' in scene['goal']['type_list']
    assert 'targets 1' in scene['goal']['type_list']
    assert 'distractors 1' in scene['goal']['type_list']


def test_Sequence_tags_distractor_novel_shape():
    sequence = MockSequence()
    target = create_tags_test_object_1()
    distractor = create_tags_test_object_2()
    distractor['novelShape'] = True
    scene = sequence._update_scene_objects(
        {},
        {'target': [target], 'distractor': [distractor]}
    )
    assert set(scene['goal']['info_list']) == {
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
    assert 'target not novel color' in scene['goal']['type_list']
    assert 'target not novel combination' in scene['goal']['type_list']
    assert 'target not novel shape' in scene['goal']['type_list']
    assert 'target not enclosed' in scene['goal']['type_list']
    assert 'distractor not novel color' in scene['goal']['type_list']
    assert 'distractor not novel combination' in scene['goal']['type_list']
    assert 'distractor novel shape' in scene['goal']['type_list']
    assert 'distractor not enclosed' in scene['goal']['type_list']
    assert 'targets 1' in scene['goal']['type_list']
    assert 'distractors 1' in scene['goal']['type_list']


def test_Sequence_tags_distractor_enclosed_novel_color_novel_shape():
    sequence = MockSequence()
    target = create_tags_test_object_1()
    distractor = create_tags_test_object_2()
    distractor['locationParent'] = 'parent'
    distractor['novelColor'] = True
    distractor['novelShape'] = True
    scene = sequence._update_scene_objects(
        {},
        {'target': [target], 'distractor': [distractor]}
    )
    assert set(scene['goal']['info_list']) == {
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
    assert 'target not novel color' in scene['goal']['type_list']
    assert 'target not novel combination' in scene['goal']['type_list']
    assert 'target not novel shape' in scene['goal']['type_list']
    assert 'target not enclosed' in scene['goal']['type_list']
    assert 'distractor novel color' in scene['goal']['type_list']
    assert 'distractor not novel combination' in scene['goal']['type_list']
    assert 'distractor novel shape' in scene['goal']['type_list']
    assert 'distractor enclosed' in scene['goal']['type_list']
    assert 'targets 1' in scene['goal']['type_list']
    assert 'distractors 1' in scene['goal']['type_list']


def test_Sequence_tags_target_distractor_enclosed_novel_color_novel_shape():
    sequence = MockSequence()
    target = create_tags_test_object_1()
    target['locationParent'] = 'parent'
    target['novelColor'] = True
    target['novelShape'] = True
    distractor = create_tags_test_object_2()
    distractor['locationParent'] = 'parent'
    distractor['novelColor'] = True
    distractor['novelShape'] = True
    scene = sequence._update_scene_objects(
        {},
        {'target': [target], 'distractor': [distractor]}
    )
    assert set(scene['goal']['info_list']) == {
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
    assert 'target novel color' in scene['goal']['type_list']
    assert 'target not novel combination' in scene['goal']['type_list']
    assert 'target novel shape' in scene['goal']['type_list']
    assert 'target enclosed' in scene['goal']['type_list']
    assert 'distractor novel color' in scene['goal']['type_list']
    assert 'distractor not novel combination' in scene['goal']['type_list']
    assert 'distractor novel shape' in scene['goal']['type_list']
    assert 'distractor enclosed' in scene['goal']['type_list']
    assert 'targets 1' in scene['goal']['type_list']
    assert 'distractors 1' in scene['goal']['type_list']
