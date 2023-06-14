from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from datetime import datetime
from passver import PasswordVer

app = Flask(__name__)
app.config.from_pyfile('config.py')

from models import db
from models import Asistencia, Curso, Estudiante, Padre, Preceptor

@app.route('/', methods=['POST', 'GET'])
def usuario():
    return render_template('login.html')

@app.route('/bienvenida', methods = ['POST', 'GET'])
def bienvenida():
    if request.method == "POST":
        if request.form['mail'] and request.form['contra'] and request.form['tipo']:
            if request.form['tipo'] == 'padre':
                padre = Padre.query.filter_by(correo=request.form['mail']).first()
                if(padre is not None):
                    passver = PasswordVer(request.form['contra'])
                    if(passver.validarPassword(padre.clave)):
                        session["id"] = padre.id
                        session["mail"] = padre.correo
                        session["tipo"] = request.form['tipo']
                        return render_template('menupadre.html', datos=[padre.nombre,padre.apellido, session["tipo"]])
                flash('Verifica tus credenciales de acceso, Email o contraseña inválidos')
                return render_template('login.html')
            else:
                preceptor = Preceptor.query.filter_by(correo=request.form['mail']).first()
                if(type(preceptor) is not None):
                    passver = PasswordVer(request.form['contra'])
                    if(passver.validarPassword(preceptor.clave)):
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
    
@app.route('/logout')
def logout():
    session.pop('mail')
    session.pop('tipo')
    return redirect(url_for('usuario'))


#@app.route('/inasistencias')
#def asistencia():
#Fin Log out
    
#@app.route('/informe_detallado')
#def informe_detallado():
    #if 'user_id' not in session:
        #return redirect('/login')

    #estudiantes = Estudiante.query.order_by(Estudiante.apellido, Estudiante.nombre).all()
    #informe = []

    #for estudiante in estudiantes:
        #asistencias_aula = Asistencia.query.filter_by(id_estudiante=estudiante.id, codigo= 1, asistio=True).count()
        #asistencias_edfisica = Asistencia.query.filter_by(id_estudiante=estudiante.id, codigo= 2 , asistio=True).count()

        #inasistencias_aula_justificadas = Asistencia.query.filter_by(id_estudiante=estudiante.id, codigo= 1 , asistio=False, justificacion.isnot(None)).count()
        #inasistencias_aula_injustificadas = Asistencia.query.filter_by(id_estudiante=estudiante.id, codigo= 1 , asistio=False, justificacion.is_(None)).count()

        #inasistencias_edfisica_justificadas = Asistencia.query.filter_by(id_estudiante=estudiante.id, codigo= 2 , asistio=False, justificacion.isnot(None)).count()
        #inasistencias_edfisica_injustificadas = Asistencia.query.filter_by(id_estudiante=estudiante.id, codigo= 2 , asistio=False, justificacion.is_(None)).count()

        #total_inasistencias = (
            #inasistencias_aula_justificadas +
            #inasistencias_aula_injustificadas +
            #(inasistencias_edfisica_justificadas * 0.5) +
            #(inasistencias_edfisica_injustificadas * 0.5) )

        #informe.append({
            #'estudiante': estudiante,
            #'asistencias_aula': asistencias_aula,
            #'asistencias_edfisica': asistencias_edfisica,
            #'inasistencias_aula_justificadas': inasistencias_aula_justificadas,
            #'inasistencias_aula_injustificadas': inasistencias_aula_injustificadas,
            #'inasistencias_edfisica_justificadas': inasistencias_edfisica_justificadas,
            #'inasistencias_edfisica_injustificadas': inasistencias_edfisica_injustificadas,
            #'total_inasistencias': total_inasistencias })

    #informe_ordenado = sorted(informe, key=lambda x: x['estudiante'].apellido)

    #return render_template('informe_detallado.html', informe=informe_ordenado)
    
if __name__ == '__main__': 
    app.run(debug = True)