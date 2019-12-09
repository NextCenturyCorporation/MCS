#
#  Determine the ground truth for evaluation
#
# for each test, there are 6 possible outcomes:
#
#   0011
#   0101
#   0110
#   1001
#   1010
#   1100
#
# Use
from PIL import Image, ImageDraw
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.widgets import Slider
import sys


from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
import pyqtgraph.metaarray as metaarray

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QSizePolicy, QSlider, QSpacerItem, \
    QVBoxLayout, QWidget


from answer import Answer

red = (255, 1, 1)
green = (1, 255, 1)
white = (255, 255, 255)


class Slider(QWidget):
    def __init__(self, minimum, maximum, parent=None):
        super(Slider, self).__init__(parent=parent)
        self.verticalLayout = QVBoxLayout(self)
        self.label = QLabel(self)
        self.verticalLayout.addWidget(self.label)
        self.horizontalLayout = QHBoxLayout()
        spacerItem = QSpacerItem(0, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.slider = QSlider(self)
        self.slider.setOrientation(Qt.Vertical)
        self.horizontalLayout.addWidget(self.slider)
        spacerItem1 = QSpacerItem(0, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.resize(self.sizeHint())

        self.minimum = minimum
        self.maximum = maximum
        self.slider.valueChanged.connect(self.setLabelValue)
        self.x = None
        self.setLabelValue(self.slider.value())

    def setLabelValue(self, value):
        self.x = self.minimum + (float(value) / (self.slider.maximum() - self.slider.minimum())) * (
        self.maximum - self.minimum)
        self.label.setText("{0:.4g}".format(self.x))


class TruthingViewer:

    def __init__(self):
        self.test_num = 1
        self.dataDir = Path("/mnt/ssd/cdorman/data/mcs/intphys/test/O2")
        self.masks = []
        self.image_map = {}
        self.texts = []
        self.image_items = [None] * 4

        self.win = QtGui.QMainWindow()
        self.win.resize(1500, 400)
        self.view = pg.GraphicsLayoutWidget()
        self.win.setCentralWidget(self.view)
        self.win.show()
        self.win.setWindowTitle('truthing')

        self.read_answers()

    def read_answers(self):
        filename = "Berkeley-m2-learned-answer.txt"
        with open(filename) as answer_file:
            answer_obj = Answer(answer_file)
            self.answer = answer_obj.get_answer()
        # answer_obj.print_answer()

    def set_test_num(self, test_num):
        self.test_num = test_num
        self.test_num_string = str(self.test_num).zfill(4)
        self.read_images()

    def read_images(self):
        self.image_map.clear()
        for scene in range(0, 4):
            frame_map = {}
            for frame_num in range(1, 101):
                frame_num_string = str(frame_num).zfill(3)
                image_name = self.dataDir / self.test_num_string / str(scene + 1) / "scene" / (
                        "scene_" + frame_num_string + ".png")
                img_src = Image.open(image_name)
                frame_map[frame_num] = img_src
            self.image_map[scene] = frame_map

    def update_keypress(self, event):

        sys.stdout.flush()

        if event.key == 'm':
            self.frame_slider.val = self.frame_slider.val + 1
            self.update_slider(1)
            return
        if event.key == 'n':
            self.frame_slider.val = self.frame_slider.val - 1
            self.update_slider(1)
            return
        if event.key == 'x':
            self.write_out_status()

        if event.key == 'right':
            self.set_test_num(self.test_num + 1)
        elif event.key == 'left':
            self.set_test_num(self.test_num - 1)

        plt.title(self.test_num_string)

        print("Reading in new test {}".format(self.test_num))
        self.frame_slider.set_val(50)

    def set_up_view(self, test_num):

        self.test_num = test_num
        self.set_test_num(test_num)

        for scene in range(0, 4):
            image_name = self.dataDir / self.test_num_string / str(scene + 1) / "scene" / "scene_001.png"
            img_src = mpimg.imread(str(image_name))
            self.image_items[scene] = pg.ImageItem(img_src, axisOrder='row-major', border='w')
            vb = self.view.ci.addViewBox(row=0, col=scene)
            vb.invertY()
            vb.addItem(self.image_items[scene])

        horizLayout = QHBoxLayout(self.view)
        horizLayout.addWidget(Slider(0,100))

    def update_slider(self, val):
        frame_num = int(self.frame_slider.val)
        self.set_test_num(frame_num)

        for text in self.texts:
            text.set_visible(False)
        self.texts.clear()

        for scene in range(0, 4):
            # self.axs[scene].imshow(self.image_map[scene][frame_num])
            self.image_items[scene].setImage(self.image_map[scene][frame_num])

            val = self.answer['O2'][self.test_num_string][str(scene+1)]
            textstr = str(val)
            self.texts.append(self.axs[scene].text(0.04, 0.95, textstr, transform=self.axs[scene].transAxes, fontsize=12,
                                 verticalalignment='top'))

        self.fig.canvas.draw_idle()

if __name__ == "__main__":

    app = QtGui.QApplication([])

    dc = TruthingViewer()
    dc.set_up_view(1)

    QtGui.QApplication.instance().exec_()
