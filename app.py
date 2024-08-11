from flask import Flask, render_template, redirect, request, session, flash, url_for, sessions
from flask_mysqldb import MySQL
from functools import wraps


app = Flask(__name__, template_folder='template')
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'clinicaMayo'
app.config['MYSQL_UNIX_SOCKET'] = '/opt/lampp/var/mysql/mysql.sock'  
app.secret_key = 'mysecretkey'

mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('index.html')

#RUTAS PARA LOS MÉDICOS ADMINISTRADORES--------------------------------------------------------------------

@app.route('/mostrarMedicos')
def mostrarMedicos():
    return render_template('vistas/mostrarMedicos.html')

@app.route('/agregarMedico')
def agregarMedico():
    return render_template('opciones/agregarMedico.html')

@app.route('/editarMedico')
def editarMedico():
    return render_template('opciones/editarMedico.html')



# Expedientes ----------------------------------------------------------------------------------

@app.route('/mostrarPacientes')
def mostrarPacientes():
    return render_template('vistas/mostrarPacientes.html') 

@app.route('/agregarCita')
def agregarCita():
    return render_template('vistas/agregarCita.html') 


@app.route('/agregarPaciente')
def agregarPaciente():
    return render_template('opciones/agregarPaciente.html') 


@app.route('/mostrarCitas')
def mostrarCitas():
    return render_template('vistas/mostrarCitas.html') 

@app.route('/exploracionPaciente')
def exploracionPaciente():
    return render_template('vistas/exploracionPaciente.html') 

# ---------


@app.route('/diagnostico')
def diagnostico():
    return render_template('diagnostico.html') 

@app.route('/editarPacientes')
def editarPacientes():
    return render_template('opciones/editarPacientes.html') 

@app.route('/menuUser')
def menuUser():
    return render_template('menuUser.html')



@app.errorhandler(404)
def paginano(e):
    return 'Revisa tu sintaxis: No encontré nada', 404

if __name__ == '__main__':
    app.run(port=3000, debug=True, threaded=True)
