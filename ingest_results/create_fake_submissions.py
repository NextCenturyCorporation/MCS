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


class SubmissionCreator:

    def __init__(self, num_sub):

        for sub in range(num_sub):
            self.create_submission(sub)

    def create_submission(self, sub):
        # Create a working directory

        # Create the answer.txt

        # create the frame dependent VOE, with same final value as the answer.txt

        # create the location information

        # zip them all together
        pass


if __name__ == "__main__":
    random.seed(9435212)

    parser = argparse.ArgumentParser()
    parser.add_argument("--num", default="1", help="Number of submissions to create")
    opt = parser.parse_args()
    num_submissions = int(opt.num)
    print("Creating {} submissions".format(num_submissions))

    handler = SubmissionCreator(num_submissions)
