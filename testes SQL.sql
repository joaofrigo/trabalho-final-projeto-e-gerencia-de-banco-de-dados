
-- Inserir um novo departamento
INSERT INTO departamentos (departamento) VALUES ('Recursos Humanos');

-- Inserir um novo cargo relacionado a esse departamento
INSERT INTO cargos (cargo, departamento_id, carga_horaria) VALUES ('Analista', 1, 40);

-- Inserir um novo funcionário associado ao cargo
INSERT INTO funcionarios (nome, cargo_id) VALUES ('João Silva', 1);

-- Inserir um turno (exemplo de turno para a escala)
INSERT INTO turnos (tipo, horario_inicio, horario_fim) VALUES ('Manhã', '08:00:00', '12:00:00');

-- Inserir uma nova semana (exemplo de período da semana)
INSERT INTO semanas (data_inicio, data_fim) VALUES ('2024-12-01', '2024-12-07');

-- Inserir uma escala para o funcionário
INSERT INTO escalas (semana_id, funcionario_id, turno_id, data, observacao)
VALUES (1, 2, 1, '2024-12-01', 'Treinamento de integração');

SELECT funcionarios.nome, cargos.cargo, departamentos.departamento
FROM funcionarios
JOIN cargos ON funcionarios.cargo_id = cargos.id
JOIN departamentos ON cargos.departamento_id = departamentos.id
WHERE funcionarios.id = 1;

SELECT escalas.data, turnos.tipo, escalas.observacao
FROM escalas
JOIN turnos ON escalas.turno_id = turnos.id
WHERE escalas.funcionario_id = 1;

DELETE FROM escalas WHERE semana_id IN (SELECT id FROM semanas);
DELETE FROM semanas;






/*
         SELECT 
            funcionarios.id,
            funcionarios.nome,
            cargos.cargo,
            turnos.tipo,
            escalas.data,
            escalas.observacao
        FROM 
            funcionarios
        JOIN 
            cargos ON funcionarios.cargo_id = cargos.id
        JOIN 
            escalas ON funcionarios.id = escalas.funcionario_id
        JOIN 
            turnos ON escalas.turno_id = turnos.id
*/