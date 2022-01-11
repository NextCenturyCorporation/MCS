import argparse
import glob
import logging
import os.path
import subprocess
from typing import Callable, Dict, List, Tuple

import machine_common_sense as mcs

logger = logging.getLogger('machine_common_sense')
mcs.LoggingConfig.init_logging(mcs.LoggingConfig.get_dev_logging_config())


SCRIPT_FOLDER = os.path.dirname(os.path.abspath(__file__))
BLACK_IMAGE_PATH = SCRIPT_FOLDER + '/black_image.png'


class AbstractRunnerScript():
    def __init__(
        self,
        name: str,
        action_callback: Callable[
            [Dict, mcs.StepMetadata, 'AbstractRunnerScript'],
            Tuple[str, Dict]
        ]
    ):
        self._name = name
        args, filenames = self._read_args()
        if not len(filenames):
            print('No matching files found... Exiting')
            exit()
        self.args = args

        debug = (args.save_videos or args.save_gifs or args.debug)
        config_suffix = 'with_debug' if debug else 'no_debug'
        if args.level1:
            config_suffix = 'level1_debug' if debug else 'level1'
        if args.level2:
            config_suffix = 'level2_debug' if debug else 'level2'
        if args.oracle:
            config_suffix = 'oracle_debug' if debug else 'oracle'

        config_file_path = (
            args.config_file or
            SCRIPT_FOLDER + '/config_' + config_suffix + '.ini'
        )

        print('========================================')
        controller = mcs.create_controller(
            unity_app_file_path=args.mcs_unity_build_file,
            unity_cache_version=args.mcs_unity_version,
            config_file_or_dict=config_file_path
        )

        for filename in filenames:
            scene_name = self.run_scene(
                controller,
                filename,
                action_callback,
                args.last_step,
                args.prefix,
                args.rename
            )
            if args.save_videos or args.save_gifs:
                # Copy the black image into the debug folder as the last frame.
                frame_image_list = glob.glob(scene_name + '/frame_image_*')
                frame_count = len(frame_image_list)
                black_frame = (
                    scene_name + '/frame_image_' + str(frame_count) + '.png'
                )
                subprocess.call(['cp', BLACK_IMAGE_PATH, black_frame])
            if args.save_videos:
                subprocess.call([
                    'ffmpeg', '-y', '-r', '20', '-i',
                    scene_name + '/frame_image_%d.png',
                    '-vcodec', 'h264', '-vf', 'format=yuv420p',
                    scene_name + '.mp4'
                ])
            if args.save_gifs:
                subprocess.call([
                    'ffmpeg', '-y', '-r', '20', '-i',
                    scene_name + '/frame_image_%d.png',
                    scene_name + '.gif'
                ])

    def _append_subclass_args_to_parser(
        self,
        parser: argparse.ArgumentParser
    ) -> argparse.ArgumentParser:
        # To override
        return parser

    def _read_args(self) -> Tuple[argparse.Namespace, List[str]]:
        parser = argparse.ArgumentParser(description=('Run ' + self._name))
        parser.add_argument(
            '--config_file',
            type=str,
            default=None,
            help='MCS config file override'
        )
        parser.add_argument(
            '--debug',
            default=False,
            action='store_true',
            help='Save debug data (inputs, outputs, and images) to local files'
        )
        parser.add_argument(
            '--last_step',
            default=None,
            help='Scene last step override'
        )
        parser.add_argument(
            '--mcs_unity_build_file',
            type=str,
            default=None,
            help='Path to MCS unity build file'
        )
        parser.add_argument(
            '--mcs_unity_version',
            type=str,
            default=None,
            help='version of MCS Unity executable.  Default: current'
        )
        parser.add_argument(
            '--prefix',
            default=None,
            help='Append a prefix to each output file'
        )
        parser.add_argument(
            '--rename',
            default=None,
            help='Rename each scene and append the corresponding scene ID'
        )
        parser.add_argument(
            '--save-gifs',
            default=False,
            action='store_true',
            help='Save GIF of each MCS scene'
        )
        parser.add_argument(
            '--save-videos',
            default=False,
            action='store_true',
            help='Save video of each MCS scene'
        )

        # Metadata tiers
        parser.add_argument(
            '--level1',
            default=False,
            action='store_true',
            help='Use level 1 metadata tier and save debug data'
        )
        parser.add_argument(
            '--level2',
            default=False,
            action='store_true',
            help='Use level 2 metadata tier and save debug data'
        )
        parser.add_argument(
            '--oracle',
            default=False,
            action='store_true',
            help='Use oracle metadata tier and save debug data'
        )

        parser = self._append_subclass_args_to_parser(parser)
        return self._read_subclass_args(parser)

    def _read_subclass_args(
        self,
        parser: argparse.ArgumentParser
    ) -> Tuple[argparse.Namespace, List[str]]:
        # To override
        return None, []

    def run_scene(
        self,
        controller: mcs.Controller,
        filename: str,
        action_callback: Callable[
            [Dict, mcs.StepMetadata, 'AbstractRunnerScript'],
            Tuple[str, Dict]
        ],
        last_step: int,
        prefix: str,
        rename: bool
    ):
        scene_data, status = mcs.load_scene_json_file(filename)

        if status is not None:
            print(status)
            return

        if last_step:
            scene_data['goal'] = scene_data.get('goal', {})
            scene_data['goal']['last_step'] = int(last_step)

        # Add a name to the scene if needed.
        if 'name' not in scene_data.keys():
            scene_data['name'] = filename[0:filename.find('.')]

        # Remove the folder prefix from the scene name if needed.
        scene_data['name'] = (
            scene_data['name'][(scene_data['name'].rfind('/') + 1):]
        )

        # Use the prefix and/or rename arguments for the new scene name.
        scene_name = ((prefix + '_') if prefix else '') + (
            rename or scene_data.get('name', '')
        )

        if rename and 'sceneInfo' in scene_data.get('goal', {}):
            # Rename the scene using its hypercube cell ID.
            scene_id = scene_data['goal']['sceneInfo']['id'][0]
            scene_name = ((scene_name + '_') if scene_name else '') + scene_id

        # Override the scene name.
        scene_data['name'] = scene_name

        step_metadata = controller.start_scene(scene_data)
        action, params = action_callback(scene_data, step_metadata, self)

        while action is not None:
            step_metadata = controller.step(action, **params)
            if step_metadata is None:
                break
            action, params = action_callback(scene_data, step_metadata, self)

        controller.end_scene("", 1)

        return scene_data['name']


