import boto3
import tensorflow as tf
import numpy as np
import io
import matplotlib.image as mpimg
import pandas as pd

config = tf.compat.v1.ConfigProto()
config.gpu_options.allow_growth = True
sess = tf.compat.v1.Session(config=config)
s3 = boto3.resource('s3', region_name='us-east-2')
bucket = s3.Bucket('dfsp-lesiones-piel')
allFiles = bucket.objects.all()
X_data = []
# Cargado de Datos del S3 de Imagenes correspondientes a Entrenamiento
for object in allFiles:
    if ".jpg" in object.key and "benigna/train/" in object.key and not "validation" in object.key:
        file_stream = io.BytesIO()
        object.Object().download_fileobj(file_stream)
        img = mpimg.imread(file_stream, format="jpg")
        X_data.append(img)  # AGREGAR A UN VECTOR
X_benigna_train = np.array(X_data)  # TODAS LAS IMAGENES EN UN NUMPY ARRAY
print(X_benigna_train.shape)
X_data = []
for object in allFiles:
    if ".jpg" in object.key and "carcinoma/train/" in object.key and not "validation" in object.key:
        file_stream = io.BytesIO()
        object.Object().download_fileobj(file_stream)
        img = mpimg.imread(file_stream, format="jpg")
        X_data.append(img)  # AGREGAR A UN VECTOR
X_carcinoma_train = np.array(X_data)  # TODAS LAS IMAGENES EN UN NUMPY ARRAY
print(X_carcinoma_train.shape)
X_data = []
for object in allFiles:
    if ".jpg" in object.key and "dfsp/train/" in object.key and not "validation" in object.key:
        file_stream = io.BytesIO()
        object.Object().download_fileobj(file_stream)
        img = mpimg.imread(file_stream, format="jpg")
        X_data.append(img)  # AGREGAR A UN VECTOR
X_dfsp_train = np.array(X_data)  # TODAS LAS IMAGENES EN UN NUMPY ARRAY
print(X_dfsp_train.shape)
X_data = []
for object in allFiles:
    if ".jpg" in object.key and "melanoma/train/" in object.key and not "validation" in object.key:
        file_stream = io.BytesIO()
        object.Object().download_fileobj(file_stream)
        img = mpimg.imread(file_stream, format="jpg")
        X_data.append(img)  # AGREGAR A UN VECTOR
X_melanoma_train = np.array(X_data)  # TODAS LAS IMAGENES EN UN NUMPY ARRAY
print(X_melanoma_train.shape)

X_data = []
# Cargado de Datos del S3 de Imagenes correspondientes a Pruebas
for object in allFiles:
    if ".jpg" in object.key and "benigna/test/" in object.key and not "validation" in object.key:
        file_stream = io.BytesIO()
        object.Object().download_fileobj(file_stream)
        img = mpimg.imread(file_stream, format="jpg")
        X_data.append(img)  # AGREGAR A UN VECTOR
X_benigna_test = np.array(X_data)  # TODAS LAS IMAGENES EN UN NUMPY ARRAY
print(X_benigna_test.shape)
X_data = []
for object in allFiles:
    if ".jpg" in object.key and "carcinoma/test/" in object.key and not "validation" in object.key:
        file_stream = io.BytesIO()
        object.Object().download_fileobj(file_stream)
        img = mpimg.imread(file_stream, format="jpg")
        X_data.append(img)  # AGREGAR A UN VECTOR
X_carcinoma_test = np.array(X_data)  # TODAS LAS IMAGENES EN UN NUMPY ARRAY
print(X_carcinoma_test.shape)
X_data = []
for object in allFiles:
    if ".jpg" in object.key and "dfsp/test/" in object.key and not "validation" in object.key:
        file_stream = io.BytesIO()
        object.Object().download_fileobj(file_stream)
        img = mpimg.imread(file_stream, format="jpg")
        X_data.append(img)  # AGREGAR A UN VECTOR
X_dfsp_test = np.array(X_data)  # TODAS LAS IMAGENES EN UN NUMPY ARRAY
print(X_dfsp_test.shape)
X_data = []
for object in allFiles:
    if ".jpg" in object.key and "melanoma/test/" in object.key and not "validation" in object.key:
        file_stream = io.BytesIO()
        object.Object().download_fileobj(file_stream)
        img = mpimg.imread(file_stream, format="jpg")
        X_data.append(img)  # AGREGAR A UN VECTOR
X_melanoma_test = np.array(X_data)  # TODAS LAS IMAGENES EN UN NUMPY ARRAY
print(X_melanoma_test.shape)

X_data = []
# Cargado de Datos del S3 de Imagenes correspondientes a Validacion
for object in allFiles:
    if ".jpg" in object.key and "benigna/validation/" in object.key:
        file_stream = io.BytesIO()
        object.Object().download_fileobj(file_stream)
        img = mpimg.imread(file_stream, format="jpg")
        X_data.append(img)  # AGREGAR A UN VECTOR
X_benigna_validation = np.array(X_data)  # TODAS LAS IMAGENES EN UN NUMPY ARRAY
print(X_benigna_validation.shape)
X_data = []
for object in allFiles:
    if ".jpg" in object.key and "carcinoma/validation/" in object.key:
        file_stream = io.BytesIO()
        object.Object().download_fileobj(file_stream)
        img = mpimg.imread(file_stream, format="jpg")
        X_data.append(img)  # AGREGAR A UN VECTOR
# TODAS LAS IMAGENES EN UN NUMPY ARRAY
X_carcinoma_validation = np.array(X_data)
print(X_carcinoma_validation.shape)
X_data = []
for object in allFiles:
    if ".jpg" in object.key and "dfsp/validation/" in object.key:
        file_stream = io.BytesIO()
        object.Object().download_fileobj(file_stream)
        img = mpimg.imread(file_stream, format="jpg")
        X_data.append(img)  # AGREGAR A UN VECTOR
