# Skin Cancer Diagnosis System

## Description

This project is an AI system that can recognize rare skin cancer through images, allows you to authenticate as a doctor, and manage diagnoses (CRUD) uploading images to verify if it is a disease or not. The system consumes a previously trained model on <a href="https://aws.amazon.com/">AWS</a>, the backend is built with Flask and uses the <a href="https://www.tensorflow.org/api_docs/python/tf/keras/Model">tf.Keras.Model</a> module to consume this model. The front-end is built with <a href="https://stackoverflow.com/questions/20435653/what-is-vanillajs">VanillaJS</a> and HTML.

## CNN

This project uses 260 images of skin lesions to train a neural network. This code implements the classification of the following diseases:

1. Benign tumours
2. Basal cell carcinoma
3. Dermatofibrosarcoma protuberans
4. Melanoma

![Clasificacion de Lesiones Cutaneas via CNN](/assets/images/CNN_DFSP.png)

## Technologies used:

### Training:

- Python
- Jupyter Notebooks
- Tensorflow
- Keras
- pandas
- numpy
- boto3

### Model Hosting

- AWS S3
- AWS Sagemaker

### Web Development

- Flask
- Python
- HTML-5
