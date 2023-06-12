from __main__ import app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

db = SQLAlchemy(app)

class Asistencia(db.Model):
    __tablename__= 'asistencia' 
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    fecha = db.Column(db.String(50), nullable=False)
    codigo = db.Column(db.Integer, nullable=False)
    asistio = db.Column(db.Boolean, nullable=False)
    justificacion = db.Column(db.String(50), nullable=False)
    idEstudiante = db.Column(db.Integer, nullable=False)
    id_estudiante = db.Column(db.Integer, db.ForeignKey('estudiante.id'))
    
class Curso(db.Model):
    __tablename__= 'curso'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    anio = db.Column(db.Integer, nullable=False)
    division = db.Column(db.Integer, nullable=False)
    idpreceptor = db.Column(db.Integer, nullable=False)
    estudiante = db.relationship('Estudiante',backref='curso',cascade='all, delete-orphan', lazy='dinamic')
    id_preceptor = db.Column(db.Integer, db.ForeignKey('preceptor.id'))
    
class Estudiante(db.Model):
    __tablename__ = 'estudiante'
    id = db.Column(db.Integer, primary_key=True,nullable=False)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    dni = db.Column(db.String(50), nullable=False)
    
    idcurso = db.Column(db.Integer, nullable=False)
    idpadre = db.Column(db.String(100), nullable=False)
    
    id_curso= db.Column(db.Integer, db.ForeignKey('curso.id'))
    id_padre = db.Column(db.Integer, db.ForeignKey('padre.id'))
    asistencia_alum = db.relationship('Asistencia',backref='estudiante', cascade='all, delete-orphans', lazy='dinamic')

class Padre(db.Model):
    __tablename__ = 'padre'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    correo = db.Column(db.String(100), nullable=False)
    clave = db.Column(db.String(100), nullable=False)
    estudiantes = db.relationship('Estudiante',backref='padre', cascade='all, delete-orphans', lazy='dinamic')
    
class Preceptor(db.Model):
    __tablename__ = 'preceptor'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    correo = db.Column(db.String(100), nullable=False)
    clave = db.Column(db.String(100), nullable=False)
    cursos = db.relationship('Curso', backref='preceptor', cascade='all, delete-orphans', lazsy='dinamic')