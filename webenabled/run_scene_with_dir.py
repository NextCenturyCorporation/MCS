#
# RunSceneWithDir runs an MCS client while watching a directory for
# commands and writing images out to another directory.
#
# Usage:
#
#     python3 run_scene_with_dir --mcs_command_in_dir indir
#          --mcs_image_out_dir outdir
#
# where 'indir' is the name of an existing directory that is watched
# files. When they appear, the commands are read in and executed.  The
# resulting images from MCS are written out and put into the 'outdir'.
#
import argparse
import os
import time
import uuid
from os.path import exists

import machine_common_sense as mcs
from machine_common_sense import StepMetadata
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer


class RunSceneWithDir:

    def __init__(self, command_in_dir, image_out_dir):
        self.scene_file = None
        self.controller = None
        self.command_in_dir = command_in_dir
        self.image_out_dir = image_out_dir

    def run_loop(self):
        print(f"Starting controller.  Watching files at {command_dir}." +
              f"  Writing images to {image_dir}")

        self.controller = mcs.create_controller(
            config_file_or_dict='./config_level1.ini')

        # print("Staring to listen for commands")
        patterns = ["command_*.txt"]
        ignore_patterns = None
        ignore_directories = False
        case_sensitive = True
        my_event_handler = PatternMatchingEventHandler(
            patterns, ignore_patterns, ignore_directories, case_sensitive)
        my_event_handler.on_create = self.on_created
        my_event_handler.on_deleted = self.on_deleted
        my_event_handler.on_modified = self.on_modified
        my_event_handler.on_moved = self.on_moved

        observer = Observer()
        observer.schedule(my_event_handler, command_dir, recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except Exception as e:
            print(f"Sleep interrupted, stopping observer: {e}")
            observer.stop()

        observer.join()

        self.controller.end_scene()

    def load_command_file(self, command_text_file):
        try:
            with open(command_text_file, 'r') as command_file:
                commands = [line.strip() for line in command_file]
        except Exception as e:
            print(f"Failed to open {command_text_file}: {e}")
            return

        for command in commands:
            # Ignore blank lines
            if command == "":
                continue

            # Handle file names (new scene file) by loading
            if command.endswith(".json"):
                self.scene_file = command
                self.load_scene()
            else:
                # Otherwise, assume that it is a valid action
                self.step_and_save(command)

    def load_scene(self):
        print(f"Loading file {self.scene_file}")

        if not exists(self.scene_file):
            print(f"File {self.scene_file} does not exist")
            return

        try:
            scene_data, status = mcs.load_scene_json_file(self.scene_file)
            if status is not None:
                raise ValueError(
                    f"Unable to read in {self.scene_file}: {status}")

            self.controller.end_scene()
            output: StepMetadata = self.controller.start_scene(scene_data)
            self.save_output(output)
        except Exception as e:
            print(f"Loading scene file failed: {e}")

        # TODO:  Decide if we need to do this.  It may allow us to get an image
        # self.step_and_save('Pass')

    def step_and_save(self, command):
        print(f"Executing command: {command}")
        try:
            output: StepMetadata = self.controller.step(command)
            if output is not None:
                self.save_output(output)
        except Exception as e:
            print(f"Error: {e}")

    def save_output(self, output: StepMetadata):
        try:
            img_list = output.image_list
            if len(img_list) > 0:
                img_path = self.image_out_dir + str(uuid.uuid4()) + ".png"
                print(f"Saved image to: {img_path}")
                img = img_list[0]
                img.save(img_path)
                return img_path
            else:
                pass
                # print("Image list is empty!!")
        except Exception as e:
            print(f"saving image didnt work: {e}")

    # ----------------------------------
    # Watchdog functions
    # ----------------------------------
    def on_created(self, event):
        # print(f"{event.src_path} created!")
        self.load_command_file(event.src_path)
        os.unlink(event.src_path)

    def on_modified(self, event):
        print(f"{event.src_path} has been modified")
        self.load_command_file(event.src_path)
        os.unlink(event.src_path)

    def on_moved(self, event):
        pass

    def on_deleted(self, event):
        pass


def parse_args():
    parser = argparse.ArgumentParser(description='Run MCS')
    # parser.add_argument(
    #     'mcs_scene_json_file',
    #     help='MCS JSON scene configuration file to load')
    parser.add_argument(
        '--mcs_command_in_dir',
        help='MCS directory that commands will appear in')
    parser.add_argument(
        '--mcs_image_out_dir',
        help='MCS directory that images will appear in')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    # scene_file = args.mcs_scene_json_file
    command_dir = args.mcs_command_in_dir
    image_dir = args.mcs_image_out_dir

    runScene = RunSceneWithDir(command_dir, image_dir)
    runScene.run_loop()
