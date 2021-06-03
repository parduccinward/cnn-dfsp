import streamlit as st
from img_classification import teachable_machine_classification
import keras
from PIL import Image, ImageOps
import numpy as np
st.title("Sistema de Diagnóstico asistido por ordenador")
st.header("Clasificación de cáncer de piel mediante CNN")
st.text("Por favor introduce una imagen de una lesión cutánea que pueda sospechar DFSP, carcinoma o melanoma:")

uploaded_file = st.file_uploader("Escoge una lesión cutánea ...", type="jpg")
if uploaded_file is not None:
  image = Image.open(uploaded_file)
  st.image(image, caption='Imagen subida exitosamente.', use_column_width=True)
  st.write("")
  st.write("Clasificando...")
  label = teachable_machine_classification(image, 'train/model.h5') # Name of the model from Teachablemachine
  if label == 0:
    st.write("The MRI scan has a brain tumor")
  else:
    st.write("The MRI scan is healthy")
