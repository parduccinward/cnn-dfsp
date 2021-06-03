import tensorflowjs as tfjs
import tensorflow as tf

keras_model = tf.keras.models.load_model("./model/model.h5")
tfjs.converters.save_keras_model(keras_model, "./model")
