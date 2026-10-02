-- ============================================================
-- Sistema web de seguimiento y control académico - U.E. Los Andes
-- Script 01: tipos ENUM y tablas (PostgreSQL 14+)
-- ============================================================

-- Tipos enumerados
CREATE TYPE cargo_admin       AS ENUM ('director', 'secretaria', 'regente', 'apoyo_tecnico');
CREATE TYPE parentesco_tipo   AS ENUM ('padre', 'madre', 'tutor', 'abuelo', 'tio', 'otro');
CREATE TYPE nivel_educativo   AS ENUM ('primaria', 'secundaria');
CREATE TYPE dia_semana_tipo   AS ENUM ('lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado');
CREATE TYPE estado_entrega    AS ENUM ('pendiente', 'entregada', 'atrasada', 'calificada');
CREATE TYPE estado_asistencia AS ENUM ('presente', 'ausente', 'atraso', 'licencia');
CREATE TYPE tipo_documento    AS ENUM ('permiso', 'licencia_medica', 'justificativo');
CREATE TYPE estado_documento  AS ENUM ('pendiente', 'aprobado', 'rechazado');
CREATE TYPE tipo_notificacion AS ENUM ('aviso_general', 'alerta_temprana', 'permiso', 'nota');
CREATE TYPE nivel_alerta      AS ENUM ('bajo', 'medio', 'alto');

-- 1. rol
CREATE TABLE rol (
    id_rol      SERIAL PRIMARY KEY,
    nombre_rol  VARCHAR(50) NOT NULL UNIQUE
);

-- 2. persona (superclase de todos los actores)
CREATE TABLE persona (
    id_persona       SERIAL PRIMARY KEY,
    dni_cedula       VARCHAR(20)  NOT NULL UNIQUE,
    nombres          VARCHAR(100) NOT NULL,
    apellidos        VARCHAR(100) NOT NULL,
    genero           CHAR(1) CHECK (genero IN ('M', 'F')),
    fecha_nacimiento DATE,
    telefono         VARCHAR(20)
);

-- 3. usuario
CREATE TABLE usuario (
    id_usuario  SERIAL PRIMARY KEY,
    id_persona  INTEGER      NOT NULL UNIQUE REFERENCES persona(id_persona),
    id_rol      INTEGER      NOT NULL REFERENCES rol(id_rol),
    username    VARCHAR(50)  NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,
    activo      BOOLEAN      NOT NULL DEFAULT TRUE
);

-- 4. padre_familia
CREATE TABLE padre_familia (
    id_padre    SERIAL PRIMARY KEY,
    id_persona  INTEGER NOT NULL UNIQUE REFERENCES persona(id_persona),
    ocupacion   VARCHAR(100)
);

-- 5. maestro
CREATE TABLE maestro (
    id_maestro    SERIAL PRIMARY KEY,
    id_persona    INTEGER NOT NULL UNIQUE REFERENCES persona(id_persona),
    especialidad  VARCHAR(100)
);

-- 6. personal_administrativo
CREATE TABLE personal_administrativo (
    id_admin    SERIAL PRIMARY KEY,
    id_persona  INTEGER NOT NULL UNIQUE REFERENCES persona(id_persona),
    cargo       cargo_admin NOT NULL
);

-- 7. estudiante
CREATE TABLE estudiante (
    id_estudiante  SERIAL PRIMARY KEY,
    id_persona     INTEGER     NOT NULL UNIQUE REFERENCES persona(id_persona),
    codigo_rude    VARCHAR(20) NOT NULL UNIQUE
);

-- 8. estudiante_padre (tabla intermedia N:M)
CREATE TABLE estudiante_padre (
    id_estudiante_padre  SERIAL PRIMARY KEY,
    id_estudiante        INTEGER NOT NULL REFERENCES estudiante(id_estudiante),
    id_padre             INTEGER NOT NULL REFERENCES padre_familia(id_padre),
    parentesco           parentesco_tipo NOT NULL,
    es_tutor             BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (id_estudiante, id_padre)
);

