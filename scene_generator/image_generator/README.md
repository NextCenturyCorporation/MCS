# Image Generator

## Usage

1. If needed, copy the latest version of the `materials.py` file from the scene_generator (parent) folder into the image_generator (this) folder.

2. If needed, add new objects to the `simplified_objects.py` file.

3. Run the image generator (it will pause for a bit after the final scene to create the output `images.py` file):

```
python image_generator.py <unity_app_file_path>
```

4. TAR all the output object images:

```
tar -czvf <name>.tar.gz *.png
```

5. Upload the output `images.py` file and the object images TAR file to our S3:  https://s3.console.aws.amazon.com/s3/buckets/mcs-unity-images/?region=us-east-1

## Tests

```
python -m unittest
```