X_dfsp_validation = np.array(X_data)  # TODAS LAS IMAGENES EN UN NUMPY ARRAY
print(X_dfsp_validation.shape)
X_data = []
for object in allFiles:
    if ".jpg" in object.key and "melanoma/validation/" in object.key:
        file_stream = io.BytesIO()
        object.Object().download_fileobj(file_stream)
        img = mpimg.imread(file_stream, format="jpg")
        X_data.append(img)  # AGREGAR A UN VECTOR
# TODAS LAS IMAGENES EN UN NUMPY ARRAY
X_melanoma_validation = np.array(X_data)
print(X_melanoma_validation.shape)

# Creacion de etiquetas para cada clase
y_benigna_train = np.zeros(X_benigna_train.shape[0])
print(y_benigna_train)
y_carcinoma_train = np.ones(X_carcinoma_train.shape[0])
print(y_carcinoma_train)
y_dfsp_train = np.full(X_dfsp_train.shape[0], 2, dtype=np.float64)
print(y_dfsp_train)
y_melanoma_train = np.full(X_melanoma_train.shape[0], 3, dtype=np.float64)
print(y_melanoma_train)

y_benigna_test = np.zeros(X_benigna_test.shape[0])
print(y_benigna_test)
y_carcinoma_test = np.ones(X_carcinoma_test.shape[0])
print(y_carcinoma_test)
y_dfsp_test = np.full(X_dfsp_test.shape[0], 2, dtype=np.float64)
print(y_dfsp_test)
y_melanoma_test = np.full(X_melanoma_test.shape[0], 3, dtype=np.float64)
print(y_melanoma_test)

y_benigna_validation = np.zeros(X_benigna_validation.shape[0])
print(y_benigna_validation)
y_carcinoma_validation = np.ones(X_carcinoma_validation.shape[0])
print(y_carcinoma_validation)
y_dfsp_validation = np.full(X_dfsp_validation.shape[0], 2, dtype=np.float64)
print(y_dfsp_validation)
y_melanoma_validation = np.full(
    X_melanoma_validation.shape[0], 3, dtype=np.float64)
print(y_melanoma_validation)

# Creacion de etiquetas para cada clase
y_benigna_train = np.zeros(X_benigna_train.shape[0])
print(y_benigna_train)
y_carcinoma_train = np.ones(X_carcinoma_train.shape[0])
print(y_carcinoma_train)
y_dfsp_train = np.full(X_dfsp_train.shape[0], 2, dtype=np.float64)
print(y_dfsp_train)
y_melanoma_train = np.full(X_melanoma_train.shape[0], 3, dtype=np.float64)
print(y_melanoma_train)

y_benigna_test = np.zeros(X_benigna_test.shape[0])
print(y_benigna_test)
y_carcinoma_test = np.ones(X_carcinoma_test.shape[0])
print(y_carcinoma_test)
y_dfsp_test = np.full(X_dfsp_test.shape[0], 2, dtype=np.float64)
print(y_dfsp_test)
y_melanoma_test = np.full(X_melanoma_test.shape[0], 3, dtype=np.float64)
print(y_melanoma_test)

y_benigna_validation = np.zeros(X_benigna_validation.shape[0])
print(y_benigna_validation)
y_carcinoma_validation = np.ones(X_carcinoma_validation.shape[0])
print(y_carcinoma_validation)
y_dfsp_validation = np.full(X_dfsp_validation.shape[0], 2, dtype=np.float64)
print(y_dfsp_validation)
y_melanoma_validation = np.full(
    X_melanoma_validation.shape[0], 3, dtype=np.float64)
print(y_melanoma_validation)

# Juntar Clases y dividir en Entrenamiento, Pruebas y Validacion
X_train = np.concatenate(
    (X_benigna_train, X_carcinoma_train, X_dfsp_train, X_melanoma_train), axis=0)
print(X_train.shape)
y_train = np.concatenate(
    (y_benigna_train, y_carcinoma_train, y_dfsp_train, y_melanoma_train), axis=0)
print(y_train)

X_test = np.concatenate(
    (X_benigna_test, X_carcinoma_test, X_dfsp_test, X_melanoma_test), axis=0)
print(X_test.shape)
y_test = np.concatenate(
    (y_benigna_test, y_carcinoma_test, y_dfsp_test, y_melanoma_test), axis=0)
print(y_test)

X_validation = np.concatenate(
    (X_benigna_validation, X_carcinoma_validation, X_dfsp_validation, X_melanoma_validation), axis=0)
print(X_validation.shape)
y_validation = np.concatenate(
    (y_benigna_validation, y_carcinoma_validation, y_dfsp_validation, y_melanoma_validation), axis=0)
print(y_validation)

# Mezclar datos entre Clases
s = np.arange(X_train.shape[0])
np.random.shuffle(s)
X_train = X_train[s]
print(X_train)
y_train = y_train[s]
print(y_train)

s = np.arange(X_test.shape[0])
np.random.shuffle(s)
X_test = X_test[s]
print(X_test)
y_test = y_test[s]
print(y_test)

s = np.arange(X_validation.shape[0])
np.random.shuffle(s)
X_validation = X_validation[s]
print(X_test)
y_validation = y_validation[s]
print(y_test)

np.save('./dataset/X_train', X_train)
np.save('./dataset/y_train', y_train)
np.save('./dataset/X_test', X_test)
np.save('./dataset/y_test', y_test)
np.save('./dataset/X_validation', X_validation)
np.save('./dataset/y_validation', y_validation)
