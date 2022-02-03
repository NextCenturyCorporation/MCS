import argparse
import os
import time
import uuid

import machine_common_sense as mcs
from machine_common_sense import StepMetadata
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer


class RunSceneWithDir:

    def __init__(self, scene_file, command_in_dir, image_out_dir):
        self.scene_file = scene_file
        self.command_in_dir = command_in_dir
        self.image_out_dir = image_out_dir
        self.controller = mcs.create_controller(config_file_or_dict='./config_level1.ini')

    def step_and_save(self, command):
        output: StepMetadata = self.controller.step(command)
        try:
            img_list = output.image_list
            if len(img_list) > 0:
                img_path = self.image_out_dir + str(uuid.uuid4()) + ".png"
                print(f"command: {command}.  Saved image to: {img_path}")
                img = img_list[0]
                img.save(img_path)
                return img_path
            else:
                pass
                # print("Image list is empty!!")
        except Exception as e:
            print(f"didnt work {e}")

    def load_command_file(self, command_text_file):
        try:
            with open(command_text_file, 'r') as command_file:
                commands = [line.strip() for line in command_file]
        except:
            print(f"Failed to open {command_text_file}")

        for command in commands:
            self.step_and_save(command)

    def on_created(self, event):
        # print(f"{event.src_path} created!")
        self.load_command_file(event.src_path)
        os.unlink(event.src_path)

        # TODO:  Write out results and save

    def on_deleted(self, event):
        # print(f"deleted {event.src_path}!")
        pass

    def on_modified(self, event):
        print(f"{event.src_path} has been modified")
        self.load_command_file(event.src_path)
        os.unlink(event.src_path)

    def on_moved(self, event):
        # print(f"moved {event.src_path} to {event.dest_path}")
        pass

    def run_loop(self):
        print(f"Starting controller.  Watching files at {command_dir}.  Writing images to {image_dir}")

        scene_data, status = mcs.load_scene_json_file(self.scene_file)
        if status is not None:
            print(status)
            exit()

        self.controller.start_scene(scene_data)
        self.step_and_save('Pass')

        # print("Staring to listen for commands")
        patterns = ["command_*.txt"]
        ignore_patterns = None
        ignore_directories = False
        case_sensitive = True
        my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)
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
        except:
            observer.stop()

        observer.join()

        self.controller.end_scene()


def parse_args():
    parser = argparse.ArgumentParser(description='Run MCS')
    parser.add_argument(
        'mcs_scene_json_file',
        help='MCS JSON scene configuration file to load')
    parser.add_argument(
        '--mcs_command_in_dir',
        help='MCS directory that commands will appear in')
    parser.add_argument(
        '--mcs_image_out_dir',
        help='MCS directory that images will appear in')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    scene_file = args.mcs_scene_json_file
    command_dir = args.mcs_command_in_dir
    image_dir = args.mcs_image_out_dir

    runScene = RunSceneWithDir(scene_file, command_dir, image_dir)
    runScene.run_loop()