-- 9. materia
CREATE TABLE materia (
    id_materia      SERIAL PRIMARY KEY,
    nombre_materia  VARCHAR(100) NOT NULL UNIQUE
);

-- 10. gestion
CREATE TABLE gestion (
    id_gestion  SERIAL PRIMARY KEY,
    anio        INTEGER NOT NULL UNIQUE,
    activa      BOOLEAN NOT NULL DEFAULT FALSE
);

-- 11. curso
CREATE TABLE curso (
    id_curso  SERIAL PRIMARY KEY,
    nombre    VARCHAR(50) NOT NULL,
    nivel     nivel_educativo NOT NULL,
    paralelo  CHAR(1) NOT NULL,
    UNIQUE (nombre, nivel, paralelo)
);

-- 12. inscripcion
CREATE TABLE inscripcion (
    id_inscripcion     SERIAL PRIMARY KEY,
    id_estudiante      INTEGER NOT NULL REFERENCES estudiante(id_estudiante),
    id_curso           INTEGER NOT NULL REFERENCES curso(id_curso),
    id_gestion         INTEGER NOT NULL REFERENCES gestion(id_gestion),
    fecha_inscripcion  DATE NOT NULL DEFAULT CURRENT_DATE,
    UNIQUE (id_estudiante, id_gestion)
);

-- 13. curso_materia (malla curricular)
CREATE TABLE curso_materia (
    id_curso_materia  SERIAL PRIMARY KEY,
    id_curso          INTEGER NOT NULL REFERENCES curso(id_curso),
    id_materia        INTEGER NOT NULL REFERENCES materia(id_materia),
    UNIQUE (id_curso, id_materia)
);

-- 14. asignacion_docente
CREATE TABLE asignacion_docente (
    id_asignacion  SERIAL PRIMARY KEY,
    id_maestro     INTEGER NOT NULL REFERENCES maestro(id_maestro),
    id_curso       INTEGER NOT NULL REFERENCES curso(id_curso),
    id_materia     INTEGER NOT NULL REFERENCES materia(id_materia),
    id_gestion     INTEGER NOT NULL REFERENCES gestion(id_gestion),
    UNIQUE (id_curso, id_materia, id_gestion)
);

-- 15. horario
CREATE TABLE horario (
    id_horario   SERIAL PRIMARY KEY,
    id_materia   INTEGER NOT NULL REFERENCES materia(id_materia),
    id_maestro   INTEGER NOT NULL REFERENCES maestro(id_maestro),
    dia_semana   dia_semana_tipo NOT NULL,
    hora_inicio  TIME NOT NULL,
    hora_fin     TIME NOT NULL,
    aula         VARCHAR(30),
    CHECK (hora_fin > hora_inicio)
);

-- 16. tarea
CREATE TABLE tarea (
    id_tarea       SERIAL PRIMARY KEY,
    id_materia     INTEGER NOT NULL REFERENCES materia(id_materia),
    id_maestro     INTEGER NOT NULL REFERENCES maestro(id_maestro),
    id_curso       INTEGER NOT NULL REFERENCES curso(id_curso),
    titulo         VARCHAR(150) NOT NULL,
    descripcion    TEXT,
    fecha_entrega  DATE NOT NULL
);

-- 17. entrega_tarea
CREATE TABLE entrega_tarea (
    id_entrega     SERIAL PRIMARY KEY,
    id_tarea       INTEGER NOT NULL REFERENCES tarea(id_tarea),
    id_estudiante  INTEGER NOT NULL REFERENCES estudiante(id_estudiante),
    estado         estado_entrega NOT NULL DEFAULT 'pendiente',
    calificacion   INTEGER CHECK (calificacion BETWEEN 0 AND 100),
    UNIQUE (id_tarea, id_estudiante)
);

-- 18. asistencia
CREATE TABLE asistencia (
    id_asistencia  SERIAL PRIMARY KEY,
    id_estudiante  INTEGER NOT NULL REFERENCES estudiante(id_estudiante),
    id_materia     INTEGER NOT NULL REFERENCES materia(id_materia),
    fecha          DATE NOT NULL DEFAULT CURRENT_DATE,
    estado         estado_asistencia NOT NULL,
    UNIQUE (id_estudiante, id_materia, fecha)
);

