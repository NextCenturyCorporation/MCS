import objects
from util import retrieve_full_object_definition_list


def test_all_objects_have_expected_properties():
    for object_definition in retrieve_full_object_definition_list(
        objects.get('ALL')
    ):
        print(f'{object_definition["type"]}')
        assert 'type' in object_definition
        assert 'size' in object_definition
        assert 'shape' in object_definition
        assert 'mass' in object_definition
        assert 'attributes' in object_definition
        assert 'dimensions' in object_definition
        assert 'materialCategory' in object_definition
        assert 'salientMaterials' in object_definition
        if len(object_definition['materialCategory']) == 0:
            assert 'color' in object_definition
        assert 'info' not in object_definition


def test_get():
    list_1 = objects.get('ALL')
    list_2 = objects.get('ALL')
    assert not (list_1 is list_2)
    assert list_1 == list_2
