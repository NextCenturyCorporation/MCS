import logging
import traceback

from extremitypathfinder.extremitypathfinder import PolygonEnvironment as Environment
from  geometry import ROOM_DIMENSIONS
from _testcapi import traceback_print


MIN_X = ROOM_DIMENSIONS[0][0]
MAX_X = ROOM_DIMENSIONS[0][1]
MIN_Z = ROOM_DIMENSIONS[1][0]
MAX_Z = ROOM_DIMENSIONS[1][1]
# passing the other_rects from my  calculations previously
# This is the source for extremitypathfinder: https://github.com/MrMinimal64/extremitypathfinder
#target_loc will probably contain the target- we'll see
def generatepath(source_loc, target_loc, other_rects):
    '''Boundary has to be CCW, Holes CW'''
    boundary_coordinates = [ (MAX_X, MAX_Z),(MIN_X, MAX_Z),(MIN_X, MIN_Z), (MAX_X,MIN_Z)]
    holes= []
    # This way does make me a bit nervous- as this is coding
    #need to convert to lists of points 
    for object in other_rects:            
        holes.append([(point['x'],point['z']) for point in object])
        
    try:
        environment = Environment()
        environment.store(boundary_coordinates, holes, validate = False)
        environment.prepare()
        path,length = environment.find_shortest_path(source_loc, target_loc)
    except Exception as e:
        traceback.print_exc()
        logObject = {
            'boundary': boundary_coordinates,
            'holes': holes,
            'start': source_loc,
            'target': target_loc
            }
        logging.error(logObject)
    return path
    
                
    


