import os
import subprocess
import time

from subprocess_runner import is_file_open, start_subprocess

from tests import long_writer


def test_start_subprocess():
    os.chdir('..')
    proc = start_subprocess("/tmp/a/", "/tmp/b/")

    print(f"proc is {proc}")


def test_is_file_open():
    proc = subprocess.Popen(["python", "long_writer.py"])
    pid = proc.pid
    print(f"Looking for {long_writer.LONG_FILE_PATH} by process {pid}")

    for x in range(0, 10):
        print(f"Test #{x}")
        is_open = is_file_open(pid, long_writer.LONG_FILE_PATH)
        print(f"is open: {is_open}")
        time.sleep(1)
