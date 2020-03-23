import pytest
from scene_generator import *



def test_collision():
    a={'x': 1, 'y': 0, 'z': 1}
    b={'x': 1, 'y': 0, 'z': -1}
    c={'x': -1, 'y': 0, 'z': -1}
    d={'x': -1, 'y': 0, 'z': 1}
    
    rect = [a,b,c,d]
    p0 = {'x': 0, 'y': 0, 'z': 0}
    p1 = {'x': 11, 'y': 0, 'z': 11}

    assert collision(rect, p0) == True
    assert collision(rect, p1) == False