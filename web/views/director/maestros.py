import json
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.db.models import Q
from web.models import Persona, Maestro

class GestionMaestrosView(View):
    template_name = 'director/gestion_persona.html'

    def get_context(self, request, search_query=None):
        # 1. Consulta optimizada para el listado principal
        queryset = Maestro.objects.select_related('id_persona').all()
        
        if search_query:
            queryset = queryset.filter(
                Q(id_persona__dni_cedula__icontains=search_query) |
                Q(id_persona__nombres__icontains=search_query) |
                Q(id_persona__apellidos__icontains=search_query)
            )

        listado_estructurado = []
        for m in queryset:
            listado_estructurado.append({
                'id_entidad_pk': m.id_maestro,
                'persona_obj': m.id_persona,
                'valor_extra': m.especialidad or 'Sin Especialidad',
            })

        # 2. CÁLCULO DE ESTADÍSTICAS REALES EN TIEMPO REAL
        total_maestros = Maestro.objects.count()
        varones = Maestro.objects.filter(id_persona__genero='M').count()
        mujeres = Maestro.objects.filter(id_persona__genero='F').count()
        
        # Cuenta cuántas especialidades diferentes existen configuradas (ignorando vacíos)
        especialidades_distintas = Maestro.objects.exclude(
            especialidad=''
        ).exclude(especialidad__isnull=True).values('especialidad').distinct().count()

        # 3. CONTEXTO TOTAL CON VARIABLES COMPATIBLES CON TU NAVBAR
        return {
            # Claves idénticas a las que usa tu Dashboard para el menú superior
            'nombres': request.session.get('nombres', 'Director'),
            'nombre_rol': request.session.get('nombre_rol', 'Director'),
            
            # Configuración del módulo polimórfico
            'config': {
                'slug': 'maestros',
                'titulo_modulo': 'Profesores / Plantel Docente',
                'entidad_singular': 'Maestro',
                'icono': 'bi-person-workspace',
                'label_campo_extra': 'Especialidad Académica',
                'placeholder_extra': 'Ej: Matemática / Física Cuántica',
                'options_campo_extra': None,
                
                # Etiquetas para las 4 tarjetas del diseño nuevo
                'stat_label_1': 'Total Maestros',
                'stat_label_2': 'Varones',
                'stat_label_3': 'Mujeres',
                'stat_label_4': 'Especialidades',
            },
            
            # Valores matemáticos reales corregidos sin variables fantasma
            'referencias': {
                'stat_1': total_maestros,
                'stat_2': varones,
                'stat_3': mujeres,
                'stat_4':  especialidades_distintas,
            },
            
            'listado': listado_estructurado,
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
                persona = Persona.objects.create(
                    dni_cedula=request.POST.get('dni_cedula'),
                    nombres=request.POST.get('nombres'),
                    apellidos=request.POST.get('apellidos'),
                    genero=request.POST.get('genero'),
                    fecha_nacimiento=request.POST.get('fecha_nacimiento'),
                    telefono=request.POST.get('telefono')
                )
                Maestro.objects.create(
                    id_persona=persona,
                    especialidad=request.POST.get('campo_extra')
                )
                messages.success(request, "Maestro y hoja de persona indexados correctamente.")
            except Exception as e:
                messages.error(request, f"Error al insertar maestro: {str(e)}")

        elif action == 'update':
            try:
                maestro = get_object_or_404(Maestro, id_maestro=request.POST.get('id_entidad'))
                p = maestro.id_persona
                p.dni_cedula = request.POST.get('dni_cedula')
                p.nombres = request.POST.get('nombres')
                p.apellidos = request.POST.get('apellidos')
                p.genero = request.POST.get('genero')
                p.fecha_nacimiento = request.POST.get('fecha_nacimiento')
                p.telefono = request.POST.get('telefono')
                p.save()

                maestro.especialidad = request.POST.get('campo_extra')
                maestro.save()
                messages.success(request, "Datos de docencia actualizados con éxito.")
            except Exception as e:
                messages.error(request, f"Fallo en actualización de maestro: {str(e)}")

        elif action == 'delete':
            try:
                maestro = get_object_or_404(Maestro, id_maestro=request.POST.get('id_entidad'))
                persona = maestro.id_persona
                persona.delete() # Provoca borrado en cascada relacional
                messages.warning(request, "Registro purgado completamente del mapa institucional.")
            except Exception as e:
                messages.error(request, f"Incapacidad de borrado físico: {str(e)}")

        return redirect('gestion_maestros')

    @classmethod
    def as_index(cls, request):
        return cls().dispatch(request)