from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from datetime import datetime
from passver import PasswordVer

app = Flask(__name__)
app.config.from_pyfile('config.py')

from models import db
from models import Asistencia, Curso, Estudiante, Padre, Preceptor

@app.route('/',) #PAGINA DE INICIO
def usuario():
    return render_template('login.html')

@app.route('/inicio', methods = ['POST', 'GET']) #LOGIN
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
    return render_template('asistencia.html', dato=estudiante)

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
            return render_template('consasistencia.html',nom=estudiante.nombre,ap=estudiante.apellido,datos=estudiante.asistencia_alum, indice=i, faltas=falta)
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
            return render_template('fechacons.html',  a=c, listaasis=lista, estudiantes=curso.estudiante, d=x)

@app.route('/informeprece')
def informeprece():
    preceptor=Preceptor.query.filter_by(id=session["id"]).first()
    return render_template('informeprece.html', cursos=preceptor.cursos, r=range(len(preceptor.cursos)))

@app.route('/consinformeprece',methods=["GET", "POST"])
def consinformeprece():
    if request.form['cursoid']:
        asisaula=[]
        asisfis=[]
        inasisaulajus=[]
        inasisfisjus=[]
        inasisfisinjus=[]
        inasisaulainjus=[]
        inas=[]
        falta=0.0
        aula=0
        fis=0
        infisjus=0
        inaulajus=0
        infisinjus=0
        inaulainjus=0
        es=0
        cursos=Curso.query.filter_by(id=request.form['cursoid']).first()
        estudiantes=cursos.estudiante
        for i in range(len(estudiantes)):
            es+=1
            asis=estudiantes[i].asistencia_alum
            for b in range(len(estudiantes[i].asistencia_alum)):
                if asis[b].codigoclase==1:
                    if asis[b].asistio == "s":
                        aula+=1
                    else:
                        if asis[b].justificacion != None:
                            falta+=1.0
                            inaulajus+=1
                        else:
                            falta+=1.0
                            inaulainjus+=1
                else:
                    if asis[b].asistio == "s":
                        fis+=1
                    else:
                        if asis[b].justificacion != None:
                            falta+=0.5
                            infisjus+=1
                        else:
                            falta+=0.5
                            infisinjus+=1
            asisaula.append(aula)
            asisfis.append(fis)
            inasisaulajus.append(inaulajus)
            inasisfisjus.append(infisjus)
            inasisfisinjus.append(infisinjus)
            inasisaulainjus.append(inaulainjus)
            inas.append(falta)
            falta=0.0
            aula=0
            fis=0
            infisjus=0
            inaulajus=0
            infisinjus=0
            inaulainjus=0
        return render_template("consinformeprece.html", indice=es, est=cursos.estudiante, aulap=asisaula, fisp=asisfis, aulafj=inasisaulajus, fisfj=inasisfisjus, aulafi=inasisaulainjus, fisfi=inasisfisinjus, inasis=inas)

@app.route("/asiscurso")
def curso():
    preceptor=Preceptor.query.filter_by(id=session["id"]).first()
    return render_template('curso.html', cursos=preceptor.cursos, r=range(len(preceptor.cursos)))

@app.route("/regasiscurso", methods=["GET", "POST"])
def regasis():
    if request.form['cursoid']:
        curso=Curso.query.filter_by(id=request.form['cursoid']).first()
        return render_template('regasis.html', estudiantes=curso.estudiante, r=range(len(curso.estudiante)))
    

if __name__ == '__main__': 
    app.run(debug = True)