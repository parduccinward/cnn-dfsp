import os
import uuid
import urllib
from flask import Blueprint, render_template, request, flash, session
from flask_login import login_user, login_required, current_user
from tensorflow.keras.models import load_model
from datetime import date
from .models import Paciente, Medico, Prediccion, Enfermedad, Diagnostico, medicoPaciente, Usuario
from .auth import requires_roles
from PIL import Image
import numpy as np
import smtplib
from . import db
from .img_classification import get_prediction, predict
from .trainining_process import train_models
from .password_generator import generate_random_password
from .tasks import training
from email.message import EmailMessage
from datetime import datetime
from werkzeug.security import generate_password_hash

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


@views.route('/entrenamiento')
@login_required
def entrenamiento():
    if Usuario.is_admin(current_user.role):
        return render_template("entrenamiento.html", user=current_user)
    else:
        flash('La página ingresada es inexistente o no cuentas con los permisos necesarios.', category="error")
        return render_template("homeMed.html", user=current_user)


@views.route('/subirImagenes')
@login_required
def subirImagenes():
    if Usuario.is_admin(current_user.role):
        return render_template("subirImagenes.html", user=current_user)
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
        usuarios = Usuario.query.all()
        return render_template("admUsuarios.html", user=current_user, usuarios=usuarios)
    else:
        flash('La página ingresada es inexistente o no cuentas con los permisos necesarios.', category="error")
        return render_template("homeMed.html", user=current_user)


@views.route('/regMedicos')
@login_required
def regMedicos():
    if Usuario.is_admin(current_user.role):
        medicos = Medico.query.all()
        return render_template("regMedicos.html", user=current_user, medicos=medicos)
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
        medico = Medico.query.filter_by(usuario_id=current_user.id).first()
        consulta = medicoPaciente.query.filter_by(
            medico_id=medico.id).all()
        id_pacientes = []
        for i in consulta:
            id_pacientes.append(i.paciente_id)

        pacientes_medico = Paciente.query.filter(
            Paciente.id.in_(id_pacientes)).all()
        return render_template("pacientes.html", user=current_user, pacientes=pacientes_medico)

    else:
        flash('La página ingresada es inexistente o no cuentas con los permisos necesarios.', category="error")
        return render_template("homeAdm.html", user=current_user)


@views.route('/historialMedico/<id>/', methods=['GET', 'POST'])
@login_required
def historialMedico(id):
    if not Usuario.is_admin(current_user.role):
        diagnosticos = Diagnostico.query.filter_by(
            id_paciente=id).all()
        print(diagnosticos)
        return render_template("historialMedico.html", user=current_user, diagnosticos=diagnosticos)

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


@views.route('/enviarReporte/<id>/', methods=['GET', 'POST'])
@login_required
def enviarReporte(id):
    if not Usuario.is_admin(current_user.role):
        msg = EmailMessage()
        reporte_medico = request.args.get("reporte_medico")
        enfermedad = request.args.get("diseases")
        msg.set_content(reporte_medico)
        user = current_user.id
        medico = Medico.query.filter_by(usuario_id=user).first()
        msg['Subject'] = "Diagnóstico médico realizado por " + \
            medico.nombre+" "+medico.apellido
        msg['From'] = "sistema.ai.cad@gmail.com"
        paciente_objetivo = Paciente.query.filter_by(id=id).first()
        email_paciente = paciente_objetivo.email
        msg['To'] = email_paciente
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login("sistema.ai.cad@gmail.com", os.getenv("MAIL_PASSWORD"))
        server.send_message(msg)
        server.quit()
        prediccion_paciente = session.get('prediccion_paciente', None)
        fecha = date.today()
        new_diagnostico = Diagnostico(
            descripcion=reporte_medico, id_paciente=paciente_objetivo.id, id_medico=medico.id, id_prediccion=prediccion_paciente, id_enfermedad=enfermedad, fecha=fecha)
        db.session.add(new_diagnostico)
        db.session.commit()
        # Enviar correo
        flash('Se envio un reporte al correo electronico del paciente.',
              category="success")
        return render_template("homeMed.html", user=current_user)
    else:
        flash('La página ingresada es inexistente o no cuentas con los permisos necesarios.', category="error")
        return render_template("homeAdm.html", user=current_user)


