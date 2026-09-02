from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.db.models import Q
from web.models import Persona, PersonalAdministrativo

class GestionAdministrativosView(View):
    # Ruta limpia sin caracteres especiales ni tildes
    template_name = 'director/gestion_persona.html'

    def get_context(self, request, search_query=None):
        queryset = PersonalAdministrativo.objects.select_related('id_persona').all()
        
        if search_query:
            queryset = queryset.filter(
                Q(id_persona__dni_cedula__icontains=search_query) |
                Q(id_persona__nombres__icontains=search_query) |
                Q(id_persona__apellidos__icontains=search_query)
            )

        listado_estructurado = []
        for adm in queryset:
            listado_estructurado.append({
                'id_entidad_pk': adm.id_admin,
                'persona_obj': adm.id_persona,
                'valor_extra': adm.cargo, # Devuelve el Enum string (DIRECTOR, SECRETARIA, etc.)
            })

        # 1. CÁLCULO DE ESTADÍSTICAS EN TIEMPO REAL (CORREGIDO PARA ENUMS DE POSTGRESQL)
        total_admins = PersonalAdministrativo.objects.count()
        varones = PersonalAdministrativo.objects.filter(id_persona__genero='M').count()
        mujeres = PersonalAdministrativo.objects.filter(id_persona__genero='F').count()
        
        # SOLUCIÓN AL DATAERROR: Para ENUMS solo filtramos por null, nunca por cadena vacía ''
        cargos_activos = PersonalAdministrativo.objects.exclude(
            cargo__isnull=True
        ).values('cargo').distinct().count()

        return {
            # 2. VARIABLES DE CONTEXTO ASIGNADAS PARA TU NAVBAR
            'nombres': request.session.get('nombres', 'Director'),
            'nombre_rol': request.session.get('nombre_rol', 'Director'),

            'config': {
                'slug': 'administrativos',
                'titulo_modulo': 'Cuerpo Técnico y Administrativo',
                'entidad_singular': 'Administrativo',
                'icono': 'bi-person-badge-fill',
                'label_campo_extra': 'Cargo Institucional Asignado',
                'placeholder_extra': None,
                'options_campo_extra': ['DIRECTOR', 'SECRETARIA', 'REGENTE', 'AUXILIAR'],
                
                # Etiquetas para renderizar en las tarjetas superiores
                'stat_label_1': 'Total Personal',
                'stat_label_2': 'Varones',
                'stat_label_3': 'Mujeres',
                'stat_label_4': 'Cargos Activos'
            },
            
            # 3. VALORES NUMÉRICOS ENVIADOS A LAS TARJETAS
            'referencias': {
                'stat_1': total_admins,
                'stat_2': varones,
                'stat_3': mujeres,
                'stat_4': cargos_activos,
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
                PersonalAdministrativo.objects.create(
                    id_persona=p,
                    cargo=request.POST.get('campo_extra')
                )
                messages.success(request, "Miembro del personal técnico registrado.")
            except Exception as e:
                messages.error(request, f"Error en inserción: {str(e)}")

        elif action == 'update':
            try:
                admin = get_object_or_404(PersonalAdministrativo, id_admin=request.POST.get('id_entidad'))
                p = admin.id_persona
                p.dni_cedula = request.POST.get('dni_cedula')
                p.nombres = request.POST.get('nombres')
                p.apellidos = request.POST.get('apellidos')
                p.genero = request.POST.get('genero')
                p.fecha_nacimiento = request.POST.get('fecha_nacimiento')
                p.telefono = request.POST.get('telefono')
                p.save()

                admin.cargo = request.POST.get('campo_extra')
                admin.save()
                messages.success(request, "Rol y cargo administrativo guardados con éxito.")
            except Exception as e:
                messages.error(request, f"Fallo al editar administrativo: {str(e)}")

        elif action == 'delete':
            try:
                admin = get_object_or_404(PersonalAdministrativo, id_admin=request.POST.get('id_entidad'))
                admin.id_persona.delete()
                messages.warning(request, "Funcionario removido del escalafón institucional.")
            except Exception as e:
                messages.error(request, f"Error relacional en eliminación: {str(e)}")

        return redirect('gestion_administrativos')

    @classmethod
    def as_index(cls, request):
        return cls().dispatch(request)