class SingleFileRunnerScript(AbstractRunnerScript):
    def _append_subclass_args_to_parser(
        self,
        parser: argparse.ArgumentParser
    ) -> argparse.ArgumentParser:
        parser.add_argument(
            'mcs_scene_filename',
            help='Filename of MCS scene to run'
        )
        return parser

    def _read_subclass_args(
        self,
        parser: argparse.ArgumentParser
    ) -> Tuple[argparse.Namespace, List[str]]:
        args = parser.parse_args()
        return args, [args.mcs_scene_filename]


class MultipleFileRunnerScript(AbstractRunnerScript):
    def __init__(
        self,
        name: str,
        action_callback: Callable[
            [Dict, mcs.StepMetadata, 'AbstractRunnerScript'],
            Tuple[str, Dict]
        ]
    ):
        super().__init__(name, action_callback)
        if self.args.zip_prefix:
            for file_type in (
                (['mp4'] if self.args.save_videos else []) +
                (['gif'] if self.args.save_gifs else [])
            ):
                subprocess.call(
                    ['zip', self.args.zip_prefix + '_' + file_type + '.zip'] +
                    glob.glob(self.args.mcs_scene_prefix + '*.' + file_type)
                )
            subprocess.call(
                ['zip', self.args.zip_prefix + '_frames.zip'] +
                glob.glob(self.args.mcs_scene_prefix + '*/frame_image_*.png')
            )

    def _append_subclass_args_to_parser(
        self,
        parser: argparse.ArgumentParser
    ) -> argparse.ArgumentParser:
        parser.add_argument(
            'mcs_scene_prefix',
            help='Filename prefix of all MCS scenes to run'
        )
        parser.add_argument(
            '--zip-prefix',
            default=None,
            help='Save ZIPs of frames/videos/GIFs with this filename prefix'
        )
        return parser

    def _read_subclass_args(
        self,
        parser: argparse.ArgumentParser
    ) -> Tuple[argparse.Namespace, List[str]]:
        args = parser.parse_args()
        filenames = glob.glob(args.mcs_scene_prefix + '*_debug.json')
        print(
            f'Found {len(filenames)} files matching '
            f'{args.mcs_scene_prefix + "*_debug.json"}'
        )
        if not len(filenames):
            print('No matching files found... trying non-debug files')
            filenames = glob.glob(args.mcs_scene_prefix + '*.json')
            print(
                f'Found {len(filenames)} files matching '
                f'{args.mcs_scene_prefix + "*.json"}'
            )
        return args, sorted(filenames)
