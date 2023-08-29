#
# RunSceneWithDir runs an MCS client while watching a directory for
# commands and writing images out to another directory.
#
# Usage:
#
#     python3 run_scene_with_dir --mcs_command_in_dir indir
#          --mcs_output_dir outdir
#
# where 'indir' is the name of an existing directory that is watched
# files. When they appear, the commands are read in and executed.  The
# resulting images from MCS are written out and put into the 'outdir'.
#
import argparse
import glob
import json
import logging
import os
import time
from os.path import exists

import machine_common_sense as mcs
from machine_common_sense import StepMetadata
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

from webenabled_common import LOG_CONFIG

logging.config.dictConfig(LOG_CONFIG)
logger = logging.getLogger('run_scene_with_dir')


class RunSceneWithDir:

    def __init__(self, command_in_dir, output_dir):
        self.scene_file = None
        self.controller = None
        self.command_in_dir = command_in_dir
        self.output_dir = output_dir
        self.step_number = 0

    def run_loop(self):
        logger.info(
            f"Starting controller: watching command directory "
            f"{self.command_in_dir[(self.command_in_dir.rfind('/') + 1):]}"
            f", writing to output directory "
            f"{self.output_dir[(self.output_dir.rfind('/') + 1):]}"
        )

        self.controller = mcs.create_controller(
            config_file_or_dict='./config_level1.ini')

        patterns = ["command_*.txt"]
        ignore_patterns = None
        ignore_directories = False
        case_sensitive = True
        event_handler = PatternMatchingEventHandler(
            patterns, ignore_patterns, ignore_directories, case_sensitive)
        event_handler.on_create = self.on_created
        event_handler.on_deleted = self.on_deleted
        event_handler.on_modified = self.on_modified
        event_handler.on_moved = self.on_moved

        observer = Observer()
        observer.schedule(event_handler, self.command_in_dir, recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except Exception:
            logger.exception("Sleep interrupted, stopping observer")
            observer.stop()

        observer.join()

        self.controller.end_scene()

    def create_command_file(self, command_text_file):
        try:
            file = open(command_text_file, 'x')
            file.close()
        except Exception:
            logger.exception(f"Failed to create {command_text_file}")

    def load_command_file(self, command_text_file):

        if os.path.exists(command_text_file) is False:
            self.create_command_file(command_text_file)

        try:
            with open(command_text_file, 'r') as command_file:
                commands = [line.strip() for line in command_file]
        except Exception:
            logger.exception(f"Failed to open {command_text_file}")
            return

        for command in commands:
            # Ignore blank lines
            if command == "":
                continue

            # Handle file names (new scene file) by loading
            if command.endswith(".json"):
                self.scene_file = command
                self.step_number = 0
                self.load_scene()
            else:
                # Otherwise, assume that it is a valid action
                self.step_and_save(command)

    def load_scene(self):
        logger.info(f"Loading file {self.scene_file}")

        if not exists(self.scene_file):
            logger.warn(f"Missing file {self.scene_file}")
            return

        try:
            scene_data = mcs.load_scene_json_file(self.scene_file)
            self.controller.end_scene()
            output: StepMetadata = self.controller.start_scene(scene_data)
            self.save_output_info(output)
            self.save_output_image(output)
        except Exception:
            logger.exception(f"Error loading file {self.scene_file}")

    def step_and_save(self, command):
        logger.info(f"Executing command {command}")
        try:
            output: StepMetadata = self.controller.step(command)
            if output is not None:
                self.save_output_info(output)
                self.save_output_image(output)
                self.step_number = output.step_number
                self.delete_old_error_files()
        except Exception as error:
            logger.exception(f"Error executing command {command}")
            self.log_error(error)

    def delete_old_error_files(self):
        # Delete outdated error files
        list_of_error_files = glob.glob(
            self.output_dir + "/error_*.json")

        if len(list_of_error_files) > 0:
            for file in list_of_error_files:
                os.unlink(file)

    def log_error(self, error):
        # Save error output to a separate file
        scene_id = self.scene_file[
            (self.scene_file.rfind('/') + 1):(self.scene_file.rfind('.'))
        ]
        error_output_file = f'{self.output_dir}/error_{scene_id}_step_{self.step_number}.json'  # noqa: E501

        try:
            f = open(error_output_file, "w")
            output_to_save_dict = {
                'step_number': self.step_number,
                'error': str(error)
            }

            output_to_save_json = json.dumps(output_to_save_dict, indent=4)

            f.write(output_to_save_json)
            f.close()
        except Exception:
            logger.exception(
                f"Error saving error output to file {error_output_file}")

    def save_output_info(self, output: StepMetadata):
        logger.info(f"Saving output info at step {output.step_number}")

        output_to_save_dict = {
            'step_number': output.step_number,
            'return_status': output.return_status,
            'reward': output.reward,
            'steps_on_lava': output.steps_on_lava
        }

        output_to_save_json = json.dumps(output_to_save_dict, indent=4)

        scene_id = self.scene_file[
            (self.scene_file.rfind('/') + 1):(self.scene_file.rfind('.'))
        ]
        try:
            output_path = (
                f'{self.output_dir}/step_output_{scene_id}_step_'
                f'{output.step_number}.json'
            )
            logger.info(
                f"Saved json file on step {output.step_number} to "
                f"{output_path}"
            )
            f = open(output_path, "a")
            f.write(output_to_save_json)
            f.close()
        except Exception:
            logger.exception(
                f"Error saving output info on step {output.step_number}")

    def save_output_image(self, output: StepMetadata):
        logger.info(f"Saving output image at step {output.step_number}")
        scene_id = self.scene_file[
            (self.scene_file.rfind('/') + 1):(self.scene_file.rfind('.'))
        ]
        try:
            img_list = output.image_list
            if len(img_list) > 0:
                img_path = (
                    f'{self.output_dir}/rgb_{scene_id}_step_'
                    f'{output.step_number}.png'
                )
                logger.info(
                    f"Saved RGB image on step {output.step_number} to "
                    f"{img_path}"
                )
                img = img_list[0]
                img.save(img_path)
                return img_path
            else:
                logger.warn(f"Missing RGB image on step {output.step_number}")
        except Exception:
            logger.exception(
                f"Error saving output image on step {output.step_number}")

    # ----------------------------------
    # Watchdog functions
    # ----------------------------------
    def on_created(self, event):
        logger.info(f"File creation: {event.src_path}")
        self.load_command_file(event.src_path)
        os.unlink(event.src_path)

    def on_modified(self, event):
        logger.info(f"File modified: {event.src_path}")
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
        '--mcs_output_dir',
        help='MCS directory that images will appear in')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    # scene_file = args.mcs_scene_json_file
    command_in_dir = args.mcs_command_in_dir
    output_dir = args.mcs_output_dir

    run_scene = RunSceneWithDir(command_in_dir, output_dir)
    run_scene.run_loop()
