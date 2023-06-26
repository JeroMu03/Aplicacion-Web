from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from datetime import datetime
from passver import PasswordVer

app = Flask(__name__)
app.config.from_pyfile('config.py')

from models import db
from models import Asistencia, Curso, Estudiante, Padre, Preceptor

@app.route('/registrarasistencia', methods=['GET', 'POST'])
def registrarasistencia():
    if request.method == 'POST':
        id_curso = request.form['curso']
        cod_clase = request.form['clase']
        fecha = request.form['fecha']
        estudiantes = Estudiante.query.filter_by(idcurso=id_curso).order_by(Estudiante.apellido, Estudiante.nombre).all()

        for estudiante in estudiantes:
            asistio = request.form.get(f'estudiante_{estudiante.id}')
            justificacion = ''

            if asistio:
                asistio = True
            else:
                asistio = False
                justificacion = 'Clase de Aula' if cod_clase == '1' else 'Educación Física'

            asistencia = Asistencia(fecha=fecha, codigoclase=cod_clase, asistio=asistio,
                                    justificacion=justificacion, idestudiante=estudiante.id)

            try:
                db.session.add(asistencia)
                db.session.commit()
                flash('Asistencia registrada exitosamente.', 'success')
            except Exception as e:
                db.session.rollback()
                flash('Ocurrió un error al registrar la asistencia.', 'error')
                print(str(e))
                return redirect(url_for('registrarasistencia'))

        return redirect(url_for('dashboard'))

    else:
        cursos = obtener_cursos_asignados(Preceptor.id)
        return render_template('selecciona_curso.html', cursos=cursos)
def obtener_curso(id_curso):
    curso = Curso.query.get(id_curso)
    return curso
def registrarasistencia(id_curso, fecha, codigoclase, asistio, justificacion,id_estudiante):
    nueva_asistencia = Asistencia(id_curso=id_curso, fecha=fecha, codigoclase=codigoclase, asistio=asistio, justificacion=justificacion,id_estudiante=id_estudiante)
    db.session.add(nueva_asistencia)
    db.session.commit()
def obtener_cursos_asignados(id_preceptor):
    preceptor = Preceptor.query.get(id_preceptor)
    cursos_asignados = preceptor.cursos
    return cursos_asignados

def obtener_estudiantes_curso(id_curso):
    estudiantes = Estudiante.query.filter_by(idcurso=id_curso).order_by(Estudiante.apellido, Estudiante.nombre).all()
    return estudiantes

def generar_informe_detalles(curso, estudiantes):
    informe = []
    for estudiante in estudiantes:
        asistencias_aula_presente = Asistencia.query.filter_by(idestudiante=estudiante.id, asistio=True).count()
        asistencias_edu_presente = Asistencia.query.filter_by(idestudiante=estudiante.id, asistio=True, justificacion='Educación Física').count()
        faltas_aula_justificadas = Asistencia.query.filter_by(idestudiante=estudiante.id, asistio=False, justificacion='Clase de Aula').count()
        faltas_aula_injustificadas = Asistencia.query.filter_by(idestudiante=estudiante.id, asistio=False, justificacion='').count()
        faltas_edu_justificadas = Asistencia.query.filter_by(idestudiante=estudiante.id, asistio=False, justificacion='Educación Física').count()
        faltas_edu_injustificadas = Asistencia.query.filter_by(idestudiante=estudiante.id, asistio=False, justificacion='').count()

        total_faltas = faltas_aula_justificadas + faltas_aula_injustificadas + 0.5 * (faltas_edu_justificadas + faltas_edu_injustificadas)

        detalle = {
            'estudiante': estudiante,
            'asistencias_aula_presente': asistencias_aula_presente,
            'asistencias_edu_presente': asistencias_edu_presente,
            'faltas_aula_justificadas': faltas_aula_justificadas,
            'faltas_aula_injustificadas': faltas_aula_injustificadas,
            'faltas_edu_justificadas': faltas_edu_justificadas,
            'faltas_edu_injustificadas': faltas_edu_injustificadas,
            'total_faltas': total_faltas
        }
        informe.append(detalle)

    informe_ordenado = sorted(informe, key=lambda x: (x['estudiante'].apellido.lower(), x['estudiante'].nombre.lower()))

    return informe_ordenado

@app.route('/',) #PAGINA DE INICIO
def usuario():
    return render_template('login.html')

