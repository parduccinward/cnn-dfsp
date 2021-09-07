import os
import uuid
import urllib
from flask import Blueprint, render_template, request, flash
from flask_login import login_user, login_required, current_user
from tensorflow.keras.models import load_model
from datetime import date
from .models import Paciente, Medico, Prediccion, Enfermedad, Diagnostico, medicoPaciente, Usuario
from .auth import requires_roles
from PIL import Image
import numpy as np
from . import db
from .img_classification import get_prediction, predict
from .trainining_process import train_models
from .tasks import training
views = Blueprint('views', __name__)

ALLOWED_EXT = set(['jpg', 'jpeg', 'png'])
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model = load_model(os.path.join('./model/model.h5'))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXT


@views.route('/homeAdm')
@login_required
def homeAdm():
    if Usuario.is_admin(current_user.role):
        return render_template("homeAdm.html", user=current_user)
    else:
        flash('La página ingresada es inexistente o no cuentas con los permisos necesarios.', category="error")
        return render_template("homeMed.html", user=current_user)


@views.route('/homeMed')
@login_required
def homeMed():
    if not Usuario.is_admin(current_user.role):
        return render_template("homeMed.html", user=current_user)
    else:
        flash('La página ingresada es inexistente o no cuentas con los permisos necesarios.', category="error")
        return render_template("homeAdm.html", user=current_user)


@views.route('/admUsuarios')
@login_required
def admUsuarios():
    if Usuario.is_admin(current_user.role):
        return render_template("admUsuarios.html", user=current_user)
    else:
        flash('La página ingresada es inexistente o no cuentas con los permisos necesarios.', category="error")
        return render_template("homeMed.html", user=current_user)


@views.route('/regMedicos')
@login_required
def regMedicos():
    if Usuario.is_admin(current_user.role):
        return render_template("regMedicos.html", user=current_user)
    else:
        flash('La página ingresada es inexistente o no cuentas con los permisos necesarios.', category="error")
        return render_template("homeMed.html", user=current_user)


@views.route('/admSistema')
@login_required
def admSistema():
    if Usuario.is_admin(current_user.role):
        return render_template("admSistema.html", user=current_user)
    else:
        flash('La página ingresada es inexistente o no cuentas con los permisos necesarios.', category="error")
        return render_template("homeMed.html", user=current_user)


@views.route('/pacientes')
@login_required
def pacientes():
    if not Usuario.is_admin(current_user.role):
        all_data = Paciente.query.all()
        return render_template("pacientes.html", user=current_user, pacientes=all_data)
    else:
        flash('La página ingresada es inexistente o no cuentas con los permisos necesarios.', category="error")
        return render_template("homeAdm.html", user=current_user)


@views.route('/diagnostico/<id>/', methods=['GET', 'POST'])
@login_required
def diagnostico(id):
    if not Usuario.is_admin(current_user.role):
        paciente = Paciente.query.get(id)
        return render_template("diagnostico.html", user=current_user, paciente=paciente)
    else:
        flash('La página ingresada es inexistente o no cuentas con los permisos necesarios.', category="error")
        return render_template("homeAdm.html", user=current_user)


@views.route('/prediccion')
@login_required
def prediccion():
    if not Usuario.is_admin(current_user.role):
        return render_template("prediccion.html", user=current_user)
    else:
        flash('La página ingresada es inexistente o no cuentas con los permisos necesarios.', category="error")
        return render_template("homeAdm.html", user=current_user)


@views.route('/diagnosticoPaciente')
@login_required
def diagnostico_paciente():
    if not Usuario.is_admin(current_user.role):
        return render_template("diagnosticoPaciente.html", user=current_user)
    else:
        flash('La página ingresada es inexistente o no cuentas con los permisos necesarios.', category="error")
        return render_template("homeAdm.html", user=current_user)


@views.route('/reporte/<id>/', methods=['GET', 'POST'])
@login_required
def reporte(id):
    if not Usuario.is_admin(current_user.role):
        paciente = Paciente.query.get(id)
        return render_template("reporte.html", user=current_user, paciente=paciente)
    else:
        flash('La página ingresada es inexistente o no cuentas con los permisos necesarios.', category="error")
        return render_template("homeAdm.html", user=current_user)


