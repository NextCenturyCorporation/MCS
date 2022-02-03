import os
from unittest import TestCase

from mcs_interface import MCSInterface


def test_mcsinterface():
    mcsif = MCSInterface()
    print(f"command dir:  {mcsif.command_out_dir}")
    print(f"image   dir:  {mcsif.image_in_dir}")


def test_start_mcs():
    # starting the unity process requires us to be
    # in the main directory
    os.chdir('..')

    mcsif = MCSInterface()
    img_name = mcsif.start_mcs()
    print(f"{img_name}")


def test_get_scene_list():
    os.chdir('..')
    mcsif = MCSInterface()
    thelist = mcsif.get_scene_list()
    for scene in thelist:
        print(f"{scene}")



if __name__ == "__main__":
    test_get_scene_list()
