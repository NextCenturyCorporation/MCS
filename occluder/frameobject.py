class FrameObject:
    """A particular object (ball, occluder, ground, etc.) in a frame """

    def __init__(self, color):
        self.color = color;
        self.pixel_count = 0
        self.minx = 10000
        self.maxx = 0
        self.miny = 10000
        self.maxy = 0
        self.label = None
        self.midx = 0
        self.midy = 0
        self.dy = 0

    def set_vals(self, list_of_vals):
        self.minx = list_of_vals[1].min()
        self.maxx = list_of_vals[1].max()
        self.miny = list_of_vals[0].min()
        self.maxy = list_of_vals[0].max()
        self.calcAR()

    def add_pixel(self, x, y):
        self.pixel_count = self.pixel_count + 1
        if x < self.minx:
            self.minx = x
        if x > self.maxx:
            self.maxx = x
        if y < self.miny:
            self.miny = y
        if y > self.maxy:
            self.maxy = y
        self.calcAR()

    def calcAR(self):
        diffy = abs(self.maxy - self.miny)
        if diffy > 0:
            self.aspect_ratio = abs(self.maxx - self.minx) / diffy
        else:
            self.aspect_ratio = 1

    def __str__(self):
        return "(" + str(self.color) + " [ " + str(self.minx) + ", " + str(self.maxx) + ", " + str(
            self.miny) + ", " + str(self.maxy) + " ] " + " ct: " + str(
            self.pixel_count) + " AR: " + str(self.aspect_ratio) + ")"

    def get_mid(self):
        return [(self.maxx + self.minx) / 2., (self.maxy + self.miny) / 2.]

    @staticmethod
    def are_objects_same(obj1, obj2):
        """Determine if two objects are the same """
        if obj1.minx == obj2.minx and obj1.maxx == obj1.maxx and obj1.miny == obj2.miny and obj1.maxy == obj2.maxy:
            return True
        return False
