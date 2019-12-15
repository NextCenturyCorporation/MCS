#
#  Training for occluders
#
# This one is for O3, which is a little different from O1 and O2.  The logic for O1/O2 didn't quite
# work for O3.

import json
import time

from PIL import Image, ImageDraw
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.widgets import Slider
import sys

debug = True
# debug = False
datadir = "/mnt/ssd/cdorman/data/mcs/intphys/test/O3"


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
        self.midx = 0
        self.midy = 0
        self.dy = 0

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

    def get_mid(self):
        return [(self.maxx + self.minx) / 2., (self.maxy + self.miny) / 2.]


class MaskInfo:
    """
    Mask information for a single mask.  One of 100 in a scene; one scene of 4 in a test
    """

    def __init__(self, path):
        self.path = path
        self.objects = {}
        self.frame_num = None

    def get_num_obj(self):
        return len(self.objects)

    def get_obj(self):
        return self.objects

    def get_objects_for_frame(self, frame_num):
        self.frame_num = frame_num
        frame_num_with_leading_zeros = str(frame_num).zfill(3)
        mask_filename = self.path / "masks" / ("masks_" + frame_num_with_leading_zeros + ".png")

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
        return self.objects

    def print_info(self):
        print("Mask info for path {}, frame {}".format(self.in_path, self.frame_num))
        for obj in self.objects.values():
            print("\t{}".format(obj))

    def clean_up_O3_50(self):
        to_be_removed = []
        for key, val in self.objects.items():

            if val.pixel_count < 1500:
                to_be_removed.append(key)
                continue

            if val.pixel_count > 20000:
                to_be_removed.append(key)
                continue

        for x in to_be_removed:
            self.objects.pop(x)

        return self.objects

