from flask import Flask, render_template, redirect, request, session, flash, url_for
from flask_mysqldb import MySQL
from functools import wraps
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash
from weasyprint import HTML, CSS
from flask import send_file
import os 

# Modelos
from models.ModelUsers import ModelUser

# Entidades
from models.entidades.User import User

def roles_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'id_rol' not in session:
                flash('Por favor, inicie sesión para acceder a esta página.')
                return redirect(url_for('login'))
            
            user_role_id = session.get('id_rol')
            
            cur = mysql.connection.cursor()
            cur.execute("SELECT nombre FROM roles WHERE id=%s", (user_role_id,))
            result = cur.fetchone()
            cur.close()
            
            if result and result[0] in allowed_roles:
                return f(*args, **kwargs)
            else:
                flash('No tiene permiso para acceder a esta página.')
                return redirect(url_for('home'))
        return decorated_function
    return decorator

app = Flask(__name__, template_folder='template')
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'clinicaMayo'
app.config['MYSQL_UNIX_SOCKET'] = '/opt/lampp/var/mysql/mysql.sock'  
app.config['SESSION_PERMANENT'] = False
app.secret_key = 'mysecretkey'

mysql = MySQL(app)
login_manager_app = LoginManager(app)
csrf = CSRFProtect()

@login_manager_app.user_loader
def load_user(user_id):
    return ModelUser.get_by_id(mysql, user_id)


@app.route('/accesoLogin', methods=["POST"])
def accesoLogin():
    if request.method == 'POST':
        rfc = request.form['txtrfc']
        password = request.form['txtpassword']
        print(f"Login attempt with RFC: {rfc}")  # Debug print

        logged_user = ModelUser.login(rfc, mysql)
        if logged_user is not None:
            print(f"User found: {logged_user.RFC}")  # Debug print
            if User.check_password(logged_user.contrasena, password):
                login_user(logged_user)
                session['id_rol'] = logged_user.id_rol
                if logged_user.id_rol == 1:
                    print("Redirecting to mostrarMedicos")  # Debug print
                    return redirect(url_for('mostrarMedicos'))
                elif logged_user.id_rol == 2:
                    print("Redirecting to mostrarPacientes")  # Debug print
                    return redirect(url_for('mostrarPacientes'))
                else:
                    print(f"Unknown role: {logged_user.id_rol}")  # Debug print
            else:
                print("Password check failed")  # Debug print
                flash('Contraseña incorrecta')
        else:
            print("User not found")  # Debug print
            flash('Usuario no encontrado')
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/')

def home():
    return render_template('index.html')

#RUTAS PARA LOS MÉDICOS ADMINISTRADORES--------------------------------------------------------------------

@app.route('/mostrarMedicos')
@login_required
@roles_required(['Administrador'])
def mostrarMedicos():
    cur = mysql.connection.cursor()
    cur.execute("SELECT medicos.*, roles.nombre FROM medicos JOIN roles ON medicos.id_rol = roles.id")
    medico = cur.fetchall()
    return render_template('vistas/mostrarMedicos.html', medico=medico)

@app.route('/agregarMedico')
@login_required
@roles_required(['Administrador'])
def agregarMedico():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM roles")
    roles = cur.fetchall()

    return render_template('/opciones/agregarMedico.html', roles=roles)

@app.route('/guardarMedico', methods=['POST'])
@login_required
@roles_required(['Administrador'])
def guardarMedico():
    if request.method == 'POST':
        nombre = request.form.get('txtNombre')
        apePaterno = request.form.get('txtApePaterno')
        apeMaterno = request.form.get('txtApeMaterno')
        cedulaProfesional = request.form.get('txtCedula')
        correo = request.form.get('txtCorreo')
        contrasena = request.form.get('txtContrasena')
        id_rol = request.form.get('txtRol')
        rfc = request.form.get('txtRFC')

        if not all([nombre, apePaterno, apeMaterno, cedulaProfesional, correo, contrasena, id_rol, rfc]):
            flash('Por favor, complete todos los campos obligatorios')
            return redirect(url_for('agregarMedico'))

        cur = mysql.connection.cursor()
        hashed_password = generate_password_hash(contrasena)
        cur.execute("INSERT INTO medicos(nombres, apeP, apeM, cedula, correo, pass, id_rol, RFC) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)", 
                    (nombre, apePaterno, apeMaterno, cedulaProfesional, correo, hashed_password, id_rol, rfc))
        mysql.connection.commit()
        cur.close()
        flash('Médico agregado correctamente')
        return redirect(url_for('mostrarMedicos'))
    else:
        flash('Método no permitido')
        return redirect(url_for('agregarMedico'))

