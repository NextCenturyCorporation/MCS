from quartets import ObjectPermanenceQuartet


def test_ObjectPermanenceQuartet_get_scene():
    template = {'wallMaterial': 'dummy'}
    quartet = ObjectPermanenceQuartet(template, False)
    for q in range(1, 5):
        scene = quartet.get_scene(q)
        # at least one object and occluder (itself 2 objects)
        assert len(scene['objects']) >= 3
