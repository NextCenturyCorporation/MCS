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

        # Create descriptive json file.  In this case all the submissions are by the
        # same TA1 performer.
        # TODO:  make multiple performers with multiple submissions
        desc_json = {"Performer": "TA1_group_test",
                     "Submission": sub_name,
                     "Description": "What data was used, what parameters"}
        desc_path = dir_path / "description.json"
        with open(desc_path, "w") as outfile:
            json.dump(desc_json, outfile, indent=4)

        # Create the answer.txt

        # create the frame dependent VOE, with same final value as the answer.txt

        # create the location information

        # zip them all together
        shutil.make_archive(sub_name, 'zip', base_dir)


if __name__ == "__main__":
    random.seed(9435212)

    parser = argparse.ArgumentParser()
    parser.add_argument("--num", default="1", help="Number of submissions to create")
    opt = parser.parse_args()
    num_submissions = int(opt.num)
    print("Creating {} submissions".format(num_submissions))

    handler = SubmissionCreator(num_submissions)