@app.route('/editarMedico/<id>')
@login_required
@roles_required(['Administrador'])
def editarMedico(id):
    medicos = mysql.connection.cursor()
    medicos.execute("SELECT * FROM medicos WHERE id=%s", (id,))
    medico = medicos.fetchone()
    medicos.close()  # Cerrar cursor después de su uso

    roles = mysql.connection.cursor()
    roles.execute("SELECT * FROM roles")
    rol = roles.fetchall()
    roles.close()  # Cerrar cursor después de su uso

    return render_template('opciones/editarMedico.html', medico=medico, roles=rol) 

@app.route('/actualizarMedico/<id>', methods=['POST'])
@login_required
@roles_required(['Administrador'])
def actualizarMedico(id):
    if request.method == 'POST':
        nombre = request.form.get('txtNombre')
        apePaterno = request.form.get('txtApePaterno')
        apeMaterno = request.form.get('txtApeMaterno')
        cedulaProfesional = request.form.get('txtCedula')
        correo = request.form.get('txtCorreo')
        contrasena = request.form.get('txtContrasena')
        id_rol = request.form.get('txtRol')
        rfc = request.form.get('txtRFC')

        if not all([nombre, apePaterno, apeMaterno, cedulaProfesional, correo, id_rol, rfc]):
            flash('Por favor, complete todos los campos obligatorios')
            return redirect(url_for('mostrarMedicos'))

        cur = mysql.connection.cursor()
        
        # Si se proporciona una nueva contraseña, actualízala
        if contrasena:
            hashed_password = generate_password_hash(contrasena)
            cur.execute("UPDATE medicos SET nombres=%s, apeP=%s, apeM=%s, cedula=%s, correo=%s, pass=%s, id_rol=%s, RFC=%s WHERE id=%s", 
                        (nombre, apePaterno, apeMaterno, cedulaProfesional, correo, hashed_password, id_rol, rfc, id))
        else:
            # Si no se proporciona una nueva contraseña, no la actualices
            cur.execute("UPDATE medicos SET nombres=%s, apeP=%s, apeM=%s, cedula=%s, correo=%s, id_rol=%s, RFC=%s WHERE id=%s", 
                        (nombre, apePaterno, apeMaterno, cedulaProfesional, correo, id_rol, rfc, id))
        
        mysql.connection.commit()
        cur.close()
        flash('Médico actualizado correctamente')
        return redirect(url_for('mostrarMedicos'))
    else:
        flash('Método no permitido')
        return redirect(url_for('mostrarMedicos'))
    

