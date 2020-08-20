# Scene Generator

## Setup

### Install Requirements

```
pip3 install -r requirements.txt
```

### Goal Images

If you want to have an image pixel array for each target object in the interactive goals, you must first run the `image_generator` to populate the `images` folder with each object/material combination pixel array text file (or download the files from S3).

Pixels (for the scene generator):

https://mcs-unity-images.s3.amazonaws.com/mcs-evaluation-pixels-summer-2020.tar.gz

Untar this file so it populates a folder called `images` inside this folder (`scene_generator`).

Images (for viewing):

https://mcs-unity-images.s3.amazonaws.com/mcs-evaluation-images-summer-2020.tar.gz

## Running

The following will show the script's options in your terminal:

```
python3 scene_generator.py
```

Here's an example that generates 10 retrieval scenes:

```
python3 scene_generator.py --prefix my_scene -c 10 --goal Retrieval --find_path
```

## Testing

```
python3 -m pytest *_test.py
```

