# web/views/director/reportes_asistencia.py
"""
Vista de Reportes de Asistencia para Directores
Permite crear, leer, actualizar y eliminar registros de asistencia con estadísticas
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.utils import timezone

from web.models import (
    Asistencia, Estudiante, Materia
)


class ReportesAsistenciaView(View):
    """
    Vista para la gestión integral de Reportes de Asistencia.
    Permite CRUD (Create, Read, Update, Delete) y visualización de estadísticas.
    """

    def get(self, request):
        if 'id_usuario' not in request.session:
            return redirect('/login/')
        
        # Parámetros de búsqueda y filtro
        search_query = request.GET.get('search', '').strip()
        filtro_estudiante = request.GET.get('estudiante', '')
        filtro_materia = request.GET.get('materia', '')
        filtro_estado = request.GET.get('estado', '')
        filtro_fecha_inicio = request.GET.get('fecha_inicio', '')
        filtro_fecha_fin = request.GET.get('fecha_fin', '')

        # Query base
        asistencias = Asistencia.objects.select_related(
            'id_estudiante__id_persona',
            'id_materia'
        ).all()

        # Aplicar búsqueda
        if search_query:
            asistencias = asistencias.filter(
                Q(id_estudiante__id_persona__nombres__icontains=search_query) |
                Q(id_estudiante__id_persona__apellidos__icontains=search_query) |
                Q(id_materia__nombre_materia__icontains=search_query) |
                Q(id_estudiante__codigo_rude__icontains=search_query)
            )

        # Aplicar filtros
        if filtro_estudiante:
            asistencias = asistencias.filter(id_estudiante__id_student=filtro_estudiante)
        if filtro_materia:
            asistencias = asistencias.filter(id_materia__id_materia=filtro_materia)
        if filtro_estado:
            asistencias = asistencias.filter(estado=filtro_estado)
        
        # Filtro de fechas
        if filtro_fecha_inicio:
            asistencias = asistencias.filter(fecha__gte=filtro_fecha_inicio)
        if filtro_fecha_fin:
            asistencias = asistencias.filter(fecha__lte=filtro_fecha_fin)

        # Estadísticas generales
        total_registros = Asistencia.objects.count()
        
        # Contar por estado
        estados_count = Asistencia.objects.values('estado').annotate(count=Count('id_asistencia'))
        estado_dict = {item['estado']: item['count'] for item in estados_count}

        # Estadísticas de asistencia
        presentes = estado_dict.get('PRESENTE', 0)
        faltas = estado_dict.get('FALTA', 0)
        licencias = estado_dict.get('LICENCIA', 0)
        atrasos = estado_dict.get('ATRASO', 0)

        # Porcentajes
        pct_presentes = round((presentes / total_registros * 100), 1) if total_registros > 0 else 0
        pct_faltas = round((faltas / total_registros * 100), 1) if total_registros > 0 else 0

        # Estudiantes únicos
        estudiantes_unicos = Asistencia.objects.values('id_estudiante').distinct().count()

        # Últimos registros
        ultimos_registros = Asistencia.objects.select_related(
            'id_estudiante__id_persona',
            'id_materia'
        ).order_by('-fecha')[:10]

        # Estudiantes para filtro
        estudiantes = Estudiante.objects.select_related('id_persona').all()
        materias = Materia.objects.all()

        estados_opciones = [
            ('PRESENTE', 'Presente'),
            ('FALTA', 'Falta'),
            ('LICENCIA', 'Licencia'),
            ('ATRASO', 'Atraso'),
        ]

        stats = {
            'total_registros': total_registros,
            'presentes': presentes,
            'faltas': faltas,
            'licencias': licencias,
            'atrasos': atrasos,
            'pct_presentes': pct_presentes,
            'pct_faltas': pct_faltas,
            'estudiantes_unicos': estudiantes_unicos,
            'registros_hoy': Asistencia.objects.filter(fecha=timezone.now().date()).count(),
        }

        context = {
            'asistencias': asistencias.order_by('-fecha'),
            'stats': stats,
            'estudiantes': estudiantes,
            'materias': materias,
            'estados': estados_opciones,
            'ultimos_registros': ultimos_registros,
            'search_query': search_query,
            'filtro_estudiante': filtro_estudiante,
            'filtro_materia': filtro_materia,
            'filtro_estado': filtro_estado,
            'filtro_fecha_inicio': filtro_fecha_inicio,
            'filtro_fecha_fin': filtro_fecha_fin,
            'nombres': request.session.get('nombres', 'Director'),
            'nombre_rol': request.session.get('nombre_rol', 'Director'),
        }

        # ✅ RUTA CORRECTA: director/reportes_asistencia.html
        return render(request, 'director/reportes_asistencia.html', context)

    def post(self, request):
        if 'id_usuario' not in request.session:
            return redirect('/login/')
        
        action = request.POST.get('action')

        if action == 'create':
            return self._create_asistencia(request)
        elif action == 'update':
            return self._update_asistencia(request)
        elif action == 'delete':
            return self._delete_asistencia(request)
        
        messages.error(request, 'Acción no reconocida.')
        return redirect('reportes_asistencia')

    def _create_asistencia(self, request):
        """
        Crear un nuevo registro de asistencia
        """
        try:
            id_estudiante = request.POST.get('id_estudiante')
            id_materia = request.POST.get('id_materia')
            fecha = request.POST.get('fecha')
            estado = request.POST.get('estado')

            # Validaciones
            if not all([id_estudiante, id_materia, fecha, estado]):
                messages.error(request, 'Todos los campos son obligatorios.')
                return redirect('reportes_asistencia')

            estudiante = get_object_or_404(Estudiante, id_student=id_estudiante)
            materia = get_object_or_404(Materia, id_materia=id_materia)

            # Verificar que no exista un registro duplicado
            if Asistencia.objects.filter(
                id_estudiante=estudiante,
                id_materia=materia,
                fecha=fecha
            ).exists():
                messages.warning(
                    request,
                    f'Ya existe un registro de asistencia para {estudiante.id_persona.nombres} '
                    f'en {materia.nombre_materia} en esa fecha.'
                )
                return redirect('reportes_asistencia')

            asistencia = Asistencia(
                id_estudiante=estudiante,
                id_materia=materia,
                fecha=fecha,
                estado=estado
            )
            asistencia.save()

            messages.success(
                request,
                f'Registro de asistencia creado: {estudiante.id_persona.nombres} - {estado}'
            )

        except Exception as e:
            messages.error(request, f'Error al crear registro: {str(e)}')

        return redirect('reportes_asistencia')

    def _update_asistencia(self, request):
        """
        Actualizar un registro de asistencia existente
        """
        try:
            id_asistencia = request.POST.get('id_asistencia')
            estado = request.POST.get('estado')

            asistencia = get_object_or_404(Asistencia, id_asistencia=id_asistencia)
            estado_anterior = asistencia.estado

            asistencia.estado = estado
            asistencia.save()

            messages.success(
                request,
                f'Asistencia actualizada: {estado_anterior} → {estado}'
            )

        except Exception as e:
            messages.error(request, f'Error al actualizar registro: {str(e)}')

        return redirect('reportes_asistencia')

    def _delete_asistencia(self, request):
        """
        Eliminar un registro de asistencia
        """
        try:
            id_asistencia = request.POST.get('id_asistencia')
            asistencia = get_object_or_404(Asistencia, id_asistencia=id_asistencia)
            
            estudiante = asistencia.id_estudiante.id_persona.nombres
            asistencia.delete()

            messages.success(
                request,
                f'Registro de asistencia de {estudiante} eliminado permanentemente.'
            )

        except Exception as e:
            messages.error(request, f'Error al eliminar registro: {str(e)}')

        return redirect('reportes_asistencia')


# API para estadísticas por estudiante (AJAX)
def estadisticas_estudiante_api(request, id_estudiante):
    """
    API que retorna estadísticas de asistencia de un estudiante
    """
    try:
        estudiante = get_object_or_404(Estudiante, id_student=id_estudiante)
        
        # Contar por estado para este estudiante
        total = Asistencia.objects.filter(id_estudiante=estudiante).count()
        presentes = Asistencia.objects.filter(id_estudiante=estudiante, estado='PRESENTE').count()
        faltas = Asistencia.objects.filter(id_estudiante=estudiante, estado='FALTA').count()
        licencias = Asistencia.objects.filter(id_estudiante=estudiante, estado='LICENCIA').count()
        atrasos = Asistencia.objects.filter(id_estudiante=estudiante, estado='ATRASO').count()

        stats = {
            'nombre': f"{estudiante.id_persona.nombres} {estudiante.id_persona.apellidos}",
            'rude': estudiante.codigo_rude,
            'total': total,
            'presentes': presentes,
            'faltas': faltas,
            'licencias': licencias,
            'atrasos': atrasos,
            'pct_asistencia': round((presentes / total * 100), 1) if total > 0 else 0,
        }

        return JsonResponse(stats)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# API para obtener materias de un estudiante (AJAX)
def materias_estudiante_api(request, id_estudiante):
    """
    API que retorna materias asociadas a un estudiante
    """
    try:
        # Obtener materias a las que asiste el estudiante
        asistencias = Asistencia.objects.filter(
            id_estudiante__id_student=id_estudiante
        ).values('id_materia__id_materia', 'id_materia__nombre_materia').distinct()

        materias_list = [
            {
                'id': a['id_materia__id_materia'],
                'nombre': a['id_materia__nombre_materia']
            }
            for a in asistencias
        ]

        return JsonResponse({'materias': materias_list})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)