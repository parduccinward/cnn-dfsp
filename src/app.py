from pyngrok import ngrok
import streamlit as st
import tensorflow as tf
from img_classification import teachable_machine_classification
import keras
from PIL import Image, ImageOps
import numpy as np

st.title("Sistema de Diagnóstico asistido por ordenador 🩺🏥")
st.header("Clasificación de cáncer de piel mediante CNN")
st.subheader(
    "Las enfermedades que el sistema puede reconocer son BCC, DFSP y Melanoma. Además, puede reconocer tumores benignos del tipo Dermatofibroma.")
st.subheader(
    "Los resultados proporcionados por esta herramienta sirven para apoyarse en el proceso diagnóstico. De todas formas es preciso siempre confirmarlo con médicos especializados.")
# open_image = Image.open('./assets/images/yelllow_ribbon.jpg')
# st.image(open_image)
st.subheader(
    "Recomendaciones para la utilización del sistema:")
st.text("-Trata de que la imagen se vea lo más nítida posible.")
st.text("-Que la imagen sea tomada de frente y de cerca.")
st.text("-Intenta de que la lesión cutánea se encuentre en el medio de la imagen.")


@st.cache(allow_output_mutation=True)
def load_model():
    model = tf.keras.models.load_model("./model/model.h5")
    return model


with st.spinner('El modelo esta siendo cargado..'):
    model = load_model()

