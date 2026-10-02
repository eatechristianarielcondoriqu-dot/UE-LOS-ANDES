-- Script 02: datos de prueba (ejecutar sobre una base recién creada)
INSERT INTO rol (nombre_rol) VALUES ('director'), ('administrativo'), ('maestro'), ('padre_familia');

INSERT INTO persona (dni_cedula, nombres, apellidos, genero, fecha_nacimiento, telefono) VALUES
 ('4567890', 'Roberto', 'Mamani Quispe',  'M', '1975-03-12', '70111111'),  -- 1 director
 ('5123456', 'Lucía',   'Flores Choque',  'F', '1988-07-21', '70222222'),  -- 2 secretaria
 ('6234567', 'Carla',   'Mendoza Huanca', 'F', '1985-11-05', '70333333'),  -- 3 maestra
 ('3345678', 'Juan',    'Apaza Mamani',   'M', '1980-01-30', '70444444'),  -- 4 padre
 ('3456789', 'Rosa',    'Condori Ticona', 'F', '1982-09-14', '70555555'),  -- 5 madre
 ('9100001', 'Mateo',   'Apaza Rojas',    'M', '2011-05-02', NULL),        -- 6 estudiante
 ('9100002', 'Valeria', 'Quispe Condori', 'F', '2011-08-19', NULL),        -- 7 estudiante
 ('9100003', 'Luis',    'Quispe Condori', 'M', '2012-02-27', NULL);        -- 8 estudiante

INSERT INTO usuario (id_persona, id_rol, username, password) VALUES
 (1, 1, 'rmamani',  'hash_bcrypt_demo'),
 (2, 2, 'lflores',  'hash_bcrypt_demo'),
 (3, 3, 'cmendoza', 'hash_bcrypt_demo'),
 (4, 4, 'japaza',   'hash_bcrypt_demo'),
 (5, 4, 'rcondori', 'hash_bcrypt_demo');

INSERT INTO padre_familia (id_persona, ocupacion) VALUES (4, 'Comerciante'), (5, 'Costurera');
INSERT INTO maestro (id_persona, especialidad) VALUES (3, 'Matemática y Lenguaje');
INSERT INTO personal_administrativo (id_persona, cargo) VALUES (1, 'director'), (2, 'secretaria');
INSERT INTO estudiante (id_persona, codigo_rude) VALUES (6, 'RUDE-0001'), (7, 'RUDE-0002'), (8, 'RUDE-0003');

INSERT INTO estudiante_padre (id_estudiante, id_padre, parentesco, es_tutor) VALUES
 (1, 1, 'padre', TRUE), (2, 2, 'madre', TRUE), (3, 2, 'madre', TRUE);

INSERT INTO gestion (anio, activa) VALUES (2026, TRUE);
INSERT INTO curso   (nombre, nivel, paralelo) VALUES ('1ro Secundaria', 'secundaria', 'A');
INSERT INTO materia (nombre_materia) VALUES ('Matemática'), ('Lenguaje');
INSERT INTO curso_materia (id_curso, id_materia) VALUES (1, 1), (1, 2);
INSERT INTO asignacion_docente (id_maestro, id_curso, id_materia, id_gestion) VALUES (1, 1, 1, 1), (1, 1, 2, 1);
INSERT INTO inscripcion (id_estudiante, id_curso, id_gestion) VALUES (1, 1, 1), (2, 1, 1), (3, 1, 1);
INSERT INTO horario (id_materia, id_maestro, dia_semana, hora_inicio, hora_fin, aula) VALUES
 (1, 1, 'lunes', '08:00', '09:30', 'Aula 3'), (2, 1, 'martes', '08:00', '09:30', 'Aula 3');

INSERT INTO tarea (id_materia, id_maestro, id_curso, titulo, descripcion, fecha_entrega) VALUES
 (1, 1, 1, 'Ecuaciones lineales', 'Resolver los ejercicios 1 al 10', '2026-09-15'),
 (2, 1, 1, 'Ensayo sobre la identidad', 'Entregar un ensayo de dos páginas', '2026-09-22');

INSERT INTO entrega_tarea (id_tarea, id_estudiante, estado, calificacion) VALUES
 (1, 1, 'calificada', 90), (1, 2, 'pendiente', NULL), (1, 3, 'atrasada', NULL),
 (2, 1, 'calificada', 85), (2, 2, 'calificada', 70), (2, 3, 'pendiente', NULL);

INSERT INTO asistencia (id_estudiante, id_materia, fecha, estado) VALUES
 (1, 1, '2026-09-01', 'presente'), (1, 1, '2026-09-08', 'presente'),
 (2, 1, '2026-09-01', 'presente'), (2, 1, '2026-09-08', 'ausente'),
 (3, 1, '2026-09-01', 'ausente'),  (3, 1, '2026-09-08', 'ausente'), (3, 1, '2026-09-15', 'ausente');

INSERT INTO documento_justificacion
 (id_padre, id_estudiante, id_aprobado_por, tipo, motivo, fecha_inicio, fecha_fin, estado) VALUES
 (2, 2, 1,    'licencia_medica', 'Consulta médica programada', '2026-09-08', '2026-09-08', 'aprobado'),
 (2, 3, NULL, 'permiso',         'Viaje familiar',             '2026-10-05', '2026-10-07', 'pendiente');

INSERT INTO calificacion (id_estudiante, id_materia, id_gestion, id_maestro, trimestre,
                          nota_ser, nota_saber, nota_hacer, nota_decidir, autoevaluacion) VALUES
 (1, 1, 1, 1, 1, 5, 40, 35, 5, 5),
 (2, 1, 1, 1, 1, 4, 30, 28, 4, 4),
 (3, 1, 1, 1, 1, 3, 18, 15, 3, 3),
 (3, 1, 1, 1, 2, 4, 15, 12, 3, 3),
 (3, 2, 1, 1, 1, 3, 20, 18, 3, 3);

INSERT INTO pronostico_academico (id_estudiante, id_gestion, trimestre, cluster, nivel_rendimiento, riesgo_reprobacion, alerta_generada) VALUES
 (1, 1, 1, 0, 'alto',  'bajo',  FALSE),
 (2, 1, 1, 1, 'medio', 'medio', FALSE),
 (3, 1, 1, 2, 'bajo',  'alto',  TRUE);

INSERT INTO notificacion (id_emisor, id_destinatario, tipo, asunto, mensaje) VALUES
 (NULL, 5, 'alerta_temprana', 'Alerta académica', 'Su hijo Luis presenta riesgo alto de reprobación en Matemática.'),
 (1,    4, 'aviso_general',   'Reunión de padres', 'Se convoca a reunión el viernes a las 15:00.');
