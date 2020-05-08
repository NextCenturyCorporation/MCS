from scene_generator import generate_scene, clean_object


def find_object(id, obj_list):
    for obj in obj_list:
        if obj['id'] == id:
            return obj
    return None


def test_generate_scene_target_enclosed():
    for _ in range(20):
        scene = generate_scene('test', 'interaction', False)
        metadata = scene['goal']['metadata']
        type_list = scene['goal']['type_list']
        assert len(type_list) == len(set(type_list))
        for target_key in ('target', 'target_1', 'target_2'):
            if target_key in metadata:
                target_md = metadata[target_key]
                target = find_object(target_md['id'], scene['objects'])
                if target.get('locationParent', None) is None:
                    assert 'target_not_enclosed' in type_list
                else:
                    assert 'target_enclosed' in type_list


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
        'shows': [{
            'stepBegin': 0,
            'bounding_box': 'dummy'
        }]
    }
    expected = {
        'id': 'thing1',
        'shows': [{
            'stepBegin': 0
        }]
    }
    clean_object(obj)
    assert obj == expected
