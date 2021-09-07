from os import name
from . import db
from flask_login import UserMixin
from sqlalchemy.orm import relationship


class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    role = db.Column(db.String(64), default='medico')
    medico = relationship("Medico", back_populates="usuario", uselist=False)
    administrador = relationship(
        "Administrador", back_populates="usuario", uselist=False)

    def is_admin(role):
        return role == 'admin'


class Administrador(db.Model):
    __tablename__ = 'administrador'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    usuario = relationship("Usuario", back_populates="administrador")


class Medico(db.Model):
    __tablename__ = 'medico'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150))
    apellido = db.Column(db.String(150))
    email = db.Column(db.String(150))
    telefono = db.Column(db.Integer)
    especialidad = db.Column(db.String(150))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    usuario = relationship("Usuario", back_populates="medico")
    pacientes = relationship("medicoPaciente", back_populates="medico")
    diagnosticos = relationship("Diagnostico", back_populates="medico")


class Paciente(db.Model):
    __tablename__ = 'paciente'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150))
    apellido = db.Column(db.String(150))
    sexo = db.Column(db.String(150))
    fecha_nacimiento = db.Column(db.DateTime)
    email = db.Column(db.String(150))
    direccion = db.Column(db.String(150))
    medicos = relationship("medicoPaciente", back_populates="paciente")
    diagnosticos = relationship("Diagnostico", back_populates="paciente")


class medicoPaciente(db.Model):
    __tablename__ = 'medicoPaciente'
    id = db.Column(db.Integer, primary_key=True)
    medico_id = db.Column(db.Integer, db.ForeignKey('medico.id'))
    medico = relationship("Medico", back_populates="pacientes")
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'))
    paciente = relationship("Paciente", back_populates="medicos")


class Prediccion(db.Model):
    __tablename__ = 'prediccion'
    id = db.Column(db.Integer, primary_key=True)
    imagen = db.Column(db.LargeBinary)
    porcentaje = db.Column(db.Float)
    diagnostico = relationship("Diagnostico", back_populates="prediccion")


class Enfermedad(db.Model):
    __tablename__ = 'enfermedad'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150))
    diagnostico = relationship("Diagnostico", back_populates="enfermedad")


class Diagnostico(db.Model):
    __tablename__ = 'diagnostico'
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(150))
    id_paciente = db.Column(db.Integer, db.ForeignKey('paciente.id'))
    paciente = relationship("Paciente", back_populates="diagnosticos")
    id_medico = db.Column(db.Integer, db.ForeignKey('medico.id'))
    medico = relationship("Medico", back_populates="diagnosticos")
    id_prediccion = db.Column(db.Integer, db.ForeignKey('prediccion.id'))
    prediccion = relationship(
        "Prediccion", back_populates="diagnostico", uselist=False)
    id_enfermedad = db.Column(db.Integer, db.ForeignKey('enfermedad.id'))
    enfermedad = relationship(
        "Enfermedad", back_populates="diagnostico", uselist=False)
