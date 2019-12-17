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

"""
Create a file 'metadata.json' that describes the tests.

"""
import random
import json
from pathlib import Path
import time

from frameobject import FrameObject
from maskinfo import MaskInfo
from occ_view import OccluderViewer

data_dir_base = "/mnt/ssd/cdorman/data/mcs/intphys/test/"


class TestMetadataCreator:

    def __init__(self):
        pass

    def process(self):
        data_json = {}
        metadata = "metadata.json"
        with open(metadata, 'w') as outfile:
            for block in range(1, 4):
                block_json = {}
                for test in range(1, 1081):
                    start_time = time.time()
                    test_json = self.get_test_json(block, test)
                    end_time = time.time()
                    diff = str(end_time - start_time)
                    test_string = str(test).zfill(4)
                    block_json[test_string] = test_json

                    print("{} {} {}   seconds: {}".format(block, test, test_json, diff))
                block_string = "O" + str(block)
                data_json[block_string] = block_json

            json.dump(data_json, outfile, indent=4)

    def get_test_json(self, block_num, test_num):
        (num_occluders, num_objects, static_scene) = self.get_max_count_objects(block_num, test_num)
        if static_scene:
            complexity = "static"
        else:
            complexity = "dynamic"

        test_json = {"num_objects": num_objects,
                     "complexity": complexity,
                     "occluder": num_occluders}
        return test_json

    def get_max_count_objects(self, block_num, test_num):
        data_dir = data_dir_base + "/O" + str(block_num) + "/"
        max_count = -1

        # Number of occluders is determined for frame 50
        scene_num = 1
        frame_num = 50
        mask = MaskInfo(Path(data_dir + str(test_num).zfill(4) + "/" + str(scene_num)), frame_num)
        if block_num == 3:
            mask.clean_up_O3()
        else:
            mask.clean_up_occluders()
        num_occluders = mask.get_num_occluders()

        num_static_scene = 0
        for scene_num in range(1, 5):
            masks_list = []
            for frame_num in range(1, 101):

                mask = MaskInfo(Path(data_dir + str(test_num).zfill(4) + "/" + str(scene_num)), frame_num)
                masks_list.append(mask)
                count = mask.get_num_obj()
                max_count = count if count > max_count else max_count
                # print("num obj: {}  occluders: {}".format(count, current_occluders))

            # see if the objects in the mask have same min/max x/y over all of them, in which case it is static
            if self.is_scene_static(masks_list):
                num_static_scene += 1

        # ground and sky are always there
        num_obj = max_count - num_occluders - 2
        if num_obj < 1:
            print("Problem with {} {}".format(block_num, test_num))

        static_scene = False
        if num_static_scene == 2:
            static_scene = True

        return (num_occluders, num_obj, static_scene)

    def is_scene_static(self, masks_list):
        """ Go through all the masks and see if they are the same;  if any are different, then not static"""
        # print("length of masks:  {}".format(len(masks_list)))
        for frame_num in range(2, 100):
            same_obj = MaskInfo.are_masks_same(masks_list[1], masks_list[frame_num])
            if not same_obj:
                return False
        return True

    def count_objects(self):
        block_num = 1
        test_num = 1
        scene_num = 2
        frame_num = 33
        data_dir = data_dir_base + "/O" + str(block_num) + "/"
        mask = MaskInfo(Path(data_dir + str(test_num).zfill(4) + "/" + str(scene_num)), frame_num)

        # should be 2, ground and sky
        print("Num objects: {}".format(mask.get_num_orig_objects()))

        # should be 4
        frame_num = 53
        mask = MaskInfo(Path(data_dir + str(test_num).zfill(4) + "/" + str(scene_num)), frame_num)
        print("Num objects: {}".format(mask.get_num_orig_objects()))

        block_num = 3
        test_num = 69
        scene_num = 1
        frame_num = 95
        data_dir = data_dir_base + "/O" + str(block_num) + "/"
        # should be 5
        mask = MaskInfo(Path(data_dir + str(test_num).zfill(4) + "/" + str(scene_num)), frame_num)
        print("Num objects: {}".format(mask.get_num_orig_objects()))

    def compare_masks(self):
        block_num = 1
        test_num = 36
        scene_num = 2
        frame_num = 33
        data_dir = data_dir_base + "/O" + str(block_num) + "/"

        mask1 = MaskInfo(Path(data_dir + str(test_num).zfill(4) + "/" + str(scene_num)), frame_num)
        frame_num = 92
        mask2 = MaskInfo(Path(data_dir + str(test_num).zfill(4) + "/" + str(scene_num)), frame_num)
        result = MaskInfo.are_masks_same(mask1, mask2)
        print(" Same:  {}".format(result))


if __name__ == "__main__":
    random.seed(2834523)
    handler = TestMetadataCreator()
    # handler.count_objects()
    # handler.compare_masks()
    handler.process()
