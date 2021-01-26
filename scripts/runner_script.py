import argparse
import glob
import subprocess

import machine_common_sense as mcs


BLACK_IMAGE_PATH = './black_image.png'


class AbstractRunnerScript():
    def __init__(
        self,
        name,
        action_callback,
        rename=False
    ):
        self._name = name
        args, filename_list = self.read_args()
        self.args = args

        if not args.mcs_unity_filename:
            return

        config_file_path = './config_no_debug.ini'
        if (args.save_videos or args.save_gifs) and args.debug:
            config_file_path = './config_with_debug.ini'
        elif args.save_videos or args.save_gifs:
            config_file_path = './config_debug_to_file.ini'
        elif args.debug:
            config_file_path = './config_debug_to_terminal.ini'

        controller = mcs.create_controller(
            args.mcs_unity_filename,
            config_file_path
        )

        for filename in filename_list:
            scene_name = self.run_scene(
                controller,
                filename,
                action_callback,
                rename
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

    def read_args(self):
        parser = argparse.ArgumentParser(description=('Run ' + self._name))
        parser.add_argument(
            'mcs_unity_filename',
            help='Path to MCS unity build file'
        )
        parser.add_argument(
            '--debug',
            default=False,
            action='store_true',
            help='Save debug images and data to local files'
        )
        parser.add_argument(
            '--save-videos',
            default=False,
            action='store_true',
            help='Save video of each MCS scene'
        )
        parser.add_argument(
            '--save-gifs',
            default=False,
            action='store_true',
            help='Save GIF of each MCS scene'
        )
        return self.read_subclass_args(parser)

    def read_subclass_args(self, parser):
        # TODO
        return None, []

    def run_scene(self, controller, filename, action_callback, rename):
        scene_data, status = mcs.load_scene_json_file(filename)

        if status is not None:
            print(status)
            return

        if rename and 'sceneInfo' in scene_data.get('goal', {}):
            # Rename the scene using its hypercube cell ID.
            scene_data['name'] = (
                (scene_data['name'] + '_') if 'name' in scene_data else ''
            ) + scene_data['goal']['sceneInfo']['id'][0]
        else:
            # Add a name to the scene if needed.
            if 'name' not in scene_data.keys():
                scene_data['name'] = filename[0:filename.find('.')]

            # Remove the folder prefix from the scene name if needed.
            scene_data['name'] = (
                scene_data['name'][(scene_data['name'].rfind('/') + 1):]
            )

        step_metadata = controller.start_scene(scene_data)
        action, params = action_callback(scene_data, step_metadata)

        while action is not None:
            step_metadata = controller.step(action, **params)
            if step_metadata is None:
                break
            action, params = action_callback(scene_data, step_metadata)

        controller.end_scene("", 1)

        return scene_data['name']


class SingleFileRunnerScript(AbstractRunnerScript):
    def read_subclass_args(self, parser):
        parser.add_argument(
            'mcs_scene_filename',
            help='Filename of MCS scene to run'
        )
        args = parser.parse_args()
        return args, [args.mcs_scene_filename]


class MultipleFileRunnerScript(AbstractRunnerScript):
    def __init__(
        self,
        name,
        action_callback,
        rename=False
    ):
        super().__init__(name, action_callback, rename)
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

    def read_subclass_args(self, parser):
        parser.add_argument(
            'mcs_scene_prefix',
            help='Filename prefix of all MCS scenes to run'
        )
        parser.add_argument(
            '--zip-prefix',
            default=None,
            help='Save ZIPs of frames/videos/GIFs with this filename prefix'
        )
        args = parser.parse_args()
        filename_list = glob.glob(args.mcs_scene_prefix + '*_debug.json')
        if len(filename_list) == 0:
            filename_list = glob.glob(args.mcs_scene_prefix + '*.json')
        return args, sorted(filename_list)
