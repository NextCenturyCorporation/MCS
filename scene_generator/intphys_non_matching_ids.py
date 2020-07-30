import uuid
import json
import io
from collections import OrderedDict
import sys
import os.path
from pathlib import Path


def non_matching_ids():
    found_match = False
    files = []
    user_input = Path(input('Enter Dataset directory: '))
    assert os.path.exists(user_input), "No file at, "+str(user_input)
    file_names = os.listdir(user_input)

    for file in file_names:
        found_match = False
        file_to_open = os.path.join(user_input,file)
        with open(file_to_open, 'r') as file_data:
            input_data = file_data.read()
            scene_data = json.loads(input_data, object_pairs_hook=OrderedDict)

        for object_a in scene_data['objects']:
            num_of_times_object_id_appears = 0
            for object_b in scene_data['objects']:
                if object_a['id'] == object_b['id']:
                    if num_of_times_object_id_appears == 0:
                        num_of_times_object_id_appears += 1
                        continue
                    else:
                        print("Matching object ID '" + object_b['id'] + "' in " + file)
                        object_b['id'] = str(uuid.uuid4())
                        found_match = True

        if found_match:
            new_scene_file = os.path.join(user_input, 'new.' + file)
            files.append(new_scene_file)
            with open(new_scene_file, 'w') as json_file:
                json.dump(scene_data, json_file, indent=2)
        else:
            print("Cannot find matching objects in " + file)

non_matching_ids()
