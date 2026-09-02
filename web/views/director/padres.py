from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.db.models import Q
from web.models import Persona, PadreFamilia

class GestionPadresView(View):
    template_name = 'director/gestion_persona.html'

    def get_context(self, request, search_query=None):
        queryset = PadreFamilia.objects.select_related('id_persona').all()
        
        if search_query:
            queryset = queryset.filter(
                Q(id_persona__dni_cedula__icontains=search_query) |
                Q(id_persona__nombres__icontains=search_query) |
                Q(id_persona__apellidos__icontains=search_query)
            )

        listado_estructurado = []
        for pf in queryset:
            listado_estructurado.append({
                'id_entidad_pk': pf.id_padre,
                'persona_obj': pf.id_persona,
                'valor_extra': pf.ocupacion or 'No Declarada',
            })

        # 1. CÁLCULO DE ESTADÍSTICAS REALES EN TIEMPO REAL
        total_padres = PadreFamilia.objects.count()
        varones = PadreFamilia.objects.filter(id_persona__genero='M').count()
        mujeres = PadreFamilia.objects.filter(id_persona__genero='F').count()
        
        # Cuenta cuántas ocupaciones o profesiones diferentes y válidas existen registradas
        ocupaciones_distintas = PadreFamilia.objects.exclude(
            ocupacion__isnull=True
        ).exclude(ocupacion='').values('ocupacion').distinct().count()

        return {
            # 2. VARIABLES INYECTADAS PARA EL NAVBAR DINÁMICO
            'nombres': request.session.get('nombres', 'Director'),
            'nombre_rol': request.session.get('nombre_rol', 'Director'),

            'config': {
                'slug': 'padres',
                'titulo_modulo': 'Padres de Familia / Tutores',
                'entidad_singular': 'Padre de Familia',
                'icono': 'bi-people-fill',
                'label_campo_extra': 'Ocupación / Oficio',
                'placeholder_extra': 'Ej: Ingeniero de Sistemas, Comerciante',
                'options_campo_extra': None,
                
                # Configuración de texto para las 4 tarjetas superiores
                'stat_label_1': 'Tutores Registrados',
                'stat_label_2': 'Padres (Varones)',
                'stat_label_3': 'Madres (Mujeres)',
                'stat_label_4': 'Diversidad Laboral'
            },
            
            # 3. VALORES MATEMÁTICOS PARA LAS TARJETAS (.ref-card)
            'referencias': {
                'stat_1': total_padres,
                'stat_2': varones,
                'stat_3': mujeres,
                'stat_4': ocupaciones_distintas,
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
                p = Persona.objects.create(
                    dni_cedula=request.POST.get('dni_cedula'),
                    nombres=request.POST.get('nombres'),
                    apellidos=request.POST.get('apellidos'),
                    genero=request.POST.get('genero'),
                    fecha_nacimiento=request.POST.get('fecha_nacimiento'),
                    telefono=request.POST.get('telefono')
                )
                PadreFamilia.objects.create(
                    id_persona=p,
                    ocupacion=request.POST.get('campo_extra')
                )
                messages.success(request, "Padre de familia registrado con éxito.")
            except Exception as e:
                messages.error(request, f"Error al insertar tutor: {str(e)}")

        elif action == 'update':
            try:
                padre = get_object_or_404(PadreFamilia, id_padre=request.POST.get('id_entidad'))
                p = padre.id_persona
                p.dni_cedula = request.POST.get('dni_cedula')
                p.nombres = request.POST.get('nombres')
                p.apellidos = request.POST.get('apellidos')
                p.genero = request.POST.get('genero')
                p.fecha_nacimiento = request.POST.get('fecha_nacimiento')
                p.telefono = request.POST.get('telefono')
                p.save()

                padre.ocupacion = request.POST.get('campo_extra')
                padre.save()
                messages.success(request, "Datos de tutoría actualizados correctamente.")
            except Exception as e:
                messages.error(request, f"Fallo de edición: {str(e)}")

        elif action == 'delete':
            try:
                padre = get_object_or_404(PadreFamilia, id_padre=request.POST.get('id_entidad'))
                padre.id_persona.delete()
                messages.warning(request, "Tutor eliminado permanentemente del sistema.")
            except Exception as e:
                messages.error(request, f"Restricción de integridad: No se pudo eliminar al tutor (Verifique si posee alumnos dependientes).")

        return redirect('gestion_padres')

    @classmethod
    def as_index(cls, request):
        return cls().dispatch(request)