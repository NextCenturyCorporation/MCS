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
    move_across = len(sys.argv) > 3
    folder_list = glob.glob(f"{folder_prefix}*")
    folder_list = sorted([
        folder for folder in folder_list if os.path.isdir(folder)
    ])

    file_list = []

    frame_1 = '0' if move_across else '32'
    frame_2 = '40' if move_across else '60'
    for folder in folder_list:
        file_list.append(f"{folder}/frame_image_{frame_1}.png")
        file_list.append(f"{folder}/frame_image_{frame_2}.png")

    zip_prefix = (
        f"eval_{eval_number}_{folder_prefix}frames_{frame_1}_{frame_2}"
    )
    print('Making ZIP of frame image files')
    subprocess.call(['zip', f"{zip_prefix}.zip"] + file_list)


if __name__ == "__main__":
    run()