class OccluderViewer:

    def __init__(self):
        self.test_num = 1
        self.dataDir = Path(datadir)
        self.masks = []

    def set_test_num(self, test_num):
        self.test_num = test_num
        self.test_num_string = str(self.test_num).zfill(4)

    def process_mask(self, mask_path, frame_num):
        self.masks.clear()
        for scene in range(4):
            mask = MaskInfo(mask_path / str(scene + 1))
            self.masks.append(mask.get_objects_for_frame(frame_num))

    def update_slider(self, val):
        # Change the frame
        frame_num = int(self.frame_slider.val)
        # self.process_mask(self.dataDir / self.test_num_string, frame_num)

        # match occluders
        mask = MaskInfo(self.dataDir / self.test_num_string / str(1))
        all_obj = mask.get_objects_for_frame(frame_num)
        new_obj = self.get_matched_obj(self.obj, all_obj)

        # Draw the images
        frame_num_string = str(frame_num).zfill(3)
        for ii in range(0, 4):
            image_name = self.dataDir / self.test_num_string / str(ii + 1) / "scene" / (
                    "scene_" + frame_num_string + ".png")

            img_src = Image.open(image_name)
            draw = ImageDraw.Draw(img_src)
            for obj in new_obj.values():
                draw_color = white
                draw.rectangle([(obj.minx, obj.miny), (obj.maxx, obj.maxy)], width=2, outline=draw_color)

            self.axs[ii].imshow(img_src)

        self.obj = new_obj

        self.fig.canvas.draw_idle()

    def write_to_occ_or_not(self):
        # which scene and frame
        scene_num = 1
        frame_num = 50

        # The image
        frame_num_string = str(frame_num).zfill(3)
        image_name = self.dataDir / self.test_num_string / str(1) / "scene" / (
                "scene_" + frame_num_string + ".png")
        img_src = Image.open(image_name)

        mask = MaskInfo(self.dataDir / self.test_num_string / str(scene_num))
        mask.get_objects_for_frame(frame_num)
        obj = mask.clean_up_O3_50()
        if len(obj) == 0:
            img_src.save("./has_no_occluder/test_" + self.test_num_string + ".png")
            print("Test {} has no occ".format(self.test_num_string))
        else:
            img_src.save("./has_occluder/test_" + str(len(obj)) + "_" + self.test_num_string + ".png")
            print("Test {} has occ {}".format(self.test_num_string, len(obj)))

    # def get_matched_obj_old(self, old, new):
    #     ret_obj = {}
    #     for old_key, old_val in old.items():
    #         old_mid = old_val.get_mid()
    #         old_size = old_val.pixel_count
    #
    #         # Get predicted y
    #         print("current loc: {} {}".format(old_mid[0], old_mid[1]))
    #         pred_y = old_mid[1] + old_val.dy
    #         print("Predicted loc: {} {}".format(old_mid[0], pred_y))
    #
    #         # find closest
    #         smallest_dist = 1000000
    #         closest_object = None
    #         for new_key, new_val in new.items():
    #             new_mid = new_val.get_mid()
    #             dx = old_mid[0] - new_mid[0]
    #             dy = pred_y - new_mid[1]
    #             dist = math.sqrt(dx * dx + dy * dy)
    #
    #             # make sure not too different in size
    #             new_size = new_val.pixel_count
    #             diff_size = abs(old_size - new_size) / old_size
    #
    #             # print(
    #             #     "   Current item loc: {} {} dist: {} diff_size {}".format(new_mid[0], new_mid[1], dist, diff_size))
    #
    #             if dist < smallest_dist:  # and diff_size < 0.5:
    #                 smallest_dist = dist
    #                 closest_object = new_key
    #
    #         ret_obj[closest_object] = new[closest_object]
    #         ret_mid = ret_obj[closest_object].get_mid()
    #         # print("   New mid {} {}".format(ret_mid[0], ret_mid[1]))
    #         dy = ret_mid[1] - old_mid[1]
    #         # print("   dy = {}".format(dy))
    #         ret_obj[closest_object].dy = dy
    #
    #     return ret_obj

    def get_matched_obj(self, old, new):
        ret_obj = {}
        for old_key, old_val in old.items():
            old_mid = old_val.get_mid()
            # print("   Old mid {} {}".format(old_mid[0], old_mid[1]))

            # find closest
            smallest_dist = 1000000
            closest_object = None
            for new_key, new_val in new.items():
                dx_left = old_val.minx - new_val.minx
                dx_right = old_val.maxx - new_val.maxx
                dy_left = old_val.miny - new_val.miny
                dy_right = old_val.maxy - new_val.maxy

                dist = dx_left * dx_left + dx_right * dx_right + dy_left * dy_left + dy_right * dy_right

                # print("  dist {} ".format(dist))

                if dist < smallest_dist:  # and diff_size < 0.5:
                    smallest_dist = dist
                    closest_object = new_key

            ret_obj[closest_object] = new[closest_object]
            ret_mid = ret_obj[closest_object].get_mid()
            # print("   New mid {} {}".format(ret_mid[0], ret_mid[1]))

        return ret_obj

    def write_out_status_for_scene(self, scene_num):
        # Create the json object
        status_json = {}
        header = {}
        header["test"] = self.test_num
        # header["scene"] = scene_num
        status_json["header"] = header

        # Get number of occluders in frame 50
        frame_num = 50
        mask = MaskInfo(self.dataDir / self.test_num_string / str(scene_num))
        mask.get_objects_for_frame(frame_num)
        obj_50 = mask.clean_up_O3_50()

        # If no occluders in frame 50, write out and return
        if len(obj_50) == 0:
            frames = []
            for frame_num in range(1, 101):
                frame_info = {}
                frame_info["frame"] = frame_num
                mask_info = {}
                frame_info["masks"] = mask_info
                frames.append(frame_info)
            status_json["frames"] = frames
            status_path = Path(("status/status_" + str(self.test_num).zfill(4) + ".json"))
            with status_path.open("w") as outfile:
                json.dump(status_json, outfile, indent=4)
            print("Wrote no occluders for {}".format(self.test_num_string))
            return

        # Dictionary to hold the frame information, since not sequential
        frame_dict = {}

        # Get the info for frame 50
        print("found {} occluders in test {}".format(len(obj_50), self.test_num_string))

        frame_info = {}
        frame_info["frame"] = frame_num
        mask_info = {}
        listofTuples = sorted(obj_50.items(), key=lambda x: x[1].minx)
        occluder_counter = 1
        for elem in listofTuples:
            occluder_name = "occluder" + str(occluder_counter)
            mask_info[occluder_name] = elem[0]
            occluder_counter = occluder_counter + 1
        frame_info["masks"] = mask_info
        frame_dict[50] = frame_info

        # go forward in time
        last_obj = obj_50
        for frame_num in range(51, 101):
            frame_info = {}
            frame_info["frame"] = frame_num
            mask_info = {}

            mask = MaskInfo(self.dataDir / self.test_num_string / str(scene_num))
            current_obj = mask.get_objects_for_frame(frame_num)
            match_obj = self.get_matched_obj(last_obj, current_obj)

            if len(match_obj) != len(last_obj):
                print("Problem in test {} scene {} frame {}. Wrong num ".format(self.test_num, scene_num, frame_num))
                print("expected {} but got {}".format(str(len(last_obj)), str(len(match_obj))))
                return

            occluder_counter = 1
            # this will sort the occluders by the left-most pixel
            listofTuples = sorted(match_obj.items(), key=lambda x: x[1].minx)
            for elem in listofTuples:
                # print(elem[0], " ::", elem[1])
                occluder_name = "occluder" + str(occluder_counter)
                mask_info[occluder_name] = elem[0]
                occluder_counter = occluder_counter + 1
            frame_info["masks"] = mask_info
            frame_dict[frame_num] = frame_info

            last_obj = match_obj

        # go backward in time
        last_obj = obj_50
        for frame_num in range(49, 0, -1):
            frame_info = {}
            frame_info["frame"] = frame_num
            mask_info = {}

            mask = MaskInfo(self.dataDir / self.test_num_string / str(scene_num))
            current_obj = mask.get_objects_for_frame(frame_num)
            match_obj = self.get_matched_obj(last_obj, current_obj)

            if len(match_obj) != len(last_obj):
                print("Problem in test {} scene {} frame {}. Wrong num ".format(self.test_num, scene_num, frame_num))
                print("expected {} but got {}".format(str(len(last_obj)), str(len(match_obj))))
                return

            occluder_counter = 1
            # this will sort the occluders by the left-most pixel
            listofTuples = sorted(match_obj.items(), key=lambda x: x[1].minx)
            for elem in listofTuples:
                # print(elem[0], " ::", elem[1])
                occluder_name = "occluder" + str(occluder_counter)
                mask_info[occluder_name] = elem[0]
                occluder_counter = occluder_counter + 1
            frame_info["masks"] = mask_info
            frame_dict[frame_num] = frame_info

            last_obj = match_obj

        # convert from frame_dict to frames
        frames = []
        for frame_num in range(1, 101):
            frames.append(frame_dict[frame_num])
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

    def set_obj_at_50(self):
        # Get number of occluders in frame 50
        frame_num = 50
        scene_num = 1
        mask = MaskInfo(self.dataDir / self.test_num_string / str(scene_num))
        mask.get_objects_for_frame(frame_num)
        self.obj = mask.clean_up_O3_50()

    def update_keypress(self, event):

        sys.stdout.flush()

        if event.key == 'q':
            exit(0)

        if event.key == 'm':
            self.frame_slider.set_val(self.frame_slider.val + 1)
            return
        if event.key == 'n':
            self.frame_slider.set_val(self.frame_slider.val - 1)
            return

        if event.key == 'x':
            self.write_out_status()

        if event.key == 'right':
            self.set_test_num(self.test_num + 1)
        elif event.key == 'left':
            self.set_test_num(self.test_num - 1)
        plt.title(self.test_num_string)
        self.set_obj_at_50()

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
        self.set_obj_at_50()

        plt.title(self.test_num_string)
        plt.show()

    def divide(self):
        for test in range(1, 1081):
            dc.set_test_num(test)
            dc.write_to_occ_or_not()


if __name__ == "__main__":
    dc = OccluderViewer()

    # splits the data into 2 directories
    # dc.divide()

    # dc.set_test_num(3)
    # dc.write_out_status()

    if debug:
        dc.set_up_view(64)
    else:
        for test in range(1, 1081):
            t = time.time()
            dc.set_test_num(test)
            dc.write_out_status()
            print("time: {}".format( str(time.time()-t)))