@app.route('/eliminarMedico/<id>')
@login_required
@roles_required(['Administrador'])
def eliminarMedico(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM medicos WHERE id=%s", (id,))
    mysql.connection.commit()
    cur.close()
    flash('Médico eliminado correctamente')
    return redirect(url_for('mostrarMedicos'))


# Expedientes ----------------------------------------------------------------------------------

@app.route('/mostrarPacientes')
@login_required
@roles_required(['Administrador', 'Médico'])
def mostrarPacientes():
    cur = mysql.connection.cursor()
    if session['id_rol'] == 1:
        cur.execute("SELECT pacientes.*,medicos.nombres,roles.nombre FROM pacientes JOIN medicos ON pacientes.id_medico = medicos.id JOIN roles ON medicos.id_rol = roles.id")
        paciente = cur.fetchall()
    else:
        cur.execute("SELECT * FROM pacientes WHERE id_medico=%s", (current_user.id,))
        paciente = cur.fetchall()
    return render_template('vistas/mostrarPacientes.html', paciente=paciente)

@app.route('/agregarCita/<id>')
@login_required
@roles_required(['Administrador', 'Médico'])
def agregarCita(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM pacientes WHERE id=%s", (id,))
    paciente = cur.fetchone()
    return render_template('vistas/agregarCita.html', paciente=paciente)

@app.route('/guardarCita', methods=['POST'])
@login_required
@roles_required(['Administrador', 'Médico'])
def guardarCita():
    id_paciente = request.form.get('txtPaciente') 
    
    if request.method == 'POST' and all(request.form.get(field) for field in ['txtDate', 'txtPeso', 'txtAlt', 'txtTemp', 'txtLat', 'txtSat', 'txtEdad', 'txtSint', 'txtEst', 'txtDiag', 'txtTrat', 'txtGlu', 'txtPaciente']):
        fecha = request.form['txtDate']
        peso = request.form['txtPeso']
        altura = request.form['txtAlt']
        temperatura = request.form['txtTemp']
        oxigenacion = request.form['txtSat']
        glucosa = request.form['txtGlu']
        edad = request.form['txtEdad']
        sintomas = request.form['txtSint']
        diagnostico = request.form['txtDiag']
        tratamiento = request.form['txtTrat']
        estudios = request.form['txtEst']
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO citas(fecha, peso, altura, temperatura, oxigenacion, glucosa, edad, sintomas, diagnostico, tratamiento, estudios, id_paciente) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", 
                    (fecha, peso, altura, temperatura, oxigenacion, glucosa, edad, sintomas, diagnostico, tratamiento, estudios, id_paciente))
        mysql.connection.commit()
        cur.close()
        flash('Cita agregada correctamente')
        return redirect(url_for('agregarCita', id=id_paciente))
    else:
        flash('Error al agregar la cita. Por favor, asegúrate de llenar todos los campos.')
        return redirect(url_for('agregarCita', id=id_paciente))
    

    

@app.route('/agregarPaciente')
def agregarPaciente():
    return render_template('opciones/agregarPaciente.html') 

@app.route('/guardarPaciente', methods=['POST'])
@login_required
@roles_required(['Administrador', 'Médico'])
def guardarPaciente():
    if request.method == 'POST' and request.form['txtNombre'] and  request.form['txtApePaterno'] and request.form['txtApeMaterno'] and request.form['txtFecha'] and request.form['txtAnte'] and request.form['txtAle'] and request.form['txtEC']:
        nombre = request.form['txtNombre']
        apePaterno = request.form['txtApePaterno']
        apeMaterno = request.form['txtApeMaterno']
        fechaNacimiento = request.form['txtFecha']
        antecedentes = request.form['txtAnte']
        alergias = request.form['txtAle']
        enfermedadesCronicas = request.form['txtEC']
        id_medico = current_user.id

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO pacientes(nombres, apeP, apeM, fechaNacimiento, antecedentes, alergias, enfermedades, id_medico) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)", 
                    (nombre, apePaterno, apeMaterno, fechaNacimiento, antecedentes, alergias, enfermedadesCronicas, id_medico))
        mysql.connection.commit()
        cur.close()
        flash('Paciente agregado correctamente')
        return redirect(url_for('mostrarPacientes'))
    
       


