import os
import subprocess
import sys

CODE_PATH = '.'
SPHINX_README = CODE_PATH + '/SPHINX_README.md'
SPHINX_VENV_FOLDER = 'venv'
SPHINX_VENV_PATH = CODE_PATH + '/' + SPHINX_VENV_FOLDER

subprocess_1 = subprocess.Popen(['git', 'status', '--porcelain'],
                                stdout=subprocess.PIPE)
subprocess_2 = subprocess.Popen(['sed', 's/^...//'],
                                stdin=subprocess_1.stdout,
                                stdout=subprocess.PIPE)
subprocess_3 = subprocess.Popen(['grep', CODE_PATH + '/.*.py'],
                                stdin=subprocess_2.stdout,
                                stdout=subprocess.PIPE)
files_count = subprocess.check_output(['wc', '-l'], stdin=subprocess_3.stdout)

if int(files_count.decode('utf-8')[:-1]) == 0:
    print('No update to Python API sphinx markdown documentation.')
    sys.exit(2)

if not os.path.exists(SPHINX_VENV_PATH) or not os.path.isdir(SPHINX_VENV_PATH):
    print(f'ERROR: Your {SPHINX_VENV_PATH} folder does not exist. Please '
          f'setup your sphinx virtual environment before making a commit to '
          f'the Python API. See {SPHINX_README} for more info.')
    sys.exit(1)
