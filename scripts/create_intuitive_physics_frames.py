import glob
import os
import subprocess
import sys

if len(sys.argv) < 3:
    print('Usage: python create_intuitive_physics_frames.py <folder_prefix> '
          '<eval_number> <move_across>')
    sys.exit()


def run():
    folder_prefix = sys.argv[1]
    eval_number = sys.argv[2]
    move_across = False
    if len(sys.argv) > 3:
        move_across = True

    folder_list = glob.glob(folder_prefix + '*')
    folder_list = [
        folder for folder in folder_list if os.path.isdir(folder)
    ]
    folder_list.sort()

    file_list = []

    frame_1 = '0' if move_across else '32'
    frame_2 = '40' if move_across else '60'
    for folder in folder_list:
        file_list.append(folder + '/frame_image_' + frame_1 + '.png')
        file_list.append(folder + '/frame_image_' + frame_2 + '.png')

    zip_prefix = (
        'eval_' + eval_number + '_' + folder_prefix + 'frames_' + frame_1 +
        '_' + frame_2
    )
    print('Making ZIP of frame image files')
    subprocess.call(['zip', zip_prefix + '.zip'] + file_list)


if __name__ == "__main__":
    run()
