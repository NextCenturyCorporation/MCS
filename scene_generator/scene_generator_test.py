from scene_generator import clean_object

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