uploaded_file = st.file_uploader(
    "Escoge una imágen jpg o png ...", type={"png", "jpg", "jpeg"})
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, width=500, caption='Imagen subida exitosamente.',
             use_column_width=True)
    st.write("")
    prediction = teachable_machine_classification(image, "./model/model.h5")
    # score = tf.nn.softmax(predictions[0]) si no funca
    label = np.argmax(prediction)
    percentage = 100 * np.max(prediction)
    if label == 0:
        st.subheader(
            "La imagen es más probable que pertenezca a un Tumor benigno, con una probabilidad del " + str("%.2f" % percentage)+"%")
        st.header("Dermatofibroma (Tumor benigno)")
        st.write("")
        st.write("El dermatofibroma es un tumor benigno, muy frecuente, que suele aparecer en extremidades, generalmente en las piernas. Tiene una forma redondeada u ovalada, generalmente es de color marrón, y algunos tienen una zona blanquecina central.")
        st.subheader("Tratamiento")
        st.write("Dado que es una lesión benigna no precisa tratamiento salvo que produzca molestias o por motivos estéticos. El tratamiento de elección, cuando es necesario, es la extirpación mediante cirugía.")

    if label == 1:
        st.subheader("La imagen es más probable que pertenezca a un Carcinoma de celulas basales, con una probabilidad del " +
                     str("%.2f" % percentage)+"%")
        st.header("Carcinoma de celulas basales (BCC)")
        st.subheader(
            "Se sugiere confirmar el diagnóstico con una prueba histopatológica.")
        st.write("")
        st.write("El carcinoma de células basales (también referido como cáncer de piel de células basales) es el tipo más común de cáncer de piel. Alrededor de 8 de cada 10 casos de cáncer de piel son carcinomas de células basales (también llamados cánceres de células basales).")
        st.write("Estos cánceres comienzan en la capa celular basal, que es la parte inferior de la epidermis. Por lo general, estos cánceres surgen en las zonas expuestas al sol, especialmente la cara, la cabeza y el cuello. Estos cánceres suelen crecer lentamente. Es muy poco común que el cáncer de células basales se propague a otras partes del cuerpo. Pero de no tratarse, el cáncer de células basales puede extenderse hacia las áreas cercanas e invadir el hueso u otros tejidos debajo de la piel.")
        st.write("El carcinoma de células basales puede reaparecer (recurrir) en el mismo lugar de la piel, si no se extrae completamente. Las personas que han tenido cánceres de piel de células basales también tienen una probabilidad mayor de padecer nuevos cánceres en otros lugares..")
        st.subheader("Tratamiento")
        st.write("El carcinoma de células basales se trata con mayor frecuencia con cirugía para extirpar todo el cáncer y parte del tejido sano que lo rodea. Las opciones pueden ser las siguientes:")
        st.subheader("Escisión quirúrgica")
        st.write("En este procedimiento, el médico corta la lesión cancerosa y un margen de piel sana que la rodea. El margen se examina en el microscopio para asegurarse de que no haya células cancerosas. Se podría recomendar la escisión para los carcinomas de células basales que tienen menos probabilidad de reaparecer, como los que se forman en el pecho, la espalda, las manos y los pies.")
        st.subheader("Cirugía de Mohs")
        st.write("Durante la cirugía de Mohs, el médico retira el cáncer capa por capa y examina cada capa bajo el microscopio hasta que no queden células anormales. Esto permite que el cirujano se asegure de retirar todo el crecimiento y evite tomar mucha cantidad de piel sana alrededor de él. La cirugía de Mohs podría recomendarse si tu carcinoma de células basales tiene un riesgo más alto de recurrencia, por ejemplo, si es más grande, se extiende más profundamente en la piel o lo tienes en la cara.")
    if label == 2:
        st.subheader(
            "La imagen es más probable que pertenezca a un DFSP, con una probabilidad del " + str("%.2f" % percentage)+"%")
        st.header("Dermatofibrosarcoma protuberans (DFSP)")
        st.subheader(
            "Se sugiere confirmar el diagnóstico con una prueba histopatológica.")
        st.write("")
        st.write("El dermatofibrosarcoma protuberans (DFSP) es un tipo muy raro de cáncer de piel que comienza en las células del tejido conectivo en la capa media de la piel (dermis).")
        st.write("El DFSP puede aparecer al principio como un hematoma o una cicatriz. A medida que crece, se pueden formar grumos de tejido (protuberanos) cerca de la superficie de la piel. Este cáncer de piel a menudo se forma en brazos, piernas y tronco.")
        st.write(
            "El DFSP crece lentamente y rara vez se disemina más allá de la piel.")
        st.subheader("Tratamiento")
        st.write("El tratamiento del dermatofibrosarcoma protuberans generalmente implica una cirugía para extirpar el cáncer. Se pueden usar otros tratamientos para destruir las células cancerosas que puedan quedar después de la cirugía. Las opciones de tratamiento pueden incluir:")
        st.subheader("Escisión quirúrgica")
        st.write("Para la mayoría de los cánceres, su médico puede recomendar un procedimiento para extirpar el cáncer y parte del tejido sano que lo rodea (cirugía de escisión con un margen normal de tejido). Esto hace que sea más probable que se extraigan todas las células cancerosas durante la cirugía.")
        st.subheader("Cirugía de Mohs")
        st.write("La cirugía de Mohs es un tipo de cirugía especializada que implica la eliminación progresiva de capas delgadas de piel que contiene cáncer hasta que solo quede tejido libre de cáncer. Después de que se quita cada capa de piel, se examina en busca de signos de cáncer. El proceso continúa hasta que no hay signos de cáncer.")
        st.subheader("Radioterapia")
        st.write("La radioterapia utiliza potentes rayos de energía, como rayos X y protones, para destruir las células cancerosas. Se  puede recomendar radioterapia si no se pudo extirpar todo el cáncer durante la cirugía.")
    if label == 3:
        st.subheader(
            "La imagen es más probable que pertenezca a un Melanoma, con una probabilidad del " + str("%.2f" % percentage)+"%")
        st.header("Melanoma")
        st.subheader(
            "Se sugiere confirmar el diagnóstico con una prueba histopatológica.")
        st.write("")
        st.write("El melanoma, el tipo más grave de cáncer de piel, se desarrolla en las células (melanocitos) que producen melanina, el pigmento que da color a la piel. El melanoma también se puede formar en los ojos y, en raras ocasiones, en el interior del cuerpo, como en la nariz o la garganta  .")
        st.write("La causa exacta de todos los melanomas no está clara, pero la exposición a la radiación ultravioleta (UV) de la luz solar o las lámparas y camas de bronceado aumenta el riesgo de desarrollar melanoma. Limitar su exposición a la radiación ultravioleta puede ayudar a reducir su riesgo de melanoma.")
        st.write(
            "El riesgo de melanoma parece estar aumentando en personas menores de 40 años, especialmente en mujeres. Conocer las señales de advertencia del cáncer de piel puede ayudar a garantizar que los cambios cancerosos se detecten y se traten antes de que el cáncer se haya propagado. El melanoma se puede tratar con éxito si se detecta a tiempo..")
        st.subheader("Tratamiento")
        st.write("El tratamiento de los melanomas en etapa temprana generalmente incluye cirugía para extirpar el melanoma. Un melanoma muy delgado se puede extirpar por completo durante la biopsia y no requiere tratamiento adicional. De lo contrario, su cirujano extirpará el cáncer, así como un borde de piel normal y una capa de tejido debajo de la piel. Para las personas con melanomas en etapa temprana, este puede ser el único tratamiento necesario.")
        st.header("Melanomas que se han extendido más allá de la piel")
        st.write(
            "Si el melanoma se ha extendido más allá de la piel, las opciones de tratamiento pueden incluir:")
        st.subheader("Cirugía para extirpar los ganglios linfáticos afectados")
        st.write("Si el melanoma se ha diseminado a los ganglios linfáticos cercanos, su cirujano puede extirpar los ganglios afectados. También se pueden recomendar tratamientos adicionales antes o después de la cirugía.")
        st.subheader("Inmunoterapia")
        st.write("La inmunoterapia es un tratamiento con medicamentos que ayuda a su sistema inmunológico a combatir el cáncer. Es posible que el sistema inmunológico de su cuerpo que combate las enfermedades no ataque al cáncer porque las células cancerosas producen proteínas que las ayudan a esconderse de las células del sistema inmunológico. La inmunoterapia actúa interfiriendo con ese proceso.")
        st.subheader("Terapia dirigida")
        st.write("Los tratamientos con medicamentos dirigidos se centran en debilidades específicas presentes en las células cancerosas. Al atacar estas debilidades, los tratamientos farmacológicos dirigidos pueden provocar la muerte de las células cancerosas. Es posible que se analicen las células de su melanoma para ver si es probable que la terapia dirigida sea eficaz contra su cáncer.")
        st.subheader("Radioterapia")
        st.write("Este tratamiento utiliza rayos de energía de alta potencia, como rayos X y protones, para destruir las células cancerosas. La radioterapia puede dirigirse a los ganglios linfáticos si el melanoma se ha diseminado allí. La radioterapia también se puede usar para tratar melanomas que no se pueden extirpar por completo con cirugía.")
        st.subheader("Quimioterapia")
        st.write("La quimioterapia usa medicamentos para destruir las células cancerosas. La quimioterapia se puede administrar por vía intravenosa, en forma de píldora o en ambas para que viaje por todo el cuerpo.")
