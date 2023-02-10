import argparse
import os
import json
import shutil
DESCRIPTION = (
    "This script does two things. First you need to copy and paste your "
    "generated hypercube scenes both debug and non-debug to a directory "
    "called 'hypercube_scenes'. There are 4 args. '--change_file_names' "
    "is for changing file names to be the Cell ID of the scene. "
    "*Note* this will also delete the non-debug .json files for you. "
    "The end result are files called something like A1, B2, C3 which "
    "are all debug scenes.'--videos' will loop through all of the .json files "
    "in the 'hypercube_scenes_directory' and make videos. It will output "
    "the videos and metadata folders to a directory called "
    "'hypercube_output'. *Note* by default the videos will only go "
    "through the actions in the action_list. If you want your own actions "
    "use the '--action_file' argument to input your own action_file that can "
    "go through the actions in the action_list and do additional actions. "
    "You also need to specifify the unity build path with the '--unity' "
    "argument only if you are using the '--videos' argument. *Note* You can "
    "combine '--change_file_names' and '-videos' to change the file names "
    "and then make the videos, or can do each one indivudally if you "
    "just need to change the file names or you just need to make videos."
)


class FileRenamerVideoCreator:
    def __init__(self, files: bool, videos: bool,
                 unity: str, action_file: str):
        self._files = files
        self._videos = videos = videos
        self._unity_build_path = unity
        self._action_file = action_file
        self._actions = None
        if not self._action_file:
            self._action_file = "action_file.txt"
            self._actions = ["Pass"] * 10

    def run(self):
        if self._change_file_names:
            self._change_file_names()
        if self._videos:
            self._make_videos()

    def _create_temp_action_file(self):
        with open("action_file.txt", "w") as file:
            for action in self._actions:
                file.write(action + "\n")

    def _delete_temp_action_file(self):
        if os.path.exists("action_file.txt"):
            os.remove("action_file.txt")

    def _change_file_names(self):
        dir_path = os.path.join(os.getcwd(), "hypercube_scenes")
        for filename in os.listdir(dir_path):
            if "debug" not in filename:
                file_path = os.path.join(dir_path, filename)
                os.remove(file_path)
                continue

            file_path = os.path.join(dir_path, filename)
            with open(file_path, "r") as f:
                data = json.load(f)
                new_file_name = filename.split("_")[-2]
                data["name"] = new_file_name
            with open(file_path, "w") as f:
                json.dump(data, f, indent=4, sort_keys=True)

            new_file_path = os.path.join(dir_path, new_file_name + ".json")
            os.rename(file_path, new_file_path)

    def _make_videos(self):
        if self._actions:
            self._create_temp_action_file()
        # Get a list of all files in the directory
        files = os.listdir("./hypercube_scenes/")
        # Loop through each file in the directory
        for file_name in files:
            command = (
                f"python run_action_file.py --mcs_unity_build_file "
                f"{self._unity_build_path} ./hypercube_scenes/{file_name} "
                f"{self._action_file} --save-videos")

            # Run the command
            os.system(command)
            # Move the generated folder and video to the HyperCubeOutput folder
            folder_name = file_name.split(".")[0]
            src_folder = folder_name
            dst_folder = f"./hypercube_output/{folder_name}"
            src_video = f"{folder_name}.mp4"
            dst_video = f"./hypercube_output/{folder_name}.mp4"
            shutil.move(src_folder, dst_folder)
            shutil.move(src_video, dst_video)
        if self._actions:
            self._delete_temp_action_file()


def main():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        '-f', '--change_file_names',
        help='Change the file names to the Cell ID. Example A1, B2, C3..',
        action='store_true')
    parser.add_argument(
        '-v',
        '--videos',
        help=("Make the videos and output them to the "
              "'hypercube_output' directory. If the directory does not exist "
              "it will be created."),
        action='store_true')
    parser.add_argument(
        '-u', '--unity',
        help='The unity build path for videos.')
    parser.add_argument(
        '-a',
        '--action_file',
        help=('Set the action file instead of having one generated. '
              'The generated one is useful if there is an action_list '
              'in the scene because the generated one will only go '
              'through the action_list actions and then end the scene.'))
    args = parser.parse_args()
    FileRenamerVideoCreator(
        args.change_file_names,
        args.videos,
        args.unity,
        args.action_file
    ).run()


main()
