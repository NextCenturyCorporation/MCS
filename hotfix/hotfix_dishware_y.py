import glob
import json
import sys

PLATES_Y_HOTFIX_ID = 'dishware_y_hotfix'
PLATES_Y_POSITION_INCREASE = 0.005

if len(sys.argv) < 2:
    print('Usage: python hotfix_dishware_y.py <mode>')
    print('<mode> is either "check" or "fix"')
    sys.exit()

mode = sys.argv[1]

json_file_list = glob.glob('./*.json')

dish_count_checked = 0
dish_count_fixed = 0
dish_count_ignored = 0

for json_file_name in json_file_list:
    dish_count_scene = 0
    json_data = None
    with open(json_file_name, 'r', encoding='utf-8-sig') as json_file:
        try:
            json_data = json.load(json_file)
        except ValueError as e:
            print('JSON load error on file ' + json_file_name)
            print(e)
    if json_data:
        if 'objects' in json_data:
            for obj in json_data['objects']:
                if obj['type'].startswith('plate') or obj['type'].startswith('cup') or obj['type'].startswith('bowl'):
                    dish_count_scene += 1
                    if mode == 'fix':
                        if not 'hotfix_list' in obj:
                            obj['hotfix_list'] = []
                        if not PLATES_Y_HOTFIX_ID in obj['hotfix_list']:
                            if 'shows' in obj:
                                for show in obj['shows']:
                                    if 'position' in show and 'y' in show['position']:
                                        show['position']['y'] += PLATES_Y_POSITION_INCREASE
                            obj['hotfix_list'].append(PLATES_Y_HOTFIX_ID)
                            dish_count_fixed += 1
                        else:
                            dish_count_ignored += 1
        else:
            print('No objects property in file ' + json_file_name)
        if dish_count_scene > 0:
            dish_count_checked += dish_count_scene
            if mode == 'fix':
                with open(json_file_name, 'w', encoding='utf-8-sig') as json_file:
                    json.dump(json_data, json_file, indent=2)

if mode == 'check':
    print('Found ' + str(dish_count_checked) + ' dishware in ' + str(len(json_file_list)) + ' files')

if mode == 'fix':
    print('Fixed ' + str(dish_count_fixed) + ' dishware in ' + str(len(json_file_list)) + ' files')
    if dish_count_ignored > 0:
        print('Ignored ' + str(dish_count_ignored) + ' dishware because they were fixed previously')
