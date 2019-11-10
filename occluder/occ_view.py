#
#  Training for occluders
#
#

import json
import os
import shutil
from PIL import Image
from pathlib import Path
import random
from statistics import mode
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.widgets import Slider
import sys

class OccluderViewer:

    def __init__(self):
        random.seed(23954)

        self.test_num = 1

        self.dataDir = Path("/mnt/ssd/cdorman/data/mcs/intphys/test/O1")
        # self.outdir = Path("/mnt/ssd/cdorman/data/mcs/intphys/split/")
        # self.make_out_dirs("train")
        # self.make_out_dirs("test")

    def update(self, val):
        frame = int(self.frame_slider.val)
        print(" Freq {}".format(frame))
        frame_num = str(frame).zfill(3)

        for ii in range(0, 4):
            image_name = self.dataDir / self.test_num_string / str(ii + 1) / "scene" / ("scene_" + frame_num + ".png")
            img_src = mpimg.imread(str(image_name))
            self.axs[ii].imshow(img_src)

        self.fig.canvas.draw_idle()

    def press(self, event):
        print('press', event.key)
        sys.stdout.flush()
        print("event.key {}".format(event.key))
        if event.key == 'right':
            self.test_num = self.test_num + 1
        elif event.key == 'left':
            self.test_num = self.test_num - 1
        self.test_num_string = str(self.test_num).zfill(4)
        plt.title(self.test_num_string)
        self.update(1)
        #
        # if event.key == 'x':
        #     print(" got x ")
        #     self.fig.canvas.draw()

    def view(self, test_num):

        matplotlib.use('GTK3Agg')
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
        self.frame_slider.on_changed(self.update)

        self.fig.canvas.mpl_connect('key_press_event', self.press)

        plt.title(self.test_num_string)
        plt.show()

    # def make_out_dirs(self, name):
    #     os.mkdir(self.outdir / name)
    #     for subdir in ["sky", "floor", "walls", "occluder", "Sphere", "Cone", "Cube"]:
    #         os.mkdir(self.outdir / name / subdir)
    #
    # def make_data(self):
    #     # Read all the intphys train directories
    #     self.get_dirs()
    #
    #     # there should be 3750 directories.  Get most of them for train, the rest for test
    #     random.shuffle(self.dirs)
    #     dividing_line = len(self.dirs) * 3 // 4
    #     print("Splitting {} training dirs into : {} {}".format(len(self.dirs), dividing_line,
    #                                                            len(self.dirs) - dividing_line))
    #     traindirs = self.dirs[:dividing_line]
    #     testdirs = self.dirs[dividing_line:]
    #
    #     # for subdir in traindirs:
    #     #     self.get_data_from_dir("train", subdir)
    #     for subdir in testdirs:
    #         self.get_data_from_dir("test", subdir)
    #     # self.get_data_from_dir(self.outdir / ("train"), traindirs[0])
    #
    # def get_data_from_dir(self, dest_dir, in_path):
    #     print("Doing directory {}".format(in_path))
    #     """ Passed a directory name, read the status.json and get images"""
    #     status = self.read_json(in_path)
    #
    #     # Go through status, get all the images
    #     for frame_index in range(0, 100):
    #         frame_num = frame_index + 1
    #         frame_json = status["frames"][frame_index]
    #         # print("masks {}".format(frame_json["masks"]))
    #         mask_json = frame_json["masks"]
    #         for obj_name in mask_json.keys():
    #             mask_color = mask_json[obj_name]
    #             obj_type = "unknown"
    #             if obj_name in ("floor", "walls", "sky"):
    #                 # obj_type = obj_name
    #                 continue
    #             elif obj_name.startswith("occluder"):
    #                 obj_type = "occluder"
    #             else:
    #                 obj_type = frame_json[obj_name]["shape"]
    #             self.get_image_for_object(dest_dir, in_path, frame_num, obj_type, mask_color)
    #
    # def get_image_for_object(self, out_path, in_path, frame_num, obj_type, mask_color):
    #     frame_num_with_leading_zeros = str(frame_num).zfill(3)
    #     mask_filename = in_path / "masks" / ("masks_" + frame_num_with_leading_zeros + ".png")
    #     scene_name = os.path.basename(os.path.normpath(in_path))
    #     out_file_path = self.outdir / out_path / obj_type / (
    #             "mask_" + scene_name + "_" + frame_num_with_leading_zeros + "_" + obj_type + ".png")
    #     # print("filename {} {} {} {} goes to {}".format(frame_num, obj_type, mask_color, str(mask_filename),
    #     #                                                out_file_path))
    #     orig_image = Image.open(mask_filename)
    #     new_image = self.get_part_of_image(orig_image, mask_color)
    #
    #     new_image.save(out_file_path)
    #
    # def get_part_of_image(self, orig, color):
    #     """
    #     Get part of an image, consisting of the parts that are of a particular color
    #     """
    #     orig_pixels = orig.load()
    #
    #     # Determine what parts belong to the mask
    #     minx = 10000
    #     maxx = 0
    #     miny = 10000
    #     maxy = 0
    #     for x in range(orig.size[0]):
    #         for y in range(orig.size[1]):
    #             if orig_pixels[x, y] == color:
    #                 if x < minx:
    #                     minx = x
    #                 if x > maxx:
    #                     maxx = x
    #                 if y < miny:
    #                     miny = y
    #                 if y > maxy:
    #                     maxy = y
    #     DIFF = 3
    #
    #     # Give a little bit of room on either side
    #     minx = minx - DIFF
    #     maxx = maxx + DIFF
    #     miny = miny - DIFF
    #     maxy = maxy + DIFF
    #
    #     # Make sure we did not go off the edge
    #     minx = minx if minx >= 0 else 0
    #     maxx = maxx if maxx < orig.size[0] else orig.size[0] - 1
    #     miny = miny if miny >= 0 else 0
    #     maxy = maxy if maxy < orig.size[1] else orig.size[1] - 1
    #
    #     # Determine what color to make the background.  Add 4 corners pixel color, removing the object color
    #     vals = [orig_pixels[minx, miny], orig_pixels[minx, maxy], orig_pixels[maxx, miny], orig_pixels[maxx, maxy]]
    #     if color in vals:
    #         vals.remove(color)
    #     background_color = max(set(vals), key=vals.count)
    #
    #     # Size of the thing we putting into the image
    #     sizex = maxx - minx + 1
    #     sizey = maxy - miny + 1
    #
    #     # Where it should go:  in the middle, minus half the size
    #     startx = orig.size[0] // 2 - (sizex // 2)
    #     starty = orig.size[1] // 2 - (sizey // 2)
    #
    #     new_img = Image.new(orig.mode, orig.size, background_color)
    #     new_img_pixels = new_img.load()
    #     for x in range(sizex):
    #         for y in range(sizey):
    #             new_img_pixels[startx + x, starty + y] = orig_pixels[minx + x, miny + y]
    #
    #     # print("Range of color: {} {} {} {}".format(minx, maxx, miny, maxy))
    #     return new_img
    #
    # def read_json(self, dirpath):
    #     status_path = dirpath / "status.json"
    #     # print(" Opening {}".format(status_path))
    #     with status_path.open() as file:
    #         status_json = json.load(file)
    #     return status_json
    #
    # def get_dirs(self):
    #     if not os.path.exists(self.dataDir):
    #         print("Dir: {} does not exist. exiting".format(str(self.dataDir)))
    #
    #     self.dirs = [Path(self.dataDir / d) for d in os.listdir(self.dataDir)]
    #     self.dirs.sort()
    #     print("Num dirs: {}".format(len(self.dirs)))


if __name__ == "__main__":
    dc = OccluderViewer()
    dc.view(123)
