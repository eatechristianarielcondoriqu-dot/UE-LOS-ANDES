"""
URL configuration for mi_sitio project.
"""
from django.contrib import admin
# IMPORTANTE: Añadimos re_path aquí junto a path
from django.urls import path, re_path 

# Importaciones modulares desde tu carpeta views
from web.views.public_views import IndexDashboardView
from web.views.auth_views import LoginView, LogoutView
from web.views.dashboard_router import DashboardRouterView
from web.views.director.views import DirectorDashboardView
from web.views.director.usuarios import GestionUsuariosView
from web.views.maestro.views import MaestroDashboardView
from web.views.padre.views import PadreDashboardView

from web.views.director.maestros import GestionMaestrosView
from web.views.director.estudiantes import GestionEstudiantesView
from web.views.director.padres import GestionPadresView
from web.views.director.administrativos import GestionAdministrativosView
from web.views.director.roles import GestionRolesView
from web.views.director.malla import MallaCurricularView
from web.views.director.asignacion_maestro import ( AsignacionMaestroView, AsignacionesFiltradasAPI, exportar_malla_general_pdf, exportar_malla_curso_pdf)
from web.views.director.justificaciones import ( DirectorJustificacionesView, ActualizarEstadoJustificacionAPI,)
from web.views.director.horarios import ( GestionHorariosView, maestros_por_materia_api)
from web.views.director.reportes_asistencia import ( ReportesAsistenciaView, estadisticas_estudiante_api, materias_estudiante_api)
from web.views.director import calificaciones_views, tareas_views

from web.views.padre.justificaciones import JustificacionTensorFlowView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexDashboardView.as_view(), name='index'),
    path('login/', LoginView.as_view(), name='login'),
    path('accounts/login/', LoginView.as_view()), 
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # 1. RUTAS ESPECÍFICAS (Django las evaluará primero sin interferencias)
    path('dashboard/director/gestion-usuarios/', GestionUsuariosView.as_view(), name='gestion_usuarios'),
    path('dashboard/director/', DirectorDashboardView.as_view(), name='dashboard_director'),
    path('dashboard/maestro/', MaestroDashboardView.as_view(), name='maestro_dashboard'),
    path('dashboard/padre/', PadreDashboardView.as_view(), name='padre_dashboard'),

    # 2. ENRUTADOR ESTRICTO (Usa re_path con el símbolo '$' al final)
    # Esto significa: "Solo se activa si la URL termina exactamente en dashboard/ o dashboard"
    # No tocará jamás a 'dashboard/director/gestion-usuarios/'
    re_path(r'^dashboard/?$', DashboardRouterView.as_view(), name='dashboard_router'),
    path('director/maestros/', GestionMaestrosView.as_index, name='gestion_maestros'),
    path('director/estudiantes/', GestionEstudiantesView.as_index, name='gestion_estudiantes'),
    path('director/padres/', GestionPadresView.as_index, name='gestion_padres'),
    path('director/administrativos/', GestionAdministrativosView.as_index, name='gestion_administrativos'),
    path('dashboard/padre/justificaciones/', JustificacionTensorFlowView.as_view(), name='justificacion_tf'),
    path('director/roles/', GestionRolesView.as_view(), name='gestion_roles'),
    path('dashboard/director/justificaciones/', DirectorJustificacionesView.as_view(), name='director_justificaciones'),
    path('dashboard/director/justificaciones/api/actualizar-estado/', ActualizarEstadoJustificacionAPI.as_view(), name='actualizar_estado_justificacion'),
    path('dashboard/director/reportes-asistencia/', ReportesAsistenciaView.as_view(), name='reportes_asistencia'),
    path('api/estadisticas-estudiante/<int:id_estudiante>/', estadisticas_estudiante_api, name='estadisticas_estudiante_api'),
    path('api/materias-estudiante/<int:id_estudiante>/', materias_estudiante_api, name='materias_estudiante_api'),
    # Malla Curricular Principal
    path('director/malla-curricular/', MallaCurricularView.as_view(), name='malla_curricular'),
    path('dashboard/director/horarios/', GestionHorariosView.as_view(), name='gestion_horarios'),
    path('api/maestros-por-materia/<int:id_materia>/', maestros_por_materia_api, name='maestros_por_materia_api'),

    # Módulo de Calificaciones
    path('dashboard/director/calificaciones/', calificaciones_views.CalificacionesDirectorView.as_view(), name='director_calificaciones'),
    path('api/director/calificaciones/curso/<int:id_curso>/', calificaciones_views.api_rendimiento_curso, name='api_rendimiento_curso'),

    # Módulo de Tareas
    path('dashboard/director/tareas/', tareas_views.TareasDirectorView.as_view(), name='director_tareas'),
    path('api/director/tareas/<int:id_tarea>/', tareas_views.api_detalle_tarea, name='api_detalle_tarea'),
    
    # Panel Principal de Carga Horaria y Asignación de Maestros
    path('director/asignacion-maestros/', AsignacionMaestroView.as_view(), name='asignacion_maestros'),

    # Rutas activas para descargas de Reportes PDF
    path('director/asignacion-maestros/pdf/general/<int:id_gestion>/', exportar_malla_general_pdf, name='pdf_malla_general'),
    path('director/asignacion-maestros/pdf/curso/<int:id_curso>/<int:id_gestion>/', exportar_malla_curso_pdf, name='pdf_malla_curso'),
    path('director/asignacion-maestros/api/materias-disponibles/', AsignacionesFiltradasAPI.as_view(), name='materias_disponibles_api'),
]