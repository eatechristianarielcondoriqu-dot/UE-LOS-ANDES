from django.shortcuts import render, redirect
from django.views import View
from web.models import PadreFamilia, Estudiante

class PadreDashboardView(View):
    template_name = 'padre/dashboard.html'

    def get(self, request):
        if 'id_usuario' not in request.session or request.session.get('nombre_rol') != 'Padre de Familia':
            request.session.flush()
            return redirect('/login/')

        id_persona_sesion = request.session.get('id_persona')
        try:
            padre = PadreFamilia.objects.get(id_persona=id_persona_sesion)
        except PadreFamilia.DoesNotExist:
            padre = None

        stats = {'hijos': 0, 'materias': 0, 'tareas_pendientes': 0, 'calificaciones': 0}

        if padre:
            stats['hijos'] = Estudiante.objects.filter(estudiantepadre__id_padre=padre).count()
            from web.models import Asistencia, EntregaTarea
            stats['materias'] = Asistencia.objects.filter(
                id_estudiante__estudiantepadre__id_padre=padre
            ).values('id_materia').distinct().count()
            stats['tareas_pendientes'] = EntregaTarea.objects.filter(
                id_estudiante__estudiantepadre__id_padre=padre, estado='NO_ENTREGADO'
            ).count()   
            stats['calificaciones'] = EntregaTarea.objects.filter(
                id_estudiante__estudiantepadre__id_padre=padre, calificacion__isnull=False
            ).count()

        context = {
            'nombres': request.session.get('nombres', 'Padre / Tutor'),
            'nombre_rol': request.session.get('nombre_rol', 'Padre de Familia'),
            'stats': stats
        }
        return render(request, self.template_name, context)