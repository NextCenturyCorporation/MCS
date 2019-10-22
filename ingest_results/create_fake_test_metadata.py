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

class TestMetadataCreator:

    def __init__(self):

        data_json = {}
        metadata = "metadata.json"
        with open(metadata, 'w') as outfile:
            for block in range(0, 3):
                block_json = {}
                for test in range(0, 1080):

                    test_json = {"num_objects": random.randint(1, 3),
                                 "variation": random.randint(1,6),
                                 "color": random.sample({"blue", "red", "green", "magenta"}, 1)[0],
                                 "object": random.sample({"sphere", "cone", "cube"}, 1)[0]}
                    test_string = str(test+1).zfill(4)
                    block_json[test_string] = test_json

                block_string = "O" + str(block+1)
                data_json[block_string] = block_json

            json.dump(data_json, outfile, indent=4)


if __name__ == "__main__":
    random.seed(2834523)
    handler = TestMetadataCreator()

