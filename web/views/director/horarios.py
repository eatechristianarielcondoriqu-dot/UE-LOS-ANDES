# web/views/director/horarios.py
"""
Vista de Gestión de Horarios para Directores
Permite crear, leer, actualizar y eliminar horarios de clases
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse


from web.models import (
    Horario, Maestro, Materia, Persona, 
    AsignacionDocente, Gestion, Curso
)
from datetime import time


class GestionHorariosView(View):
    """
    Vista para la gestión integral de horarios de clases.
    Permite CRUD (Create, Read, Update, Delete) y visualización de estadísticas.
    """

    def get(self, request):
        if 'id_usuario' not in request.session:
            return redirect('/login/')
    
        """
        GET: Renderiza la página de gestión de horarios con filtros y búsqueda
        """
        # Parámetros de búsqueda y filtro
        search_query = request.GET.get('search', '').strip()
        filtro_maestro = request.GET.get('maestro', '')
        filtro_materia = request.GET.get('materia', '')
        filtro_dia = request.GET.get('dia', '')

        # Query base
        horarios = Horario.objects.select_related(
            'id_maestro__id_persona',
            'id_materia'
        ).all()

        # Aplicar búsqueda
        if search_query:
            horarios = horarios.filter(
                Q(id_maestro__id_persona__nombres__icontains=search_query) |
                Q(id_maestro__id_persona__apellidos__icontains=search_query) |
                Q(id_materia__nombre_materia__icontains=search_query) |
                Q(aula__icontains=search_query)
            )

        # Aplicar filtros
        if filtro_maestro:
            horarios = horarios.filter(id_maestro__id_persona__id_persona=filtro_maestro)
        if filtro_materia:
            horarios = horarios.filter(id_materia__id_materia=filtro_materia)
        if filtro_dia:
            horarios = horarios.filter(dia_semana=filtro_dia)

        # Estadísticas
        stats = {
            'total_horarios': Horario.objects.count(),
            'horarios_activos': horarios.count(),
            'maestros_asignados': Horario.objects.values('id_maestro').distinct().count(),
            'materias_programadas': Horario.objects.values('id_materia').distinct().count(),
        }

        # Datos para selects en formularios
        maestros = Maestro.objects.select_related('id_persona').all()
        materias = Materia.objects.all()
        
        dias_semana = [
            ('LUNES', 'Lunes'),
            ('MARTES', 'Martes'),
            ('MIERCOLES', 'Miércoles'),
            ('JUEVES', 'Jueves'),
            ('VIERNES', 'Viernes'),
            ('SABADO', 'Sábado'),
            ('DOMINGO', 'Domingo'),
        ]

        context = {
            'horarios': horarios,
            'stats': stats,
            'maestros': maestros,
            'materias': materias,
            'dias_semana': dias_semana,
            'search_query': search_query,
            'filtro_maestro': filtro_maestro,
            'filtro_materia': filtro_materia,
            'filtro_dia': filtro_dia,
            'nombres': request.session.get('nombres', 'Administrador'),
            'nombre_rol': request.session.get('nombre_rol', 'Director'),
        }

        return render(request, 'director/horarios.html', context)

    def post(self, request):
        if 'id_usuario' not in request.session:
            return redirect('/login/')
        """
        POST: Procesa acciones CRUD sobre horarios
        """
        action = request.POST.get('action')

        if action == 'create':
            return self._create_horario(request)
        elif action == 'update':
            return self._update_horario(request)
        elif action == 'soft_delete':
            return self._soft_delete_horario(request)
        elif action == 'hard_delete':
            return self._hard_delete_horario(request)
        
        messages.error(request, 'Acción no reconocida.')
        return redirect('gestion_horarios')

    def _create_horario(self, request):
        """
        Crear un nuevo horario
        """
        try:
            id_maestro = request.POST.get('id_maestro')
            id_materia = request.POST.get('id_materia')
            dia_semana = request.POST.get('dia_semana')
            hora_inicio = request.POST.get('hora_inicio')
            hora_fin = request.POST.get('hora_fin')
            aula = request.POST.get('aula')

            # Validaciones
            if not all([id_maestro, id_materia, dia_semana, hora_inicio, hora_fin, aula]):
                messages.error(request, 'Todos los campos son obligatorios.')
                return redirect('gestion_horarios')

            # Validar que la hora_fin sea mayor que hora_inicio
            h_inicio = time.fromisoformat(hora_inicio)
            h_fin = time.fromisoformat(hora_fin)
            
            if h_fin <= h_inicio:
                messages.error(request, 'La hora de fin debe ser posterior a la hora de inicio.')
                return redirect('gestion_horarios')

            maestro = get_object_or_404(Maestro, id_maestro=id_maestro)
            materia = get_object_or_404(Materia, id_materia=id_materia)

            # Verificar conflicto de horarios para el maestro
            conflicto = Horario.objects.filter(
                id_maestro=maestro,
                dia_semana=dia_semana,
                hora_inicio__lt=h_fin,
                hora_fin__gt=h_inicio
            ).exists()

            if conflicto:
                messages.error(
                    request,
                    f'El maestro {maestro.id_persona.nombres} ya tiene una clase asignada en ese horario.'
                )
                return redirect('gestion_horarios')

            horario = Horario(
                id_maestro=maestro,
                id_materia=materia,
                dia_semana=dia_semana,
                hora_inicio=h_inicio,
                hora_fin=h_fin,
                aula=aula
            )
            horario.save()

            messages.success(
                request,
                f'Horario creado exitosamente: {materia.nombre_materia} - {dia_semana}'
            )

        except Exception as e:
            messages.error(request, f'Error al crear horario: {str(e)}')

        return redirect('gestion_horarios')

    def _update_horario(self, request):
        """
        Actualizar un horario existente
        """
        try:
            id_horario = request.POST.get('id_horario')
            id_maestro = request.POST.get('id_maestro')
            id_materia = request.POST.get('id_materia')
            dia_semana = request.POST.get('dia_semana')
            hora_inicio = request.POST.get('hora_inicio')
            hora_fin = request.POST.get('hora_fin')
            aula = request.POST.get('aula')

            horario = get_object_or_404(Horario, id_horario=id_horario)
            maestro = get_object_or_404(Maestro, id_maestro=id_maestro)
            materia = get_object_or_404(Materia, id_materia=id_materia)

            # Validar tiempos
            h_inicio = time.fromisoformat(hora_inicio)
            h_fin = time.fromisoformat(hora_fin)
            
            if h_fin <= h_inicio:
                messages.error(request, 'La hora de fin debe ser posterior a la hora de inicio.')
                return redirect('gestion_horarios')

            # Verificar conflicto (excluyendo el horario actual)
            conflicto = Horario.objects.filter(
                id_maestro=maestro,
                dia_semana=dia_semana,
                hora_inicio__lt=h_fin,
                hora_fin__gt=h_inicio
            ).exclude(id_horario=id_horario).exists()

            if conflicto:
                messages.error(
                    request,
                    f'El maestro {maestro.id_persona.nombres} ya tiene una clase asignada en ese horario.'
                )
                return redirect('gestion_horarios')

            # Actualizar
            horario.id_maestro = maestro
            horario.id_materia = materia
            horario.dia_semana = dia_semana
            horario.hora_inicio = h_inicio
            horario.hora_fin = h_fin
            horario.aula = aula
            horario.save()

            messages.success(request, 'Horario actualizado exitosamente.')

        except Exception as e:
            messages.error(request, f'Error al actualizar horario: {str(e)}')

        return redirect('gestion_horarios')

    def _soft_delete_horario(self, request):
        """
        Eliminación lógica: marcar como inactivo
        """
        try:
            id_horario = request.POST.get('id_horario')
            horario = get_object_or_404(Horario, id_horario=id_horario)
            
            materia = horario.id_materia.nombre_materia
            
            horario.activo = False
            horario.save()

            messages.success(
                request,
                f'Horario de {materia} marcado como inactivo.'
            )

        except Exception as e:
            messages.error(request, f'Error al desactivar horario: {str(e)}')

        return redirect('gestion_horarios')

    def _hard_delete_horario(self, request):
        """
        Eliminación física: borrar definitivamente
        """
        try:
            id_horario = request.POST.get('id_horario')
            horario = get_object_or_404(Horario, id_horario=id_horario)
            
            materia = horario.id_materia.nombre_materia
            
            horario.delete()

            messages.success(
                request,
                f'Horario de {materia} eliminado permanentemente de la base de datos.'
            )

        except Exception as e:
            messages.error(request, f'Error al eliminar horario: {str(e)}')

        return redirect('gestion_horarios')


# API para obtener maestros por materia (AJAX)

def maestros_por_materia_api(request, id_materia):
    """
    API que retorna maestros asignados a una materia específica
    """
    try:
        asignaciones = AsignacionDocente.objects.filter(
            id_materia__id_materia=id_materia
        ).select_related('id_maestro__id_persona').values(
            'id_maestro',
            'id_maestro__id_persona__nombres',
            'id_maestro__id_persona__apellidos'
        ).distinct()

        maestros_list = [
            {
                'id': a['id_maestro'],
                'nombre': f"{a['id_maestro__id_persona__nombres']} {a['id_maestro__id_persona__apellidos']}"
            }
            for a in asignaciones
        ]

        return JsonResponse({'maestros': maestros_list})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)