-- 19. documento_justificacion
CREATE TABLE documento_justificacion (
    id_documento     SERIAL PRIMARY KEY,
    id_padre         INTEGER NOT NULL REFERENCES padre_familia(id_padre),
    id_estudiante    INTEGER NOT NULL REFERENCES estudiante(id_estudiante),
    id_aprobado_por  INTEGER REFERENCES personal_administrativo(id_admin),
    tipo             tipo_documento NOT NULL,
    motivo           TEXT NOT NULL,
    fecha_inicio     DATE NOT NULL,
    fecha_fin        DATE NOT NULL,
    archivo_url      VARCHAR(255),
    estado           estado_documento NOT NULL DEFAULT 'pendiente',
    fecha_subida     TIMESTAMP NOT NULL DEFAULT NOW(),
    observaciones    TEXT,
    CHECK (fecha_fin >= fecha_inicio)
);

-- ===== Tablas de ampliación (módulos del proyecto no incluidos en el diagrama base) =====

-- 20. calificacion (4 dimensiones + autoevaluación = 100 puntos)
CREATE TABLE calificacion (
    id_calificacion  SERIAL PRIMARY KEY,
    id_estudiante    INTEGER NOT NULL REFERENCES estudiante(id_estudiante),
    id_materia       INTEGER NOT NULL REFERENCES materia(id_materia),
    id_gestion       INTEGER NOT NULL REFERENCES gestion(id_gestion),
    id_maestro       INTEGER NOT NULL REFERENCES maestro(id_maestro),
    trimestre        SMALLINT NOT NULL CHECK (trimestre BETWEEN 1 AND 3),
    nota_ser         INTEGER NOT NULL DEFAULT 0 CHECK (nota_ser     BETWEEN 0 AND 5),
    nota_saber       INTEGER NOT NULL DEFAULT 0 CHECK (nota_saber   BETWEEN 0 AND 45),
    nota_hacer       INTEGER NOT NULL DEFAULT 0 CHECK (nota_hacer   BETWEEN 0 AND 40),
    nota_decidir     INTEGER NOT NULL DEFAULT 0 CHECK (nota_decidir BETWEEN 0 AND 5),
    autoevaluacion   INTEGER NOT NULL DEFAULT 0 CHECK (autoevaluacion BETWEEN 0 AND 5),
    nota_total       INTEGER GENERATED ALWAYS AS
                     (nota_ser + nota_saber + nota_hacer + nota_decidir + autoevaluacion) STORED,
    UNIQUE (id_estudiante, id_materia, id_gestion, trimestre)
);

-- 21. notificacion (id_emisor NULL = generada por el sistema)
CREATE TABLE notificacion (
    id_notificacion  SERIAL PRIMARY KEY,
    id_emisor        INTEGER REFERENCES usuario(id_usuario),
    id_destinatario  INTEGER NOT NULL REFERENCES usuario(id_usuario),
    tipo             tipo_notificacion NOT NULL,
    asunto           VARCHAR(150) NOT NULL,
    mensaje          TEXT NOT NULL,
    leida            BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_envio      TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 22. pronostico_academico (resultado del módulo de aprendizaje no supervisado)
CREATE TABLE pronostico_academico (
    id_pronostico        SERIAL PRIMARY KEY,
    id_estudiante        INTEGER NOT NULL REFERENCES estudiante(id_estudiante),
    id_gestion           INTEGER NOT NULL REFERENCES gestion(id_gestion),
    trimestre            SMALLINT NOT NULL CHECK (trimestre BETWEEN 1 AND 3),
    cluster              INTEGER NOT NULL,
    nivel_rendimiento    nivel_alerta NOT NULL,
    riesgo_reprobacion   nivel_alerta NOT NULL,
    alerta_generada      BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_generacion     TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (id_estudiante, id_gestion, trimestre)
);
