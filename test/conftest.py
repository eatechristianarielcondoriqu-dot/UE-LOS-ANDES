"""
conftest.py - Configuración global de fixtures para pytest
Sistema Web Inteligente de Gestión y Control Estudiantil
Unidad Educativa Los Andes
"""

import pytest
from datetime import datetime, timedelta


# ============================================================================
# FIXTURES - Datos simulados para pruebas
# ============================================================================

@pytest.fixture
def app_config():
    """Configuración base de la aplicación"""
    return {
        'app_name': 'SistemaUELosAndes',
        'version': '1.0.0',
        'environment': 'testing',
        'database': 'postgresql://test:test@localhost/ue_losandes_test',
        'debug': True
    }


@pytest.fixture
def test_user_director():
    """Usuario director para pruebas"""
    return {
        'id': 1,
        'email': 'director@uelosandes.edu.bo',
        'password': 'SecureDir2024!',
        'nombre': 'Dr. Juan García',
        'rol': 'director',
        'estado': 'activo'
    }


@pytest.fixture
def test_user_docente():
    """Usuario docente para pruebas"""
    return {
        'id': 2,
        'email': 'profesor@uelosandes.edu.bo',
        'password': 'ProfPass2024!',
        'nombre': 'Lic. Maria Condori',
        'rol': 'docente',
        'materia': 'Matemáticas',
        'estado': 'activo'
    }


@pytest.fixture
def test_user_administrativo():
    """Usuario administrativo para pruebas"""
    return {
        'id': 3,
        'email': 'admin@uelosandes.edu.bo',
        'password': 'AdminPass2024!',
        'nombre': 'Sr. Carlos López',
        'rol': 'administrativo',
        'estado': 'activo'
    }


@pytest.fixture
def test_user_padre():
    """Usuario padre de familia para pruebas"""
    return {
        'id': 4,
        'email': 'padre@correo.com',
        'password': 'PadrePass2024!',
        'nombre': 'Srta. Rosa Mamani',
        'rol': 'padre',
        'estado': 'activo'
    }


@pytest.fixture
def test_estudiante():
    """Estudiante para pruebas"""
    return {
        'id': 101,
        'nombre': 'Luis Felipe Quispe',
        'apellido': 'Quispe Mamani',
        'ci': '12345678',
        'grado': '6to B',
        'fecha_nacimiento': '2015-05-15',
        'genero': 'M',
        'estado': 'activo',
        'padre_id': 4
    }


@pytest.fixture
def test_calificacion():
    """Calificación para pruebas"""
    return {
        'id': 501,
        'estudiante_id': 101,
        'docente_id': 2,
        'materia': 'Matemáticas',
        'primer_trimestre': 85,
        'segundo_trimestre': 88,
        'tercer_trimestre': 90,
        'nota_final': 87.67,
        'estado': 'registrada',
        'fecha_registro': datetime.now().isoformat()
    }


@pytest.fixture
def test_asistencia():
    """Registro de asistencia para pruebas"""
    return {
        'id': 201,
        'estudiante_id': 101,
        'docente_id': 2,
        'fecha': datetime.now().strftime('%Y-%m-%d'),
        'estado_asistencia': 'presente',
        'hora_registro': datetime.now().time().isoformat(),
        'observaciones': 'Asistencia normal'
    }


@pytest.fixture
def test_tarea():
    """Tarea académica para pruebas"""
    return {
        'id': 301,
        'titulo': 'Resolver ejercicios de fracciones',
        'descripcion': 'Resolver 20 ejercicios de operaciones con fracciones',
        'docente_id': 2,
        'grado': '6to B',
        'fecha_creacion': datetime.now().isoformat(),
        'fecha_vencimiento': (datetime.now() + timedelta(days=3)).isoformat(),
        'estado': 'activa'
    }


@pytest.fixture
def test_permiso():
    """Permiso o licencia para pruebas"""
    return {
        'id': 401,
        'estudiante_id': 101,
        'tipo': 'justificación',
        'motivo': 'Cita médica',
        'fecha_inicio': datetime.now().isoformat(),
        'fecha_fin': (datetime.now() + timedelta(days=2)).isoformat(),
        'estado': 'pendiente',
        'aprobado_por': None
    }


@pytest.fixture
def test_reporte_kardex():
    """Reporte académico Kardex para pruebas"""
    return {
        'id': 601,
        'estudiante_id': 101,
        'grado': '6to B',
        'periodo': '2024',
        'nota_final': 87.67,
        'materias_aprobadas': 8,
        'materias_reprobadas': 0,
        'estado_promocion': 'promovido',
        'fecha_generacion': datetime.now().isoformat(),
        'generado_por': 1
    }


@pytest.fixture
def test_notificacion():
    """Notificación para pruebas"""
    return {
        'id': 701,
        'destinatario_id': 4,
        'remitente_id': 2,
        'asunto': 'Calificación registrada: Matemáticas',
        'mensaje': 'Se ha registrado la calificación de Luis Felipe en Matemáticas: 88/100',
        'tipo': 'calificacion',
        'estado': 'no_leida',
        'fecha_envio': datetime.now().isoformat()
    }


@pytest.fixture
def session_user():
    """Sesión de usuario autenticado"""
    return {
        'user_id': 1,
        'user_email': 'director@uelosandes.edu.bo',
        'user_rol': 'director',
        'session_id': 'sess_7f4a8d2c9e1b3f6a',
        'login_time': datetime.now().isoformat(),
        'ip_address': '192.168.1.100'
    }


@pytest.fixture
def payload_sql_injection():
    """Payload malicioso para pruebas de seguridad"""
    return {
        'email': "' OR '1'='1",
        'password': "' DROP TABLE users--",
        'nombre': "'; DELETE FROM estudiantes;--"
    }


@pytest.fixture
def payload_xss():
    """Payload XSS para pruebas de seguridad"""
    return {
        'script': '<script>alert("XSS")</script>',
        'img_tag': '<img src=x onerror="alert(1)">',
        'event_handler': '<div onmouseover="alert(\'XSS\')">'
    }


@pytest.fixture
def payload_buffer_overflow():
    """String masivo para prueba de buffer overflow"""
    return "A" * 5000  # 5000 caracteres


# ============================================================================
# HOOKS - Configuración de pytest
# ============================================================================

def pytest_configure(config):
    """Configuración inicial de pytest"""
    config.addinivalue_line(
        "markers", "smoke: Marca pruebas de humo (smoke tests)"
    )
    config.addinivalue_line(
        "markers", "integration: Marca pruebas de integración"
    )
    config.addinivalue_line(
        "markers", "security: Marca pruebas de seguridad"
    )
    config.addinivalue_line(
        "markers", "e2e: Marca pruebas end-to-end"
    )
    config.addinivalue_line(
        "markers", "unit: Marca pruebas unitarias (caja blanca)"
    )


def pytest_collection_modifyitems(config, items):
    """Modificación de items recolectados"""
    for item in items:
        if "smoke" in item.nodeid:
            item.add_marker(pytest.mark.smoke)
        elif "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        elif "security" in item.nodeid:
            item.add_marker(pytest.mark.security)
        elif "e2e" in item.nodeid:
            item.add_marker(pytest.mark.e2e)
        elif "unit" in item.nodeid:
            item.add_marker(pytest.mark.unit)
