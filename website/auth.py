from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login.utils import logout_user
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, current_user
from functools import wraps

auth = Blueprint('auth', __name__)


@auth.route('/')
def home():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('views.homeAdm'))
        else:
            return redirect(url_for('views.homeMed'))
    else:
        return redirect("login")


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Autentificado correctamente!', category='success')
                login_user(user, remember=True)
                if user.role == 'admin':
                    return redirect(url_for('views.homeAdm'))
                else:
                    return redirect(url_for('views.homeMed'))
            else:
                flash(
                    'Contraseña invalida, por favor verifique e intente nuevamente.', category='error')
        else:
            flash('El usuario ingresado no existe.', category='error')
    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(username=username).first()
        if user:
            flash('El usuario ya existe.', category='error')
        elif len(username) < 4:
            flash('El usuario debe ser de por lo menos 3 caracteres.',
                  category='error')
        elif password1 != password2:
            flash('Las contraseñas no coinciden.', category='error')
        elif len(password1) < 7:
            flash('La contraseña debe ser de por lo menos 7 caracteres.',
                  category='error')
        else:
            new_user = User(username=username, password=generate_password_hash(
                password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Cuenta creada correctamente!', category='success')
            if user.role == 'admin':
                return redirect(url_for('views.homeAdm'))
            else:
                return redirect(url_for('views.homeMed'))
    return render_template("sign_up.html", user=current_user)


def requires_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.role not in roles:
                # Redirect the user to an unauthorized notice!
                return "You are not authorized to access this page"
            return f(*args, **kwargs)
        return wrapped
    return wrapper
