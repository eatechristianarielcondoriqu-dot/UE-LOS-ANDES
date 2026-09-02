from django.shortcuts import render, redirect
from django.views import View
from django.db.models import Avg, Max, Min, Count, Q
from django.http import JsonResponse
from web.models import EntregaTarea, Curso, Materia, Estudiante

class CalificacionesDirectorView(View):
    def get(self, request):
        if 'id_usuario' not in request.session:
            return redirect('/login/')

        # Filtros del Request
        filtro_curso = request.GET.get('curso', '')
        filtro_materia = request.GET.get('materia', '')
        search_query = request.GET.get('search', '').strip()

        # Query base de entregas calificadas
        entregas = EntregaTarea.objects.select_related(
            'id_estudiante__id_persona', 
            'id_tarea__id_materia', 
            'id_tarea__id_maestro__id_persona'
        ).filter(calificacion__isnull=False)

        # Aplicación estricta de filtros
        if filtro_curso:
            entregas = entregas.filter(id_estudiante__inscripcion__id_curso=filtro_curso)
        if filtro_materia:
            entregas = entregas.filter(id_tarea__id_materia=filtro_materia)
        if search_query:
            entregas = entregas.filter(
                Q(id_estudiante__id_persona__nombres__icontains=search_query) |
                Q(id_estudiante__id_persona__apellidos__icontains=search_query) |
                Q(id_tarea__titulo__icontains=search_query)
            )

        # KPIs Globales (Dinámicos al filtro)
        stats = entregas.aggregate(
            promedio_gen=Avg('calificacion'),
            nota_maxima=Max('calificacion'),
            nota_minima=Min('calificacion'),
            total_evaluados=Count('id_entrega')
        )

        # Contar aprobados (>= 51) y reprobados (< 51)
        aprobados = entregas.filter(calificacion__gte=51).count()
        reprobados = entregas.filter(calificacion__lt=51).count()
        total = stats['total_evaluados'] or 1
        
        kpis = {
            'promedio': round(stats['promedio_gen'] or 0, 1),
            'maxima': round(stats['nota_maxima'] or 0, 1),
            'minima': round(stats['nota_minima'] or 0, 1),
            'total_registros': stats['total_evaluados'],
            'pct_aprobados': round((aprobados / total) * 100, 1) if total > 0 else 0,
            'pct_reprobados': round((reprobados / total) * 100, 1) if total > 0 else 0,
        }

        context = {
            'entregas': entregas.order_by('-id_entrega')[:100], # Top 100 recientes
            'cursos': Curso.objects.all(),
            'materias': Materia.objects.all(),
            'kpis': kpis,
            'filtro_curso': filtro_curso,
            'filtro_materia': filtro_materia,
            'search_query': search_query,
            'nombres': request.session.get('nombres', 'Administrador'),
            'nombre_rol': request.session.get('nombre_rol', 'Director'),
        }
        return render(request, 'director/calificaciones.html', context)

def api_rendimiento_curso(request, id_curso):
    """ Retorna datos promedio por materia de un curso específico para construir gráficos """
    entregas = EntregaTarea.objects.filter(
        id_estudiante__inscripcion__id_curso=id_curso, 
        calificacion__isnull=False
    ).values('id_tarea__id_materia__nombre_materia').annotate(promedio=Avg('calificacion'))

    datos = {item['id_tarea__id_materia__nombre_materia']: round(item['promedio'], 1) for item in entregas}
    return JsonResponse({'rendimiento': datos})