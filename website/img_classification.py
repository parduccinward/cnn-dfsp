import tensorflow.keras
from PIL import Image, ImageOps
import numpy as np
from tensorflow.keras.preprocessing.image import load_img, img_to_array

classes = ['benigno', 'carcinoma', 'dfsp', 'melanoma']


def get_prediction(img, weights_file):
    # Cargar el modelo
    model = tensorflow.keras.models.load_model(weights_file)

    # crear una matriz del tamaño exacto para ser alimentado por el modelo keras
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    image = img
    # cambiando el tamaño de la imagen que sera utilizada
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.ANTIALIAS)

    # Convirtiendo la imagen en un numpy array
    image_array = np.asarray(image)
    # Normalizando la imagen
    normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1

    # Cargando la imagen en una matriz (paso que puede omitirse)
    data[0] = normalized_image_array

    # correr con el modelo
    prediction = model.predict(data)
    return (prediction)


def predict(filename, model):
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    image = Image.open(filename)
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.ANTIALIAS)
    image_array = np.asarray(image)
    normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1
    data[0] = normalized_image_array
    result = model.predict(data)

    dict_result = {}
    for i in range(4):
        dict_result[result[0][i]] = classes[i]

    res = result[0]
    res.sort()
    res = res[::-1]
    prob = res[:3]

    prob_result = []
    class_result = []
    for i in range(3):
        prob_result.append((prob[i]*100).round(2))
        class_result.append(dict_result[prob[i]])

    return class_result, prob_result
