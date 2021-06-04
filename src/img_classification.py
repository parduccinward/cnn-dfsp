import tensorflow.keras
from PIL import Image, ImageOps
import numpy as np


def teachable_machine_classification(img, weights_file):
    # Cargar el modelo
    model = tensorflow.keras.models.load_model(weights_file)

    # crear una matriz del tamaño exacto para ser alimentado por el modelo keras
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    image = img
    # cambiando el tamaño de la imagen
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.ANTIALIAS)

    # convirtiendo la imagen en un numpy array
    image_array = np.asarray(image)
    # normalizando la imagen
    normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1

    # Cargando la imagen en una matriz (paso que puede omitirse)
    data[0] = normalized_image_array

    # correr con el modelo
    prediction = model.predict(data)
    return (prediction)
