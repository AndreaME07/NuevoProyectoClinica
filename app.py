from flask import Flask, render_template, redirect, request, session, flash, url_for
from flask_mysqldb import MySQL
from functools import wraps


app = Flask(__name__, template_folder='template')
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'db_clinicamayo'
app.config['MYSQL_UNIX_SOCKET'] = '/opt/lampp/var/mysql/mysql.sock'  
app.secret_key = 'mysecretkey'

mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('index.html')

#RUTAS PARA LOS MÉDICOS ADMINISTRADORES--------------------------------------------------------------------
@app.route('/agregarMedico')
def agregarMedico():
    return render_template('agregarMedico.html')

@app.route('/buscarMedico')
def buscarMedico():
    return render_template('buscarMedico.html')

@app.route('/editarMedico')
def editarMedico():
    return render_template('editarMedico.html')

@app.route('/registroMedico')
def registroMedico():
    return render_template('registroMedico.html') 
#se supone que esta ruta es para el inicio de la pagina y muestra los registros de los médicos que tiene cada admin

@app.route('/menuAdmin')
def menuAdmin():
    return render_template('menuAdmin.html')

#RUTAS PARA MÉDICOS GENERALES----------------------------------------------------------------------------------

@app.route('/agregarPacientes')
def agregarPacientes():
    return render_template('agregarPaciente.html') 

@app.route('/mostrarExpediente')
def mostrarExpediente():
    return render_template('mostrarExpediente.html') 

@app.route('/citaPaciente')
def citaPaciente():
    return render_template('citaPaciente.html') 

@app.route('/mostrarCitas')
def mostrarCitas():
    return render_template('mostrarCitas.html') 

@app.route('/exploracionPaciente')
def exploracionPaciente():
    return render_template('exploracionPaciente.html') 

@app.route('/diagnostico')
def diagnostico():
    return render_template('diagnostico.html') 

@app.route('/editarPaciente')
def editarPaciente():
    return render_template('editarPaciente.html') 

@app.route('/menuUser')
def menuUser():
    return render_template('menuUser.html')



@app.errorhandler(404)
def paginano(e):
    return 'Revisa tu sintaxis: No encontré nada', 404

if __name__ == '__main__':
    app.run(port=3000, debug=True, threaded=True)
