DROP SCHEMA escalas;
CREATE SCHEMA escalas;
USE ESCALAS;

-- Script para criar a tabela 'departamentos'
CREATE TABLE departamentos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    departamento VARCHAR(255) NOT NULL
);

-- Script para criar a tabela 'cargos'
CREATE TABLE cargos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    cargo VARCHAR(255) NOT NULL,
    departamento_id INT,
    carga_horaria INT,
    FOREIGN KEY (departamento_id) REFERENCES departamentos(id)
);

-- Script para criar a tabela 'funcionarios'
CREATE TABLE funcionarios (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(255) NOT NULL,
    cargo_id INT,
    FOREIGN KEY (cargo_id) REFERENCES cargos(id)
);

-- Script para criar a tabela 'turnos'
CREATE TABLE turnos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    tipo VARCHAR(255) NOT NULL,
    horario_inicio TIME NOT NULL,
    horario_fim TIME NOT NULL
);

-- Script para criar a tabela 'semanas'
CREATE TABLE semanas (
    id INT PRIMARY KEY AUTO_INCREMENT,
    data_inicio DATE NOT NULL,
    data_fim DATE NOT NULL
);

-- Script para criar a tabela 'escalas'
CREATE TABLE escalas (
    id INT PRIMARY KEY AUTO_INCREMENT,
    semana_id INT,
    funcionario_id INT,
    turno_id INT,
    data DATE NOT NULL,
    observacao VARCHAR(255),
    FOREIGN KEY (semana_id) REFERENCES semanas(id),
    FOREIGN KEY (funcionario_id) REFERENCES funcionarios(id),
    FOREIGN KEY (turno_id) REFERENCES turnos(id)
);


SHOW VARIABLES LIKE 'bind_address';