@views.route('/prediccionDiagnostico/<id>/', methods=['GET', 'POST'])
@login_required
def prediccionDiagnostico(id):
    if not Usuario.is_admin(current_user.role):
        paciente = Paciente.query.get(id)
        return render_template("prediccionDiagnostico.html", user=current_user, paciente=paciente)
    else:
        flash('La página ingresada es inexistente o no cuentas con los permisos necesarios.', category="error")
        return render_template("homeAdm.html", user=current_user)


@views.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    if not Usuario.is_admin(current_user.role):
        if request.method == 'POST':
            nombre = request.form['nombrePaciente']
            apellido = request.form['apellidoPaciente']
            sexo = request.form['sexoPaciente']
            f_nacimiento = request.form['nacimientoPaciente']
            year, month, day = f_nacimiento.split('-')
            fecha_nacimiento = date(int(year), int(month), int(day))
            email = request.form['emailPaciente']
            direccion = request.form['direccionPaciente']
            new_patient = Paciente(nombre=nombre, apellido=apellido, sexo=sexo,
                                   fecha_nacimiento=fecha_nacimiento, email=email, direccion=direccion)
            #new_assignment = medicoPaciente()
            db.session.add(new_patient)
            db.session.commit()
            flash('Paciente creado exitosamente!', category="success")
        return render_template("homeMed.html", user=current_user)
    else:
        flash('La página ingresada es inexistente o no cuentas con los permisos necesarios.', category="error")
        return render_template("homeAdm.html", user=current_user)


@views.route('/update_patient', methods=['GET', 'POST'])
def update_patient():

    if not Usuario.is_admin(current_user.role):
        if request.method == 'POST':
            paciente = Paciente.query.get(request.form.get('id'))

            paciente.nombre = request.form['nombrePaciente']
            paciente.apellido = request.form['apellidoPaciente']
            paciente.sexo = request.form['sexoPaciente']
            f_nacimiento = request.form['nacimientoPaciente']
            year, month, day = f_nacimiento.split('-')
            paciente.fecha_nacimiento = date(int(year), int(month), int(day))
            paciente.email = request.form['emailPaciente']
            paciente.direccion = request.form['direccionPaciente']
            db.session.commit()
            flash('Paciente actualizado!', category="success")
        return render_template("homeMed.html", user=current_user)
    else:
        flash('La página ingresada es inexistente o no cuentas con los permisos necesarios.', category="error")
        return render_template("homeAdm.html", user=current_user)


@views.route('/delete_patient/<id>/', methods=['GET', 'POST'])
def delete_patient(id):
    if not Usuario.is_admin(current_user.role):
        my_data = Paciente.query.get(id)
        db.session.delete(my_data)
        db.session.commit()
        flash('Paciente actualizado!', category="success")
        return render_template("homeMed.html", user=current_user)
    else:
        flash('La página ingresada es inexistente o no cuentas con los permisos necesarios.', category="error")
        return render_template("homeAdm.html", user=current_user)


@views.route('/loading', methods=['GET', 'POST'])
@login_required
def loading():
    if Usuario.is_admin(current_user.role):
        if request.method == 'POST':
            f1_min = int(request.form.get('f1_min'))
            f1_max = int(request.form.get('f1_max'))
            d1_min = float(request.form.get('d1_min'))
            d1_max = float(request.form.get('d1_max'))
            f2_min = int(request.form.get('f2_min'))
            f2_max = int(request.form.get('f2_max'))
            d2_min = float(request.form.get('d2_min'))
            d2_max = float(request.form.get('d2_max'))
            batch = int(request.form.get('batch'))
            epoch = int(request.form.get('epoch'))
            combinations = int(request.form.get('combinations'))
            models_list = training.delay(f1mn=f1_min, f1mx=f1_max, d1mn=d1_min, d1mx=d1_max, f2mn=f2_min,
                                         f2mx=f2_max, d2mn=d2_min, d2mx=d2_max, btch=batch, epch=epoch, cmbntins=combinations)
            print(models_list)
            # CONECTAR ESTOS VALORES CON TRAIN_MODELS
            # Editar TRAIN_MODELS PARA QUE DEVUELVA UNA CADENA CON LOS MEJORES MODELOS (PUEDE SER)
            # IMPLEMENTAR CELERY PARA REALIZAR EL PROCESO DE ENTRENAMIENTO (CREAR BOTONES)
        return render_template("loading.html", user=current_user)
    else:
        flash('La página ingresada es inexistente o no cuentas con los permisos necesarios.', category="error")
        return render_template("homeAdm.html", user=current_user)