@views.route('/enviarReporteSinSistema/<id>/', methods=['GET', 'POST'])
@login_required
def enviarReporteSinSistema(id):
    if not Usuario.is_admin(current_user.role):
        msg = EmailMessage()
        reporte_medico = request.args.get("reporte_medico")
        enfermedad = request.args.get("diseases")
        msg.set_content(reporte_medico)
        user = current_user.id
        medico = Medico.query.filter_by(usuario_id=user).first()
        msg['Subject'] = "Diagnóstico médico realizado por " + \
            medico.nombre+" "+medico.apellido
        msg['From'] = "sistema.ai.cad@gmail.com"
        paciente_objetivo = Paciente.query.filter_by(id=id).first()
        email_paciente = paciente_objetivo.email
        msg['To'] = email_paciente
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login("sistema.ai.cad@gmail.com", os.getenv("MAIL_PASSWORD"))
        server.send_message(msg)
        server.quit()
        fecha = date.today()
        new_diagnostico = Diagnostico(
            descripcion=reporte_medico, id_paciente=paciente_objetivo.id, id_medico=medico.id, id_prediccion=None, id_enfermedad=enfermedad, fecha=fecha)
        db.session.add(new_diagnostico)
        db.session.commit()
        # Enviar correo
        flash('Se envio un reporte al correo electronico del paciente.',
              category="success")
        return render_template("homeMed.html", user=current_user)
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
        enfermedades = Enfermedad.query.all()
        return render_template("reporte.html", user=current_user, paciente=paciente, enfermedades=enfermedades)
    else:
        flash('La página ingresada es inexistente o no cuentas con los permisos necesarios.', category="error")
        return render_template("homeAdm.html", user=current_user)


@views.route('/reporteSinSistema/<id>/', methods=['GET', 'POST'])
@login_required
def reporteSinSistema(id):
    if not Usuario.is_admin(current_user.role):
        paciente = Paciente.query.get(id)
        enfermedades = Enfermedad.query.all()
        return render_template("reporteSinSistema.html", user=current_user, paciente=paciente, enfermedades=enfermedades)
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
            id_user = current_user.id
            medico = Medico.query.filter_by(usuario_id=id_user).first()
            db.session.add(new_patient)
            db.session.commit()
            consulta = medicoPaciente(
                medico_id=medico.id, paciente_id=new_patient.id)
            db.session.add(consulta)
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
        consulta = medicoPaciente.query.filter_by(paciente_id=id).first()
        db.session.delete(consulta)
        db.session.commit()
        my_data = Paciente.query.get(id)
        db.session.delete(my_data)
        db.session.commit()
        flash('Paciente eliminado!', category="success")
        return render_template("homeMed.html", user=current_user)
    else:
        flash('La página ingresada es inexistente o no cuentas con los permisos necesarios.', category="error")
        return render_template("homeAdm.html", user=current_user)


