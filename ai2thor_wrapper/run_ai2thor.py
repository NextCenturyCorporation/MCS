import ai2thor.controller
from PIL import Image
import sys

if len(sys.argv) < 2:
    print('Usage: python run_ai2thor.py <path_to_mcs_unity_build_file>')
    sys.exit()

controller = ai2thor.controller.Controller(
    quality='Medium',
    fullscreen=False,
    headless=False, # The headless flag did not work for me
    local_executable_path=sys.argv[1],
    width=600,
    height=400,
    scene="MCS"
)

event = controller.step(dict(action='Initialize', renderClassImage=True, renderDepthImage=True, renderObjectImage=True))
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

