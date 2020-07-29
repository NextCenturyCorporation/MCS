from scene_generator import generate_scene, clean_object


def find_object(id, obj_list):
    for obj in obj_list:
        if obj['id'] == id:
            return obj
    return None


def test_clean_object():
    obj = {
        'id': 'thing1',
        'info': ['a', 'b', 'c', 'd'],
        'goal_string': 'abcd',
        'materialCategory': ['wood'],
        'dimensions': { 'x': 13, 'z': 42 },
        'offset': { 'x': 13, 'z': 42 },
        'closedDimensions': { 'x': 13, 'z': 42 },
        'closedOffset': { 'x': 13, 'z': 42 },
        'enclosedAreas': [{}],
        'openAreas': [{}],
        'intphysOption': 'stuff',
        'novelColor': True,
        'novelCombination': False,
        'novelShape': True,
        'color': ['black', 'white'],
        'shape': 'shape',
        'size': 'medium',
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

