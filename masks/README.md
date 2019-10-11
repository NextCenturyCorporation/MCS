
# Masks Processor

Code in this directory processes a train/ directory, reading each
directory under it and creating a newmasks/ directory with mask files
that are consistent across mask files.  It also creates a
newstatus.json file with the mask values in the header section.

Usage:
   python3 masks.py --dir /path/to/train/


## Results

Before:

/mnt/ssd/cdorman/data/mcs/intphys$ tree smalltrain/
  smalltrain/
  ├── 2
  │   ├── depth
  │   │   ├── depth_001.png
  │   │   ├── .....
  │   │   └── depth_100.png
  │   ├── masks
  │   │   ├── masks_001.png
  │   │   ├── ....
  │   │   └── masks_100.png
  │   ├── scene
  │   │   ├── scene_001.png
  │   │   ├── ....
  │   │   └── scene_100.png
  │   └── status.json

/mnt/ssd/cdorman/data/mcs/intphys$ tree smalltrain/

/mnt/ssd/cdorman/data/mcs/mcs_github/masks[master ]$ python3 masks.py --dir /mnt/ssd/cdorman/data/mcs/intphys/smalltrain/

After:

  smalltrain/
  ├── 2
  │   ├── depth
  │   │   ├── depth_001.png
  │   │   ├── .....
  │   │   └── depth_100.png
  │   ├── masks
  │   │   ├── masks_001.png
  │   │   ├── ....
  │   │   └── masks_100.png
  │   ├── newmasks
  │   │   ├── masks_001.png
  │   │   ├── ...
  │   │   ├── masks_100.png
  │   ├── newstatus.json
  │   ├── scene
  │   │   ├── scene_001.png
  │   │   ├── ....
  │   │   └── scene_100.png
  │   └── status.json
