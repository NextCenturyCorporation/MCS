import ai2thor.controller
import json
from PIL import Image
import sys

if len(sys.argv) < 3:
    print('Usage: python run_ai2thor.py <mcs_unity_build_file> <mcs_config_json_file>')
    sys.exit()

config = {}

with open(sys.argv[2], encoding='utf-8-sig') as config_file:
    config = json.load(config_file)

controller = ai2thor.controller.Controller(
    quality='Medium',
    fullscreen=False,
    headless=False, # The headless flag did not work for me
    local_executable_path=sys.argv[1],
    width=600,
    height=400,
    scene='MCS',
    # Initialize Properties:
    logs=True,
    renderClassImage=True,
    renderDepthImage=True,
    renderObjectImage=True,
    sceneConfig=config
)

# Initialize is called in the Controller's constructor and its output is saved in last_event
event = controller.last_event
img = Image.fromarray(event.frame)
img.save(fp='frame0.png')
img = Image.fromarray(event.depth_frame / 30)
img = img.convert('L')
img.save(fp='depth0.png')
img = Image.fromarray(event.class_segmentation_frame)
img.save(fp='classes0.png')
img = Image.fromarray(event.instance_segmentation_frame)
img.save(fp='objects0.png')

for i in range(1, 31):
    print('i=' + str(i))
    event = controller.step(dict(action='Pass', renderClassImage=True, renderDepthImage=True, renderObjectImage=True))
    img = Image.fromarray(event.frame)
    img.save(fp='frame' + str(i) + '.png')
    img = Image.fromarray(event.depth_frame / 30)
    img = img.convert('L')
    img.save(fp='depth' + str(i) + '.png')
    img = Image.fromarray(event.class_segmentation_frame)
    img.save(fp='classes' + str(i) + '.png')
    img = Image.fromarray(event.instance_segmentation_frame)
    img.save(fp='objects' + str(i) + '.png')

