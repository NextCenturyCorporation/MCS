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
This file processes a train/ directory, reading each directory under it and
creating a newmasks/ directory with mask files that are consistent across
mask files.  It also creates a newstatus.json file with the mask values in
the header section.

Usage:
   python3 masks.py --dir /path/to/train/
   
"""
import argparse
import json
import os
import shutil
from PIL import Image
from pathlib import Path

import option


def map_image(orig_image, mask_map):
    """Map the image pixels for a single image, returning a new image"""
    orig_image_pixels = orig_image.load()

    new_image = orig_image
    new_image_pixels = new_image.load()
    for i in range(orig_image.size[0]):
        for j in range(orig_image.size[1]):
            new_image_pixels[i, j] = mask_map[orig_image_pixels[i, j]]
    return new_image


class TopLevelProcessor:
    """Handle the top level directory, which should contain a lot of subdirectories,
    each of which has a status.json and a masks directory.
    """

    def __init__(self, top_level_dir):
        dir_path = Path(top_level_dir)
        if not os.path.exists(dir_path):
            print("Top level dir does not exist.  Cannot process {} ".format(dir_path))
            exit(1)

        # Get all the subdirectories under there
        dirs = [(dir_path / f) for f in os.listdir(dir_path) if os.path.isdir(dir_path / f)]
        dirs.sort()
        print("Processing {} directories.  ".format(len(dirs)))

        for directory in dirs:
            scene = SceneProcessor(directory)
            print("Processing masks in {}".format(directory))
            scene.process_mask_files()
            scene.save_new_status()


class SceneProcessor:
    """Handle the masks in a single scene"""

    def __init__(self, single_dir):
        """Initialize the class with directory that contains /masks, /frames/, /depth, and status.json"""
        self.dir_path = Path(single_dir)
        self.masks_dir = self.dir_path / "masks"
        if not os.path.exists(self.masks_dir):
            print("Path does not exist.  Cannot process masks in {}".format(self.masks_dir))
            return

        # Create place where we will put the new masks
        self.new_masks_dir = self.dir_path / "newmasks"
        if not os.path.exists(self.new_masks_dir):
            os.mkdir(self.new_masks_dir)

        status_file = self.dir_path / "status.json"
        with open(status_file) as file:
            self.status_json = json.load(file)
            # print("status.json header: ", self.status_json["header"])
            self.frames = self.status_json["frames"]
            self.first_mask = self.frames[0]["masks"]
            # print("First mask ", first_mask)

        # Sanity check:  Make sure there are 100 image files
        self.mask_files = [(self.masks_dir / f) for f in os.listdir(self.masks_dir) if
                           os.path.isfile(self.masks_dir / f)]
        self.mask_files.sort()
        if not len(self.mask_files) == 100:
            print("Wrong number of mask files! In {}: {}".format(self.masks_dir, len(self.mask_files)))

    def save_new_status(self):
        new_status = self.status_json
        new_status["header"]["masks"] = self.first_mask

        new_status_file = self.dir_path / "newstatus.json"
        with open(new_status_file, 'w') as outfile:
            json.dump(new_status, outfile, indent=4)

    def process_mask_files(self):

        # Get the initial mask values.  Will be like:  {'floor':34, 'object_1':241, etc.}
        mask_values = self.first_mask

        # Copy over the first mask image.
        shutil.copy(self.mask_files[0], self.new_masks_dir)

        # Go through the rest of the frames.
        for index in range(1, len(self.mask_files)):
            frame_obj = self.frames[index]

            # Get the new mask values, if any.  Looks like:  {'floor':111, 'object_1':31, etc.}
            if "masks" in frame_obj:
                mask_values = frame_obj["masks"]
                # print("New Mask Values, for index {} (frame {}):  {}".format(index, (index + 1), mask_values))

            # Map the current mask_values to the first_mask values
            # Example:   { 111:34, 31:241 } , since 'floor' is 111 but should be 34
            mask_map = dict()
            for value in mask_values:
                # If there are new objects (i.e. not in first_mask), add them to first_mask.  Todo: Does this happen?
                if value not in self.first_mask:
                    self.first_mask[value] = mask_values[value]
                mask_map[mask_values[value]] = self.first_mask[value]

            # print(" Mask map: ", mask_map)

            self.create_new_mask(index, mask_map)

    def create_new_mask(self, index, mask_map):
        """Create new file (newmasks/mask_123.png) from old file (masks/mask_123.png)
        with the pixels values changed according to the mask_map.
        """

        #  Be careful with naming: the first mask is index 0 but the file is called "masks_001.png"
        image_file_name = "masks_" + "{:03d}".format(index + 1) + ".png"
        full_path = self.masks_dir / image_file_name
        if not os.path.exists(full_path):
            print("File {} does not exist".format(image_file_name))
            return
        orig_image = Image.open(full_path)

        mapped_image = map_image(orig_image, mask_map)
        mapped_image.save(self.new_masks_dir / image_file_name)


if __name__ == "__main__":
    opt = option.make(argparse.ArgumentParser())

    print("Directory to use: ", opt.dir)

    handler = TopLevelProcessor(opt.dir)
