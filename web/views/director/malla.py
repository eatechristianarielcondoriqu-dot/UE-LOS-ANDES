from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from web.models import Gestion, Curso, Materia, CursoMateria

class MallaCurricularView(View):
    template_name = 'director/malla_curricular.html'

    def get_context(self, request):
        gestiones = Gestion.objects.all().order_by('-anio')
        cursos = Curso.objects.all().order_by('nombre', 'paralelo')
        materias = Materia.objects.all().order_by('nombre_materia')

        gestion_id = request.GET.get('gestion_id') or request.session.get('malla_gestion_id')
        gestion_activa = None

        if gestion_id:
            gestion_activa = Gestion.objects.filter(id_gestion=gestion_id).first()
        if not gestion_activa:
            gestion_activa = Gestion.objects.filter(activa=True).first() or gestiones.first()

        if gestion_activa:
            request.session['malla_gestion_id'] = str(gestion_activa.id_gestion)

        # Reconstruimos la matriz adaptada exactamente a tu diseño de lista/fila original
        matriz_malla = []
        relaciones = CursoMateria.objects.select_related('id_materia').all()

        for curso in cursos:
            # Filtrar los registros de curso_materia asociados a este curso en particular
            fila_materias = []
            for rel in relaciones:
                if rel.id_curso_id == curso.id_curso:
                    fila_materias.append({
                        'id_curso_materia': rel.id_curso_materia,
                        'materia': rel.id_materia
                    })
            
            matriz_malla.append({
                'curso': curso,
                'fila': fila_materias  # Lista de asignaturas asignadas a este curso
            })

        return {
            'nombres': request.session.get('nombres', 'Administrador'),
            'nombre_rol': request.session.get('nombre_rol', 'Director'),
            'gestiones': gestiones,
            'gestion_activa': gestion_activa,
            'cursos': cursos,
            'materias': materias,
            'matriz_malla': matriz_malla
        }

    def get(self, request):
        if 'id_usuario' not in request.session:
            return redirect('/login/')
        return render(request, self.template_name, self.get_context(request))

    def post(self, request):
        if 'id_usuario' not in request.session:
            return redirect('/login/')

        action = request.POST.get('action')

        # REGISTRAR EN CURSO_MATERIA
        if action == 'crear_malla':
            curso_id = request.POST.get('id_curso')
            materia_id = request.POST.get('id_materia')
            
            curso = get_object_or_404(Curso, id_curso=curso_id)
            materia = get_object_or_404(Materia, id_materia=materia_id)

            if CursoMateria.objects.filter(id_curso=curso, id_materia=materia).exists():
                messages.warning(request, f"La asignatura {materia.nombre_materia} ya se encuentra asignada a este curso.")
            else:
                CursoMateria.objects.create(id_curso=curso, id_materia=materia)
                messages.success(request, f"Asignatura {materia.nombre_materia} vinculada exitosamente.")

        # ELIMINAR DE CURSO_MATERIA (Si te equivocaste al agregar)
        elif action == 'eliminar_malla':
            id_cm = request.POST.get('id_curso_materia')
            relacion = get_object_or_404(CursoMateria, id_curso_materia=id_cm)
            relacion.delete()
            messages.success(request, "Asignación removida correctamente de la malla.")

        # --- SECCIONES DE SOPORTE INTACTAS ---
        elif action == 'guardar_gestion':
            anio = request.POST.get('anio', '').strip()
            activa = request.POST.get('activa') == 'true'
            if activa:
                Gestion.objects.all().update(activa=False)
            Gestion.objects.create(anio=int(anio), activa=activa)
            messages.success(request, "Gestión agregada correctamente.")

        elif action == 'editar_gestion':
            id_g = request.POST.get('id_gestion')
            gestion = get_object_or_404(Gestion, id_gestion=id_g)
            activa = request.POST.get('activa') == 'true'
            if activa:
                Gestion.objects.all().update(activa=False)
            gestion.anio = int(request.POST.get('anio'))
            gestion.activa = activa
            gestion.save()
            messages.success(request, "Gestión actualizada.")

        elif action == 'eliminar_gestion':
            id_g = request.POST.get('id_gestion')
            get_object_or_404(Gestion, id_gestion=id_g).delete()
            messages.success(request, "Gestión eliminada.")

        elif action == 'guardar_curso':
            nombre = request.POST.get('nombre')
            nivel = request.POST.get('nivel')
            paralelo = request.POST.get('paralelo')
            Curso.objects.create(nombre=nombre, nivel=nivel, paralelo=paralelo)
            messages.success(request, "Curso creado.")

        elif action == 'editar_curso':
            id_c = request.POST.get('id_curso')
            curso = get_object_or_404(Curso, id_curso=id_c)
            curso.nombre = request.POST.get('nombre')
            curso.nivel = request.POST.get('nivel')
            curso.paralelo = request.POST.get('paralelo')
            curso.save()
            messages.success(request, "Curso actualizado.")

        elif action == 'eliminar_curso':
            id_c = request.POST.get('id_curso')
            get_object_or_404(Curso, id_curso=id_c).delete()
            messages.success(request, "Curso eliminado.")

        elif action == 'guardar_materia':
            nombre_materia = request.POST.get('nombre_materia')
            Materia.objects.create(nombre_materia=nombre_materia)
            messages.success(request, "Asignatura agregada.")

        elif action == 'editar_materia':
            id_m = request.POST.get('id_materia')
            materia = get_object_or_404(Materia, id_materia=id_m)
            materia.nombre_materia = request.POST.get('nombre_materia')
            materia.save()
            messages.success(request, "Asignatura actualizada.")

        elif action == 'eliminar_materia':
            id_m = request.POST.get('id_materia')
            get_object_or_404(Materia, id_materia=id_m).delete()
            messages.success(request, "Asignatura eliminada.")

        return redirect('malla_curricular')