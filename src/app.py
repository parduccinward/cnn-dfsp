from pyngrok import ngrok
import streamlit as st
import tensorflow as tf
from img_classification import teachable_machine_classification
import keras
from PIL import Image, ImageOps
import numpy as np
st.title("Sistema de Diagnóstico asistido por ordenador")
st.header("Clasificación de cáncer de piel mediante CNN")
st.text("Por favor introduce una imagen de una lesión cutánea que pueda sospechar DFSP, carcinoma o melanoma:")


@st.cache(allow_output_mutation=True)
def load_model():
    model = tf.keras.models.load_model('model/model.h5')
    return model


with st.spinner('Model is being loaded..'):
    model = load_model()

uploaded_file = st.file_uploader("Escoge una lesión cutánea ...", type="jpg")
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Imagen subida exitosamente.',
             use_column_width=True)
    st.write("")
    st.write("Clasificando...")
    # Name of the model from Teachablemachine
    label = teachable_machine_classification(image, model)
    if label == 0:
        st.write("The MRI scan has a brain tumor")
    else:
        st.write("The MRI scan is healthy")


public_url = ngrok.connect(port='8501')
print('Link to web app:')
print(public_url)
