import glob
import os
import subprocess
import sys

BLACK_IMAGE = '../machine_common_sense/scenes/images/black_image.png'


if len(sys.argv) < 3:
    print('Usage: python create_videos.py <folder_prefix> <eval_number> '
          '<sample_number>')
    sys.exit()


def run():
    folder_prefix = sys.argv[1]
    eval_number = sys.argv[2]
    sample_number = sys.argv[3]

    folder_list = glob.glob(folder_prefix + '*')
    folder_list = [
        folder for folder in folder_list if os.path.isdir(folder)
    ]
    folder_list.sort()

    for folder in folder_list:
        print('Making GIF and videos for scene ' + folder)
        frame_image_list = glob.glob(folder + '/frame_image_*')
        frame_count = len(frame_image_list)
        black_frame = folder + '/frame_image_' + str(frame_count) + '.png'
        subprocess.call(['cp', BLACK_IMAGE, black_frame])
        subprocess.call([
            'ffmpeg',
            '-y',
            '-r',
            '5',
            '-i',
            folder + '/frame_image_%d.png',
            folder + '.gif'
        ])
        for file_type in ['mov', 'mp4']:
            subprocess.call([
                'ffmpeg',
                '-y',
                '-r',
                '5',
                '-i',
                folder + '/frame_image_%d.png',
                '-vcodec',
                'h264',
                folder + '.' + file_type
            ])
        subprocess.call(['rm', black_frame])

    zip_prefix = (
        'eval_' + eval_number + '_' + folder_prefix + 'example_' +
        sample_number + '_'
    )
    for file_type in ['gif', 'mov', 'mp4']:
        print('Making ZIP of ' + file_type + ' files')
        subprocess.call(
            ['zip', zip_prefix + file_type + '.zip'] +
            glob.glob(folder_prefix + '*.' + file_type)
        )
    print('Making ZIP of frame image files')
    subprocess.call(
        ['zip', zip_prefix + 'frames.zip'] +
        glob.glob(folder_prefix + '*/frame_image_*.png')
    )


if __name__ == "__main__":
    run()