@ views.route('/resultado', methods=['GET', 'POST'])
@ login_required
def resultado():
    if not Usuario.is_admin(current_user.role):
        error = ''
        target_img = os.path.join(os.getcwd(), 'website/static/images')
        if request.method == 'POST':
            if (request.files):
                file = request.files['file']
                if file and allowed_file(file.filename):
                    file.save(os.path.join(target_img, file.filename))
                    img_path = os.path.join(target_img, file.filename)
                    img = file.filename

                    class_result, prob_result = predict(img_path, model)

                    predictions = {
                        "class1": class_result[0],
                        "class2": class_result[1],
                        "class3": class_result[2],
                        "prob1": prob_result[0],
                        "prob2": prob_result[1],
                        "prob3": prob_result[2],
                    }

                    disease = class_result[0]
                    if (disease == "benigno"):
                        disease = "Dermatofibroma (Tumor benigno)"
                        description = "El dermatofibroma es un tumor benigno, muy frecuente, que suele aparecer en extremidades, generalmente en las piernas. Tiene una forma redondeada u ovalada, generalmente es de color marrón, y algunos tienen una zona blanquecina central."
                        treatment = "Dado que es una lesión benigna no precisa tratamiento salvo que produzca molestias o por motivos estéticos. El tratamiento de elección, cuando es necesario, es la extirpación mediante cirugía."
                    if (disease == "carcinoma"):
                        disease = "Carcinoma de células basales (BCC)"
                        description = "El carcinoma de células basales (también referido como cáncer de piel de células basales) es el tipo más común de cáncer de piel. Alrededor de 8 de cada 10 casos de cáncer de piel son carcinomas de células basales (también llamados cánceres de células basales). Estos cánceres comienzan en la capa celular basal, que es la parte inferior de la epidermis. Por lo general, estos cánceres surgen en las zonas expuestas al sol, especialmente la cara, la cabeza y el cuello. Estos cánceres suelen crecer lentamente. Es muy poco común que el cáncer de células basales se propague a otras partes del cuerpo. Pero de no tratarse, el cáncer de células basales puede extenderse hacia las áreas cercanas e invadir el hueso u otros tejidos debajo de la piel. El carcinoma de células basales puede reaparecer (recurrir) en el mismo lugar de la piel, si no se extrae completamente. Las personas que han tenido cánceres de piel de células basales también tienen una probabilidad mayor de padecer nuevos cánceres en otros lugares."
                        treatment = "El carcinoma de células basales se trata con mayor frecuencia con cirugía para extirpar todo el cáncer y parte del tejido sano que lo rodea. Se sugiere confirmar el diagnostico con una prueba histopatológica, posteriormente se recomienda una escisión quirúrgica o una cirugía de MOHS."
                    if (disease == "dfsp"):
                        disease = "Dermatofibrosarcoma protuberans (DFSP)"
                        description = "El dermatofibrosarcoma protuberans (DFSP) es un tipo muy raro de cáncer de piel que comienza en las células del tejido conectivo en la capa media de la piel (dermis). El DFSP puede aparecer al principio como un hematoma o una cicatriz. A medida que crece, se pueden formar grumos de tejido (protuberanos) cerca de la superficie de la piel. Este cáncer de piel a menudo se forma en brazos, piernas y tronco."
                        treatment = "El tratamiento del dermatofibrosarcoma protuberans generalmente implica una cirugía para extirpar el cáncer. Se pueden usar otros tratamientos para destruir las células cancerosas que puedan quedar después de la cirugía, como ser la radioterapia. Se sugiere confirmar el diagnostico con una prueba histopatológica, posteriormente se recomienda una escisión quirúrgica o una cirugía de MOHS."
                    if (disease == "melanoma"):
                        disease = "Melanoma"
                        description = "El melanoma, el tipo de cáncer de piel que requiere más cuidado, se desarrolla en las células (melanocitos) que producen melanina, el pigmento que da color a la piel. El melanoma también se puede formar en los ojos y, en raras ocasiones, en el interior del cuerpo, como en la nariz o la garganta. La causa exacta de todos los melanomas no está clara, pero la exposición a la radiación ultravioleta (UV) de la luz solar o las lámparas y camas de bronceado aumenta el riesgo de desarrollar melanoma. Limitar su exposición a la radiación ultravioleta puede ayudar a reducir su riesgo de melanoma. El riesgo de melanoma parece estar aumentando en personas menores de 40 años, especialmente en mujeres. Conocer las señales de advertencia del cáncer de piel puede ayudar a garantizar que los cambios cancerosos se detecten y se traten antes de que el cáncer se haya propagado. El melanoma se puede tratar con éxito si se detecta a tiempo."
                        treatment = "El tratamiento de los melanomas en etapa temprana generalmente incluye cirugía para extirpar el melanoma. Un melanoma muy delgado se puede extirpar por completo durante la biopsia y no requiere tratamiento adicional. De lo contrario, su cirujano extirpará el cáncer, así como un borde de piel normal y una capa de tejido debajo de la piel. Para las personas con melanomas en etapa temprana, este puede ser el único tratamiento necesario. Si el melanoma se ha diseminado a los ganglios linfáticos cercanos, su cirujano puede extirpar los ganglios afectados. También se pueden recomendar tratamientos adicionales antes o después de la cirugía, como ser inmunoterapia, terapia dirigida, radioterapia y quimioterapia."

                else:
                    error = "Por favor introduce una imagen con extensión jpg, jpeg y png."

                if(len(error) == 0):
                    return render_template('resultado.html', img=img, predictions=predictions, disease=disease, description=description, treatment=treatment, user=current_user)
                else:
                    flash(
                        'Por favor introduce una imagen con extensión jpg, jpeg o png.', category="error")
                    return render_template('prediccion.html', error=error, user=current_user)

        else:
            return render_template('prediccion.html', user=current_user)
    else:
        flash('La página ingresada es inexistente o no cuentas con los permisos necesarios.', category="error")
        return render_template("homeAdm.html", user=current_user)


