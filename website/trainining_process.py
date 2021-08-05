import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import pandas as pd
import os
from glob import glob
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, KFold, cross_val_score, GridSearchCV
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
import tensorflow as tf
from tensorflow import keras
from keras.utils.np_utils import to_categorical
from keras.models import Sequential, Model
from keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D, Activation
from keras import backend as K
from keras.layers.normalization import BatchNormalization
from keras.utils.np_utils import to_categorical
from keras.preprocessing.image import ImageDataGenerator
from keras.callbacks import ReduceLROnPlateau
from keras.wrappers.scikit_learn import KerasClassifier
from keras_tuner.tuners import RandomSearch
from keras_tuner.engine.hyperparameters import HyperParameters
import time


LOG_DIR = f"./train/training_results/{int(time.time())}/"
range_values = []
X_train = np.load(
    r'C:\Users\pardu\OneDrive\Desktop\cnn-dfsp\dataset\X_train.npy')
y_train = np.load(
    r'C:\Users\pardu\OneDrive\Desktop\cnn-dfsp\dataset\y_train.npy')
X_test = np.load(
    r'C:\Users\pardu\OneDrive\Desktop\cnn-dfsp\dataset\X_test.npy')
y_test = np.load(
    r'C:\Users\pardu\OneDrive\Desktop\cnn-dfsp\dataset\y_test.npy')
X_validation = np.load(
    r'C:\Users\pardu\OneDrive\Desktop\cnn-dfsp\dataset\X_validation.npy')
y_validation = np.load(
    r'C:\Users\pardu\OneDrive\Desktop\cnn-dfsp\dataset\y_validation.npy')

# One hot encoder
y_train = to_categorical(y_train, num_classes=4)
y_test = to_categorical(y_test, num_classes=4)
y_validation = to_categorical(y_validation, num_classes=4)

# Normalizar
X_train = X_train/255.
X_test = X_test/255.

# Aumentar algunas imagenes mas
datagen = ImageDataGenerator(
    featurewise_center=False,
    samplewise_center=False,
    featurewise_std_normalization=False,
    samplewise_std_normalization=False,
    zca_whitening=False,
    rotation_range=30,
    zoom_range=0.1,
    width_shift_range=0.1,
    height_shift_range=0.1,
    horizontal_flip=False,
    vertical_flip=False)
datagen.fit(X_train)

learning_rate_reduction = ReduceLROnPlateau(monitor='accuracy',
                                            patience=3,
                                            verbose=1,
                                            factor=0.5,
                                            min_lr=1e-7)


def build_model(hp):
    val = range_values
    model = keras.models.Sequential()
    model.add(Conv2D(hp.Int("conv1_units", val[0], val[1], step=32), kernel_size=(
        3, 3), input_shape=X_train.shape[1:], kernel_initializer='glorot_uniform'))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(
        Dropout(hp.Float("dropout1_units", val[2], val[3], step=0.05)))

    model.add(Conv2D(hp.Int("conv2_units", val[4], val[5], step=32), kernel_size=(3, 3),
                     kernel_initializer='glorot_uniform'))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(hp.Float("dropout2_units",
              val[6], val[7], step=0.05)))

    model.add(Flatten())
    model.add(Dense(128, activation='relu', kernel_initializer='normal'))
    model.add(Dense(4, activation='softmax'))
    hp_learning_rate = hp.Choice('learning_rate', values=[1e-4, 1e-5, 1e-6])
    opt = keras.optimizers.Adam(learning_rate=hp_learning_rate)
    model.compile(optimizer=opt,
                  loss="binary_crossentropy", metrics=["accuracy"])
    return model


def tuners(b, e, c):
    tuner = RandomSearch(
        build_model,
        objective="val_accuracy",
        max_trials=c,
        directory=LOG_DIR
    )

    tuner.search(x=X_train, y=y_train, epochs=e, batch_size=b,
                 validation_data=(X_validation, y_validation))
    #best_models = tuner.get_best_models()[0]
    # return best_models


def train_models(f1_min, f1_max, d1_min, d1_max, f2_min, f2_max, d2_min, d2_max, batch, epoch, combinations):
    global range_values
    range_values = [f1_min, f1_max, d1_min,
                    d1_max, f2_min, f2_max, d2_min, d2_max]
    search = tuners(b=batch, e=epoch, c=combinations)
    return search


# Eliminar despues
# models_list = train_models(f1_min=64, f1_max=192, d1_min=0.10, d1_max=0.30, f2_min=64,
#                           f2_max=224, d2_min=0.10, d2_max=0.30, batch=10, epoch=1, combinations=1)
# print(models_list)
