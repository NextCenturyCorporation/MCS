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
Create a file 'ground_truth.txt' that has the results of the test.

This is just random, setting 2 of the 4 scenes in a test to possible (1) and 2 to impossible (0)
"""
import random

class GroundTruthCreator:

    def __init__(self):
        ground_truth = "ground_truth.txt"
        with open(ground_truth, 'w') as outfile:
            for block in range(0, 3):
                for test in range(0, 1080):
                    results = [0, 0, 0, 0]
                    indexes = random.sample({0, 1, 2, 3}, 2)
                    results[indexes[0]] = 1
                    results[indexes[1]] = 1
                    for index in range(4):
                        outfile.write("O{}/{:04d}/{} {}\n".format(block+1, test+1, index+1, results[index]))


if __name__ == "__main__":
    random.seed(1354289787)
    handler = GroundTruthCreator()
