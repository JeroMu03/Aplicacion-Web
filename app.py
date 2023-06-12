from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime


app = Flask(__name__)



@app.route('/', methods=['POST', 'GET'])
def usuario():
    return render_template('login.html')

@app.route('/bienvenida', methods = ['POST', 'GET'])
def bienvenida():
    if request.method == "POST":
        if request.form['mail'] and request.form['contra']:
            datosform=request.form
            return render_template('bienvenida.html', datos=datosform)
    else:
        return render_template('login.html')
    
if __name__ == '__main__': 
    app.run(debug = True)