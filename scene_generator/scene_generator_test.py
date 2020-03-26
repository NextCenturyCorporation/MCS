import pytest
from scene_generator import *

from separating_axis_theorem import *




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
    
    
def test_rect_intersection():
    A=[ {'x': 0, 'y':0, 'z':0},{'x': 1, 'y':0, 'z':0},{'x': 1, 'y':0, 'z':1},{'x': 0, 'y':0, 'z':1}]
    B=[{'x': .25, 'y':0, 'z':.25},{'x': .75, 'y':0, 'z':.25},{'x': .75, 'y':0, 'z':.75},{'x': .25, 'y':0, 'z':.75}]
    C=[{'x': .8, 'y':0, 'z':1.2}, {'x': 1.1, 'y':0, 'z':1.8},{'x': 2, 'y':0, 'z':1.5},{'x': 1.1, 'y':0, 'z':.3}]
    D=[{'x': 1, 'y':0, 'z':0},{'x': 2, 'y':0, 'z':1.5},{'x': 3, 'y':0, 'z':0},{'x': 2, 'y':0, 'z':-1.5}]
    #A intersects B,C,D. B ints A , C ints A & D, D ints A C
    #Testing transitivity as well
    assert sat_entry(A,B) == True
    assert sat_entry(A,D) == True
    assert sat_entry(C,B) == False
    assert sat_entry(D,C) == True
    assert sat_entry(B,C) == False
    assert sat_entry(A,C) == True
    assert sat_entry(C,A) == True
    
    

    