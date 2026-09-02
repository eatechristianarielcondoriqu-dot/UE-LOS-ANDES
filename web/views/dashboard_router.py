from django.shortcuts import redirect
from django.views import View

class DashboardRouterView(View):
    def get(self, request):
        # Si no ha iniciado sesión, directo al login
        if 'id_usuario' not in request.session:
            return redirect('/login/')
        
        # Obtenemos el nombre del rol guardado por el LoginView
        rol = request.session.get('nombre_rol', '')

        # Validamos el rol ignorando mayúsculas o minúsculas
        if rol.lower() == 'director':
            return redirect('/dashboard/director/')
        elif rol.lower() == 'administrativo':
            return redirect('/dashboard/administrativo/')
        elif rol.lower() == 'maestro':
            return redirect('/dashboard/maestro/')
        elif rol.lower() == 'padre de familia':
            return redirect('/dashboard/padre/')
        else:
            return redirect('/login/')