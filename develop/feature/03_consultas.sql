-- Script 03: consultas SELECT del proyecto

-- C1. Estudiantes En Desarrollo (<= 50 puntos) en el trimestre 1 de la gestión activa
SELECT pe.apellidos, pe.nombres, m.nombre_materia, c.trimestre, c.nota_total,
       CASE WHEN c.nota_total <= 50 THEN 'En Desarrollo (ED)'
            WHEN c.nota_total <= 68 THEN 'Desarrollo Aceptable (DA)'
            WHEN c.nota_total <= 84 THEN 'Desarrollo Óptimo (DO)'
            ELSE 'Desarrollo Pleno (DP)' END AS valoracion
FROM calificacion c
JOIN estudiante e ON e.id_estudiante = c.id_estudiante
JOIN persona pe   ON pe.id_persona   = e.id_persona
JOIN materia m    ON m.id_materia    = c.id_materia
JOIN gestion g    ON g.id_gestion    = c.id_gestion
WHERE g.activa = TRUE AND c.trimestre = 1 AND c.nota_total <= 50
ORDER BY c.nota_total ASC;

-- C2. Estudiantes con 3 o más inasistencias sin justificación aprobada
SELECT pe.apellidos, pe.nombres, COUNT(*) AS inasistencias_sin_justificar
FROM asistencia a
JOIN estudiante e ON e.id_estudiante = a.id_estudiante
JOIN persona pe   ON pe.id_persona   = e.id_persona
WHERE a.estado = 'ausente'
  AND NOT EXISTS (SELECT 1
                  FROM documento_justificacion d
                  WHERE d.id_estudiante = a.id_estudiante
                    AND d.estado = 'aprobado'
                    AND a.fecha BETWEEN d.fecha_inicio AND d.fecha_fin)
GROUP BY e.id_estudiante, pe.apellidos, pe.nombres
HAVING COUNT(*) >= 3
ORDER BY inasistencias_sin_justificar DESC;

-- C3. Cantidad de tareas vencidas sin entregar por estudiante
SELECT pe.apellidos, pe.nombres, COUNT(*) AS tareas_vencidas
FROM entrega_tarea et
JOIN tarea t      ON t.id_tarea      = et.id_tarea
JOIN estudiante e ON e.id_estudiante = et.id_estudiante
JOIN persona pe   ON pe.id_persona   = e.id_persona
WHERE et.estado IN ('pendiente', 'atrasada')
  AND t.fecha_entrega < CURRENT_DATE
GROUP BY e.id_estudiante, pe.apellidos, pe.nombres
ORDER BY tareas_vencidas DESC;

-- C4. Permisos y licencias pendientes de aprobación
SELECT d.id_documento,
       pe.apellidos || ' ' || pe.nombres AS estudiante,
       pp.apellidos || ' ' || pp.nombres AS solicitante,
       d.tipo, d.fecha_inicio, d.fecha_fin, d.motivo
FROM documento_justificacion d
JOIN estudiante e    ON e.id_estudiante = d.id_estudiante
JOIN persona pe      ON pe.id_persona   = e.id_persona
JOIN padre_familia pf ON pf.id_padre    = d.id_padre
JOIN persona pp      ON pp.id_persona   = pf.id_persona
WHERE d.estado = 'pendiente'
ORDER BY d.fecha_subida;

-- C5. Estudiantes con riesgo alto de reprobación y teléfono de su tutor
SELECT pe.apellidos, pe.nombres, cu.nombre AS curso, cu.paralelo,
       pr.cluster, pr.riesgo_reprobacion, pt.telefono AS telefono_tutor
FROM pronostico_academico pr
JOIN estudiante e   ON e.id_estudiante = pr.id_estudiante
JOIN persona pe     ON pe.id_persona   = e.id_persona
JOIN inscripcion i  ON i.id_estudiante = e.id_estudiante AND i.id_gestion = pr.id_gestion
JOIN curso cu       ON cu.id_curso     = i.id_curso
LEFT JOIN estudiante_padre ep ON ep.id_estudiante = e.id_estudiante AND ep.es_tutor = TRUE
LEFT JOIN padre_familia pf    ON pf.id_padre      = ep.id_padre
LEFT JOIN persona pt          ON pt.id_persona    = pf.id_persona
WHERE pr.riesgo_reprobacion = 'alto'
ORDER BY pr.fecha_generacion DESC;

-- C6. Estudiantes con promedio anual menor a 51 en alguna materia (riesgo de retención)
SELECT pe.apellidos, pe.nombres, m.nombre_materia,
       ROUND(AVG(c.nota_total), 0) AS promedio_parcial
FROM calificacion c
JOIN estudiante e ON e.id_estudiante = c.id_estudiante
JOIN persona pe   ON pe.id_persona   = e.id_persona
JOIN materia m    ON m.id_materia    = c.id_materia
JOIN gestion g    ON g.id_gestion    = c.id_gestion
WHERE g.activa = TRUE
GROUP BY e.id_estudiante, pe.apellidos, pe.nombres, m.id_materia, m.nombre_materia
HAVING AVG(c.nota_total) < 51
ORDER BY promedio_parcial ASC;

-- C7. Características por estudiante para el módulo de aprendizaje no supervisado (K-Means)
WITH asis AS (
    SELECT id_estudiante, COUNT(*) AS total,
           COUNT(*) FILTER (WHERE estado <> 'ausente') AS presentes
    FROM asistencia GROUP BY id_estudiante),
nota AS (
    SELECT id_estudiante, AVG(nota_total) AS promedio
    FROM calificacion GROUP BY id_estudiante),
tar AS (
    SELECT id_estudiante, COUNT(*) AS total,
           COUNT(*) FILTER (WHERE estado IN ('entregada', 'calificada')) AS entregadas
    FROM entrega_tarea GROUP BY id_estudiante)
SELECT e.id_estudiante,
       ROUND(100.0 * COALESCE(a.presentes, 0)
             / NULLIF(a.total, 0), 1)   AS pct_asistencia,
       ROUND(n.promedio, 1)             AS promedio_notas,
       ROUND(100.0 * COALESCE(t.entregadas, 0)
             / NULLIF(t.total, 0), 1)   AS pct_tareas_entregadas
FROM estudiante e
LEFT JOIN asis a ON a.id_estudiante = e.id_estudiante
LEFT JOIN nota n ON n.id_estudiante = e.id_estudiante
LEFT JOIN tar  t ON t.id_estudiante = e.id_estudiante
ORDER BY e.id_estudiante;
