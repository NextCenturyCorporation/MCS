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

# debug = True
debug = False
red = (255, 1, 1)
green = (1, 255, 1)
white = (255, 255, 255)


class Obj:

    def __init__(self, color):
        self.color = color;
        self.pixel_count = 0
        self.minx = 10000
        self.maxx = 0
        self.miny = 10000
        self.maxy = 0
        self.label = None

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
            self.pixel_count) + " AR: " + str(self.aspect_ratio) + ")"


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

        x_spacing = [1, 20, 30, 40, 100, 120, 150, 180, 240, 277]
        y_sky_spacing = [1, 20, 50]
        sky_color = []
        # Try to find the sky
        for x in x_spacing:
            for y in y_sky_spacing:
                sky_color.append(pixels[x, y])
        sky_color = max(sky_color, key=sky_color.count)
        self.objects[sky_color].label = 'sky'

        y_ground_spacing = [163, 183]
        ground_color = []
        for x in x_spacing:
            for y in y_ground_spacing:
                ground_color.append(pixels[x, y])
        ground_color = max(ground_color, key=ground_color.count)
        self.objects[ground_color].label = 'ground'

        if debug:
            self.clean_up_objects(frame_num)
            print("Mask info for path {}, frame {}".format(in_path, frame_num))
            for obj in self.objects.values():
                print("\t{}".format(obj))
        else:
            self.clean_up_objects(frame_num)

    def clean_up_objects(self, frame_num):
        to_be_removed = []
        sky_found = False
        ground_found = False

        for key, val in self.objects.items():

            # sky is usually the top region
            if val.minx == 0 and val.miny == 0 and val.maxx == 287 and val.maxy > 100:
                sky_found = True
                to_be_removed.append(key)
                continue

            # ground might be entire bottom
            if val.minx == 0 and val.miny == 152 and val.maxx == 287 and val.maxy == 287:
                ground_found = True
                to_be_removed.append(key)
                continue

            # Ground might start at bottom
            if val.minx == 0 and val.maxx == 287 and val.miny == 152 and val.maxy > 200:
                ground_found = True
                to_be_removed.append(key)
                continue

            # too small, must be non-occluder object
            if val.pixel_count < 501:
                to_be_removed.append(key)
                continue

            # aspect ratio wrong for medium sized
            if 500 < val.pixel_count < 1680:
                if 0.5 < val.aspect_ratio < 1.8:
                    to_be_removed.append(key)
                    continue

            # if big and not ground or sky, must be occluder
            if sky_found and ground_found and val.pixel_count > 10000:
                continue

            # If wide and flat, then must be occluder
            if val.aspect_ratio > 3:
                continue

            # If not too big, then occluder
            if val.pixel_count > 1400:
                continue

            # bad ground or sky?
            print("Got to here {} {}".format(frame_num, val))
            to_be_removed.append(key)

        for x in to_be_removed:
            self.objects.pop(x)

        # If there are two left, and one is much bigger, then it is the ground
        keys = list(self.objects.keys())
        if len(keys) == 2:
            size_1 = self.objects.get(keys[0]).pixel_count
            size_2 = self.objects.get(keys[1]).pixel_count
            if size_1 > size_2 and size_1 > 20000:
                self.objects.pop(keys[0])
            elif size_2 > size_1 and size_2 > 20000:
                self.objects.pop(keys[1])


class OccluderViewer:

    def __init__(self):
        self.test_num = 1
        self.dataDir = Path("/mnt/ssd/cdorman/data/mcs/intphys/test/O1")
        self.masks = []

    def set_test_num(self, test_num):
        self.test_num = test_num
        self.test_num_string = str(self.test_num).zfill(4)

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
                draw_color = white
                if obj.label is 'sky':
                    draw_color = red
                elif obj.label is 'ground':
                    draw_color = green
                draw.rectangle([(obj.minx, obj.miny), (obj.maxx, obj.maxy)], width=2, outline=draw_color)

            self.axs[ii].imshow(img_src)

        self.fig.canvas.draw_idle()

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

    if debug:
        dc.set_up_view(984)
    else:
        for test in range(1, 1081):
            dc.set_test_num(test)
            dc.write_out_status()
