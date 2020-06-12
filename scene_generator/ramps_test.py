from ramps import create_ramp


def test_create_ramp():
    material_string = 'mymaterial'
    ramp_type, x_term, ramp = create_ramp(material_string, 0.42, False)
    assert 1 <= len(ramp) <= 3
    for obj in ramp:
        assert material_string in obj['materials']
