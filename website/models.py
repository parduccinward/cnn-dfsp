from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime, date


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    role = db.Column(db.String(64), default='medico')


class Medico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150))
    apellido = db.Column(db.String(150))
    email = db.Column(db.String(150))
    telefono = db.Column(db.Integer)
    especialidad = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Paciente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150))
    apellido = db.Column(db.String(150))
    sexo = db.Column(db.String(150))
    fecha_nacimiento = db.Column(db.DateTime)
    email = db.Column(db.String(150))
    direccion = db.Column(db.String(150))


pacientes = db.Table('pacientes',
                     db.Column('id', db.Integer, db.ForeignKey(
                         'paciente.id'), primary_key=True),
                     db.Column('id', db.Integer, db.ForeignKey(
                         'medico.id'), primary_key=True)
                     )


class Prediccion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    imagen = db.Column(db.LargeBinary)
    porcentaje = db.Column(db.Float)


class Enfermedad(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150))


class Diagnostico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(150))
    id_paciente = db.Column(db.Integer, db.ForeignKey('paciente.id'))
    id_medico = db.Column(db.Integer, db.ForeignKey('medico.id'))
    id_prediccion = db.Column(db.Integer, db.ForeignKey('prediccion.id'))
    id_enfermedad = db.Column(db.Integer, db.ForeignKey('enfermedad.id'))
