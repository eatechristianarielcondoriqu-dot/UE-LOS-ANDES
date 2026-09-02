# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AsignacionDocente(models.Model):
    id_asignacion = models.AutoField(primary_key=True)
    id_maestro = models.ForeignKey('Maestro', models.DO_NOTHING, db_column='id_maestro')
    id_curso = models.ForeignKey('Curso', models.DO_NOTHING, db_column='id_curso')
    id_materia = models.ForeignKey('Materia', models.DO_NOTHING, db_column='id_materia')
    id_gestion = models.ForeignKey('Gestion', models.DO_NOTHING, db_column='id_gestion')

    class Meta:
        managed = False
        db_table = 'asignacion_docente'


class Asistencia(models.Model):
    id_asistencia = models.AutoField(primary_key=True)
    id_estudiante = models.ForeignKey('Estudiante', models.DO_NOTHING, db_column='id_estudiante')
    id_materia = models.ForeignKey('Materia', models.DO_NOTHING, db_column='id_materia')
    fecha = models.DateField()
    estado = models.TextField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'asistencia'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Curso(models.Model):
    id_curso = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    nivel = models.CharField(max_length=20)
    paralelo = models.CharField(max_length=5)

    class Meta:
        managed = False
        db_table = 'curso'


class CursoMateria(models.Model):
    id_curso_materia = models.AutoField(primary_key=True)
    id_curso = models.ForeignKey(Curso, models.DO_NOTHING, db_column='id_curso')
    id_materia = models.ForeignKey('Materia', models.DO_NOTHING, db_column='id_materia')

    class Meta:
        managed = False
        db_table = 'curso_materia'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class DocumentoJustificacion(models.Model):
    id_documento = models.AutoField(primary_key=True)
    id_padre = models.ForeignKey('PadreFamilia', models.DO_NOTHING, db_column='id_padre')
    id_estudiante = models.ForeignKey('Estudiante', models.DO_NOTHING, db_column='id_estudiante')
    id_aprobado_por = models.ForeignKey('PersonalAdministrativo', models.DO_NOTHING, db_column='id_aprobado_por', blank=True, null=True)
    tipo = models.TextField()  # This field type is a guess.
    motivo = models.TextField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    archivo_url = models.CharField(max_length=500, blank=True, null=True)
    estado = models.TextField(blank=True, null=True)  # This field type is a guess.
    fecha_subida = models.DateTimeField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'documento_justificacion'


class EntregaTarea(models.Model):
    id_entrega = models.AutoField(primary_key=True)
    id_tarea = models.ForeignKey('Tarea', models.DO_NOTHING, db_column='id_tarea')
    id_estudiante = models.ForeignKey('Estudiante', models.DO_NOTHING, db_column='id_estudiante')
    estado = models.TextField()  # This field type is a guess.
    calificacion = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'entrega_tarea'


class Estudiante(models.Model):
    id_student = models.AutoField(primary_key=True)
    id_persona = models.OneToOneField('Persona', models.DO_NOTHING, db_column='id_persona')
    codigo_rude = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'estudiante'


class EstudiantePadre(models.Model):
    id_estudiante_padre = models.AutoField(primary_key=True)
    id_estudiante = models.ForeignKey(Estudiante, models.DO_NOTHING, db_column='id_estudiante')
    id_padre = models.ForeignKey('PadreFamilia', models.DO_NOTHING, db_column='id_padre')
    parentesco = models.TextField()  # This field type is a guess.
    es_tutor = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'estudiante_padre'


class Gestion(models.Model):
    id_gestion = models.AutoField(primary_key=True)
    anio = models.IntegerField(unique=True)
    activa = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'gestion'


class Horario(models.Model):
    id_horario = models.AutoField(primary_key=True)
    id_materia = models.ForeignKey('Materia', models.DO_NOTHING, db_column='id_materia')
    id_maestro = models.ForeignKey('Maestro', models.DO_NOTHING, db_column='id_maestro')
    dia_semana = models.TextField()  # This field type is a guess.
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    aula = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'horario'


class Inscripcion(models.Model):
    id_inscripcion = models.AutoField(primary_key=True)
    id_estudiante = models.ForeignKey(Estudiante, models.DO_NOTHING, db_column='id_estudiante')
    id_curso = models.ForeignKey(Curso, models.DO_NOTHING, db_column='id_curso')
    id_gestion = models.ForeignKey(Gestion, models.DO_NOTHING, db_column='id_gestion')
    fecha_inscripcion = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'inscripcion'


class Maestro(models.Model):
    id_maestro = models.AutoField(primary_key=True)
    id_persona = models.ForeignKey('Persona', models.DO_NOTHING, db_column='id_persona')
    especialidad = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'maestro'


class Materia(models.Model):
    id_materia = models.AutoField(primary_key=True)
    nombre_materia = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'materia'


class PadreFamilia(models.Model):
    id_padre = models.AutoField(primary_key=True)
    id_persona = models.ForeignKey('Persona', models.DO_NOTHING, db_column='id_persona')
    ocupacion = models.CharField(max_length=100, blank=True, null=True)
    firma_base = models.ImageField(upload_to='firmas_padres/', blank=True, null=True, verbose_name="Firma Patrón")
    
    class Meta:
        managed = False
        db_table = 'padre_familia'


class Persona(models.Model):
    id_persona = models.AutoField(primary_key=True)
    dni_cedula = models.CharField(unique=True, max_length=20)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    genero = models.CharField(max_length=1)
    fecha_nacimiento = models.DateField()
    telefono = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'persona'


class PersonalAdministrativo(models.Model):
    id_admin = models.AutoField(primary_key=True)
    id_persona = models.ForeignKey(Persona, models.DO_NOTHING, db_column='id_persona')
    cargo = models.TextField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'personal_administrativo'


class Rol(models.Model):
    id_rol = models.AutoField(primary_key=True)
    nombre_rol = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'rol'


class Tarea(models.Model):
    id_tarea = models.AutoField(primary_key=True)
    id_materia = models.ForeignKey(Materia, models.DO_NOTHING, db_column='id_materia')
    id_maestro = models.ForeignKey(Maestro, models.DO_NOTHING, db_column='id_maestro')
    titulo = models.CharField(max_length=200)
    fecha_entrega = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tarea'


class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    id_persona = models.ForeignKey(Persona, models.DO_NOTHING, db_column='id_persona')
    id_role = models.ForeignKey(Rol, models.DO_NOTHING, db_column='id_role')
    username = models.CharField(unique=True, max_length=50)
    password = models.CharField(max_length=255)
    activo = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'usuario'
