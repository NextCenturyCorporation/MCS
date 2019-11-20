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

"""Parse a submission file and attempt to validate it, checking the
zip and the files inside.  If it does not validate, then print a
useful message about why it did not validate.
"""
import json
import argparse
import shutil
from pathlib import Path
import tempfile
import zipfile
import os
from collections import defaultdict
import traceback


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('zipfile', help='The submission file, a zip file')
    return parser.parse_args()


class MCSEval1Validator:
    """
    Validate a submission file (a zip), making sure that it has all the files in it that it needs and
    that they are all in the right format.
    """

    def __init__(self):
        # There are 3 blocks, with 1080 tests in each, with 4 scenes in each
        self.num_scenes = 3 * 1080 * 4

    def validate(self, filename):

        # Make sure that it exists
        if not os.path.exists(filename):
            print("The file {} does not exist.".format(filename))
            return False

        # Make sure that it ends with .zip
        if not filename.endswith(".zip"):
            print("The file {} does not end with .zip".format(filename))
            return False

        # Make sure it is a valid .zip file
        if not self.valid_zip(filename):
            return False

        # Extract the data to a temp dir
        temp_dir = tempfile.mkdtemp()
        # print("Temp dir: {}".format(temp_dir))

        try:
            my_zip = zipfile.ZipFile(filename)
            my_zip.extractall(temp_dir)

            # Make sure it has an answer.txt file
            if not self.valid_answer(temp_dir):
                return False

            # Make sure that it has a description file
            if not self.valid_description(temp_dir):
                return False

            if not self.valid_location(temp_dir):
                return False

            if not self.valid_voe(temp_dir):
                return False

        except Exception as e:
            print("Unknown exception in validate on file {}: {}".format(filename, e))
            traceback.print_exc()
            return False

        finally:
            # shutil.rmtree(temp_dir)
            pass

        # If we have passed all the tests, then return true
        return True

    def valid_voe(self, dir):
        # Make sure that there are VOE files
        voe_files = [f for f in os.listdir(dir) if f.startswith("voe_") and f.endswith(".txt")]
        num_voe_files = len(voe_files)
        if num_voe_files != self.num_scenes:
            print("Wrong number of voe files: {}. Should be {}".format(num_voe_files, self.num_scenes))
            return False

        # Pick one and make sure that it is correct
        dirpath = Path(dir)
        filepath = dirpath / voe_files[123]
        return self.parse_voe(filepath)

    def parse_voe(self, voe_filepath):
        with voe_filepath.open("r") as voe_file:
            line_counter = 1
            for line in voe_file:
                split_line = line.split()
                if not int(split_line[0]) == line_counter:
                    print("Line {} of {} is {}, should start with line number".format(line_counter, voe_filepath, split_line[0]))
                    return False

                val = float(split_line[1])
                if not 0.0 <= val <= 1.0:
                    print("Line {} of {} is {}, should end with a float [0,1]".format(line_counter, voe_filepath, split_line[0]))
                    return False

                line_counter = line_counter + 1

        # Allow off by one in case there is a return at the end of the file 
        if line_counter not in [100, 101]:
            print("VOE file {} has {} lines, should be 100".format(voe_filepath, line_counter))
            return False

        return True

    def valid_location(self, dir):
        dirpath = Path(dir)
        filepath = dirpath / "location.txt"
        if not filepath.exists():
            print("location.txt does not exist in unzipped")
            return False
        return self.parse_location(filepath)

    def parse_location(self, location_filepath):
        with location_filepath.open("r") as location_file:
            line_counter = 0
            for line in location_file:
                # Line should look like:  O1/0005/4 97 46 51
                split_line = line.split()
                if (len(split_line)) != 4:
                    print("Line {}: {} does not have 4 fields in location.txt".format(line_counter, line))
                    return False

                if not self.parse_block_test_scene(split_line[0]):
                    print("Line {} failed to parse block / test / scene".format(line))
                    return False

                for index in [1, 2]:
                    val = int(split_line[index])
                    if val == -1:
                        pass
                    elif 0 <= val <= 100:
                        pass
                    else:
                        print("Line {} does not have valid location {}".format(line, val))
                        return False

                val = int(split_line[3])
                if val == -1:
                    pass
                elif 0 <= val <= 256:
                    pass
                else:
                    print("Line {} does not have valid mask value {}".format(line, val))
                    return False

        return True

    def parse_block_test_scene(self, first_part):
        """
        Parse the part of the line from answer.txt and location.txt that has
        the block / test / scene.  It should look like:  O1/0005/4, so block
        is O1, the test is 0005, and the scene is 4.
        """
        key = first_part.split('/')
        if len(key) != 3:
            print("Line {} does not have 3 parts of key".format(first_part))
            return False

        block = str(key[0])
        test = str(key[1])
        scene = str(key[2])
        # print("{} {} {} {}".format(block, test, scene, split_line[1]))

        if block not in ['O1', 'O2', 'O3']:
            print("Line does not have correct block {}".format(first_part))
            return False

        test_as_int = int(test)
        if not 0 < test_as_int < 1081:
            print("Line does not have correct test number {} != {}".format(test, test_as_int))
            return False

        if scene not in ['1', '2', '3', '4']:
            print("Line does not have correct scene {}".format(scene))
            return False

        return True

    def valid_description(self, dir):
        dirpath = Path(dir)
        filepath = dirpath / "description.json"
        if not filepath.exists():
            print("description.json does not exist in unzipped")
            return False
        return self.parse_description(filepath)

    def parse_description(self, description_filepath):
        with description_filepath.open() as description_file:
            try:
                description = json.load(description_file)

                if "Performer" not in description.keys():
                    print("No performer in description {}".format(description))
                    return False

                if "Submission" not in description.keys():
                    print("No submission information in description {}".format(description))
                    return False

            except Exception as e:
                print("Unknown exception in parse_description on file {}: {}".format(description_filepath, e))
                return False

        return True

    def valid_answer(self, dir):
        dirpath = Path(dir)
        filepath = dirpath / "answer.txt"
        if not filepath.exists():
            print("answer.txt does not exist in unzipped")
            return False
        return self.parse_answer(filepath)

    def parse_answer(self, answerpath):
        with answerpath.open("r") as answer_file:
            line_counter = 0
            for line in answer_file:
                # Line should look like:  O3/1076/2 1
                split_line = line.split()
                if len(split_line) != 2:
                    print("Line {}: {} does not have 2 fields in answer.txt".format(line_counter, line))
                    return False

                if not self.parse_block_test_scene(split_line[0]):
                    print("Line {} failed to parse block / test / scene".format(line))
                    return False

                try:
                    val = float(split_line[1])
                    if not 0 <= val <= 1:
                        print("Line {} does not have valid plausibility {}".format(line, val))
                        return False
                except Exception as e:
                    print("Line {} does not have parse-able plausibility {}: {}".format(line, split_line[1], e))
                    return False
                line_counter = line_counter + 1

        if not line_counter == self.num_scenes:
            print("Wrong number of lines in answer.txt: {}.  Should be {}".format(line_counter, self.num_scenes))
            return False

        return True

    def valid_zip(self, filename):
        try:
            my_zip = zipfile.ZipFile(filename)
            ret = my_zip.testzip()
            if ret is not None:
                print(" Bad zip.  Zipfile reports {}".format(ret))
                return False
        except Exception as e:
            print("Caught exception reading zipfile {}:  {}".format(filename, str(e)))
            return False
        return True


if __name__ == "__main__":
    arguments = parse_arguments()
    validator = MCSEval1Validator()
    result = validator.validate(arguments.zipfile)
    if result:
        print("Valid file")
    else:
        print("Invalid")
