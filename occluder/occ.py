#
#  Training for occluders
#
#
# from numpy import mean
# from numpy import std
# from matplotlib import pyplot
# from sklearn.model_selection import KFold
# # from keras.datasets import mnist
# from keras.utils import to_categorical
# from keras.models import Sequential
# from keras.layers import Conv2D
# from keras.layers import MaxPooling2D
# from keras.layers import Dense
# from keras.layers import Flatten
# from keras.optimizers import SGD

import argparse
import json
import os
import shutil
from PIL import Image
from pathlib import Path
import random


class OccluderDataCreator:

    def __init__(self):
        random.seed(23954)
        self.dataDir = Path("/mnt/ssd/cdorman/data/mcs/intphys/train/")

    def make_data(self):
        # Read all the intphys train directories
        self.get_dirs()

        # there should be 3750 directories.  Get most of them for train, the rest for test
        random.shuffle(self.dirs)
        dividing_line = len(self.dirs) * 3 // 4
        print("Splitting {} training dirs into : {} {}".format(len(self.dirs), dividing_line,
                                                               len(self.dirs) - dividing_line))
        traindirs = self.dirs[:dividing_line]
        testdirs = self.dirs[dividing_line:]

        # for subdir in traindirs:
        #     self.get_data_from_dir("train", subdir)
        self.get_data_from_dir(Path("train"), traindirs[0])

    def get_data_from_dir(self, dest_dir, in_path):
        """ Passed a directory name, read the status.json and get images"""
        status = self.read_json(in_path)

        # Go through status, get all the images
        for frame_index in range(0, 100):
            frame_num = frame_index + 1
            frame_json = status["frames"][frame_index]
            # print("masks {}".format(frame_json["masks"]))
            mask_json = frame_json["masks"]
            for obj_name in mask_json.keys():
                mask_color = mask_json[obj_name]
                obj_type = "unknown"
                if obj_name in ("floor", "walls", "sky"):
                    obj_type = obj_name
                elif obj_name.startswith("occluder"):
                    obj_type = "occluder"
                else:
                    obj_type = frame_json[obj_name]["shape"]
                self.get_image_for_object(dest_dir, in_path, frame_num, obj_type, mask_color)

    def get_image_for_object(self, out_path, in_path, frame_num, obj_type, mask_color):
        frame_num_with_leading_zeros = str(frame_num).zfill(3)
        scene_filename = in_path / "scene" / ("scene_" + frame_num_with_leading_zeros + ".png")
        out_dir_path = out_path / obj_type
        print("filename {} {} {} {} goes to {}".format(frame_num, obj_type, mask_color, str(scene_filename),
                                                       out_dir_path))

    def read_json(self, dirpath):
        status_path = dirpath / "status.json"
        # print(" Opening {}".format(status_path))
        with status_path.open() as file:
            status_json = json.load(file)
        return status_json

    def readImage(self):
        pass

    def get_dirs(self):
        if not os.path.exists(self.dataDir):
            print("Dir: {} does not exist. exiting".format(str(self.dataDir)))

        self.dirs = [Path(self.dataDir / d) for d in os.listdir(self.dataDir)]
        self.dirs.sort()
        print("Num dirs: {}".format(len(self.dirs)))


if __name__ == "__main__":
    dc = OccluderDataCreator()
    dc.make_data()

#
#
# # load train and test dataset
# def load_dataset():
#     (trainX, trainY), (testX, testY) = mnist.load_data()
#     # reshape dataset to have a single channel
#     trainX = trainX.reshape((trainX.shape[0], 28, 28, 1))
#     testX = testX.reshape((testX.shape[0], 28, 28, 1))
#     # one hot encode target values
#     trainY = to_categorical(trainY)
#     testY = to_categorical(testY)
#     return trainX, trainY, testX, testY
#
#
# # scale pixels
# def prep_pixels(train, test):
#     # convert from integers to floats
#     train_norm = train.astype('float32')
#     test_norm = test.astype('float32')
#     # normalize to range 0-1
#     train_norm = train_norm / 255.0
#     test_norm = test_norm / 255.0
#     # return normalized images
#     return train_norm, test_norm
#
#
# # define cnn model
# def define_model():
#     model = Sequential()
#     model.add(Conv2D(32, (3, 3), activation='relu', kernel_initializer='he_uniform', input_shape=(28, 28, 1)))
#     model.add(MaxPooling2D((2, 2)))
#     model.add(Flatten())
#     model.add(Dense(100, activation='relu', kernel_initializer='he_uniform'))
#     model.add(Dense(10, activation='softmax'))
#     # compile model
#     opt = SGD(lr=0.01, momentum=0.9)
#     model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])
#     return model
#
#
# # evaluate a model using k-fold cross-validation
# def evaluate_model(model, dataX, dataY, n_folds=5):
#     scores, histories = list(), list()
#     # prepare cross validation
#     kfold = KFold(n_folds, shuffle=True, random_state=1)
#     # enumerate splits
#     for train_ix, test_ix in kfold.split(dataX):
#         # select rows for train and test
#         trainX, trainY, testX, testY = dataX[train_ix], dataY[train_ix], dataX[test_ix], dataY[test_ix]
#         # fit model
#         history = model.fit(trainX, trainY, epochs=10, batch_size=32, validation_data=(testX, testY), verbose=0)
#         # evaluate model
#         _, acc = model.evaluate(testX, testY, verbose=0)
#         print('> %.3f' % (acc * 100.0))
#         # stores scores
#         scores.append(acc)
#         histories.append(history)
#     return scores, histories
#
#
# # plot diagnostic learning curves
# def summarize_diagnostics(histories):
#     for i in range(len(histories)):
#         # plot loss
#         pyplot.subplot(211)
#         pyplot.title('Cross Entropy Loss')
#         pyplot.plot(histories[i].history['loss'], color='blue', label='train')
#         pyplot.plot(histories[i].history['val_loss'], color='orange', label='test')
#         # plot accuracy
#         pyplot.subplot(212)
#         pyplot.title('Classification Accuracy')
#         pyplot.plot(histories[i].history['acc'], color='blue', label='train')
#         pyplot.plot(histories[i].history['val_acc'], color='orange', label='test')
#     pyplot.show()
#
#
# # summarize model performance
# def summarize_performance(scores):
#     # print summary
#     print('Accuracy: mean=%.3f std=%.3f, n=%d' % (mean(scores) * 100, std(scores) * 100, len(scores)))
#     # box and whisker plots of results
#     pyplot.boxplot(scores)
#     pyplot.show()
#
#
# # run the test harness for evaluating a model
# def run_test_harness():
#     # load dataset
#     trainX, trainY, testX, testY = load_dataset()
#     # prepare pixel data
#     trainX, testX = prep_pixels(trainX, testX)
#     # define model
#     model = define_model()
#     # evaluate model
#     scores, histories = evaluate_model(model, trainX, trainY)
#     # learning curves
#     summarize_diagnostics(histories)
#     # summarize estimated performance
#     summarize_performance(scores)
#
#
# # entry point, run the test harness
# run_test_harness()
