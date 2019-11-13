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
from keras.layers import Conv2D, Dropout
from keras.layers import MaxPooling2D
from keras.layers import Dense
from keras.layers import Flatten
from keras.optimizers import SGD
from keras.models import load_model
from sklearn.metrics import classification_report, confusion_matrix

from keras.applications.vgg16 import VGG16
from keras.preprocessing import image
from keras.applications.vgg16 import preprocess_input


class Occluder:

    def __init__(self):
        self.size = 224

        # Not sure if we need the rescale or not.
        self.datagen = ImageDataGenerator(rescale=1. / 255 )

        # self.train_dir = "/mnt/ssd/cdorman/data/mcs/intphys/split/train"
        # self.test_dir = "/mnt/ssd/cdorman/data/mcs/intphys/split/test"

        self.train_dir = "/mnt/ssd/cdorman/data/mcs/intphys/split/smalltrain"
        self.test_dir = "/mnt/ssd/cdorman/data/mcs/intphys/split/smalltest"

    def read_in_data(self):
        # prepare an iterators for each dataset
        self.train_it = self.datagen.flow_from_directory(self.train_dir, color_mode="grayscale",
                                                         target_size=(self.size, self.size),
                                                         class_mode='categorical')

        # confirm the iterator works
        batchX, batchy = self.train_it.next()
        print('Batch shape=%s, min=%.3f, max=%.3f' % (batchX.shape, batchX.min(), batchX.max()))

        # val_it = self.datagen.flow_from_directory('data/validation/', class_mode='binary')

    def read_in_test(self):
        self.test_it = self.datagen.flow_from_directory(self.test_dir, color_mode="grayscale",
                                                        target_size=(self.size, self.size),
                                                        shuffle=False, class_mode='categorical')

    def define_model_vgg(self):
        self.model = VGG16(weights='imagenet', include_top=False)
        opt = SGD(lr=0.01, momentum=0.9)
        self.model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])

    def define_model_2(self):
        # Build neural network
        model = Sequential()

        model.add(Conv2D(32, 3, 3, activation='relu', input_shape=(self.size, self.size, 1)))
        model.add(Conv2D(32, 3, 3, activation='relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Dropout(0.25))

        model.add(Flatten())
        model.add(Dense(128, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(4, activation='softmax'))

        opt = SGD(lr=0.01, momentum=0.9)
        model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])

        self.model = model

    def define_model(self):
        model = Sequential()
        model.add(Conv2D(32, (3, 3), activation='relu', kernel_initializer='he_uniform',
                         input_shape=(self.size, self.size, 3)))
        # model.add(Conv2D(32, (3, 3), activation='relu', kernel_initializer='he_uniform', input_shape=(28, 28, 1)))

        model.add(MaxPooling2D((2, 2)))
        model.add(Flatten())
        model.add(Dense(100, activation='relu', kernel_initializer='he_uniform'))
        model.add(Dense(4, activation='softmax'))

        # compile model
        opt = SGD(lr=0.01, momentum=0.9)
        model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])

        self.model = model

    def train(self):
        """
        Train the model
        """
        start_time = time.time()

        # For steps for epoch when using fit_generator: https://datascience.stackexchange.com/questions/47405/what-to-set-in-steps-per-epoch-in-keras-fit-generator
        # basically want it = num_samples / batch_size.  400,000 / 32 ~= 10000, which seems too big
        step_size = self.train_it.n // self.train_it.batch_size
        print("Step size should be: {}".format(step_size))
        self.model.fit_generator(self.train_it, steps_per_epoch=1000, epochs=20)  # , verbose=0)
        print("Train time: {}".format(time.time() - start_time))
        # Store model
        self.model.save('final_model.h5')

    def eval(self):
        model = load_model('final_model.h5')

        # Eval
        start_time = time.time()

        step_size = self.test_it.n // self.test_it.batch_size
        score = model.evaluate_generator(self.test_it, steps=step_size)
        print("Eval time: {}".format(time.time() - start_time))
        print("Score: {}".format(score))

        y_pred = model.predict_generator(self.test_it, steps=step_size)
        classes = self.test_it.classes
        y_pred = np.argmax(y_pred, axis=1)
        print('Confusion Matrix')
        print(confusion_matrix(classes, y_pred))
        print('Classification Report')
        target_names = ['Cone', 'Cube', 'occluder', 'Sphere']
        print(classification_report(classes, y_pred, target_names=target_names))


if __name__ == "__main__":
    dc = Occluder()
    dc.read_in_data()
    # dc.define_model()
    # dc.define_model_2()
    dc.define_model_vgg()
    dc.train()

    dc.read_in_test()
    dc.eval()
