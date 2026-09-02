import json
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.db.models import Q
from web.models import Persona, Estudiante, PadreFamilia, EstudiantePadre

class GestionEstudiantesView(View):
    template_name = 'director/gestion_persona.html'

    def get_context(self, request, search_query=None):
        queryset = Estudiante.objects.select_related('id_persona').all()
        
        if search_query:
            queryset = queryset.filter(
                Q(id_persona__dni_cedula__icontains=search_query) |
                Q(id_persona__nombres__icontains=search_query) |
                Q(id_persona__apellidos__icontains=search_query) |
                Q(codigo_rude__icontains=search_query)
            )

        listado_estructurado = []
        for est in queryset:
            # Traer los registros relacionales de la tabla estudiante_padre
            relaciones = EstudiantePadre.objects.filter(id_estudiante=est).select_related('id_padre__id_persona')
            
            padres_asociados_lista = []
            json_padres_array = []
            
            for rel in relaciones:
                padres_asociados_lista.append({
                    'padre': rel.id_padre,
                    'parentesco': rel.parentesco,
                    'es_tutor': rel.es_tutor
                })
                json_padres_array.append({
                    'id_padre': rel.id_padre.id_padre,
                    'parentesco': rel.parentesco,
                    'es_tutor': rel.es_tutor
                })

            listado_estructurado.append({
                'id_entidad_pk': est.id_student, # Ojo: mapeado en models.py como id_student
                'persona_obj': est.id_persona,
                'valor_extra': est.codigo_rude,
                'padres_relacionados': padres_asociados_lista,
                'json_padres_str': json.dumps(json_padres_array)
            })

        # 1. CÁLCULO DE ESTADÍSTICAS REALES EN TIEMPO REAL
        total_estudiantes = Estudiante.objects.count()
        varones = Estudiante.objects.filter(id_persona__genero='M').count()
        mujeres = Estudiante.objects.filter(id_persona__genero='F').count()
        
        # Cuenta cuántos estudiantes tienen asignado al menos un tutor legal activo
        con_tutor = EstudiantePadre.objects.filter(es_tutor=True).values('id_estudiante').distinct().count()

        return {
            # 2. VARIABLES ASIGNADAS PARA CORREGIR EL NAVBAR DINÁMICO
            'nombres': request.session.get('nombres', 'Director'),
            'nombre_rol': request.session.get('nombre_rol', 'Director'),

            'config': {
                'slug': 'estudiantes',
                'titulo_modulo': 'Estudiantes Matriculados',
                'entidad_singular': 'Estudiante',
                'icono': 'bi-mortarboard-fill',
                'label_campo_extra': 'Código RUDE Nacional',
                'placeholder_extra': 'Ej: 80740123202305A',
                'options_campo_extra': None,
                
                # Etiquetas dinámicas para renderizar las 4 tarjetas superiores
                'stat_label_1': 'Alumnos Inscritos',
                'stat_label_2': 'Varones',
                'stat_label_3': 'Mujeres',
                'stat_label_4': 'Con Tutor Legal'
            },
            
            # 3. VALORES NUMÉRICOS ENVIADOS A LAS TARJETAS (.ref-card)
            'referencias': {
                'stat_1': total_estudiantes,
                'stat_2': varones,
                'stat_3': mujeres,
                'stat_4': con_tutor,
            },

            'listado': listado_estructurado,
            'padres_disponibles': PadreFamilia.objects.select_related('id_persona').all(),
            'search_query': search_query or ''
        }

    def get(self, request):
        if 'id_usuario' not in request.session or request.session.get('nombre_rol') != 'Director':
            return redirect('/login/')
        query = request.GET.get('search')
        return render(request, self.template_name, self.get_context(request, query))

    def post(self, request):
        if 'id_usuario' not in request.session or request.session.get('nombre_rol') != 'Director':
            return redirect('/login/')

        action = request.POST.get('action')
        
        if action == 'create':
            try:
                p = Persona.objects.create(
                    dni_cedula=request.POST.get('dni_cedula'),
                    nombres=request.POST.get('nombres'),
                    apellidos=request.POST.get('apellidos'),
                    genero=request.POST.get('genero'),
                    fecha_nacimiento=request.POST.get('fecha_nacimiento'),
                    telefono=request.POST.get('telefono')
                )
                estudiante = Estudiante.objects.create(
                    id_persona=p,
                    codigo_rude=request.POST.get('campo_extra')
                )

                # --- PROCESAMIENTO MATEMÁTICO DE RELACIÓN DE PADRES MULTIPLES ---
                padres_ids = request.POST.getlist('padres_ids')
                padres_parentescos = request.POST.getlist('padres_parentescos')
                tutores_indices = request.POST.getlist('padres_tutores_indices')

                for i in range(len(padres_ids)):
                    es_tutor = str(i) in tutores_indices
                    EstudiantePadre.objects.create(
                        id_estudiante=estudiante,
                        id_padre=PadreFamilia.objects.get(id_padre=padres_ids[i]),
                        parentesco=padres_parentescos[i],
                        es_tutor=es_tutor
                    )
                
                messages.success(request, "Estudiante incorporado e historial de consanguinidad guardado.")
            except Exception as e:
                messages.error(request, f"Error en alta de estudiante: {str(e)}")

        elif action == 'update':
            try:
                estudiante = get_object_or_404(Estudiante, id_student=request.POST.get('id_entidad'))
                p = estudiante.id_persona
                p.dni_cedula = request.POST.get('dni_cedula')
                p.nombres = request.POST.get('nombres')
                p.apellidos = request.POST.get('apellidos')
                p.genero = request.POST.get('genero')
                p.fecha_nacimiento = request.POST.get('fecha_nacimiento')
                p.telefono = request.POST.get('telefono')
                p.save()

                estudiante.codigo_rude = request.POST.get('campo_extra')
                estudiante.save()

                # --- RE-ESTRUCTURAR ENLACES DE PADRES (WIPE & REBUILD) ---
                EstudiantePadre.objects.filter(id_estudiante=estudiante).delete()
                
                edit_padres_ids = request.POST.getlist('edit_padres_ids')
                edit_padres_parentescos = request.POST.getlist('edit_padres_parentescos')
                edit_tutores_indices = request.POST.getlist('edit_padres_tutores_indices')

                for i in range(len(edit_padres_ids)):
                    es_tutor = str(i) in edit_tutores_indices
                    EstudiantePadre.objects.create(
                        id_estudiante=estudiante,
                        id_padre=PadreFamilia.objects.get(id_padre=edit_padres_ids[i]),
                        parentesco=edit_padres_parentescos[i],
                        es_tutor=es_tutor
                    )

                messages.success(request, "Historial del estudiante y apoderados modificado.")
            except Exception as e:
                messages.error(request, f"Error de sincronización: {str(e)}")

        elif action == 'delete':
            try:
                estudiante = get_object_or_404(Estudiante, id_student=request.POST.get('id_entidad'))
                estudiante.id_persona.delete()
                messages.warning(request, "Matrícula y enlaces de filiación del alumno borrados.")
            except Exception as e:
                messages.error(request, f"Excepción al purgar alumno: {str(e)}")

        return redirect('gestion_estudiantes')

    @classmethod
    def as_index(cls, request):
        return cls().dispatch(request)