drop database if exists clinicaMayo;
create database clinicaMayo;
use clinicaMayo;

create table medicos(
	id int primary key auto_increment,
    nombres varchar(50),
    apeP varchar(50),
    apeM varchar(50),
    RFC varchar(50),
    cedula varchar(50),
    correo varchar(50),
    pass varchar(50),
    rol int
);

create table pacientes (
	id int primary key auto_increment,
    nombres varchar(50),
    apeP varchar(50),
    apeM varchar(50),
    fechaNacimiento date,
    antecedentes text,
    alergias text,
    enfermedades text,
    id_medico int,
    
    foreign key (id_medico) references medicos(id) on delete cascade
);

create table citas (
	id int primary key auto_increment,
    fecha date,
    peso float,
    altura float,
    temperatura float,
    bpm int,
    oxigenacion int,
    glucosa float,
    edad int,
    sintomas text,
    diagnostico text,
    tratamiento text,
    estudios text,
    pdf varchar(50),
    id_paciente int,
    
    foreign key (id_paciente) references pacientes(id) on delete cascade
);


insert into medicos(nombres, apeP ,apeM ,RFC ,cedula ,correo , pass ,rol)
values 
('María','Barrera','Everardo','asdjnasnjdad','sasds','maria@gmail.com','admin123',1);