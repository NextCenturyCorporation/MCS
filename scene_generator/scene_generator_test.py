from scene_generator import generate_scene, clean_object


def test_generate_scene_goal_info():
    scene = generate_scene('test', 'interaction', False)
    info_list = scene['goal']['info_list']
    info_set = set(info_list)
    assert len(info_list) == len(info_set)
    for obj in scene['objects']:
        obj_info_set = set(obj.get('info', []))
        assert obj_info_set <= info_set


def test_clean_object():
    obj = {
        'id': 'thing1',
        'dimensions': {
            'x': 13,
            'z': 42
        },
        'intphys_option': 'stuff',
        'shows': {
            'stepBegin': 0,
            'bounding_box': 'dummy'
        }
    }
    expected = {
        'id': 'thing1',
        'shows': {
            'stepBegin': 0
        }
    }
    clean_object(obj)
    assert obj == expected
