#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2019 Next Century Corporation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
from PIL import Image

from frameobject import FrameObject


class MaskInfo:
    """
    Mask information for a single mask.  One of 100 in a scene; one scene of 4 in a test
    """

    def __init__(self, path, frame_num):
        """The path must be the path including block and scene.   """
        self.path = path
        self.objects = {}
        self.frame_num = frame_num
        self.get_objects_for_frame(frame_num)

    def get_num_obj(self):
        return len(self.objects)

    def get_obj(self):
        return self.objects

    def get_num_orig_objects(self):
        return self.orig_num_objects

    def print_info(self):
        print("Mask info for path {}, frame {}".format(self.path, self.frame_num))
        for obj in self.objects.values():
            print("\t{}".format(obj))

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
                    obj = FrameObject(color)
                    obj.add_pixel(x, y)
                    self.objects[color] = obj

        self.orig_num_objects = len(self.objects)

    def clean_up_occluders(self):
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
            print("Got to here {}. Not sure what to do with color: {}. assuming not occluder".format(self.frame_num, val))
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

    def clean_up_O3(self):
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
