#
#  Training for occluders
#

import json
import os
import shutil
from PIL import Image, ImageDraw
from pathlib import Path
import random
from statistics import mode
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.widgets import Slider
import sys


class Obj:

    def __init__(self, color):
        self.color = color;
        self.pixel_count = 0
        self.minx = 10000
        self.maxx = 0
        self.miny = 10000
        self.maxy = 0

    def add_pixel(self, x, y):
        self.pixel_count = self.pixel_count + 1
        if x < self.minx:
            self.minx = x
        if x > self.maxx:
            self.maxx = x
        if y < self.miny:
            self.miny = y
        if y > self.maxy:
            self.maxy = y
        diffy = abs(self.maxy - self.miny)
        if diffy > 0:
            self.aspect_ratio = abs(self.maxx - self.minx) / diffy
        else:
            self.aspect_ratio = 1

    def __str__(self):
        return "(" + str(self.color) + " [ " + str(self.minx) + ", " + str(self.maxx) + ", " + str(
            self.miny) + ", " + str(self.maxy) + " ] " + " ct: " + str(
            self.pixel_count) + " AR: " + str(self.aspect_ratio) \
               + ")"


class MaskInfo:
    """
    Mask information for a single mask.  One of 100 in a scene; one scene of 4 in a test
    """

    def __init__(self, path, frame_num):
        self.path = path
        self.objects = {}
        self.get_objects_for_frame(self.path, frame_num)

    def get_num_obj(self):
        return len(self.objects)

    def get_obj(self):
        return self.objects

    def get_objects_for_frame(self, in_path, frame_num):
        frame_num_with_leading_zeros = str(frame_num).zfill(3)
        mask_filename = in_path / "masks" / ("masks_" + frame_num_with_leading_zeros + ".png")

        mask_image = Image.open(mask_filename)
        pixels = mask_image.load()

        # Determine what parts belong to the mask
        for x in range(mask_image.size[0]):
            for y in range(mask_image.size[1]):
                color = pixels[x, y]
                if color in self.objects:
                    self.objects.get(color).add_pixel(x, y)
                else:
                    obj = Obj(color)
                    obj.add_pixel(x, y)
                    self.objects[color] = obj

        self.clean_up_objects()

        print("Mask info for path {}, frame {}".format(in_path, frame_num))
        for obj in self.objects.values():
            print("\t{}".format(obj))

    def clean_up_objects(self):
        to_be_removed = []
        for key, val in self.objects.items():
            # too big, must be ground or sky
            if val.pixel_count > 12000:
                to_be_removed.append(key)

            # too small, must be non-occluder object
            elif val.pixel_count < 800:
                to_be_removed.append(key)

            # aspect ratio wrong
            elif 800 < val.pixel_count < 1400:
                if 0.8 < val.aspect_ratio < 1.5:
                    to_be_removed.append(key)

        for x in to_be_removed:
            self.objects.pop(x)


class OccluderViewer:

    def __init__(self):
        self.test_num = 1
        self.dataDir = Path("/mnt/ssd/cdorman/data/mcs/intphys/test/O1")
        self.masks = []

    def process_mask(self, mask_path, frame_num):
        self.masks.clear()
        for scene in range(4):
            self.masks.append(MaskInfo(mask_path / str(scene + 1), frame_num))

    def update_slider(self, val):
        # Change the frame
        frame_num = int(self.frame_slider.val)
        self.process_mask(self.dataDir / self.test_num_string, frame_num)

        # Draw the images
        frame_num_string = str(frame_num).zfill(3)
        for ii in range(0, 4):
            image_name = self.dataDir / self.test_num_string / str(ii + 1) / "scene" / (
                    "scene_" + frame_num_string + ".png")

            img_src = Image.open(image_name)
            # img_src = mpimg.imread(str(image_name))
            draw = ImageDraw.Draw(img_src)
            for obj in self.masks[ii].get_obj().values():
                draw.rectangle([(obj.minx, obj.miny), (obj.maxx, obj.maxy)], width=2)

            self.axs[ii].imshow(img_src)

        self.fig.canvas.draw_idle()

    def write_out_status_for_scene(self, scene_num):

        status_json = {}
        frames = []
        header = {}
        statu
        # Make sure there are the same number of occluders in the scene over all frames
        num = -1
        for frame_num in range(1,101):
            mask= MaskInfo(self.dataDir / self.test_num_string / str(scene_num), frame_num)
            obj = mask.get_obj
            if num == -1:
                num = len(obj)
            elif len(obj) != num:
                print("Problem in test {} scene {} frame {}. Wrong num ".format(self.test_num, scene_num, frame_num))



        status_path = self.dataDir / self.test_num_string / str(scene_num) / "status.json"
        with status_path.open("w") as outfile:



    def write_out_status(self):
        for ii in range(0, 4):
            self.write_out_status_for_scene(ii+1)

    def update_keypress(self, event):

        sys.stdout.flush()

        if event.key == 'x':
            self.write_out_status()

        if event.key == 'right':
            self.test_num = self.test_num + 1
        elif event.key == 'left':
            self.test_num = self.test_num - 1
        self.test_num_string = str(self.test_num).zfill(4)
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

        axcolor = 'lightgoldenrodyellow'
        axfreq = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor=axcolor)
        self.frame_slider = Slider(axfreq, 'frame', 1, 100, valfmt='%0d    ')
        self.frame_slider.on_changed(self.update_slider)

        self.fig.canvas.mpl_connect('key_press_event', self.update_keypress)

        plt.title(self.test_num_string)
        plt.show()


if __name__ == "__main__":
    dc = OccluderViewer()
    dc.set_up_view(1000)
