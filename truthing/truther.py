#
#  Determine the ground truth for evaluation
#
# for each test, there are 6 possible outcomes:
#
#   0011
#   0101
#   0110
#   1001
#   1010
#   1100
#
# Use

import json
from PIL import Image, ImageDraw
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.widgets import Slider
import sys

red = (255, 1, 1)
green = (1, 255, 1)
white = (255, 255, 255)


class TruthingViewer:

    def __init__(self):
        self.test_num = 1
        self.dataDir = Path("/mnt/ssd/cdorman/data/mcs/intphys/test/O2")
        self.masks = []
        self.imageMap = {}

    def set_test_num(self, test_num):
        self.test_num = test_num
        self.test_num_string = str(self.test_num).zfill(4)

    # def process_mask(self, mask_path, frame_num):
    #     self.masks.clear()
    #     for scene in range(4):
    #         self.masks.append(MaskInfo(mask_path / str(scene + 1), frame_num))

    def write_out_status_for_scene(self, scene_num):

        # Crate the json object
        status_json = {}
        header = {}
        header["test"] = self.test_num
        # header["scene"] = scene_num
        status_json["header"] = header

        # Make sure there are the same number of occluders in the scene over all frames
        num = -1
        frames = []
        for frame_num in range(1, 101):
            frame_info = {}
            frame_info["frame"] = frame_num
            mask_info = {}

            # mask = MaskInfo(self.dataDir / self.test_num_string / str(scene_num), frame_num)
            # obj = mask.get_obj()
            # if num == -1:
            #     num = len(obj)
            # elif len(obj) != num:
            #     print("Problem in test {} scene {} frame {}. Wrong num ".format(self.test_num, scene_num, frame_num))
            #     print("expected {} but got {}".format(str(num), len(obj)))
            #     return

            occluder_counter = 1
            # this will sort the occluders by the left-most pixel
            listofTuples = sorted(obj.items(), key=lambda x: x[1].minx)
            for elem in listofTuples:
                # print(elem[0], " ::", elem[1])
                occluder_name = "occluder" + str(occluder_counter)
                mask_info[occluder_name] = elem[0]
                occluder_counter = occluder_counter + 1
            frame_info["masks"] = mask_info
            frames.append(frame_info)
        status_json["frames"] = frames

        # This one includes the scene num
        #         status_path = Path(("status/status_" + str(self.test_num) + "_" + str(scene_num) + ".json"))
        status_path = Path(("status/status_" + str(self.test_num).zfill(4) + ".json"))
        with status_path.open("w") as outfile:
            json.dump(status_json, outfile, indent=4)

        print("wrote out data for test {}".format(self.test_num))

    def write_out_status(self):
        self.write_out_status_for_scene(1)
        # for ii in range(0, 4):
        #     self.write_out_status_for_scene(ii + 1)

    def update_keypress(self, event):

        sys.stdout.flush()

        if event.key == 'm':
            self.frame_slider.val = self.frame_slider.val + 1
            self.update_slider(1)
            return
        if event.key == 'n':
            self.frame_slider.val = self.frame_slider.val - 1
            self.update_slider(1)
            return
        if event.key == 'x':
            self.write_out_status()

        if event.key == 'right':
            self.set_test_num(self.test_num + 1)
            self.read_images()
        elif event.key == 'left':
            self.set_test_num(self.test_num - 1)
            self.read_images()
        plt.title(self.test_num_string)

        print("Reading in new test {}".format(self.test_num))
        self.frame_slider.set_val(50)

    def set_up_view(self, test_num):

        self.test_num = test_num
        self.test_num_string = str(test_num).zfill(4)
        self.fig, self.axs = plt.subplots(1, 4)

        for ii in range(0, 4):
            image_name = self.dataDir / self.test_num_string / str(ii + 1) / "scene" / "scene_001.png"
            img_src = mpimg.imread(str(image_name))
            self.axs[ii].imshow(img_src)
            self.axs[ii].axis("off")

        axis_color = 'lightgoldenrodyellow'
        axis_freq = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor=axis_color)
        self.frame_slider = Slider(axis_freq, 'frame', 1, 100, valfmt='%0d    ')
        self.frame_slider.on_changed(self.update_slider)

        self.fig.canvas.mpl_connect('key_press_event', self.update_keypress)

        plt.title(self.test_num_string)
        self.read_images()
        plt.show()

    def update_slider(self, val):
        frame_num = int(self.frame_slider.val)
        for scene in range(0, 4):
            self.axs[scene].imshow(self.imageMap[scene][frame_num])
        self.fig.canvas.draw_idle()

    def read_images(self):
        self.imageMap.clear()
        for scene in range(0, 4):
            frame_map = {}
            for frame_num in range(1, 101):
                frame_num_string = str(frame_num).zfill(3)
                image_name = self.dataDir / self.test_num_string / str(scene + 1) / "scene" / (
                        "scene_" + frame_num_string + ".png")
                img_src = Image.open(image_name)
                frame_map[frame_num] = img_src
            self.imageMap[scene] = frame_map


if __name__ == "__main__":
    dc = TruthingViewer()
    dc.set_up_view(1)
