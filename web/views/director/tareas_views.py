from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.db.models import Count, Q
from django.http import JsonResponse
from web.models import Tarea, EntregaTarea, Materia

class TareasDirectorView(View):
    def get(self, request):
        if 'id_usuario' not in request.session:
            return redirect('/login/')

        filtro_materia = request.GET.get('materia', '')

        tareas = Tarea.objects.select_related('id_materia', 'id_maestro__id_persona').all()

        if filtro_materia:
            tareas = tareas.filter(id_materia=filtro_materia)

        total_tareas = tareas.count()
        
        # ⚠️ AJUSTE DE ENUM: Si tu base de datos guardó el ENUM en minúsculas ('entregado', 'pendiente', 'retrasado')
        # Si sigue fallando, cámbialos aquí por cómo estén guardados exactamente en tu tabla 'entrega_tarea'
        total_entregas = EntregaTarea.objects.count()
        entregadas = EntregaTarea.objects.filter(estado__icontains='entregado').count()
        pendientes = EntregaTarea.objects.filter(estado__icontains='pendiente').count()
        retrasadas = EntregaTarea.objects.filter(estado__icontains='retrasado').count()

        kpis = {
            'total_tareas': total_tareas,
            'pct_entregadas': round((entregadas / total_entregas * 100), 1) if total_entregas > 0 else 0,
            'pct_pendientes': round((pendientes / total_entregas * 100), 1) if total_entregas > 0 else 0,
            'pct_retrasadas': round((retrasadas / total_entregas * 100), 1) if total_entregas > 0 else 0,
        }

        context = {
            'tareas': tareas.order_by('-fecha_entrega'),
            'materias': Materia.objects.all(),
            'kpis': kpis,
            'filtro_materia': filtro_materia,
            # Regresamos a tus llaves originales de sesión:
            'nombres': request.session.get('nombres', 'Administrador'),
            'nombre_rol': request.session.get('nombre_rol', 'Director'),
        }
        return render(request, 'director/tareas.html', context)

def api_detalle_tarea(request, id_tarea):
    """ Retorna el desglose de estados de entrega usando filtros insensibles a mayúsculas """
    tarea = get_object_or_404(Tarea, id_tarea=id_tarea)
    entregas = EntregaTarea.objects.filter(id_tarea=tarea)
    
    # Búsqueda manual preventiva para evitar errores de sintaxis ENUM en conversiones estrictas
    entregados = entregas.filter(estado__icontains='entregado').count()
    pendientes = entregas.filter(estado__icontains='pendiente').count()
    retrasados = entregas.filter(estado__icontains='retrasado').count()

    data = {
        'titulo': tarea.titulo,
        'materia': tarea.id_materia.nombre_materia,
        'docente': f"{tarea.id_maestro.id_persona.nombres} {tarea.id_maestro.id_persona.apellidos}",
        'fecha_entrega': tarea.fecha_entrega.strftime('%d/%m/%Y %H:%M'),
        'entregados': entregados,
        'pendientes': pendientes,
        'retrasados': retrasados,
    }
    return JsonResponse(data)