@ views.route('/resultadoDiagnostico/<id>/', methods=['GET', 'POST'])
@ login_required
def resultadoDiagnostico(id):
    if not Usuario.is_admin(current_user.role):
        error = ''
        paciente = Paciente.query.get(id)
        target_img = os.path.join(os.getcwd(), 'website/static/images')
        if request.method == 'POST':
            if (request.files):
                file = request.files['file']
                if file and allowed_file(file.filename):
                    file.save(os.path.join(target_img, file.filename))
                    img_path = os.path.join(target_img, file.filename)
                    img = file.filename

                    class_result, prob_result = predict(img_path, model)

                    predictions = {
                        "class1": class_result[0],
                        "class2": class_result[1],
                        "class3": class_result[2],
                        "prob1": prob_result[0],
                        "prob2": prob_result[1],
                        "prob3": prob_result[2],
                    }

                    disease = class_result[0]
                    if (disease == "benigno"):
                        disease = "Dermatofibroma (Tumor benigno)"
                        description = "El dermatofibroma es un tumor benigno, muy frecuente, que suele aparecer en extremidades, generalmente en las piernas. Tiene una forma redondeada u ovalada, generalmente es de color marrón, y algunos tienen una zona blanquecina central."
                        treatment = "Dado que es una lesión benigna no precisa tratamiento salvo que produzca molestias o por motivos estéticos. El tratamiento de elección, cuando es necesario, es la extirpación mediante cirugía."
                    if (disease == "carcinoma"):
                        disease = "Carcinoma de células basales (BCC)"
                        description = "El carcinoma de células basales (también referido como cáncer de piel de células basales) es el tipo más común de cáncer de piel. Alrededor de 8 de cada 10 casos de cáncer de piel son carcinomas de células basales (también llamados cánceres de células basales). Estos cánceres comienzan en la capa celular basal, que es la parte inferior de la epidermis. Por lo general, estos cánceres surgen en las zonas expuestas al sol, especialmente la cara, la cabeza y el cuello. Estos cánceres suelen crecer lentamente. Es muy poco común que el cáncer de células basales se propague a otras partes del cuerpo. Pero de no tratarse, el cáncer de células basales puede extenderse hacia las áreas cercanas e invadir el hueso u otros tejidos debajo de la piel. El carcinoma de células basales puede reaparecer (recurrir) en el mismo lugar de la piel, si no se extrae completamente. Las personas que han tenido cánceres de piel de células basales también tienen una probabilidad mayor de padecer nuevos cánceres en otros lugares."
                        treatment = "El carcinoma de células basales se trata con mayor frecuencia con cirugía para extirpar todo el cáncer y parte del tejido sano que lo rodea. Se sugiere confirmar el diagnostico con una prueba histopatológica, posteriormente se recomienda una escisión quirúrgica o una cirugía de MOHS."
                    if (disease == "dfsp"):
                        disease = "Dermatofibrosarcoma protuberans (DFSP)"
                        description = "El dermatofibrosarcoma protuberans (DFSP) es un tipo muy raro de cáncer de piel que comienza en las células del tejido conectivo en la capa media de la piel (dermis). El DFSP puede aparecer al principio como un hematoma o una cicatriz. A medida que crece, se pueden formar grumos de tejido (protuberanos) cerca de la superficie de la piel. Este cáncer de piel a menudo se forma en brazos, piernas y tronco."
                        treatment = "El tratamiento del dermatofibrosarcoma protuberans generalmente implica una cirugía para extirpar el cáncer. Se pueden usar otros tratamientos para destruir las células cancerosas que puedan quedar después de la cirugía, como ser la radioterapia. Se sugiere confirmar el diagnostico con una prueba histopatológica, posteriormente se recomienda una escisión quirúrgica o una cirugía de MOHS."
                    if (disease == "melanoma"):
                        disease = "Melanoma"
                        description = "El melanoma, el tipo de cáncer de piel que requiere más cuidado, se desarrolla en las células (melanocitos) que producen melanina, el pigmento que da color a la piel. El melanoma también se puede formar en los ojos y, en raras ocasiones, en el interior del cuerpo, como en la nariz o la garganta. La causa exacta de todos los melanomas no está clara, pero la exposición a la radiación ultravioleta (UV) de la luz solar o las lámparas y camas de bronceado aumenta el riesgo de desarrollar melanoma. Limitar su exposición a la radiación ultravioleta puede ayudar a reducir su riesgo de melanoma. El riesgo de melanoma parece estar aumentando en personas menores de 40 años, especialmente en mujeres. Conocer las señales de advertencia del cáncer de piel puede ayudar a garantizar que los cambios cancerosos se detecten y se traten antes de que el cáncer se haya propagado. El melanoma se puede tratar con éxito si se detecta a tiempo."
                        treatment = "El tratamiento de los melanomas en etapa temprana generalmente incluye cirugía para extirpar el melanoma. Un melanoma muy delgado se puede extirpar por completo durante la biopsia y no requiere tratamiento adicional. De lo contrario, su cirujano extirpará el cáncer, así como un borde de piel normal y una capa de tejido debajo de la piel. Para las personas con melanomas en etapa temprana, este puede ser el único tratamiento necesario. Si el melanoma se ha diseminado a los ganglios linfáticos cercanos, su cirujano puede extirpar los ganglios afectados. También se pueden recomendar tratamientos adicionales antes o después de la cirugía, como ser inmunoterapia, terapia dirigida, radioterapia y quimioterapia."

                else:
                    error = "Por favor introduce una imagen con extensión jpg, jpeg y png."

                if(len(error) == 0):
                    return render_template('resultadoDiagnostico.html', img=img, predictions=predictions, disease=disease, description=description, treatment=treatment, paciente=paciente, user=current_user)
                else:
                    flash(
                        'Por favor introduce una imagen con extensión jpg, jpeg o png.', category="error")
                    return render_template('prediccionDiagnostico.html', error=error, user=current_user)

        else:
            return render_template('prediccionDiagnostico.html', user=current_user)
    else:
        flash('La página ingresada es inexistente o no cuentas con los permisos necesarios.', category="error")
        return render_template("homeAdm.html", user=current_user)
