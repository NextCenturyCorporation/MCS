import argparse
import os
import pathlib
import shutil
import subprocess
from typing import List

import machine_common_sense as mcs


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i',
                        '--input',
                        required=True,
                        help="Input directory path")
    parser.add_argument('-o',
                        '--output',
                        required=True,
                        help="Output directory")
    parser.add_argument('-e',
                        '--engine',
                        required=True,
                        help="Path to Unity runtime")
    return parser.parse_args()


def run_scene(controller, file_name: str) -> None:
    '''Run the passive physics scene to generate the image frames'''
    scene_data, status = mcs.load_scene_json_file(file_name)

    if status is not None:
        print(status)
        return

    scene_file_path = file_name
    scene_file_name = scene_file_path[scene_file_path.rfind('/') + 1:]

    if 'name' not in scene_data.keys():
        scene_data['name'] = scene_file_name[0:scene_file_name.find('.')]

    last_step = 30
    if (
        'goal' in scene_data.keys(
        ) and 'last_step' in scene_data['goal'].keys()
    ):
        last_step = scene_data['goal']['last_step']

    output = controller.start_scene(scene_data)

    for _ in range(output.step_number + 1, last_step + 1):
        action = output.action_list[len(output.action_list) - 1]
        output = controller.step(action)


def list_quartets(input_dir: str) -> List:
    '''From the input directory, list the non-debug quartet files'''
    files = list(sorted(pathlib.Path(input_dir).glob('*[!debug].json')))
    num_files = len(files)
    if num_files % 4 != 0:
        raise ValueError('Number of scene files is not a multiple of 4')
    return [files[x:x + 4] for x in range(0, num_files, 4)]


def cleanup(quartet: List) -> None:
    '''Remove quartet directories and images'''
    for q in quartet:
        shutil.rmtree(str(q.stem), ignore_errors=True)


def main():
    args = parse_args()
    quartets = list_quartets(args.input)
    output_dir = pathlib.Path(args.output)
    controller = mcs.create_controller(config_file_or_dict={},
                                       unity_app_file_path=args.engine)

    # object_permanence, shape_constancy, spatio_temporal_continuity -
    # {0001 - 0100} - {1 - 4}
    for quartet in quartets:
        for q in quartet:
            run_scene(controller, str(q))

        basename = str(quartet[0].stem[:-2])
        # make a system call to ffmpeg to make the quad video
        try:
            # yapf: disable
            subprocess.run(['ffmpeg',
                            '-y',
                            '-i', f'{str(quartet[0].stem)}/frame_image_%d.png',
                            '-i', f'{str(quartet[1].stem)}/frame_image_%d.png',
                            '-i', f'{str(quartet[2].stem)}/frame_image_%d.png',
                            '-i', f'{str(quartet[3].stem)}/frame_image_%d.png',
                            '-filter_complex', 'nullsrc=size=640x480 [base]; [0:v] setpts=PTS-STARTPTS, scale=320x240 [upperleft]; [1:v] setpts=PTS-STARTPTS, scale=320x240 [upperright]; [2:v] setpts=PTS-STARTPTS, scale=320x240 [lowerleft]; [3:v] setpts=PTS-STARTPTS, scale=320x240 [lowerright]; [base][upperleft] overlay=shortest=1 [tmp1]; [tmp1][upperright] overlay=shortest=1:x=320 [tmp2]; [tmp2][lowerleft] overlay=shortest=1:y=240 [tmp3]; [tmp3][lowerright] overlay=shortest=1:x=320:y=240',  # noqa: E501
                            '-c:v', 'libx264', output_dir / f'{basename}.mp4'
                            ])
            # yapf: enable
        except OSError as e:
            if e.errno == os.errno.ENOENT:
                raise OSError('ffmpeg command missing')

        cleanup(quartet)


if __name__ == "__main__":
    main()
