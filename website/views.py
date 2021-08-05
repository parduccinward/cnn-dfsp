import os
import uuid
import urllib
from flask import Blueprint, render_template, request
from flask_login import login_user, login_required, current_user
from tensorflow.keras.models import load_model
from .auth import requires_roles
from PIL import Image
import numpy as np
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
    return render_template("homeAdm.html", user=current_user)


@views.route('/homeMed')
@login_required
def homeMed():
    return render_template("homeMed.html", user=current_user)


@views.route('/admUsuarios')
@login_required
def admUsuarios():
    return render_template("admUsuarios.html", user=current_user)


@views.route('/regMedicos')
@login_required
def regMedicos():
    return render_template("regMedicos.html", user=current_user)


@views.route('/admSistema')
@login_required
def admSistema():
    return render_template("admSistema.html", user=current_user)


@views.route('/pacientes')
@login_required
def pacientes():
    return render_template("pacientes.html", user=current_user)


@views.route('/regPacientes')
@login_required
def regPacientes():
    return render_template("regPacientes.html", user=current_user)


@views.route('/diagnostico')
@login_required
def diagnostico():
    return render_template("diagnostico.html", user=current_user)


@views.route('/prediccion')
@login_required
def prediccion():
    return render_template("prediccion.html", user=current_user)


@views.route('/loading', methods=['GET', 'POST'])
@login_required
def loading():
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


@ views.route('/resultado', methods=['GET', 'POST'])
@ login_required
def resultado():
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

            else:
                error = "Please upload images of jpg , jpeg and png extension only"

            if(len(error) == 0):
                return render_template('resultado.html', img=img, predictions=predictions, user=current_user)
            else:
                return render_template('prediccion.html', error=error, user=current_user)

    else:
        return render_template('prediccion.html', user=current_user)
