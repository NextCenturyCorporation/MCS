from PIL import Image

from frameobject import FrameObject


class MaskInfo:
    """
    Mask information for a single mask.  One of 100 in a scene; one scene of 4 in a test
    """

    def __init__(self, path, frame_num):
        """The path must be the path including block and scene.   """
        self.path = path
        self.objects = {}
        self.get_objects_for_frame(frame_num)

    def get_num_obj(self):
        return len(self.objects)

    def get_obj(self):
        return self.objects

    def get_num_orig_objects(self):
        return self.orig_num_objects

    def get_objects_for_frame(self, frame_num):
        frame_num_with_leading_zeros = str(frame_num).zfill(3)
        mask_filename = self.path / "masks" / ("masks_" + frame_num_with_leading_zeros + ".png")

        mask_image = Image.open(mask_filename)
        pixels = mask_image.load()

        # Determine what parts belong to the mask
        for x in range(mask_image.size[0]):
            for y in range(mask_image.size[1]):
                color = pixels[x, y]
                if color in self.objects:
                    self.objects.get(color).add_pixel(x, y)
                else:
                    obj = FrameObject(color)
                    obj.add_pixel(x, y)
                    self.objects[color] = obj

        self.orig_num_objects = len(self.objects)

        x_spacing = [1, 20, 30, 40, 100, 120, 150, 180, 240, 277]
        y_sky_spacing = [1, 20, 50]
        sky_color = []

        # Try to find the sky
        for x in x_spacing:
            for y in y_sky_spacing:
                sky_color.append(pixels[x, y])
        sky_color = max(sky_color, key=sky_color.count)
        self.objects[sky_color].label = 'sky'

        y_ground_spacing = [163, 183]
        ground_color = []
        for x in x_spacing:
            for y in y_ground_spacing:
                ground_color.append(pixels[x, y])
        ground_color = max(ground_color, key=ground_color.count)
        self.objects[ground_color].label = 'ground'

        self.clean_up_objects(frame_num)

    def clean_up_objects(self, frame_num):
        to_be_removed = []
        sky_found = False
        ground_found = False

        for key, val in self.objects.items():

            # sky is usually the top region
            if val.minx == 0 and val.miny == 0 and val.maxx == 287 and val.maxy > 100:
                sky_found = True
                to_be_removed.append(key)
                continue

            # ground might be entire bottom
            if val.minx == 0 and val.miny == 152 and val.maxx == 287 and val.maxy == 287:
                ground_found = True
                to_be_removed.append(key)
                continue

            # Ground might start at bottom
            if val.minx == 0 and val.maxx == 287 and val.miny == 152 and val.maxy > 200:
                ground_found = True
                to_be_removed.append(key)
                continue

            # too small, must be non-occluder object
            if val.pixel_count < 501:
                to_be_removed.append(key)
                continue

            # aspect ratio wrong for medium sized
            if 500 < val.pixel_count < 1680:
                if 0.5 < val.aspect_ratio < 1.8:
                    to_be_removed.append(key)
                    continue

            # if big and not ground or sky, must be occluder
            if sky_found and ground_found and val.pixel_count > 10000:
                continue

            # If wide and flat, then must be occluder
            if val.aspect_ratio > 3:
                continue

            # If not too big, then occluder
            if val.pixel_count > 1400:
                continue

            # bad ground or sky?
            print("Got to here {} {}".format(frame_num, val))
            to_be_removed.append(key)

        for x in to_be_removed:
            self.objects.pop(x)

        # If there are two left, and one is much bigger, then it is the ground
        keys = list(self.objects.keys())
        if len(keys) == 2:
            size_1 = self.objects.get(keys[0]).pixel_count
            size_2 = self.objects.get(keys[1]).pixel_count
            if size_1 > size_2 and size_1 > 20000:
                self.objects.pop(keys[0])
            elif size_2 > size_1 and size_2 > 20000:
                self.objects.pop(keys[1])
