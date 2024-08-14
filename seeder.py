import MySQLdb
from werkzeug.security import generate_password_hash

def seed():
    db = MySQLdb.connect(
        host="localhost",
        user= "root",
        passwd= "",
        unix_socket= "/opt/lampp/var/mysql/mysql.sock"
    )
    cursor = db.cursor()
    db.select_db("clinicaMayo")
    #Roles
    cursor.execute("INSERT INTO roles (nombre) VALUES ('Administrador')")
    cursor.execute("INSERT INTO roles (nombre) VALUES ('Médico')")

    #Obtener ids de roles
    cursor.execute("SELECT id FROM roles WHERE nombre='Administrador'")
    id_admin = cursor.fetchone()[0]
    cursor.execute("SELECT id FROM roles WHERE nombre='Médico'")
    id_medico = cursor.fetchone()[0]

    contrasena = generate_password_hash("password123")

    cursor.execute("INSERT INTO medicos (nombres, apeP, apeM, RFC, cedula, correo, pass, id_rol) VALUES ('Juan', 'Perez', 'Lopez', '123456789', '123456', 'juan@juan.com', %s, %s)", (contrasena, id_admin))

    cursor.execute("INSERT INTO medicos (nombres, apeP, apeM, RFC, cedula, correo, pass, id_rol) VALUES ('Pedro', 'Gomez', 'Hernandez', '987654321', '654321', 'pedro@pedro.com', %s, %s)", (contrasena, id_medico))

    db.commit()
    cursor.close()
    db.close()

if __name__ == "__main__":
    seed()



