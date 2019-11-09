#
#   Train on occluder images, using keras
#
import time

from keras.preprocessing.image import ImageDataGenerator
from numpy import mean
from numpy import std
from matplotlib import pyplot
from sklearn.model_selection import KFold
from keras.datasets import mnist
from keras.utils import to_categorical
import numpy as np
from keras.models import Sequential
from keras.layers import Conv2D
from keras.layers import MaxPooling2D
from keras.layers import Dense
from keras.layers import Flatten
from keras.optimizers import SGD
from keras.models import load_model
from sklearn.metrics import classification_report, confusion_matrix


class Occluder:

    def __init__(self):

        # Not sure if we need the rescale or not.
        self.datagen = ImageDataGenerator(rescale=1. / 255)

        # self.train_dir = "/mnt/ssd/cdorman/data/mcs/intphys/split/train"
        # self.test_dir = "/mnt/ssd/cdorman/data/mcs/intphys/split/test"

        self.train_dir = "/mnt/ssd/cdorman/data/mcs/intphys/split/smalltrain"
        self.test_dir = "/mnt/ssd/cdorman/data/mcs/intphys/split/smalltest"

    def read_in_data(self):
        # prepare an iterators for each dataset
        self.train_it = self.datagen.flow_from_directory(self.train_dir, class_mode='categorical')
        # val_it = self.datagen.flow_from_directory('data/validation/', class_mode='binary')
        self.test_it = self.datagen.flow_from_directory(self.test_dir, class_mode='categorical')
        # confirm the iterator works
        batchX, batchy = self.train_it.next()
        print('Batch shape=%s, min=%.3f, max=%.3f' % (batchX.shape, batchX.min(), batchX.max()))

    # define cnn model
    def define_model(self):
        model = Sequential()
        model.add(Conv2D(32, (3, 3), activation='relu', kernel_initializer='he_uniform', input_shape=(256, 256, 3)))
        # model.add(Conv2D(32, (3, 3), activation='relu', kernel_initializer='he_uniform', input_shape=(28, 28, 1)))

        model.add(MaxPooling2D((2, 2)))
        model.add(Flatten())
        model.add(Dense(100, activation='relu', kernel_initializer='he_uniform'))
        model.add(Dense(4, activation='softmax'))

        # compile model
        opt = SGD(lr=0.01, momentum=0.9)
        model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])

        self.model = model

    def process(self):
        # Train
        start_time = time.time()
        self.model.fit_generator(self.train_it, steps_per_epoch=10, verbose=0)
        print("Train time: {}".format(time.time()-start_time))
        # Store model
        self.model.save('final_model.h5')

    def eval(self):

        model = load_model('final_model.h5')

        # Eval
        start_time = time.time()
        score = model.evaluate_generator(self.test_it, steps=10)
        print("Eval time: {}".format(time.time()-start_time))
        print("Score: {}".format(score))

        y_pred = model.predict_generator(self.test_it, steps=10)
        y_pred = np.argmax(y_pred, axis=1)
        print('Confusion Matrix')
        print(confusion_matrix(self.test_it.classes, y_pred))
        print('Classification Report')
        target_names = ['Cone', 'Cube', 'occluder', 'Sphere']
        print(classification_report(self.test_it.classes, y_pred, target_names=target_names))

if __name__ == "__main__":
    dc = Occluder()
    dc.read_in_data()
    # dc.define_model()
    # dc.process()
    dc.eval()
