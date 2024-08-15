import MySQLdb

def execute_queries():
    # Conectar a la base de datos MySQL
    db = MySQLdb.connect(
        host="localhost",
        user="mich",
        passwd="mich",
        unix_socket="/opt/lampp/var/mysql/mysql.sock"
    )
    cursor = db.cursor()

    # Lista de consultas SQL
    queries = [
        "DROP DATABASE IF EXISTS clinicaMayo;",
        "CREATE DATABASE clinicaMayo;",
        "USE clinicaMayo;",
        """
        CREATE TABLE roles(
            id INT PRIMARY KEY AUTO_INCREMENT,
            nombre VARCHAR(50)
        );
        """,
        """
        CREATE TABLE medicos(
            id INT PRIMARY KEY AUTO_INCREMENT,
            nombres VARCHAR(50),
            apeP VARCHAR(50),
            apeM VARCHAR(50),
            RFC VARCHAR(50),
            cedula VARCHAR(50),
            correo VARCHAR(50),
            pass VARCHAR(255),  -- Cambiado a VARCHAR(255) para almacenar hashes de contraseñas
            id_rol INT,
            FOREIGN KEY (id_rol) REFERENCES roles(id) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE pacientes(
            id INT PRIMARY KEY AUTO_INCREMENT,
            nombres VARCHAR(50),
            apeP VARCHAR(50),
            apeM VARCHAR(50),
            fechaNacimiento DATE,
            antecedentes TEXT,
            alergias TEXT,
            enfermedades TEXT,
            id_medico INT,
            FOREIGN KEY (id_medico) REFERENCES medicos(id) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE citas(
            id INT PRIMARY KEY AUTO_INCREMENT,
            fecha DATE,
            peso FLOAT,
            altura FLOAT,
            temperatura FLOAT,
            oxigenacion INT,
            glucosa FLOAT,
            edad INT,
            sintomas TEXT,
            diagnostico TEXT,
            tratamiento TEXT,
            estudios TEXT,
            pdf VARCHAR(50),
            id_paciente INT,
            FOREIGN KEY (id_paciente) REFERENCES pacientes(id) ON DELETE CASCADE
        );
        """
    ]

    # Ejecutar cada consulta en la lista
    for query in queries:
        cursor.execute(query)

    # Confirmar los cambios
    db.commit()

    # Cerrar la conexión
    cursor.close()
    db.close()

if __name__ == "__main__":
    execute_queries()