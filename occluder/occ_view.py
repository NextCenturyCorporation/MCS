#
#  Training for occluders
#

import json
from PIL import Image, ImageDraw
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.widgets import Slider
import sys

from maskinfo import MaskInfo

purpose = 'images'  # 'view   # 'status'

# datadir = "/mnt/ssd/cdorman/data/mcs/intphys/test/O1"
datadir = "/mnt/ssd/cdorman/data/mcs/intphys/test/O2"

red = (255, 1, 1)
green = (1, 255, 1)
white = (255, 255, 255)

class OccluderViewer:

    def __init__(self, data_dir):
        self.test_num = 1
        self.dataDir = Path(data_dir)
        self.masks = []

    def set_test_num(self, test_num):
        self.test_num = test_num
        self.test_num_string = str(self.test_num).zfill(4)
        self.process_mask(self.dataDir / self.test_num_string, 50)

    def update_slider(self, val):
        # Change the frame
        frame_num = int(self.frame_slider.val)
        self.process_mask(self.dataDir / self.test_num_string, frame_num)

        # Draw the images
        for scene_num in range(0, 4):
            img_src = self.get_overlaid_image(frame_num, scene_num)
            self.axs[scene_num].imshow(img_src)

        self.fig.canvas.draw_idle()

    def get_num_occluders(self, scene_num):
        self.masks[scene_num].clean_up_occluders()
        return len(self.masks[scene_num].get_obj())

    def get_overlaid_image(self, frame_num, scene_num):
        frame_num_string = str(frame_num).zfill(3)
        image_name = self.dataDir / self.test_num_string / str(scene_num + 1) / "scene" / (
                "scene_" + frame_num_string + ".png")

        img_src = Image.open(image_name)
        draw = ImageDraw.Draw(img_src)
        for obj in self.masks[scene_num].get_obj().values():
            draw_color = white
            if obj.label is 'sky':
                draw_color = red
            elif obj.label is 'ground':
                draw_color = green
            draw.rectangle([(obj.minx, obj.miny), (obj.maxx, obj.maxy)], width=2, outline=draw_color)

        return img_src

    def process_mask(self, mask_path, frame_num):
        self.masks.clear()
        for scene in range(4):
            self.masks.append(MaskInfo(mask_path / str(scene + 1), frame_num))

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

            mask = MaskInfo(self.dataDir / self.test_num_string / str(scene_num), frame_num)
            obj = mask.get_obj()
            if num == -1:
                num = len(obj)
            elif len(obj) != num:
                print("Problem in test {} scene {} frame {}. Wrong num ".format(self.test_num, scene_num, frame_num))
                print("expected {} but got {}".format(str(num), len(obj)))
                return

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
        elif event.key == 'left':
            self.set_test_num(self.test_num - 1)
        plt.title(self.test_num_string)

        print("Reading in new test {}".format(self.test_num))
        self.frame_slider.set_val(50)

    def set_up_view(self, test_num):

        self.set_test_num(test_num)
        self.fig, self.axs = plt.subplots(1, 4)

        for ii in range(0, 4):
            image_name = self.dataDir / self.test_num_string / str(ii + 1) / "scene" / "scene_001.png"
            img_src = mpimg.imread(str(image_name))
            self.axs[ii].imshow(img_src)
            self.axs[ii].axis("off")

        axcolor = 'lightgoldenrodyellow'
        axfreq = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor=axcolor)
        self.frame_slider = Slider(axfreq, 'frame', 1, 100, valfmt='%0d    ')
        self.frame_slider.on_changed(self.update_slider)

        self.fig.canvas.mpl_connect('key_press_event', self.update_keypress)

        plt.title(self.test_num_string)
        plt.show()

    def make_image(self):
        """Write out an image with occluders labeled"""
        img_src = self.get_overlaid_image(50, 0)
        num_occ = len(self.masks[0].get_obj())
        image_filename = "images" + str(num_occ) + "/test_" + self.test_num_string + ".png"
        img_src.save(image_filename)


if __name__ == "__main__":
    dc = OccluderViewer(datadir)

    if purpose == 'images':
        for test in range(1, 1081):
            dc.set_test_num(test)
            dc.make_image()
    elif purpose == 'view':
        dc.set_up_view(1)
    else:
        for test in range(1, 1081):
            dc.set_test_num(test)
            dc.write_out_status()
