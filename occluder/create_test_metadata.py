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
                    print("{} {} {}   seconds: {}".format(block, test, test_json, diff))
                    test_string = str(test).zfill(4)
                    block_json[test_string] = test_json
                    print("")

                block_string = "O" + str(block)
                data_json[block_string] = block_json

            json.dump(data_json, outfile, indent=4)

    def get_test_json(self, block_num, test_num):
        (num_occluders, num_objects) = self.get_max_count_objects(block_num, test_num)
        complexity = self.get_complexity(block_num, test_num)

        test_json = {"num_objects": num_objects,
                     "complexity": complexity,
                     "occluder": num_occluders}
        return test_json

    # def get_num_occluders(self, block_num, test_num):
    #     data_dir = data_dir_base + "/O" + str(block_num)
    #     dc = OccluderViewer(data_dir)
    #     dc.set_test_num(test_num)
    #     num_occluders = dc.get_num_occluders(scene_num=1)
    #     return num_occluders

    def get_max_count_objects(self, block_num, test_num):
        data_dir = data_dir_base + "/O" + str(block_num) + "/"
        max_count = -1
        num_occluders = -1
        for scene_num in range(1, 5):
            for frame_num in range(1, 101):
                mask = MaskInfo(Path(data_dir + str(test_num).zfill(4) + "/" + str(scene_num)), frame_num)
                count = mask.get_num_orig_objects()
                max_count = count if count > max_count else max_count

                mask.clean_up_occluders()
                current_occluders = mask.get_num_obj()
                if num_occluders == -1:
                    num_occluders = current_occluders
                elif not num_occluders == current_occluders:
                    print("Number of occluders changed!!.  Was: {}.  In frame {} it is {}".format(num_occluders,
                                                                                                  frame_num,
                                                                                                  current_occluders))

                # print(
                #     "block {} test {} scene {} frame {} occluders {} objects {}".format(block_num, test_num, scene_num,
                #                                                                         frame_num, num_occluders,
                #                                                                         count))
        num_obj = max_count - num_occluders - 2
        if num_obj < 1:
            print("Problem with {} {}".format(block_num, test_num))
        return (num_occluders, num_obj)

    def get_complexity(self, block_num, test_num):
        return random.sample({"static", "dynamic 1", "dynamic 2"}, 1)[0]

    def count_objects(self):
        block_num = 1
        test_num = 1
        scene_num = 1
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


if __name__ == "__main__":
    random.seed(2834523)
    handler = TestMetadataCreator()
    # handler.count_objects()

    handler.process()