@views.route('/add_medico', methods=['GET', 'POST'])
def add_medico():
    if Usuario.is_admin(current_user.role):
        if request.method == 'POST':
            nombre = request.form['nombreMedico']
            apellido = request.form['apellidoMedico']
            email = request.form['emailMedico']
            telefono = request.form['telefonoMedico']
            especialidad = request.form['especialidadMedico']
            user = nombre[0].lower()
            username = user + apellido.lower()
            password = generate_random_password()
            new_user = Usuario(username=username, password=generate_password_hash(
                password, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            new_medico = Medico(nombre=nombre, apellido=apellido, email=email,
                                telefono=telefono, especialidad=especialidad, usuario_id=new_user.id)
            db.session.add(new_medico)
            db.session.commit()
            msg = EmailMessage()
            mensaje = "Dr. " + apellido + ":\r\n\r\nEl sistema DermAI asignó una cuenta para que pueda autenticarse en el sistema. Le pedimos por favor que no comparta sus credenciales con ninguna otra persona, y que elimine el siguiente mensaje posteriormente. Las credenciales de su cuenta son las siguientes:\r\n\r\nusuario: " + \
                username + "\r\ncontraseña: " + password + \
                "\r\n\r\nAtentamente,\r\n\r\nAdministrador DermAI"
            msg.set_content(mensaje)
            msg['Subject'] = "Nueva cuenta sistema CAD DermAI"
            msg['From'] = "sistema.ai.cad@gmail.com"
            msg['To'] = email
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login("sistema.ai.cad@gmail.com",
                         os.getenv("MAIL_PASSWORD"))
            server.send_message(msg)
            server.quit()

            flash('Médico creado exitosamente!', category="success")
        return render_template("homeAdm.html", user=current_user)
    else:
        flash('La página ingresada es inexistente o no cuentas con los permisos necesarios.', category="error")
        return render_template("homeMed.html", user=current_user)


@views.route('/update_medico', methods=['GET', 'POST'])
def update_medico():

    if Usuario.is_admin(current_user.role):
        if request.method == 'POST':
            medico = Medico.query.get(request.form.get('id'))
            medico.nombre = request.form['nombreMedico']
            medico.apellido = request.form['apellidoMedico']
            medico.email = request.form['emailMedico']
            medico.telefono = request.form['telefonoMedico']
            medico.especialidad = request.form['especialidadMedico']
            db.session.commit()
            flash('Médico actualizado!', category="success")
        return render_template("homeAdm.html", user=current_user)
    else:
        flash('La página ingresada es inexistente o no cuentas con los permisos necesarios.', category="error")
        return render_template("homeMed.html", user=current_user)


@views.route('/delete_medico/<id>/', methods=['GET', 'POST'])
def delete_medico(id):
    if Usuario.is_admin(current_user.role):
        my_data = Medico.query.get(id)
        db.session.delete(my_data)
        db.session.commit()
        flash('Medico eliminado!', category="success")
        return render_template("homeAdm.html", user=current_user)
    else:
        flash('La página ingresada es inexistente o no cuentas con los permisos necesarios.', category="error")
        return render_template("homeMed.html", user=current_user)


@views.route('/delete_user/<id>/', methods=['GET', 'POST'])
def delete_user(id):
    if Usuario.is_admin(current_user.role):
        usuario = Usuario.query.get(id)
        db.session.delete(usuario)
        db.session.commit()
        flash('Usuario eliminado!', category="success")
        return render_template("homeAdm.html", user=current_user)
    else:
        flash('La página ingresada es inexistente o no cuentas con los permisos necesarios.', category="error")
        return render_template("homeMed.html", user=current_user)


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
                unique_filename = str(uuid.uuid4())
                if file and allowed_file(unique_filename+file.filename):
                    file.save(os.path.join(
                        target_img, unique_filename+file.filename))
                    img_path = os.path.join(
                        target_img, unique_filename+file.filename)
                    img = unique_filename+file.filename

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
                unique_filename = str(uuid.uuid4())
                if file and allowed_file(unique_filename+file.filename):
                    file.save(os.path.join(
                        target_img, unique_filename+file.filename))
                    img_path = os.path.join(
                        target_img, unique_filename+file.filename)
                    img = unique_filename+file.filename

                    class_result, prob_result = predict(img_path, model)

                    predictions = {
                        "class1": class_result[0],
                        "class2": class_result[1],
                        "class3": class_result[2],
                        "prob1": prob_result[0],
                        "prob2": prob_result[1],
                        "prob3": prob_result[2],
                    }
                    new_prediccion = Prediccion(
                        imagen=img, porcentaje=prob_result[0])
                    db.session.add(new_prediccion)
                    db.session.commit()
                    session['prediccion_paciente'] = new_prediccion.id
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
                    return render_template('prediccionDiagnostico.html', error=error, user=current_user, paciente=paciente)

        else:
            return render_template('prediccionDiagnostico.html', user=current_user)
    else:
        flash('La página ingresada es inexistente o no cuentas con los permisos necesarios.', category="error")
        return render_template("homeAdm.html", user=current_user)
