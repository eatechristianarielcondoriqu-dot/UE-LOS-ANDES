<div align="center">

# 🎓 Sistema Web Multiplataforma — Unidad Educativa "Los Andes"

### Seguimiento y Control Académico Estudiantil con Verificación Biométrica Inteligente

[![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.0.5-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-5C3EE8?logo=opencv&logoColor=white)](https://opencv.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![License](https://img.shields.io/badge/Licencia-Uso%20Acad%C3%A9mico-lightgrey)]()

*Un sistema de gestión académica con un motor biométrico propio (firma + rostro) que **aprueba o rechaza justificativos de inasistencia automáticamente**, sin intervención humana.*

</div>

---

## 📖 Índice

- [¿Qué es este proyecto?](#-qué-es-este-proyecto)
- [Lo más destacado](#-lo-más-destacado-el-motor-biométrico)
- [Roles del sistema](#-roles-del-sistema)
- [Stack tecnológico](#-stack-tecnológico)
- [Arquitectura](#-arquitectura)
- [Modelo de datos](#-modelo-de-datos)
- [Estructura del repositorio](#-estructura-del-repositorio)
- [Instalación](#-instalación-y-puesta-en-marcha)
- [Módulos funcionales](#-módulos-funcionales)
- [Seguridad](#-seguridad)
- [Pruebas](#-pruebas)
- [Roadmap](#-roadmap--mejoras-pendientes)
- [Autor](#-autor)

---

## 📌 ¿Qué es este proyecto?

**UE Los Andes** es un sistema web desarrollado con **Django** para digitalizar la gestión académica y administrativa de una unidad educativa: matrícula, calificaciones, asistencia, horarios, tareas, permisos y licencias — todo desde un único portal con **paneles diferenciados por rol** (Director, Maestro, Administrativo y Padre de Familia).

Su diferencial es el módulo de **justificación inteligente de inasistencias**: en lugar de que un administrativo revise manualmente cada solicitud de permiso, el propio sistema **verifica la identidad del padre de familia comparando su firma y su rostro** contra un patrón biométrico registrado previamente, y decide automáticamente si el trámite se **APRUEBA** o se **RECHAZA**.

---

## 🧠 Lo más destacado: el motor biométrico

El módulo `web/views/padre/justificaciones.py` implementa, desde cero y con **OpenCV + scikit-image** (sin frameworks de deep learning ni servicios externos de pago), un pipeline completo de verificación biométrica:

```
 Padre registra su patrón          Padre solicita un permiso
 (1 sola vez)                      (cada trámite)
 ┌─────────────────────┐           ┌──────────────────────────┐
 │  ✍️  Firma en canvas  │           │  ✍️  Firma del trámite     │
 │  📷 Foto por webcam   │           │  📷 Foto del trámite       │
 └──────────┬───────────┘           └────────────┬─────────────┘
            │                                     │
            ▼                                     ▼
     Patrón guardado                    ┌───────────────────────┐
     en el servidor                     │   MOTOR DE COMPARACIÓN │
                                        │  • Binarización Otsu   │
                                        │  • Recorte a tinta     │
                                        │  • cv2.matchShapes     │
                                        │    (Hu-Moments)        │
                                        │  • SSIM estructural    │
                                        │  • Haar Cascade (cara) │
                                        │  • Histograma de color │
                                        └───────────┬────────────┘
                                                    ▼
                                    ¿Firma ✅ Y Rostro ✅ coinciden?
                                       │                  │
                                    SÍ │                  │ NO
                                       ▼                  ▼
                                  APROBADO           RECHAZADO
                             (PDF generado          (queda registrado
                              automáticamente         para revisión)
                              con ReportLab)
```

**Detalles técnicos que vale la pena resaltar:**

- 🔒 **Verificación de dos factores real**: se exige que **firma Y rostro** coincidan (operador `AND`), no basta con que uno solo pase.
- ✍️ **Comparación de firmas por forma, no por trazo**: usa `cv2.matchShapes` (Hu-Moments), que es invariante a escala, traslación y rotación — no le importa si la firma es más grande, más pequeña o está más gruesa, sino si la **forma** coincide.
- 📄 **Doble modalidad de trámite**:
  1. **Formulario biométrico**: firma en `<canvas>` + foto por webcam → el sistema genera automáticamente la carta de justificación en PDF (con `ReportLab`), incrustando la firma y la foto.
  2. **Documento adjunto**: el padre sube un PDF o imagen ya existente → el sistema extrae el texto con `PyMuPDF`, identifica al estudiante y el motivo con expresiones regulares, localiza la firma embebida dentro del documento (distinguiéndola de la foto por su relación de aspecto) y la compara contra el patrón.
- 👨‍💼 **Supervisión humana disponible**: el Director puede revisar el historial completo de trámites y **anular manualmente** el veredicto de la IA vía una API AJAX, dejando un sello de auditoría con su nombre y fecha.

---

## 👥 Roles del sistema

| Rol | Puede hacer |
|---|---|
| 🧑‍💼 **Director** | Gestionar usuarios, roles, maestros, estudiantes, padres, administrativos, malla curricular, asignación de docentes, horarios, calificaciones, tareas, reportes de asistencia y revisar/anular justificativos generados por la IA. |
| 👨‍🏫 **Maestro** | Ver su panel con tareas creadas, entregas recibidas, materias y estudiantes a su cargo. |
| 👨‍👩‍👧 **Padre de Familia** | Ver el seguimiento académico de sus hijos y tramitar justificativos de inasistencia mediante el motor biométrico. |
| 🗂️ **Administrativo** | Panel de apoyo a la gestión institucional. |

---

## 🛠️ Stack tecnológico

| Categoría | Tecnología |
|---|---|
| **Backend** | Python 3 + Django 6.0.5 (arquitectura MVT clásica) |
| **Base de datos** | PostgreSQL (modelos generados vía `inspectdb`, `managed = False`) |
| **Frontend** | HTML5, CSS3, JavaScript (vanilla) + Bootstrap 5.3 + Font Awesome 6.4 |
| **Visión por computadora** | OpenCV (`cv2`), scikit-image (SSIM), NumPy |
| **Procesamiento de documentos** | PyMuPDF (`fitz`) para lectura de PDF, ReportLab para generación de PDF |
| **Seguridad de acceso** | Google reCAPTCHA v2, hashing de contraseñas con `django.contrib.auth.hashers` |
| **Sesión y autenticación** | Sistema de sesión propio sobre tabla `Usuario` (independiente de `django.contrib.auth.User`) |

---

## 🏗️ Arquitectura

```
Navegador (Bootstrap + JS: canvas de firma, captura de webcam, filtros AJAX)
        │  HTTP (formularios POST / fetch AJAX)
        ▼
Django (Views por rol en web/views/{director,maestro,padre,administrativo}/)
        │  ORM
        ▼
PostgreSQL (persona, usuario, estudiante, maestro, asistencia, tarea, ...)
        │
        ▼
Motor biométrico (OpenCV + scikit-image) ── genera/lee PDFs (ReportLab / PyMuPDF)
```

**Patrón de enrutamiento:** las URLs específicas se declaran antes que las genéricas en `mi_sitio/urls.py`, y el acceso al dashboard pasa siempre por un único punto de entrada (`DashboardRouterView`) que redirige según el rol guardado en sesión — evitando URLs de dashboard "adivinables" por rol.

**Patrón de vistas repetido:** los módulos de gestión del Director (usuarios, maestros, estudiantes, padres, administrativos) comparten una misma estructura: `get_context()` para preparar los datos + un único `post()` que despacha por un parámetro `action` (`create`, `update`, `toggle_status`, `soft_delete`, `hard_delete`), reutilizando incluso la misma plantilla (`gestion_persona.html`) mediante un diccionario de configuración (`config`) que cambia las etiquetas según la entidad.

---

## 🗄️ Modelo de datos

`Persona` actúa como entidad base, y los distintos roles institucionales se modelan como tablas satélite vinculadas por clave foránea/uno-a-uno:

```
Persona ──┬── Estudiante ── EstudiantePadre ── PadreFamilia
          ├── Maestro
          ├── PadreFamilia
          └── PersonalAdministrativo

Usuario ── (persona + rol + credenciales de acceso)

Curso ── CursoMateria ── Materia ── AsignacionDocente ── Maestro
Estudiante ── Inscripcion ── Curso ── Gestion (año lectivo)
Estudiante ── Asistencia ── Materia
Maestro ── Tarea ── EntregaTarea ── Estudiante
PadreFamilia ── DocumentoJustificacion ── Estudiante
Maestro ── Horario ── Materia
```

> El campo `firma_base` de `PadreFamilia` guarda las rutas de las imágenes patrón (firma + rostro) usadas por el motor biométrico.

---

## 📁 Estructura del repositorio

```
UE_LosAndes/
├── manage.py
├── mi_sitio/                     # Configuración del proyecto Django
│   ├── settings.py
│   ├── urls.py                   # Enrutador principal
│   └── wsgi.py / asgi.py
├── web/                          # Aplicación principal
│   ├── models.py                 # Modelos (inspectdb desde PostgreSQL)
│   ├── views/
│   │   ├── auth_views.py         # Login/Logout + reCAPTCHA
│   │   ├── dashboard_router.py   # Enrutador por rol
│   │   ├── public_views.py       # Landing pública
│   │   ├── director/             # 14 módulos de gestión institucional
│   │   ├── maestro/
│   │   ├── padre/                # Incluye el motor biométrico
│   │   └── administrativo/
│   └── templates/
│       ├── web/                  # Login y landing
│       ├── includes/navbar.html  # Navbar compartido
│       ├── director/ · maestro/ · padre/ · administrativo/
├── static/
│   ├── css/ · js/                # Un archivo por módulo funcional
│   ├── img/                      # Firmas y fotos capturadas (patrón y trámites)
│   ├── pdf/                      # Justificativos generados automáticamente
│   └── adjuntos/                 # Documentos subidos por los padres
└── test/                         # Suite de pruebas con pytest
```

---

## 🚀 Instalación y puesta en marcha

### Requisitos previos
- Python 3.11+
- PostgreSQL en ejecución
- Una cámara web (para el módulo biométrico)

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/<tu-usuario>/UE_LosAndes.git
cd UE_LosAndes

# 2. Crear y activar un entorno virtual
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

# 3. Instalar dependencias
pip install django psycopg2-binary opencv-python scikit-image numpy \
            PyMuPDF reportlab requests

# 4. Configurar la base de datos
# Crea una base llamada "sistema_educativo" en PostgreSQL y ajusta las
# credenciales en mi_sitio/settings.py (usuario, contraseña, host, puerto).

# 5. Ejecutar el servidor de desarrollo
python manage.py runserver
```

Luego abre `http://127.0.0.1:8000/` en el navegador.

> ⚠️ **Antes de desplegar en producción**: cambia `DEBUG = False`, mueve `SECRET_KEY` y las credenciales de la base de datos a variables de entorno, y configura `ALLOWED_HOSTS`.

---

## 🧩 Módulos funcionales

- **Autenticación** — Login con reCAPTCHA, sesión propia por rol, logout con `session.flush()`.
- **Gestión de usuarios** — CRUD completo con activar/desactivar, eliminación lógica y física, buscador y filtro dinámico de "personas disponibles" para crear cuentas.
- **Gestión de personas** (estudiantes, maestros, padres, administrativos) — Alta/edición/baja con vínculos familiares múltiples (un estudiante puede tener varios padres/tutores).
- **Malla curricular** — Gestión de años lectivos, cursos, materias y su relación curso↔materia.
- **Asignación docente** — Asigna maestros a materias por curso y gestión, con exportación a PDF (general e individual por curso).
- **Horarios** — CRUD de horarios con **validación de choques de horario** por maestro.
- **Calificaciones** — KPIs (promedio, máxima, mínima, % aprobados/reprobados) con filtros por curso/materia y gráfico de rendimiento vía API.
- **Tareas** — Publicación de tareas, seguimiento de entregas (entregado/pendiente/retrasado) con detalle vía API.
- **Reportes de asistencia** — CRUD de asistencia con estadísticas en tiempo real y consulta por estudiante vía API.
- **Justificaciones inteligentes** — El motor biométrico descrito arriba, con panel de auditoría para el Director.

---

## 🔐 Seguridad

- Verificación **reCAPTCHA v2** en el login.
- Contraseñas con hashing de Django (`make_password` / `check_password`), nunca en texto plano.
- Control de acceso por rol verificado en cada vista contra la sesión activa.
- Auditoría de las decisiones manuales del Director sobre los justificativos (queda registrado quién, cuándo y qué cambió).

---

## 🧪 Pruebas

El proyecto incluye una suite en `test/` con **pytest** organizada en 5 categorías (unitarias, integración, seguridad, E2E y humo).

```bash
cd test
pip install -r requirements.txt
pytest -v
```

> **Nota de mantenimiento:** la suite actual está pensada como plantilla/documentación de casos de prueba y todavía no ejecuta contra la aplicación Django real (no usa `django.test.TestCase` ni importa `web.models`). Es un buen punto de partida para escribir pruebas de integración reales con el ORM y el cliente de pruebas de Django.

---

## 🗺️ Roadmap / mejoras pendientes

- [ ] Corregir `GestionHorariosView._soft_delete_horario`, que referencia un campo `activo` inexistente en el modelo `Horario`.
- [ ] Conectar o retirar `GestionPersonalView` (no está enlazada en `urls.py` ni tiene plantilla).
- [ ] Externalizar `SECRET_KEY` y credenciales de base de datos a variables de entorno.
- [ ] Migrar la suite de pruebas a `django.test.TestCase` contra la base real.
- [ ] Sustituir el chequeo de sesión repetido en cada vista por un mixin/decorador (`LoginRequiredMixin` + verificación de rol).

---

## 👤 Autor

**Christian Ariel Condori Quispe**
Ingeniería de Sistemas — Universidad Privada Franz Tamayo
Proyecto de Grado — El Alto, Bolivia

---

<div align="center">

*Desarrollado con fines académicos para la Unidad Educativa "Los Andes".*

</div>
