from django.shortcuts import render, redirect
from django.views import View
from web.models import Maestro, Tarea, EntregaTarea

class MaestroDashboardView(View):
    # ¡IMPORTANTE! Cambiamos la ruta para que busque en una carpeta 'maestro' 
    # y así no se confunda con el panel del director
    template_name = 'maestro/dashboard.html' 

    def get(self, request):
        # 1. Seguridad: Verificar si la sesión existe
        if 'id_usuario' not in request.session:
            return redirect('/login/') # Redirección externa limpia al login si no está autenticado

        # 2. Verificar estrictamente el rol
        if request.session.get('nombre_rol') != 'Maestro':
            # Si NO es maestro, lo mandamos al login para romper el bucle infinito de inmediato
            return redirect('/login/') 

        id_persona_sesion = request.session.get('id_persona')
        
        # 3. Obtener el ID del maestro asociado a la persona logueada
        try:
            maestro = Maestro.objects.get(id_persona=id_persona_sesion)
            id_maestro = maestro.id_maestro
        except Maestro.DoesNotExist:
            id_maestro = None

        # 4. Inicializar estadísticas en ceros
        stats = {'tareas': 0, 'entregas': 0, 'materias': 0, 'estudiantes': 0}

        if id_maestro:
            # Contar tareas creadas por el maestro
            stats['tareas'] = Tarea.objects.filter(id_maestro=id_maestro).count()

            # Contar entregas asociadas a las tareas del maestro
            stats['entregas'] = EntregaTarea.objects.filter(id_tarea__id_maestro=id_maestro).count()

            # Contar materias únicas donde el maestro ha asignado tareas
            stats['materias'] = Tarea.objects.filter(id_maestro=id_maestro).values('id_materia').distinct().count()

            # Contar estudiantes únicos que han entregado tareas al maestro
            stats['estudiantes'] = EntregaTarea.objects.filter(id_tarea__id_maestro=id_maestro).values('id_estudiante').distinct().count()

        # 5. Contexto para la plantilla
        context = {
            'nombres': request.session.get('nombres', 'Maestro'),
            'nombre_rol': request.session.get('nombre_rol', 'maestro'),
            'stats': stats
        }
        
        return render(request, self.template_name, context)