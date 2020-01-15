# MCS AI2-THOR Python Wrapper

- AI2-THOR Documentation:  http://ai2thor.allenai.org/documentation
- AI2-THOR GitHub:  https://github.com/allenai/ai2thor
- MCS AI2-THOR GitHub Fork:  https://github.com/NextCenturyCorporation/ai2thor

## Setup

1. Build the MCS Unity application using the MCS fork of the AI2-THOR GitHub repository.  On Linux, this will create the file `<path_to_cloned_repository>/unity/MCS-AI2-THOR.x86_64`.

2. Install the Python dependencies (I tested on Python v3.6.5)

```
pip install ai2thor
pip install Pillow
```

## Run

To run via command line with visual output:

```
python run_ai2thor.py <path_to_mcs_unity_build_file>
```

To run via command line headlessly, first install xvfb (on Ubuntu, run `sudo apt-get install xvfb`), then:

```
xvfb-run --auto-servernum --server-args='-screen 0 640x480x24' python run_ai2thor.py <path_to_mcs_unity_build_file>
```