@app.route('/bienvenida', methods = ['POST', 'GET']) #LOGIN
def bienvenida():
    if request.method == "POST":
        if request.form['mail'] and request.form['contra'] and request.form['tipo']:
            if request.form['tipo'] == 'padre': #EVALUA EL TIPO, SI ES TIPO PADRE:
                padre = Padre.query.filter_by(correo=request.form['mail']).first() #FILTRA EN LA BASE DE DATOS CON EL MAIL Y OBTIENE EL PADRE
                if(padre is not None): #SI EXISTE LA CUENTA:
                    passver = PasswordVer(request.form['contra']) #VERIFICAMOS LA CONTRASE;A CON EL CIFRADO
                    if(passver.validarPassword(padre.clave)): #SI ES CORRECTA, GUARDAMOS LA SESSION Y ENTRAMOS AL CAMPUS
                        session["id"] = padre.id
                        session["mail"] = padre.correo
                        session["tipo"] = request.form['tipo']
                        return render_template('menupadre.html', datos=[padre.nombre,padre.apellido, session["tipo"]])
                flash('Verifica tus credenciales de acceso, Email o contraseña inválidos') #SI NO SALTA UN FLASH INDICANDO EL ERROR
                return render_template('login.html')
            else: #SI NO ES TIPO PADRE, ENTONCES SERA TIPO PRECEPTOR
                preceptor = Preceptor.query.filter_by(correo=request.form['mail']).first() #FILTRA EN LA BASE DE DATOS CON EL MAIL Y OBTIENE EL PRECEPTOR
                if(type(preceptor) is not None): #SI EXISTE LA CUENTA
                    passver = PasswordVer(request.form['contra'])
                    if(passver.validarPassword(preceptor.clave)):
                        session["id"] = preceptor.id
                        session["mail"] = preceptor.correo
                        session["tipo"] = request.form['tipo']
                        return render_template('menupreceptor.html', datos=[preceptor.nombre,preceptor.apellido])
                flash('Verifica tus credenciales de acceso, Email o contraseña inválidos')
                return render_template('login.html')
        else:
            flash('Verifica tus credenciales de acceso, DNI o contraseña inválidos')
            return render_template('login.html')
    else:
        return render_template('login.html')

@app.route('/logout') #SE CIERRA LA SESION
def logout():
    session.pop('id')
    session.pop('mail')
    session.pop('tipo')
    return redirect(url_for('usuario'))

@app.route('/asistencia') #LANDING PAGE DE LA ASISTENCIA
def asistencia():
    padre = Padre.query.filter_by(id=session["id"]).first()
    estudiante = padre.estudiantes
    return render_template('a.html', dato=estudiante)

@app.route('/consasistencia', methods=["GET", "POST"]) #SE CONSULTA LA ASISTENCIA PARA EL HIJO SOLICITADO, DE LOS DATOS QUE SE INTRODUCEN EN /asistencia
def consasistencia():
    if request.method == "POST":
        if request.form['hijo']:
            estudiante = Estudiante.query.filter_by(id=request.form['hijo']).first() #FILTRA HIJO POR ID
            i=0
            falta=0.0
            for i in range(len(estudiante.asistencia_alum)): #CANTTIDAD DE FALTAS + COMPUTO DE ASISTENCIA
                i+=1
                if estudiante.asistencia_alum[i-1].codigoclase == 1:
                    falta+=1.0
                else:
                    falta+=0.5
            return render_template('b.html',nom=estudiante.nombre,ap=estudiante.apellido,datos=estudiante.asistencia_alum, indice=i, faltas=falta)
    else:
        return redirect(url_for('asistencia'))

@app.route('/fecha')
def fecha():
    return render_template('fecha.html')

@app.route('/consasistenciafecha', methods=["GET", "POST"])
def fechacons():
    lista=[]
    if request.form['curso'] and request.form['division'] and request.form['clase'] and request.form['fecha']:
            curso= Curso.query.filter_by(anio=request.form['curso'], division=request.form['division']).first()
            estudiantes=curso.estudiante
            c=0
            x=0
            for i in range(len(curso.estudiante)):
                x+=1
                for b in range(len(estudiantes[i].asistencia_alum)):
                    if estudiantes[i].asistencia_alum[b].fecha==request.form['fecha'] and estudiantes[i].asistencia_alum[b].codigoclase==int(request.form['clase']):
                        c+=1
                        lista.append(estudiantes[i].asistencia_alum[b])
                        print(lista)
            return render_template('fechacons.html',  a=c, listaasis=lista, estudiantes=curso.estudiante, d=x)

@app.route('/informe_detalles', methods=['GET', 'POST'])
def informe_detalles():
    if request.method == 'POST':
        id_curso = request.form['curso']
        curso = obtener_curso(id_curso)
        estudiantes = obtener_estudiantes_curso(id_curso)
        informe = generar_informe_detalles(curso, estudiantes)
        return render_template('informe_detalles.html', curso=curso, informe=informe)
    else:
        id_preceptor = session["id"]
        cursos = obtener_cursos_asignados(id_preceptor)
        return render_template('seleccionar_curso.html', cursos=cursos, selected_curso=request.args.get('curso_id'))

     
#@app.route('/inasistencias')
#def asistencia():
#Fin Log out
    

if __name__ == '__main__': 
    app.run(debug = True)