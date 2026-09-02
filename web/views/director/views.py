from django.shortcuts import render, redirect
from django.views import View
from web.models import Estudiante, Maestro, Materia, Usuario

class DirectorDashboardView(View):
    template_name = 'director/dashboard.html'

    def get(self, request):
        if 'id_usuario' not in request.session:
            return redirect('/login/')
            
        if request.session.get('nombre_rol') != 'Director':
            return redirect('/login/')

        stats = {
            'estudiantes': Estudiante.objects.count(),
            'maestros': Maestro.objects.count(),
            'materias': Materia.objects.count(),
            'usuarios': Usuario.objects.filter(activo=True).count(),
        }

        context = {
            'nombres': request.session.get('nombres', 'Director'),
            'nombre_rol': request.session.get('nombre_rol', 'Director'),
            'stats': stats
        }
        
        return render(request, self.template_name, context)