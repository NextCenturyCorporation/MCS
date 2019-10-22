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
Create json file that can be ingested into ElasticSearch

"""
import json


class JsonImportCreator:

    def __init__(self):
        pass
        # ground_truth = "ground_truth.txt"
        # with open(ground_truth, 'w') as outfile:
        #     for block in range(1, 3):
        #         for test in range(1, 1080):
        #             results = [0, 0, 0, 0]
        #             indexes = random.sample({0, 1, 2, 3}, 2)
        #             results[indexes[0]] = 1
        #             results[indexes[1]] = 1
        #             for index in range(4):
        #                 outfile.write("O{}/{:04d}/{} {}\n".format(block, test, index+1, results[index]))


if __name__ == "__main__":
    handler = JsonImportCreator()
