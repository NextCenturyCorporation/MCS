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
import datetime
import time
from itertools import starmap

from pathlib import Path
import matplotlib.image as mpimg
from matplotlib.widgets import Slider
import sys

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QSizePolicy, QSlider, QSpacerItem, \
    QVBoxLayout, QWidget

from answer import Answer

berkeley = "Berkeley-m2-learned-answer.txt"
gt = "ground_truth.txt"
block = 'O3'
test_data_path = "/mnt/ssd/cdorman/data/mcs/intphys/test/"

# Set this if you want to jump to a specific test;  otherwise it gets the next -1 in the current block
starting_test = -1  #  821

class KeyPressWindow(QtGui.QMainWindow):
    sigKeyPress = QtCore.pyqtSignal(object)
    sigMouseClick = QtCore.pyqtSignal(object)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set_function(self, fn):
        self.fn = fn

    def keyPressEvent(self, ev):
        self.fn(ev)


class Slider(QWidget):
    def __init__(self, minimum, maximum, parent=None):
        super(Slider, self).__init__(parent=parent)
        self.verticalLayout = QHBoxLayout(self)
        self.label = QLabel(self)
        self.verticalLayout.addWidget(self.label)
        self.horizontalLayout = QHBoxLayout()
        spacerItem = QSpacerItem(0, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.slider = QSlider(self)
        self.slider.setOrientation(Qt.Horizontal)
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

    def setCallback(self, fn):
        self.slider.valueChanged.connect(fn)

    def setLabelValue(self, value):
        self.x = self.minimum + (float(value) / (self.slider.maximum() - self.slider.minimum())) * (
                self.maximum - self.minimum)
        self.label.setText("{0:d}".format(int(self.x)))

    def set_val(self, value):
        self.slider.setValue(value)

    def get_val(self):
        return self.slider.value()


class TruthingViewer:

    def __init__(self):

        # init
        self.dataDir = Path(test_data_path + block)
        self.masks = []
        self.image_map = {}
        self.image_items = [None] * 4

        self.selected = []
        self.start = time.time()

        # Windowing
        self.win = KeyPressWindow()
        self.win.set_function(self.update_keypress)
        self.win.resize(1500, 400)

        self.view = pg.GraphicsLayoutWidget()
        self.view.setBackground('w')
        self.win.setCentralWidget(self.view)
        self.win.show()
        self.win.setWindowTitle('truthing')

        # self.answer = self.read_answers(berkeley)
        self.ground_truth = self.read_answers(gt)
        self.write_results()

    def read_answers(self, filename):
        try:
            with open(filename) as answer_file:
                answer = Answer()
                answer.parse_answer_file(answer_file)
                return answer
        except:
            print(" No such file {}".format(filename))
            answer = Answer()
            return answer

    def set_test_num(self, test_num):
        if test_num < 0 or test_num > 1080:
            print("going off edge of tests")
            return

        self.test_num = test_num
        self.test_num_string = str(self.test_num).zfill(4)
        self.read_images()

        self.win.setWindowTitle(str('truthing ') + str(block) + " / " + str(self.test_num_string))

    def read_images(self):
        self.image_map.clear()
        for scene in range(0, 4):
            frame_map = {}
            for frame_num in range(1, 101):
                frame_num_string = str(frame_num).zfill(3)
                image_name = self.dataDir / self.test_num_string / str(scene + 1) / "scene" / (
                        "scene_" + frame_num_string + ".png")
                img_src = mpimg.imread(str(image_name))
                frame_map[frame_num] = img_src
            self.image_map[scene] = frame_map

    def update_keypress(self, event):

        sys.stdout.flush()

        if event.key() == 70:
            self.set_test_num(self.test_num + 1)
            self.update_slider(1)
        elif event.key() == 66:
            self.set_test_num(self.test_num - 1)
            self.update_slider(1)
        elif event.key() == 49:  # This is '1'
            print("1")
            self.selected.append(1)
        elif event.key() == 50:  # this is '2'
            print("2")
            self.selected.append(2)
        elif event.key() == 51:  # this is '3'
            print("3")
            self.selected.append(3)
        elif event.key() == 52:  # this is '4'
            print("4")
            self.selected.append(4)
        elif event.key() == 81:   # this is 'q', for quit
            exit(0)
        elif event.key() == 84:  # this is 't', for toggle
            current_val = int(self.slider.get_val())
            if current_val == 1:
                self.slider.set_val(100)
            else:
                self.slider.set_val(1)
        else:
            print("key: {}".format(event.key()))

        self.handle_selected()

    def handle_selected(self):
        """If both have been selected, write out and reset"""
        if not len(self.selected) == 2:
            return

        if self.selected[0] == self.selected[1]:
            print("Cannot have same!! {}".format(self.selected[0]))
            self.selected.clear()
            return

        if self.selected[0] < 1 or self.selected[0] > 4 or self.selected[1] < 1 or self.selected[1] > 4:
            print("Not in Range!! {} {}".format(self.selected[0], self.selected[1]))
            self.selected.clear()
            return

        self.set_results()
        self.write_results()
        self.selected.clear()

        self.set_test_num(self.test_num + 1)
        self.update_slider(1)
        diff = time.time() - self.start
        print("Wrote results for: {}.  {} sec".format(self.test_num, str(diff)))
        self.start = time.time()

    def set_results(self):
        vals = [1, 1, 1, 1]
        vals[self.selected[0] - 1] = 0
        vals[self.selected[1] - 1] = 0
        test = str(self.test_num).zfill(4)
        self.ground_truth.set_vals(block, test, vals)

    def write_results(self):

        self.ground_truth.write_answer_file(gt)

        # backup file
        gt_name = str(gt + "." + datetime.datetime.now().isoformat())
        self.ground_truth.write_answer_file(gt_name)

    def mouseMoved(self, ev):
        print(" mouse moved {}".format(ev))

    def set_up_view(self):

        # Use specified test or get the latest one that has not been truthed
        test_num = starting_test
        if starting_test == -1:
            test_num = self.ground_truth.next_test(block)
        self.set_test_num(test_num)

        for scene in range(0, 4):
            image_name = self.dataDir / self.test_num_string / str(scene + 1) / "scene" / "scene_001.png"
            img_src = mpimg.imread(str(image_name))
            self.image_items[scene] = pg.ImageItem(img_src, axisOrder='row-major', border='w')

            vb = self.view.ci.addViewBox(row=0, col=scene)
            vb.invertY()
            vb.addItem(self.image_items[scene])

        self.create_slider()

    def create_slider(self):
        horizLayout = QHBoxLayout(self.view)
        self.slider = Slider(0, 100)
        self.slider.setCallback(self.update_slider)
        horizLayout.addWidget(self.slider)

    def update_slider(self, val):
        frame_num = int(val)
        if frame_num > 100 or frame_num < 1:
            return

        answer = self.ground_truth.get_answer()

        for scene in range(0, 4):
            img = self.image_map[scene][frame_num]
            scene_name = str(scene + 1)
            # If already truthed as implausible, show as red
            if answer[block][self.test_num_string][scene_name] == 0:
                self.image_items[scene].setImage(img, border=pg.mkPen(color=(255,0,0), width=8))
            else:
                self.image_items[scene].setImage(img, border='w')


if __name__ == "__main__":
    app = QtGui.QApplication([])

    dc = TruthingViewer()
    dc.set_up_view()

    QtGui.QApplication.instance().exec_()

    dc.get_input()
