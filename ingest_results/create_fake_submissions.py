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
Create some submissions, which includes:
    answer.txt    -- same format as ground_truth.txt and intphys answer.txt
    frame-dependedent VOE
    which location

Pass in an integer that determines the number of submissions to create, default to 1.
"""
import random
import argparse
import os
import json
import shutil
import tempfile
from pathlib import Path


class SubmissionCreator:

    def __init__(self, num_sub):
        for sub in range(num_sub):
            self.create_submission(sub)

    def create_submission(self, sub):
        sub_name = "submission_" + str(sub)

        # Create a working directory
        base_dir = Path(tempfile.mkdtemp())
        dir_path = Path(base_dir / sub_name)
        if not os.path.exists(dir_path):
            print("Creating directory " + str(dir_path))
            os.mkdir(dir_path)

        # Create descriptive json file.  In this case all the submissions are by the same TA1 performer.
        # TODO:  make multiple performers with multiple submissions
        desc_json = {"Performer": "TA1_group_test",
                     "Submission": sub_name,
                     "Description": "What data was used, what parameters"}
        desc_path = dir_path / "description.json"
        with open(desc_path, "w") as outfile:
            json.dump(desc_json, outfile, indent=4)

        # Create the answer.txt
        answer_json = self.create_answer_txt(dir_path)

        # create the frame dependent VOE, with same final value as the answer.txt
        self.create_frame_dependent_voe(dir_path, answer_json)

        # create the location information
        self.create_location_information(dir_path, answer_json)

        # zip them all together
        shutil.make_archive(sub_name, 'zip', base_dir)

    def create_answer_txt(self, path):
        answer_file = "answer.txt"
        answer_json = {}
        with open(path / answer_file, 'w') as outfile:
            for block in range(0, 3):
                block_json = {}
                for test in range(0, 1080):
                    test_json = {}
                    # Create 2 high, 2 low and shuffle
                    results = [random.uniform(0.0, 0.3), random.uniform(0.0, 0.2), random.uniform(0.7, 1.0),
                               random.uniform(0.8, 1.0)]
                    random.shuffle(results)
                    for scene in range(4):
                        outfile.write("O{}/{:04d}/{} {:04f}\n".format(block + 1, test + 1, scene + 1, results[scene]))
                        test_json[str(scene + 1)] = results[scene]
                    block_json[str(test + 1)] = test_json
                answer_json[str(block + 1)] = block_json

        return answer_json

    def create_frame_dependent_voe(self, path, answer_json):

        for block in range(0, 3):
            for test in range(0, 1080):
                for scene in range(0, 4):

                    file_name = "voe_O" + str(block + 1) + "_" + str(test + 1).zfill(4) + "_" + str(scene + 1) + ".txt"
                    final_answer = answer_json[str(block + 1)][str(test + 1)][str(scene + 1)]

                    with open(path / file_name, 'w') as outfile:
                        for frame_num in range(0, 20):
                            outfile.write("{} 1.0000\n".format(frame_num + 1))

                        frame_val = 1.0
                        index_of_final = random.randint(20, 100)
                        for frame_num in range(0, index_of_final):
                            frame_val = frame_val - random.uniform(0, (1. - final_answer) / (101 - index_of_final))
                            if frame_val < final_answer:
                                frame_val = final_answer
                            outfile.write("{} {:04f}\n".format(frame_num + 1, frame_val))

                        for frame_num in range(index_of_final, 100):
                            outfile.write("{} {:04f}\n".format(frame_num + 1, final_answer))

    def create_location_information(self, path, answer_json):
        location_file = "location.txt"
        with open(path / location_file, 'w') as outfile:
            for block in range(0, 3):
                for test in range(0, 1080):
                    for scene in range(0, 4):
                        final_answer = answer_json[str(block + 1)][str(test + 1)][str(scene + 1)]
                        if final_answer > 0.5:
                            frame_num = random.randint(0, 100)
                            location = [random.randint(0, 100), random.randint(0, 100)]
                            outfile.write("O{}/{:04d}/{} {} {} {}\n".format(block + 1, test + 1, scene + 1, frame_num,
                                                                            location[0], location[1]))
                        else:
                            outfile.write("O{}/{:04d}/{} -1 -1 -1\n".format(block + 1, test + 1, scene + 1))


if __name__ == "__main__":
    random.seed(9435212)

    parser = argparse.ArgumentParser()
    parser.add_argument("--num", default="1", help="Number of submissions to create")
    opt = parser.parse_args()
    num_submissions = int(opt.num)
    print("Creating {} submissions".format(num_submissions))

    handler = SubmissionCreator(num_submissions)