@app.route('/mostrarCitas/<id>')
@login_required
@roles_required(['Administrador', 'Médico'])
def mostrarCitas(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM pacientes WHERE id=%s", (id,))
    paciente = cur.fetchone()

    expediente = None
    citas = None
    if paciente:
        cur.execute("SELECT * FROM citas WHERE id_paciente=%s", (id,))
        citas = cur.fetchall()
    
    return render_template('vistas/mostrarCitas.html', paciente=paciente, citas=citas)


@app.route('/buscarCita', methods=['POST'])
@login_required
@roles_required(['Administrador', 'Médico'])
def buscarCita():
    nombre = request.form.get('txtNombre')
    apePaterno = request.form.get('txtApeP')
    apeMaterno = request.form.get('txtApeM')
    fechaCita = request.form.get('txtDate')

    query = "SELECT p.id FROM pacientes p JOIN citas c ON p.id = c.id_paciente WHERE 1=1"
    params = []

    if nombre:
        query += " AND p.nombres LIKE %s"
        params.append(f'%{nombre}%')
    if apePaterno:
        query += " AND p.apeP LIKE %s"
        params.append(f'%{apePaterno}%')
    if apeMaterno:
        query += " AND p.apeM LIKE %s"
        params.append(f'%{apeMaterno}%')
    if fechaCita:
        query += " AND c.fecha = %s"
        params.append(fechaCita)

    try:
        cur = mysql.connection.cursor()
        cur.execute(query, params)
        paciente = cur.fetchone()
        cur.close()

        if paciente:
            return redirect(url_for('mostrarCitas', id=paciente[0]))
        else:
            flash('No se encontraron pacientes con los criterios de búsqueda.')
            return redirect(url_for('buscarPaciente'))
    except Exception as e:
        flash(f'Error en la búsqueda: {str(e)}')
        return redirect(url_for('buscarPaciente'))

@app.route('/exploracionPaciente/')
@login_required
@roles_required(['Administrador', 'Médico'])
def exploracionPaciente():
    return render_template('vistas/exploracionPaciente.html') 

# ---------
@app.route('/crearCita/<id>')
@login_required
@roles_required(['Administrador', 'Médico'])
def crearCita(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT citas.*, pacientes.* FROM citas JOIN pacientes ON citas.id_paciente = pacientes.id WHERE citas.id=%s", (id,))
    cita = cur.fetchone()

    print(cita)
    os.makedirs('recetas', exist_ok=True)

    html_content = render_template('receta.html', cita=cita)

    pdf_path = f"recetas/receta_{cita[0]}_{cita[1]}.pdf"

    pdf = HTML(string=html_content).write_pdf()

    with open(pdf_path, 'wb') as f:
        f.write(pdf)
    
    flash('Receta generada correctamente')
    
    return send_file(pdf_path, as_attachment=True)





@app.route('/diagnostico')
def diagnostico():
    return render_template('diagnostico.html') 

@app.route('/editarPacientes/<id>')
@login_required
@roles_required(['Administrador', 'Médico'])
def editarPacientes(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM pacientes WHERE id=%s", (id,))
    paciente = cur.fetchone()
    return render_template('opciones/editarPacientes.html', paciente=paciente) 

@app.route('/actualizarPaciente/<id>', methods=['POST'])
@login_required
@roles_required(['Administrador', 'Médico'])
def actualizarPaciente(id):
    if request.method == 'POST' and all([request.form.get('txtNombre'), request.form.get('txtApePaterno'), request.form.get('txtApeMaterno'), request.form.get('txtFecha'), request.form.get('txtAnte'), request.form.get('txtAle'), request.form.get('txtEC')]):
        nombre = request.form['txtNombre']
        apePaterno = request.form['txtApePaterno']
        apeMaterno = request.form['txtApeMaterno']
        fechaNacimiento = request.form['txtFecha']
        antecedentes = request.form['txtAnte']
        alergias = request.form['txtAle']
        enfermedadesCronicas = request.form['txtEC']
        id_medico = current_user.id

        cur = mysql.connection.cursor()
        cur.execute("UPDATE pacientes SET nombres=%s, apeP=%s, apeM=%s, fechaNacimiento=%s, antecedentes=%s, alergias=%s, enfermedades=%s, id_medico=%s WHERE id=%s", 
                    (nombre, apePaterno, apeMaterno, fechaNacimiento, antecedentes, alergias, enfermedadesCronicas, id_medico, id))
        mysql.connection.commit()
        cur.close()
        flash('Paciente actualizado correctamente')
        return redirect(url_for('mostrarPacientes'))
    else:
        flash('Error al actualizar el paciente. Por favor, asegúrate de llenar todos los campos.')
        return redirect(url_for('editarPaciente', id=id))

@app.route('/eliminarPaciente/<id>')
@login_required
@roles_required(['Administrador', 'Médico'])
def eliminarPaciente(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM pacientes WHERE id=%s", (id,))
    mysql.connection.commit()
    cur.close()
    flash('Paciente eliminado correctamente')
    return redirect(url_for('mostrarPacientes'))

@app.route('/buscarPaciente', methods=['POST'])
@login_required
@roles_required(['Administrador', 'Médico'])
def buscarPaciente():
    nombre = request.form.get('txtNombre', '')
    apePaterno = request.form.get('txtApePaterno', '')
    apeMaterno = request.form.get('txtApeMaterno', '')
    
    query = "SELECT * FROM pacientes WHERE 1=1"
    params = []

    if nombre:
        query += " AND nombres LIKE %s"
        params.append('%' + nombre + '%')
    if apePaterno:
        query += " AND apeP LIKE %s"
        params.append('%' + apePaterno + '%')
    if apeMaterno:
        query += " AND apeM LIKE %s"
        params.append('%' + apeMaterno + '%')

    cur = mysql.connection.cursor()
    cur.execute(query, tuple(params))
    paciente = cur.fetchall()
    cur.close()

    if paciente:
        return render_template('vistas/mostrarPacientes.html', paciente=paciente)
    else:
        flash('No se encontraron resultados.')
        return redirect(url_for('mostrarPacientes'))

    

@app.route('/menuUser')
def menuUser():
    return render_template('menuUser.html')



@app.errorhandler(404)
def paginano(e):
    return 'Revisa tu sintaxis: No encontré nada', 404

if __name__ == '__main__':
    csrf.init_app(app)
    app.run(port=3000, debug=True, threaded=True)
